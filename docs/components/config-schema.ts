/* prettier-ignore */
const CONFIG_SCHEMA: any = {
    "additionalProperties": false,
    "description": "Schema of the config file for this version of the software.\n\nA rendered API reference can be found in the documentation at TODO.",
    "properties": {
        "version": {
            "const": "0.1.0",
            "description": "The version of the software this config file is for",
            "title": "Version"
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
            "title": "LoggingVerbosityConfig",
            "type": "object"
        },
        "updater": {
            "anyOf": [
                {
                    "properties": {
                        "repository": {
                            "description": "The repository in which this source code is hosted, i.e. 'orgname/reponame'",
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
        "dummy_procedure": {
            "description": "Settings for the dummy procedure.",
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
            "title": "DummyProcedureConfig",
            "type": "object"
        },
        "system_checks": {
            "description": "Settings for the system checks procedure.",
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
            "title": "SystemChecksConfig",
            "type": "object"
        }
    },
    "required": [
        "version",
        "logging_verbosity",
        "dummy_procedure",
        "system_checks"
    ],
    "title": "Config",
    "type": "object"
};

export default CONFIG_SCHEMA;