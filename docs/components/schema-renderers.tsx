import React from "react";
import CONFIG_SCHEMA_OBJECT from "./config-schema-object";

function renderConfigProperty(
  depth: number,
  propertyKey: string,
  propertyObject: any,
  required: boolean,
  isUnionOption: boolean = false
) {
  if (!required && propertyObject.default === undefined) {
    propertyObject.default = null;
  }

  let fontSize: string;
  let bgColor: string;
  let dividerColor: string;

  switch (depth) {
    case 0:
      fontSize = "text-[17px]";
      bgColor = "bg-slate-100 dark:bg-slate-800";
      dividerColor = "divide-slate-200 dark:divide-slate-700";
      break;
    case 1:
      fontSize = "text-[16px]";
      bgColor = "bg-slate-200 dark:bg-slate-700";
      dividerColor = "divide-slate-300 dark:divide-slate-600";
      break;
    case 2:
      fontSize = "text-[15px]";
      bgColor = "bg-slate-300 dark:bg-slate-600";
      dividerColor = "divide-slate-400 dark:divide-slate-500";
      break;
    case 3:
      fontSize = "text-[14px]";
      bgColor = "bg-slate-400 dark:bg-slate-500";
      dividerColor = "divide-slate-500 dark:divide-slate-400";
      break;
    case 4:
      fontSize = "text-[13px]";
      bgColor = "bg-slate-500 dark:bg-slate-400";
      dividerColor = "divide-slate-600 dark:divide-slate-300";
      break;
    case 5:
      fontSize = "text-[12px]";
      bgColor = "bg-slate-600 dark:bg-slate-300";
      dividerColor = "divide-slate-700 dark:divide-slate-200";
      break;
    case 6:
      fontSize = "text-[11px]";
      bgColor = "bg-slate-700 dark:bg-slate-200";
      dividerColor = "divide-slate-800 dark:divide-slate-100";
      break;
  }
  return (
    <div className={`flex flex-col p-3`} key={propertyKey}>
      <div className={`font-semibold ${fontSize} leading-tight`}>
        <span className="font-bold text-slate-950 dark:text-slate-100">
          {propertyKey}
        </span>
        {required && (
          <span
            className="px-0.5 rounded text-rose-700 dark:text-rose-300"
            title="required"
          >
            *
          </span>
        )}
        <span className="px-0.5 rounded text-rose-700 dark:text-rose-300">
          ({propertyObject.type || "union"})
        </span>
      </div>
      {propertyObject.description !== undefined && (
        <div
          className={`mt-1 mb-2 ${fontSize} text-slate-800 dark:text-slate-300`}
        >
          {propertyObject.description}
        </div>
      )}
      <div
        className={`flex flex-col leading-tight ${fontSize} text-slate-800 dark:text-slate-300`}
      >
        {[
          ["examples", "examples"],
          ["default", "default"],
          ["pattern", "regex pattern"],
          ["minLength", "min. length"],
          ["maxLength", "max. length"],
          ["minimum", "min."],
          ["maximum", "max."],
          ["minItems", "min. items"],
          ["maxItems", "max. items"],
          ["enum", "allowed values"],
        ].map(([key, label], index) => (
          <React.Fragment key={index}>
            {!(key === "default" && (propertyKey === "#" || isUnionOption)) &&
              propertyObject[key] !== undefined && (
                <div className="flex flex-row mt-1 gap-x-2">
                  <div className="font-normal">{label}:</div>
                  <div className="font-normal">
                    {JSON.stringify(propertyObject[key], null, 4).replaceAll(
                      "\\\\",
                      "\\"
                    )}
                  </div>
                </div>
              )}
          </React.Fragment>
        ))}
      </div>

      {["object", "array"].includes(propertyObject.type) && (
        <div className={`flex flex-col ml-6 rounded ${bgColor} mt-2`}>
          {propertyObject.type === "object" && (
            <div className={`flex flex-col divide-y ${dividerColor}`}>
              {Object.keys(propertyObject.properties).map((key) =>
                renderConfigProperty(
                  depth + 1,
                  key,
                  propertyObject.properties[key],
                  propertyObject.required?.includes(key) || false
                )
              )}
            </div>
          )}
          {propertyObject.type === "array" &&
            renderConfigProperty(depth + 1, "#", propertyObject.items, false)}
        </div>
      )}
      {propertyObject.anyOf !== undefined && (
        <div className={`flex flex-col ml-6 rounded ${bgColor} mt-2`}>
          <div className={`flex flex-col divide-y ${dividerColor}`}>
            {propertyObject.anyOf.map((key, i) =>
              renderConfigProperty(
                depth + 1,
                `option ${i + 1}`,
                key,
                false,
                true
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export function ConfigSchema() {
  return (
    <div className="flex flex-col mt-4 gap-y-4 text-slate-950">
      {Object.keys(CONFIG_SCHEMA_OBJECT.properties).map((key) =>
        renderConfigProperty(
          0,
          key,
          CONFIG_SCHEMA_OBJECT.properties[key],
          CONFIG_SCHEMA_OBJECT.required.includes(key)
        )
      )}
    </div>
  );
}
