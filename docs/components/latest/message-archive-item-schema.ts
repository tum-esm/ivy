/* prettier-ignore */
const MESSAGE_ARCHIVE_ITEM_SCHEMA: any = {
    "properties": {
        "timestamp": {
            "title": "Timestamp",
            "type": "number"
        },
        "message_body": {
            "anyOf": [
                {
                    "properties": {
                        "variant": {
                            "const": "data",
                            "default": "data",
                            "title": "Variant"
                        },
                        "data": {
                            "additionalProperties": {
                                "anyOf": [
                                    {
                                        "type": "number"
                                    },
                                    {
                                        "type": "integer"
                                    },
                                    {
                                        "type": "string"
                                    }
                                ]
                            },
                            "description": "The data to send to the backend",
                            "examples": [
                                {
                                    "temperature": 19.7
                                },
                                {
                                    "humidity": 45.3,
                                    "temperature": 19.7
                                }
                            ],
                            "title": "Data",
                            "type": "object"
                        }
                    },
                    "required": [
                        "data"
                    ],
                    "title": "DataMessageBody",
                    "type": "object"
                },
                {
                    "properties": {
                        "variant": {
                            "const": "log",
                            "default": "log",
                            "title": "Variant"
                        },
                        "level": {
                            "enum": [
                                "DEBUG",
                                "INFO",
                                "WARNING",
                                "ERROR",
                                "EXCEPTION"
                            ],
                            "title": "Level",
                            "type": "string"
                        },
                        "subject": {
                            "title": "Subject",
                            "type": "string"
                        },
                        "body": {
                            "title": "Body",
                            "type": "string"
                        }
                    },
                    "required": [
                        "level",
                        "subject",
                        "body"
                    ],
                    "title": "LogMessageBody",
                    "type": "object"
                },
                {
                    "properties": {
                        "variant": {
                            "const": "config",
                            "default": "config",
                            "title": "Variant"
                        },
                        "status": {
                            "enum": [
                                "received",
                                "accepted",
                                "rejected",
                                "startup"
                            ],
                            "title": "Status",
                            "type": "string"
                        },
                        "config": {
                            "additionalProperties": true,
                            "description": "Schema of a foreign config file for any other version of the software\nto update to.\n\nA rendered API reference can be found in the documentation at TODO.",
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
                                    "title": "_ForeignGeneralConfig",
                                    "type": "object"
                                }
                            },
                            "required": [
                                "general"
                            ],
                            "title": "ForeignConfig",
                            "type": "object"
                        }
                    },
                    "required": [
                        "status",
                        "config"
                    ],
                    "title": "ConfigMessageBody",
                    "type": "object"
                }
            ],
            "title": "Message Body"
        }
    },
    "required": [
        "timestamp",
        "message_body"
    ],
    "title": "MessageArchiveItem",
    "type": "object"
};

export default MESSAGE_ARCHIVE_ITEM_SCHEMA;