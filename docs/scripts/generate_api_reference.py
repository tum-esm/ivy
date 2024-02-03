from typing import Any
import typing
import docstring_parser
import inspect
import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)

import src


def clean_type_name(type_name: Any) -> str:
    type_name = str(type_name)
    if type_name.startswith("<class '") and type_name.endswith("'>"):
        return type_name[8 :-2]
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


def get_module_markdown(module: object, module_depth: int = 1) -> str:
    output = f"{'#' * module_depth} `{module.__name__}`\n\n"
    if module.__doc__ is not None:
        output += f"{module.__doc__}\n\n"

    if not module.__file__.endswith("__init__.py"):
        variables = inspect.get_annotations(module)
        if len(variables) > 0:
            output += f"{'#' * (module_depth + 1)} Variables\n\n"
            for var, t in variables.items():
                output += f"```python\n{var}: "
                if isinstance(t, typing._AnnotatedAlias):
                    output += f"{clean_type_name(t.__origin__)}\n```\n\n"
                    if len(t.__metadata__
                          ) > 0 and isinstance(t.__metadata__[0], str):
                        output += f"{t.__metadata__[0]}\n\n"
                else:
                    output += f"{t}\n```\n\n"

        functions = [
            f[1] for f in inspect.getmembers(module, inspect.isfunction)
            if (f[1].__module__ == module.__name__)
        ]
        if len(functions) > 0:
            output += f"{'#' * (module_depth + 1)} Functions\n\n"
            for function in functions:
                output += f"```python\ndef {function.__name__}"
                argspec = inspect.getfullargspec(function)
                if len(argspec.args) == 0:
                    output += f"() -> {clean_type_name(argspec.annotations.get('return', Any))}\n```\n\n"
                else:
                    output += "(\n"
                    for arg in argspec.args:
                        output += f"    {arg}"
                        annotation = argspec.annotations.get(arg, None)
                        if annotation is not None:
                            output += f": {clean_type_name(annotation)}"
                        if argspec.defaults is not None and arg in argspec.defaults:
                            output += f" = {argspec.defaults[argspec.args.index(arg)]}"
                        output += ",\n"
                    output += f") -> {argspec.annotations.get('return', Any)}:\n```\n\n"

                output += prettify_docstring(function)

        classes = [
            c[1] for c in inspect.getmembers(module, inspect.isclass)
            if c[1].__module__ == module.__name__ and not c[0].startswith("_")
        ]
        if len(classes) > 0:
            output += f"{'#' * (module_depth + 1)} Classes\n\n"
            for c in classes:
                output += f"```python\nclass {c.__name__}:\n"
                class_variables = inspect.get_annotations(c)
                for var, t in class_variables.items():
                    output += f"    {var}: {clean_type_name(t)}\n"
                output += "```\n\n"
                output += prettify_docstring(c)

                for member in inspect.getmembers(c):
                    if inspect.isfunction(member[1]):
                        function = member[1]
                        if ((
                            function.__name__.startswith("__") and
                            (function.__name__ != "__init__")
                        ) or (function.__name__ not in c.__dict__)):
                            continue
                        output += f"```python\n"
                        if isinstance(
                            c.__dict__.get(function.__name__, None),
                            staticmethod
                        ):
                            output += f"@staticmethod\n"
                        output += f"def {function.__name__}"
                        argspec = inspect.getfullargspec(function)
                        if len(argspec.args) == 0:
                            output += f"() -> {clean_type_name(argspec.annotations.get('return', Any))}\n```\n\n"
                        else:
                            output += "(\n"
                            for arg in argspec.args:
                                output += f"    {arg}"

                                annotation = argspec.annotations.get(arg, None)
                                if annotation is not None:
                                    output += f": {clean_type_name(annotation)}"
                                if argspec.defaults is not None and arg in argspec.defaults:
                                    output += f" = {argspec.defaults[argspec.args.index(arg)]}"
                                output += ",\n"
                            output += f") -> {clean_type_name(argspec.annotations.get('return', Any))}:\n```\n\n"

                        output += prettify_docstring(function)
        return output
    else:
        members = inspect.getmembers(module, inspect.ismodule)
        members = sorted(
            members,
            key=lambda x: 1 if x[1].__file__.endswith("__init__.py") else 0
        )
        for m in members:
            output += get_module_markdown(m[1], module_depth + 1)

        return output


markdown_content = get_module_markdown(src)
with open("output.md", "w") as f:
    f.write(markdown_content)
