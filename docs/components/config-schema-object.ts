/* prettier-ignore */
const CONFIG_SCHEMA_OBJECT: any = {
    "$defs": {
        "LoggingConfig": {
            "properties": {
                "print_to_console": {
                    "default": true,
                    "title": "Print To Console",
                    "type": "boolean"
                },
                "write_to_files": {
                    "default": true,
                    "title": "Write To Files",
                    "type": "boolean"
                }
            },
            "title": "LoggingConfig",
            "type": "object"
        },
        "UpdaterConfig": {
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
        }
    },
    "additionalProperties": false,
    "description": "Schema of the config file for this version of the software.\n\nA rendered API reference can be found in the documentation at TODO.",
    "properties": {
        "version": {
            "description": "The version of the software this config file is for",
            "examples": [
                "0.1.0",
                "1.2.3",
                "0.4.0-alpha.1",
                "0.5.0-beta.12",
                "0.6.0-rc.123"
            ],
            "pattern": "^\\d+\\.\\d+\\.\\d+(-(alpha|beta|rc)\\.\\d+)?$",
            "title": "Version",
            "type": "string"
        },
        "logging": {
            "properties": {
                "print_to_console": {
                    "default": true,
                    "title": "Print To Console",
                    "type": "boolean"
                },
                "write_to_files": {
                    "default": true,
                    "title": "Write To Files",
                    "type": "boolean"
                }
            },
            "title": "LoggingConfig",
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
        }
    },
    "required": [
        "version",
        "logging"
    ],
    "title": "Config",
    "type": "object"
};

export default CONFIG_SCHEMA_OBJECT;