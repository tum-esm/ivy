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
        }
    },
    "title": "State",
    "type": "object"
};

export default STATE_SCHEMA;