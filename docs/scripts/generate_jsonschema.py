import json
import typing
import jsonref


def _remove_allof_wrapping(o: typing.Any) -> typing.Any:
    if isinstance(o, list):
        return [_remove_allof_wrapping(x) for x in o]
    elif isinstance(o, dict):
        if "properties" in o.keys():
            return {
                **o,
                "properties": {
                    k: _remove_allof_wrapping(v)
                    for k, v in o["properties"].items()
                },
            }
        elif "allOf" in o.keys():
            assert len(o["allOf"]) == 1
            return {
                **o["allOf"][0],
                **{k: v
                   for k, v in o.items() if k != "allOf"},
            }
        else:
            return {k: _remove_allof_wrapping(v) for k, v in o.items()}
    else:
        return o


def generate_jsonschema_tsfile(obj: typing.Any, label: str) -> str:
    # remove $ref usages
    schema_without_refs = jsonref.loads(
        json.dumps(obj.model_json_schema(by_alias=False))
    )

    # remove $defs section
    schema_without_defs = json.loads(
        jsonref.dumps(schema_without_refs, indent=4)
    )
    if "$defs" in schema_without_defs.keys():
        del schema_without_defs["$defs"]

    # convert weird "allOf" wrapping to normal wrapping
    schema_without_allofs = _remove_allof_wrapping(schema_without_defs)

    # write out file
    return (
        f"/* prettier-ignore */\nconst {label}: any = " +
        json.dumps(schema_without_allofs, indent=4) +
        f";\n\nexport default {label};"
    )
