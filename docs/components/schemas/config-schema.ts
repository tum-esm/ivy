/* prettier-ignore */
const CONFIG_SCHEMA: any = {
    "additionalProperties": false,
    "description": "Schema of the config file for this version of the software.\n\nA rendered API reference can be found in the documentation.",
    "properties": {
        "general": {
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
                },
                "system_identifier": {
                    "description": "The identifier of this system. If possible, it is convenient to use the hostname of the system.",
                    "maxLength": 512,
                    "minLength": 1,
                    "title": "System Identifier",
                    "type": "string"
                }
            },
            "required": [
                "config_revision",
                "software_version",
                "system_identifier"
            ],
            "title": "_GeneralConfig",
            "type": "object"
        },
        "logging_verbosity": {
            "description": "How verbose to log to the different data streams.\n\nFor example, If the level is set to \"WARNING\", only warnings, errors\nand exceptions will be written to the respective data stream. If the\nlevel is set to \"DEBUG\", all logs will be written to the respective\ndata stream.\n\nImportance: DEBUG > INFO > WARNING > ERROR > EXCEPTION\n\nIf the level is set to None, no logs will be written to the respective\ndata stream.",
            "properties": {
                "file_archive": {
                    "description": "The minimum log level for the file archive in `data/logs`",
                    "enum": [
                        "DEBUG",
                        "INFO",
                        "WARNING",
                        "ERROR",
                        "EXCEPTION",
                        null
                    ],
                    "title": "File Archive"
                },
                "console_prints": {
                    "description": "The minimum log level for the console prints",
                    "enum": [
                        "DEBUG",
                        "INFO",
                        "WARNING",
                        "ERROR",
                        "EXCEPTION",
                        null
                    ],
                    "title": "Console Prints"
                },
                "message_sending": {
                    "description": "The minimum log level for the message sending",
                    "enum": [
                        "DEBUG",
                        "INFO",
                        "WARNING",
                        "ERROR",
                        "EXCEPTION",
                        null
                    ],
                    "title": "Message Sending"
                }
            },
            "required": [
                "file_archive",
                "console_prints",
                "message_sending"
            ],
            "title": "_LoggingVerbosityConfig",
            "type": "object"
        },
        "updater": {
            "anyOf": [
                {
                    "properties": {
                        "repository": {
                            "description": "The repository in which this source code is hosted, i.e. `orgname/reponame`",
                            "pattern": "[a-zA-Z0-9-]+/[a-zA-Z0-9-]+",
                            "title": "Repository",
                            "type": "string"
                        },
                        "provider": {
                            "description": "You can suggest more providers in the issue tracker",
                            "enum": [
                                "github",
                                "gitlab"
                            ],
                            "title": "Provider",
                            "type": "string"
                        },
                        "provider_host": {
                            "description": "The host of the code provider.",
                            "examples": [
                                "github.com",
                                "gitlab.com",
                                "gitlab.yourcompany.com"
                            ],
                            "minLength": 3,
                            "title": "Provider Host",
                            "type": "string"
                        },
                        "access_token": {
                            "anyOf": [
                                {
                                    "maxLength": 256,
                                    "minLength": 3,
                                    "type": "string"
                                },
                                {
                                    "type": "null"
                                }
                            ],
                            "default": null,
                            "description": "The access token to use for the provider. If the repository is public, this can be left empty.",
                            "title": "Access Token"
                        },
                        "source_conflict_strategy": {
                            "default": "reuse",
                            "description": "The strategy to follow, when upgrading to a new version and the source code already exists. 'reuse' will keep the existing source code but create a new venv. 'overwrite' will remove the existing code directory and create a new one. You can keep this at 'reuse' by default and if a version upgrade fails during the download phase, temporarily change this to 'overwrite' to force a redownload of the source code.",
                            "enum": [
                                "overwrite",
                                "reuse"
                            ],
                            "title": "Source Conflict Strategy",
                            "type": "string"
                        }
                    },
                    "required": [
                        "repository",
                        "provider",
                        "provider_host"
                    ],
                    "title": "UpdaterConfig",
                    "type": "object"
                },
                {
                    "type": "null"
                }
            ],
            "default": null,
            "description": "If this is not set, the updater will not be used."
        },
        "backend": {
            "anyOf": [
                {
                    "properties": {
                        "provider": {
                            "description": "The provider to use for the backend. The template ships with these two providers but is easily extendable to support other backends.",
                            "enum": [
                                "tenta",
                                "thingsboard"
                            ],
                            "title": "Provider",
                            "type": "string"
                        },
                        "mqtt_connection": {
                            "properties": {
                                "host": {
                                    "description": "The host to use for the MQTT connection",
                                    "maxLength": 512,
                                    "minLength": 1,
                                    "title": "Host",
                                    "type": "string"
                                },
                                "port": {
                                    "description": "The port to use for the MQTT connection",
                                    "maximum": 65535,
                                    "minimum": 1,
                                    "title": "Port",
                                    "type": "integer"
                                },
                                "client_id": {
                                    "description": "The client ID to use for the MQTT connection. Not necessarily the same as the username.",
                                    "maxLength": 512,
                                    "minLength": 1,
                                    "title": "Client Id",
                                    "type": "string"
                                },
                                "username": {
                                    "description": "The username to use for the MQTT connection.",
                                    "maxLength": 512,
                                    "minLength": 1,
                                    "title": "Username",
                                    "type": "string"
                                },
                                "password": {
                                    "description": "The password to use for the MQTT connection.",
                                    "maxLength": 512,
                                    "minLength": 1,
                                    "title": "Password",
                                    "type": "string"
                                }
                            },
                            "required": [
                                "host",
                                "port",
                                "client_id",
                                "username",
                                "password"
                            ],
                            "title": "MQTTBrokerConfig",
                            "type": "object"
                        },
                        "max_parallel_messages": {
                            "default": 50,
                            "description": "How many messages that are not published yet should be passed to the backend at once",
                            "maximum": 10000,
                            "minimum": 1,
                            "title": "Max Parallel Messages",
                            "type": "integer"
                        },
                        "max_drain_time": {
                            "default": 600,
                            "description": "When the mainloop wants to shut down (after a config change, or an update), how many seconds should the backend be allowed to continue sending out unsent messages.",
                            "maximum": 7200,
                            "minimum": 10,
                            "title": "Max Drain Time",
                            "type": "integer"
                        }
                    },
                    "required": [
                        "provider",
                        "mqtt_connection"
                    ],
                    "title": "BackendConfig",
                    "type": "object"
                },
                {
                    "type": "null"
                }
            ],
            "default": null,
            "description": "If this is not set, the backend will not be used."
        },
        "dummy_procedure": {
            "properties": {
                "seconds_between_datapoints": {
                    "description": "How many seconds should be between each datapoint in the dummy procedure",
                    "maximum": 7200,
                    "minimum": 1,
                    "title": "Seconds Between Datapoints",
                    "type": "integer"
                }
            },
            "required": [
                "seconds_between_datapoints"
            ],
            "title": "_DummyProcedureConfig",
            "type": "object"
        },
        "system_checks": {
            "properties": {
                "seconds_between_checks": {
                    "description": "How many seconds should be between each run of the system checks",
                    "maximum": 7200,
                    "minimum": 1,
                    "title": "Seconds Between Checks",
                    "type": "integer"
                }
            },
            "required": [
                "seconds_between_checks"
            ],
            "title": "_SystemChecksConfig",
            "type": "object"
        }
    },
    "required": [
        "general",
        "logging_verbosity",
        "dummy_procedure",
        "system_checks"
    ],
    "title": "Config",
    "type": "object"
};

export default CONFIG_SCHEMA;