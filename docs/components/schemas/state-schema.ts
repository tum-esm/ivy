/* prettier-ignore */
const STATE_SCHEMA: any = {
    "description": "Central state used to communicate between prodedures and with the mainloop.",
    "properties": {
        "system": {
            "description": "The state of the system",
            "properties": {
                "last_boot_time": {
                    "anyOf": [
                        {
                            "format": "date-time",
                            "type": "string"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": null,
                    "description": "The last boot time of the system",
                    "examples": [
                        "2021-01-01T00:00:00.000000"
                    ],
                    "title": "Last Boot Time"
                },
                "last_5_min_load": {
                    "anyOf": [
                        {
                            "type": "number"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": null,
                    "description": "The average CPU load in the last 5 minutes in percent",
                    "examples": [
                        1,
                        15.5,
                        85,
                        99.5
                    ],
                    "title": "Last 5 Min Load"
                }
            },
            "title": "SystemState",
            "type": "object",
            "default": {
                "last_boot_time": null,
                "last_5_min_load": null
            }
        },
        "pending_configs": {
            "default": [],
            "description": "A list of pending config changes. This will be written to by the backend procedure and read by the updater procedure.",
            "items": {
                "additionalProperties": true,
                "description": "Schema of a foreign config file for any other version of the software\nto update to. It probably has more fields than listed in the schema. This\nschema only includes the fields that are required in any new config to be\naccepted by the updater in this version of the software.\n\nA rendered API reference can be found in the documentation.",
                "properties": {
                    "general": {
                        "additionalProperties": true,
                        "properties": {
                            "config_revision": {
                                "description": "The revision of this config file. This should be incremented when the config file is changed. It is used to tag messages with the settings that were active at the time of sending.",
                                "minimum": 0,
                                "title": "Config Revision",
                                "type": "integer"
                            },
                            "software_version": {
                                "description": "The version of the software this config file is for. The updater only works if this is set.",
                                "examples": [
                                    "0.1.0",
                                    "0.2.0"
                                ],
                                "pattern": "^\\d+\\.\\d+\\.\\d+(-(alpha|beta|rc)\\.\\d+)?$",
                                "title": "Software Version",
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
            },
            "title": "Pending Configs",
            "type": "array"
        }
    },
    "title": "State",
    "type": "object"
};

export default STATE_SCHEMA;