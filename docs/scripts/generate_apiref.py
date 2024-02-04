import typing
import re
import docstring_parser
import inspect


def _get_object_source(obj: typing.Any) -> tuple[str, str]:
    """Get the definition and decorators of a function or class.
    This is used to detect decorators and class inheritance."""
    s = inspect.getsource(obj)
    indent: str = re.match(r"^(\s*)", s).group(0)  # type: ignore
    s = "\n".join([l[len(indent):] for l in s.split("\n")])
    decorator: str = ""
    definition: str = ""
    for i, l in enumerate(s.split("\n")):
        if l.startswith("def ") or l.startswith("class "):
            decorator = "\n".join(s.split("\n")[: i])
            definition = "\n".join(s.split("\n")[i :])
            break

    depth: int = 0
    for i, c in enumerate(definition):
        if c == "(":
            depth += 1
        if c == ")":
            depth -= 1
        if c == ":" and depth == 0:
            definition = definition[: i + 1]
            break
    return decorator, definition


def _clean_type_name(type_name: typing.Any) -> str:
    parsed_type_name = str(type_name).replace("NoneType", "None")
    if (
        parsed_type_name.startswith("<class '") and
        parsed_type_name.endswith("'>")
    ):
        parsed_type_name = parsed_type_name[8 :-2]
    return parsed_type_name


def _prettify_docstring(module: typing.Any) -> str:
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


def _render_variables(module: typing.Any, module_depth: int) -> str:
    type_hints = typing.get_type_hints(module)
    type_hint_extras = typing.get_type_hints(module, include_extras=True)
    output: str = ""
    if len(type_hints) > 0:
        output += f"{'#' * (module_depth + 1)} Variables"
        output += f" [#{module.__name__}.variables]\n\n"
        for name, type_hint in type_hints.items():
            output += f"```python\n{name}: {_clean_type_name(type_hint)}\n```\n\n"
            if name in type_hint_extras:
                extra_type_hint = type_hint_extras[name]
                if isinstance(
                    extra_type_hint,
                    typing._AnnotatedAlias  # type: ignore
                ):
                    metadata = extra_type_hint.__metadata__
                    if len(metadata) > 0 and isinstance(metadata[0], str):
                        output += f"{metadata[0]}\n\n"
    return output


def _render_function(function: typing.Any) -> str:
    output = f"**`{function.__name__}`**\n\n```python\n"
    decorators, _ = _get_object_source(function)
    if decorators != "":
        output += f"{decorators}\n"
    output += f"def {function.__name__}"
    argspec = inspect.getfullargspec(function)
    type_hints = typing.get_type_hints(function)
    if len(argspec.args) == 0:
        output += f"() -> {_clean_type_name(type_hints.get('return', typing.Any))}:\n```\n\n"
    else:
        output += "(\n"
        for i, arg in enumerate(argspec.args):
            output += f"    {arg}"
            if i > 0 or arg != "self":
                annotation = type_hints.get(arg, typing.Any)
                output += f": {_clean_type_name(annotation)}"
                if argspec.defaults is not None and arg in argspec.defaults:
                    output += f" = {argspec.defaults[argspec.args.index(arg)]}"
            output += ",\n"
        output += f") -> {_clean_type_name(type_hints.get('return', typing.Any))}:\n```\n\n"

    output += _prettify_docstring(function)
    return output


def _render_class(cls: typing.Any) -> str:
    output = f"**`{cls.__name__}`**\n\n```python\n"
    decorators, definition = _get_object_source(cls)
    if decorators != "":
        output += f"{decorators}\n"
    output += f"{definition}\n```\n\n"
    output += _prettify_docstring(cls)

    # class methods
    for member in inspect.getmembers(cls):
        if inspect.isfunction(member[1]):
            function = member[1]
            if ((
                function.__name__.startswith("__") and
                (function.__name__ != "__init__")
            ) or (function.__name__ not in cls.__dict__)):
                continue
            output += _render_function(function)
        # does not render "@property" and "@classmethod" methods (yet)

    return output


def generate_module_reference(module: typing.Any, module_depth: int = 1) -> str:
    """Generate the markdown API Reference for a module."""

    output = f"{'#' * module_depth} Module `{module.__name__}`"
    output += f" [#{module.__name__}]\n\n"
    if module.__doc__ is not None:
        output += f"{module.__doc__}\n\n"

    output += _render_variables(module, module_depth)

    if module.__file__.endswith("__init__.py"):
        # render submodules (directories first, then files)
        for m in sorted(
            inspect.getmembers(module, inspect.ismodule),
            key=lambda x: 1
            if ((x[1].__file__ or "").endswith("__init__.py")) else 0
        ):
            output += generate_module_reference(m[1], module_depth + 1)

    else:
        functions = [
            f[1] for f in inspect.getmembers(module, inspect.isfunction) if
            (f[1].__module__ == module.__name__) and not f[0].startswith("_")
        ]
        if len(functions) > 0:
            output += f"{'#' * (module_depth + 1)} Functions"
            output += f" [#{module.__name__}.functions]\n\n"
            for function in functions:
                output += _render_function(function)

        classes = [
            c[1] for c in inspect.getmembers(module, inspect.isclass)
            if c[1].__module__ == module.__name__ and not c[0].startswith("_")
        ]
        if len(classes) > 0:
            output += f"{'#' * (module_depth + 1)} Classes"
            output += f" [#{module.__name__}.classes]\n\n"
            for c in classes:
                output += _render_class(c)

    return output
