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
        },
        "revision": {
            "description": "The revision of this config file. This should be incremented when the config file is changed. It is used to tag messages with the settings that were active at the time of sending.",
            "minimum": 0,
            "title": "Revision",
            "type": "integer"
        }
    },
    "required": [
        "version",
        "revision"
    ],
    "title": "ForeignConfig",
    "type": "object"
};

export default FOREIGN_CONFIG_SCHEMA;