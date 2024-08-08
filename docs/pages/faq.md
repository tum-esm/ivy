---
title: Frequently Asked Questions
---

# Frequently Asked Questions

## Why are the `MessagingAgent` and the backends two separate things?

The `MessagingAgent` should always be able to save messages locally and schedule them to be sent out. The code that creates the message should not wait until the message is sent out to continue its work. The `MessagingAgent` write the message to a local database which only takes a fraction of a second. The backends pick up the messages from this local database and send them out when they can. This way a connection issue with the backend or a long delay in sending out messages does not affect the rest of the system.

Additionally, the `MessagingAgent` is protocol-independent - it uses its own logic to communicate with the local message storage but the backend connector can use any protocol to send out the queued messages.

Read about Semantic Versioning [here](https://semver.org/).

## How does the versioning of the Ivy Template work?

All versions 1.X will have the same architecture as version 1.0. Meaning, you can upgrade your own DAS-repository to non-breaking versions. Versions 1.X and following can add new backends, fix bugs and improve performance, expand the documentation, and so on - but they will not break your existing DAS-repository because the internal APIs will remain the same.

We are happy to accept feedback on the architecture itself though, which will lead to a new major version (2.X).

## Is the Ivy Template complete?

Yes, it is usable and yes, we thought long about its archictecure. The core architecture should hopefully cater to most use cases. However, we want to add everything to the template repository that could help most users: more backends, more documentation, better CI, better tests, more utility functions.

Hence, if you are using Ivy and think your developments could help others in developing their own DAS, we are happy to include your contributions and of course add you and your institution to the list of contributors.

## Which backends do you see fit for the Ivy Template?

Since the `MessagingAgent` is independent of the protocol used to communicate with the backend, one can use HTTPS, LoRaWAN, CoAP, or any other protocol to communicate with the outside world.

We included [ThingsBoard](https://thingsboard.io/) and [Tenta](https://tenta.onrender.com/) for now, because these two are primarily design for this type of workload. We are happy to include any backend that fits and does not require many additional dependencies.

**Customizable Backends (CMSs):** The storing of messages, configurations and logs does actually not require that much logic when using HTTPS and could be achieved using [Strapi](https://strapi.io/), [PocketBase](https://pocketbase.io/), or [Directus](https://directus.io/). However all of these just mentioned platforms are not targeting at storing a large amount of time series data generated by a sensor network. Nevertheless both [Strapi](https://strapi.io/) and [Directus](https://directus.io/) can be self-hosted, are open-source and can connect to many database flavors (like PostgreSQL). Hence, we do not see an architectural reason why they should be less performant than dedicated IoT backends besides storing more metadata than necessary and not having time-wise aggregation queries built-in. I would not recommend [PocketBase](https://pocketbase.io/) for this use case since it uses SQLite under the hood.

**Other IoT backends:**

_The indicator of "readiness" is our personal judgement._

- Early-stage but under active development: [Magistrala](https://github.com/absmach/magistrala), [SimpleIoT](https://simpleiot.org/), [ThingsPanel](https://github.com/ThingsPanel), [ThingLinks](https://github.com/mqttsnet/thinglinks)
- Ready to use: [Kuzzle](https://kuzzle.io/), [OpenRemote](https://github.com/openremote/openremote)
- Cloud Provider Options: [Azure IoT Hub](https://azure.microsoft.com/en-gb/products/iot-hub)
- Abandoned: [ThingSpeak](https://thingspeak.com/), [Zeus IoT](https://github.com/zmops/zeus-iot), AWS, GCP and IBM have abandoned their IoT platforms.

## How can I host versioned documentation?

It might be that you have a version `0.1` of your DAS and a version `0.2` of the DAS and you want to have a hosted documentation for both of these. Like `v0-1.yourdas.youruniversity.edu` and `v0-2.yourdas.youruniversity.edu`.

The easiest way to achieve this is by checking out a branch for each old version and then deploying a new site for each of those branches. After that, you can link each of these sites in a dropdown menu in the navigation bar using the file `docs/pages/_meta.json`:

```json
{
  "Versions": {
    "title": "Versions",
    "type": "menu",
    "items": {
      "latest": {
        "title": "Latest",
        "href": "https://ivy-docs.pages.dev/"
      },
      "v0.2": {
        "title": "v0.2",
        "href": "https://docs-v0-2.ivy-docs.pages.dev/"
      },
      "v0.1": {
        "title": "v0.1",
        "href": "https://docs-v0-1.ivy-docs.pages.dev/"
      }
    }
  }
}
```

Normally, you should only have to do this if you keep an old version of your DAS in production (only migrate part of your systems from a `1.X` to a `2.X`).

## Why is this template only compatible with `python>=3.10`?

Because the Python3.10 release added many new ways of type hinting. We will not increase this minimum Python version in the near future though.