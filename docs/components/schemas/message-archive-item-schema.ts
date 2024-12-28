/* prettier-ignore */
const MESSAGE_ARCHIVE_ITEM_SCHEMA: any = {
    "properties": {
        "timestamp": {
            "description": "Unix timestamp on the system when this message was created",
            "title": "Timestamp",
            "type": "number"
        },
        "message_body": {
            "anyOf": [
                {
                    "description": "The body of a data message, defined by `body.variant == \"data\"`.",
                    "properties": {
                        "variant": {
                            "const": "data",
                            "default": "data",
                            "description": "Indicating the variant of the message. All possible message bodies have this field.",
                            "title": "Variant",
                            "type": "string"
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
                    "description": "The body of a log message, defined by `body.variant == \"log\"`.",
                    "properties": {
                        "variant": {
                            "const": "log",
                            "default": "log",
                            "description": "Indicating the variant of the message. All possible message bodies have this field.",
                            "title": "Variant",
                            "type": "string"
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
                            "description": "The subject of the log message. Try to move specific detailsto the body because then messages can be grouped by the subject - i.e. \"give me all messages reporting high system load\".",
                            "examples": [
                                "Starting procedure",
                                "System load too high"
                            ],
                            "title": "Subject",
                            "type": "string"
                        },
                        "body": {
                            "description": "The body of the log message",
                            "examples": [
                                "Here are some more details on the procedure starting",
                                "The system load is 87%"
                            ],
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
                    "description": "The body of a config message, defined by `body.variant == \"config\"`.",
                    "properties": {
                        "variant": {
                            "const": "config",
                            "default": "config",
                            "description": "Indicating the variant of the message. All possible message bodies have this field.",
                            "title": "Variant",
                            "type": "string"
                        },
                        "status": {
                            "description": "The status of the config. \"received\" is sent out by the backend process upon arrival. \"accepted\" means the config passed the tests and will be used after the termination that is issues upon acceptance. \"rejected\" means the config did either not fulfil the schema or not pass the tests. \"startup\" means that a mainloop using this config was started.",
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