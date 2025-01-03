/* prettier-ignore */
const FOREIGN_CONFIG_SCHEMA: any = {
    "additionalProperties": true,
    "description": "Schema of a foreign config file for any other version of the software\nto update to. It probably has more fields than listed in the schema. This\nschema only includes the fields that are required in any new config to be\naccepted by the updater in this version of the software.\n\nA rendered API reference can be found in the documentation.",
    "properties": {
        "general": {
            "additionalProperties": true,
            "properties": {
                "config_revision": {
                    "description": "The revision of this config file. This should be incremented when the config file is changed. It is used to tag messages with the settings that were active at the time of sending.",
                    "minimum": -1,
                    "title": "Config Revision",
                    "type": "integer"
                },
                "software_version": {
                    "description": "A version string in the format of MAJOR.MINOR.PATCH[-(alpha|beta|rc).N]",
                    "pattern": "^\\d+\\.\\d+\\.\\d+(-(alpha|beta|rc)\\.\\d+)?$",
                    "title": "Version",
                    "type": "string"
                }
            },
            "required": [
                "config_revision",
                "software_version"
            ],
            "title": "ForeignGeneralConfig",
            "type": "object"
        }
    },
    "required": [
        "general"
    ],
    "title": "ForeignConfig",
    "type": "object"
};

export default FOREIGN_CONFIG_SCHEMA;