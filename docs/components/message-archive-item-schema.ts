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
                        "message_body": {
                            "title": "Message Body",
                            "type": "object"
                        }
                    },
                    "required": [
                        "message_body"
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