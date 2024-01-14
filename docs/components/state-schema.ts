/* prettier-ignore */
const STATE_SCHEMA: any = {
    "description": "Central state used to communicate between prodedures and with the mainloop.",
    "properties": {
        "system": {
            "default": {
                "last_boot_time": null,
                "last_5_min_load": null
            },
            "description": "State values determined in the system checks procedure.",
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
            "type": "object"
        },
        "pending_configs": {
            "default": [],
            "description": "A list of pending config changes. This will be written to by the backend procedure and read by the updater procedure.",
            "items": {
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
            },
            "title": "Pending Configs",
            "type": "array"
        }
    },
    "title": "State",
    "type": "object"
};

export default STATE_SCHEMA;