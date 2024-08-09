# 🌱 Ivy

TODO: link supported python versions (>= 3.10)
TODO: possibly link codeclimate analysis

<img alt="GitHub License" src="https://img.shields.io/github/license/tum-esm/ivy?style=flat&label=License&labelColor=%230f172a&color=%23fef08a" className="inline p-0 m-px mt-6"/> <img alt="GitHub Tag" src="https://img.shields.io/github/v/tag/tum-esm/ivy?sort=semver&style=flat&label=Latest%20Template%20Version&color=%23fef08a&cacheSeconds=60&labelColor=%230f172a" className="inline p-0 m-px mt-6"/>

A Python boilerplate for an IoT node data acqusition system (DAS) supporting remote configuration and software updates. An Ivy-based network is made up of many (remote) computers running autonomously - e.g. performing measurements, controlling actors, etc. - and a central backend connects these devices.

The idea of Ivy is that you can start building your own DAS based on Ivy instead of starting from scratch. You have full control over the codebase but do not have to rewrite all the logic that every autonomous DAS has to implement. In addition, Ivy provides you with a well-tested and proven way of upgrading your sensor nodes remotely.

TODO: link documentation

**Related Projects:**

🪽 The Ivy software template is based on the experienced gained when realizing the [Hermes Project](https://github.com/tum-esm/hermes)<br/>
🔨 Many utility functions from the [`tum-esm-utils` package](https://github.com/tum-esm/utils) are included here.<br/>
🕷️ This client-side code connects to the following IoT platforms: [Tenta](https://github.com/iterize/tenta), [ThingsBoard](https://thingsboard.io/)<br/>
🌤️ The software architecture of [Pyra](https://github.com/tum-esm/pyra) is quite similar to the Ivy template. If we were to start building Pyra again today, we would use the Ivy template and save a ton of time.
📚 The [EM27 Retrieval Pipeline](https://github.com/tum-esm/em27-retrieval-pipeline) uses the same code to generate the API reference (code and JSON files)
