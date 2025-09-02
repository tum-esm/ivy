# 🌱 Ivy

<img
  alt="Supported Python Versions"
  src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Ftum-esm%2Fivy%2Fmain%2Fpyproject.toml&label=Supported%20Python%20Versions&labelColor=0f172a&color=f43f5e"
  className="inline p-0 m-px mt-6"
/>
<a href="https://github.com/tum-esm/ivy/releases">
<img
  alt="GitHub Tag"
  src="https://img.shields.io/github/v/tag/tum-esm/ivy?sort=semver&style=flat&label=Latest%20Template%20Version&color=f43f5e&cacheSeconds=60&labelColor=0f172a"
  className="inline p-0 m-px mt-6"
/>
</a>
<br />
<a href="https://github.com/tum-esm/ivy/blob/main/LICENSE">
<img
  alt="GitHub License"
  src="https://img.shields.io/github/license/tum-esm/ivy?style=flat&label=License&labelColor=0f172a&color=4ade80&cacheSeconds=60"
  className="inline p-0 m-px"
/>
</a>
<a href="https://tum-esm-ivy.netlify.app/">
<img
    alt="Documentation Status"
    src="https://img.shields.io/website?url=https%3A%2F%2Ftum-esm-ivy.netlify.app%2F&up_message=online&up_color=4ade80&down_message=unavailable&down_color=f87171&label=Documentation&labelColor=0f172a&cacheSeconds=60"
    className="inline p-0 m-px"
  />
</a>
<a href="https://doi.org/10.5281/zenodo.14562882">
<img
    alt="DOI"
    src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.14562882-0ea5e9?labelColor=0f172a&color=0ea5e9&cacheSeconds=60"
    className="inline p-0 m-px"
  />
</a>

A Python boilerplate for an IoT node data acquisition system (DAS) supporting remote configuration and software updates. An Ivy-based network is made up of many (remote) computers running autonomously - e.g., performing measurements, controlling actuators, etc. - and a central backend connecting these devices.

The idea of Ivy is that you can start building your own DAS based on Ivy instead of starting from scratch. You have full control over the codebase but do not have to rewrite all the logic that every autonomous DAS has to implement. In addition, Ivy provides you with a well-tested and proven way of upgrading your sensor nodes remotely.

_This work is funded by the Horizon 2020 ICOS Cities PAUL Project under [grant no. 101037319](https://cordis.europa.eu/project/id/101037319), and the ERC Consolidator Grant CoSense4Climate under [grant no. 101089203](https://cordis.europa.eu/project/id/101089203)._

**Related Projects:**

🪽 The Ivy software template is based on the experience gained when realizing the [Hermes Project](https://github.com/tum-esm/hermes)<br/>
🔨 Many utility functions from the [`tum-esm-utils` package](https://github.com/tum-esm/utils) are included here.<br/>
🕷️ This client-side code connects to the following IoT platforms: [Tenta](https://github.com/iterize/tenta), [ThingsBoard](https://thingsboard.io/)<br/>
🌤️ The software architecture of [Pyra](https://github.com/tum-esm/pyra) is quite similar to the Ivy template. If we were to start building Pyra again today, we could use the Ivy template and save time on developing a new reliable architecture.
