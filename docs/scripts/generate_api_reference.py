import re
from typing import Any
import typing
import docstring_parser
import inspect
import sys
import os

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(PROJECT_DIR)

import src


def get_object_source(obj: Any) -> tuple[str, str]:
    """Get the source code of an object and split it into decorator
    and header. Works for functions and classes. The header is useful
    because `inspect` does not provide the full inheritance information
    (like generics) for classes.
    
    For the following code:

    ```python
    @decorator(
        arg1: int,
    )
    @decorator2
    def function(arg: int) -> str:
        pass
    ```

    The output will be:

    ```
    (
        "@decorator(\n    arg1: int,\n)\n@decorator2",
        "def function(arg: int) -> str:"
    )
    ```

    Args:
        obj: The object to get the source code from.
    
    Returns:
        A tuple containing the decorator (0) and the header (1)
        of the object.
    """
    s = inspect.getsource(obj)
    indent: str = re.match(r"^(\s*)", s).group(0)
    s = "\n".join([l[len(indent):] for l in s.split("\n")])
    decorator: str = ""
    header: str = ""
    for i, l in enumerate(s.split("\n")):
        if l.startswith("def ") or l.startswith("class "):
            decorator = "\n".join(s.split("\n")[: i])
            header = "\n".join(s.split("\n")[i :])
            break

    header_depth: int = 0
    for i, c in enumerate(header):
        if c == "(":
            header_depth += 1
        if c == ")":
            header_depth -= 1
        if c == ":" and header_depth == 0:
            header = header[: i + 1]
            break
    return decorator, header


def clean_type_name(type_name: Any) -> str:
    type_name = str(type_name).replace("NoneType", "None")
    if type_name.startswith("<class '") and type_name.endswith("'>"):
        type_name = type_name[8 :-2]
    return type_name


def prettify_docstring(module: Any) -> str:
    doc: str
    try:
        doc = module.__doc__
        assert isinstance(doc, str)
    except:
        return ""

    docstring = docstring_parser.parse(doc)
    docstring_text: str = ""

    if docstring.short_description is not None:
        docstring_text += docstring.short_description + "\n\n"

    if docstring.long_description is not None:
        docstring_text += docstring.long_description + "\n\n"

    params = [
        f" * `{param.arg_name}`: {param.description}"
        for param in docstring.params if param.description is not None
    ]
    if len(params) > 0:
        docstring_text += "**Arguments:**\n\n"
        docstring_text += "\n".join(params) + "\n\n"

    if (docstring.returns
        is not None) and (docstring.returns.description is not None):
        docstring_text += f"**Returns:** {docstring.returns.description}\n\n"

    raises = [
        f" * `{raises.type_name}`: {raises.description}"
        for raises in docstring.raises
        if ((raises.description is not None) and (raises.type_name is not None))
    ]
    if len(raises) > 0:
        docstring_text += "**Raises:**\n\n"
        docstring_text += "\n".join(raises) + "\n\n"

    return docstring_text


def _render_variables(module: object, module_depth: int) -> str:
    type_hints = typing.get_type_hints(module)
    type_hint_extras = typing.get_type_hints(module, include_extras=True)
    output: str = ""
    if len(type_hints) > 0:
        output += f"{'#' * (module_depth + 1)} Variables\n\n"
        for name, type_hint in type_hints.items():
            output += f"```python\n{name}: {clean_type_name(type_hint)}\n```\n\n"
            if name in type_hint_extras:
                extra_type_hint = type_hint_extras[name]
                if isinstance(extra_type_hint, typing._AnnotatedAlias):
                    metadata = extra_type_hint.__metadata__
                    if len(metadata) > 0 and isinstance(metadata[0], str):
                        output += f"{metadata[0]}\n\n"
    return output


def _render_function(function: Any) -> str:
    output = f"**`{function.__name__}`**\n\n```python\n"
    decorators, _ = get_object_source(function)
    if decorators != "":
        output += f"{decorators}\n"
    # it is good to use the argspec instead of the header
    # because the header might contain some weird edge cases
    # that are not correclty parsed by `get_object_source`
    output += f"def {function.__name__}"
    argspec = inspect.getfullargspec(function)
    type_hints = typing.get_type_hints(function)
    if len(argspec.args) == 0:
        output += f"() -> {clean_type_name(type_hints.get('return', Any))}:\n```\n\n"
    else:
        output += "(\n"
        for i, arg in enumerate(argspec.args):
            output += f"    {arg}"
            if i > 0 or arg != "self":
                annotation = type_hints.get(arg, Any)
                output += f": {clean_type_name(annotation)}"
                if argspec.defaults is not None and arg in argspec.defaults:
                    output += f" = {argspec.defaults[argspec.args.index(arg)]}"
            output += ",\n"
        output += f") -> {clean_type_name(type_hints.get('return', Any))}:\n```\n\n"

    output += prettify_docstring(function)
    return output


def get_module_markdown(module: object, module_depth: int = 1) -> str:
    output = f"{'#' * module_depth} `{module.__name__}`\n\n"
    if module.__doc__ is not None:
        output += f"{module.__doc__}\n\n"

    output += _render_variables(module, module_depth)

    if module.__file__.endswith("__init__.py"):
        for m in sorted(
            inspect.getmembers(module, inspect.ismodule),
            key=lambda x: 1 if x[1].__file__.endswith("__init__.py") else 0
        ):
            output += get_module_markdown(m[1], module_depth + 1)
    else:
        functions = [
            f[1] for f in inspect.getmembers(module, inspect.isfunction)
            if (f[1].__module__ == module.__name__)
        ]
        if len(functions) > 0:
            output += f"{'#' * (module_depth + 1)} Functions\n\n"
            for function in functions:
                output += _render_function(function)

        classes = [
            c[1] for c in inspect.getmembers(module, inspect.isclass)
            if c[1].__module__ == module.__name__ and not c[0].startswith("_")
        ]
        if len(classes) > 0:
            output += f"{'#' * (module_depth + 1)} Classes\n\n"
            for c in classes:
                decorators, header = get_object_source(c)

                output += f"**`{c.__name__}`**\n\n```python\n"
                if decorators != "":
                    output += f"{decorators}\n"
                output += f"{header}\n```\n\n"

                output += prettify_docstring(c)

                for member in inspect.getmembers(c):
                    if inspect.isfunction(member[1]):
                        function = member[1]
                        if ((
                            function.__name__.startswith("__") and
                            (function.__name__ != "__init__")
                        ) or (function.__name__ not in c.__dict__)):
                            continue
                        output += _render_function(function)

    return output


markdown_content = get_module_markdown(src)
with open(
    os.path.join(PROJECT_DIR, "docs", "pages", "api-reference", "src.md"), "w"
) as f:
    f.write("# API Reference of the `src` Module\n\n")
    f.write(markdown_content)
