/* prettier-ignore */
const CONFIG_SCHEMA_OBJECT: any = {
  "$defs": {
    "UpdaterConfig": {
      "properties": {
        "repository": {
          "pattern": "[a-zA-Z0-9-]+/[a-zA-Z0-9-]+",
          "title": "Repository",
          "type": "string"
        },
        "provider": {
          "enum": [
            "github",
            "gitlab"
          ],
          "title": "Provider",
          "type": "string"
        },
        "provider_host": {
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
          "title": "Access Token"
        },
        "source_conflict_strategy": {
          "default": "reuse",
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
      "pattern": "^\\d+\\.\\d+\\.\\d+(-(alpha|beta|rc)\\.\\d+)?$",
      "title": "Version",
      "type": "string"
    },
    "updater": {
      "anyOf": [
        {
          "properties": {
            "repository": {
              "pattern": "[a-zA-Z0-9-]+/[a-zA-Z0-9-]+",
              "title": "Repository",
              "type": "string"
            },
            "provider": {
              "enum": [
                "github",
                "gitlab"
              ],
              "title": "Provider",
              "type": "string"
            },
            "provider_host": {
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
              "title": "Access Token"
            },
            "source_conflict_strategy": {
              "default": "reuse",
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
      "default": null
    }
  },
  "required": [
    "version"
  ],
  "title": "Config",
  "type": "object"
};

export default CONFIG_SCHEMA_OBJECT;