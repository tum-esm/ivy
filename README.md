# 🌱 Ivy

<img
  alt="Supported Python Versions"
  src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Ftum-esm%2Fivy%2Fmain%2Fpyproject.toml&label=Supported%20Python%20Versions&labelColor=0f172a&color=f43f5e"
  className="inline p-0 m-px mt-6"
/>
<img
  alt="GitHub Tag"
  src="https://img.shields.io/github/v/tag/tum-esm/ivy?sort=semver&style=flat&label=Latest%20Template%20Version&color=f43f5e&cacheSeconds=60&labelColor=0f172a"
  className="inline p-0 m-px mt-6"
/>
<img
  alt="GitHub License"
  src="https://img.shields.io/github/license/tum-esm/ivy?style=flat&label=License&labelColor=0f172a&color=4ade80&cacheSeconds=60"
  className="inline p-0 m-px mt-6"
/>
<img
  alt="Documentation Status"
  src="https://img.shields.io/website?url=https%3A%2F%2Ftum-esm-ivy.netlify.app%2F&up_message=online&up_color=4ade80&down_message=unavailable&down_color=f87171&label=Documentation&labelColor=0f172a&cacheSeconds=60"
  className="inline p-0 m-px mt-6"
/>

A Python boilerplate for an IoT node data acquisition system (DAS) supporting remote configuration and software updates. An Ivy-based network is made up of many (remote) computers running autonomously - e.g., performing measurements, controlling actuators, etc. - and a central backend connecting these devices.

The idea of Ivy is that you can start building your own DAS based on Ivy instead of starting from scratch. You have full control over the codebase but do not have to rewrite all the logic that every autonomous DAS has to implement. In addition, Ivy provides you with a well-tested and proven way of upgrading your sensor nodes remotely.

**Related Projects:**

🪽 The Ivy software template is based on the experience gained when realizing the [Hermes Project](https://github.com/tum-esm/hermes)<br/>
🔨 Many utility functions from the [`tum-esm-utils` package](https://github.com/tum-esm/utils) are included here.<br/>
🕷️ This client-side code connects to the following IoT platforms: [Tenta](https://github.com/iterize/tenta), [ThingsBoard](https://thingsboard.io/)<br/>
🌤️ The software architecture of [Pyra](https://github.com/tum-esm/pyra) is quite similar to the Ivy template. If we were to start building Pyra again today, we would use the Ivy template and save a ton of time.
