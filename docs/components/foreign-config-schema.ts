/* prettier-ignore */
const FOREIGN_CONFIG_SCHEMA: any = {
    "additionalProperties": true,
    "description": "Schema of a foreign config file for any other version of the software\nto update to.\n\nA rendered API reference can be found in the documentation at TODO.",
    "properties": {
        "version": {
            "description": "The version of the software this config file is for",
            "examples": [
                "0.1.0",
                "0.2.0"
            ],
            "pattern": "^\\d+\\.\\d+\\.\\d+(-(alpha|beta|rc)\\.\\d+)?$",
            "title": "Version",
            "type": "string"
        }
    },
    "required": [
        "version"
    ],
    "title": "ForeignConfig",
    "type": "object"
};

export default FOREIGN_CONFIG_SCHEMA;