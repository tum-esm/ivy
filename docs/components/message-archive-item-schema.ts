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