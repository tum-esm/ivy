---
title: "Ivy v1: A Data Acquisition System for Distributed Sensor Networks Supporting Remote Configuration and Software Updates"
tags:
  - Environmental Sensing
  - Sensor Networks
  - Data Acquisition System
  - Wireless Sensor Networks
  - Cyber-Physical System
  - Autonomous System
  - Remote Configuration
  - Software Updates
  - Reproducible Research
  - Observability
  - Monitoring
  - Autonomous Systems
  - Boilerplate
  - Publish-Subscribe
  - Message Broker
  - MQTT
  - Real-time
  - IoT
  - Python
  - Pydantic
authors:
  - name: Moritz Makowski
    orcid: 0000-0002-2948-2993
    corresponding: true
    affiliation: 1
  - name: Jia Chen
    orcid: 0000-0002-6350-6610
    corresponding: true
    affiliation: 1
affiliations:
  - name: Environmental Sensing and Modeling, Technical University of Munich (TUM), Munich, Germany
    index: 1
date: 4 July 2025
bibliography: paper.bib
---

# Summary

Distributed sensor networks monitor environmental conditions at remote locations. Each sensor node produces various time series data streams and system logs and sends this data to a central backend. A "sensor node" is an autonomous system collecting data from one or multiple sensors connected to it, operated 24/7 by a Data Acquisition System (DAS). As part of the ICOS Cities PAUL Project [@paul], our group has developed a network of 20 autonomous GHG (greenhouse gas) sensor nodes [@midcost].

Since the software architecture of a DAS is independent of a specific sensor network, we present Ivy – a boilerplate for a DAS that supports configuring and updating itself remotely. Research teams building a new sensor network can use Ivy as a base for their own network-specific DAS. Ivy provides the core architecture, and users of the boilerplate only have to plug in their network-specific hardware logic to make it operational. Ivy is designed to be owned and customized: one can switch to another documentation system, add another backend, or remove unused parts of the boilerplate.

\vspace{4mm}

![System architecture of a distributed sensor network based on a DAS like Ivy.\label{fig:architecture1}](figures/ivy-architecture-fig-1.png){ width=94.3% }

The architecture of Ivy shown in \autoref{fig:architecture1} results from many iterations of the sensor networks our research group has built and operated [@Dietrich2021;@hermes;@Aigner2023]. This publication aims to share a reference architecture of how a reliable DAS can be built, not claiming that Ivy is the only architecture for this use case.

\pagebreak

# Statement of Need and Similar Efforts

Continuous monitoring of our environment improves our understanding of anthropogenic impacts on the environment [@IPCC_2021_WGI_SPM;@IPCC_2022_WGII_SPM]. Distributed sensor networks are used to monitor atmospheric composition [@Shusterman2016;@Bares2019;@Dietrich2021], forest ecosystems [@AndersonTeixeira2014;@Zweifel2021;@Zweifel2023], soil composition [@Dorigo2021;@AlYaari2018;@Bogena2022], and air quality [@Caubel2019;@Wenzel2021;@Wenzel2025;@Popoola2018].

These sensor networks are typically built in a waterfall process: first, the DAS software is written, then the sensor nodes are deployed. However, many studies report post-deployment failures that can only be fixed by visiting sites in person [@Bart2014;@Tolle2005]. A DAS allowing component failures and supporting remote reconfiguration and software updates enables teams to deploy their sensor nodes early and continuously improve their software remotely.

Many backends support collecting data from distributed sensor nodes. The FROST Server [@frost-server] implements the OGC SensorThings API specification [@ogcsensorthingsapi]. The Things Network [@thethingsnetwork] is a platform to manage LoRaWAN devices using The Things Stack [@thethingsstack]. Thingsboard [@thingsboard] and Tenta [@tenta] are similar backends offering MQTT and HTTP APIs to store and retrieve sensor network data.

Backends often provide client libraries [@frostpythonclient;@thingsboardclientsdk;@tentapythonclient], but the complete code autonomously operating a specific network's sensor nodes is rarely published. This lack of open-sourced architectures makes it hard to assess how systems like this are built. Wireless Sensor Networks (WSNs), which have been widely studied [@Kandris2020], consist of a "base station" communicating with many distributed "motes". However, Ivy focuses on the architecture of many distributed autonomous base stations, not motes. Basing a DAS on the Robot Operating System (ROS) [@ros1;@ros2] is a reasonable choice for environmental sensing applications. However, one still has to write the operational logic of the DAS because ROS only comes with the communication infrastructure. Both WSNs and ROS are complementary to Ivy since Ivy can operate a base station of a WSN or run inside a ROS node.

The Hermes software [@hermes] driving the Acropolis network has been open-sourced[^1] and used from early 2023 to early 2025, enabling our group to deploy 38 software updates to the network. By now, this sensor network uses a modified variant of Hermes, Acropolis-Edge [@acropolis-edge], that runs the DAS inside a container and separates the DAS from the updater. However, both Hermes and Acropolis-Edge are not directly reusable for similar networks since they are tailored to the Acropolis network. Ivy refines the DAS architecture of Hermes and Pyra [@Dietrich2021;@Aigner2023] and makes it reusable for other sensor networks.

[^1]: https://github.com/tum-esm/hermes

# General System Design

Ivy uses a `config.json` file to store its active configuration. It can receive new configurations from the backend, change the config file it runs with, or perform a software update. The software update logic is built into the DAS, meaning it can also be updated. \autoref{fig:architecture2} shows the update process of Ivy, which ensures that the DAS does not update itself to a version that does not run on the local hardware.

![The software update process of Ivy.\label{fig:architecture2}](figures/ivy-architecture-fig-2.png){ width=100% }

Ivy comes with connectors for two backends out of the box – Thingsboard and Tenta – and uses the MQTT protocol to communicate with them. Nevertheless, Ivy is not bound to a specific backend or communication protocol. This flexibility prevents vendor lock-in and makes the boilerplate more reusable. We are happy to support more backends out of the box in the future, like Strapi [@strapi], Kuzzle [@kuzzle], or FROST. Furthermore, many utility functions have been moved to the `tum-esm-utils` Python package [@tumesmutils].

## Evolution of the Runtime Model

Whereas Hermes, Acropolis-Edge, and earlier versions of Pyra run much of the logic on a single thread, Ivy uses a fully parallel architecture, eliminating the possibility of one faulty component blocking other components. Each block of functionality running in an infinite loop is packaged into a "procedure". The "mainloop" is only responsible for managing procedure lifecycles and handling configuration changes. Starting with Pyra version 4.2, Pyra follows this parallel architecture of Ivy. \autoref{fig:architecture3} shows the communication structure within Ivy.

![The communication between Ivy procedures.\label{fig:architecture3}](figures/ivy-architecture-fig-3.png){ width=100% }

## Testing and Documentation

Ivy is statically typed and tested using Mypy [@mypy]. Its test suite contains a test that tries to update a known working version to the current codebase and a test that tries to update the current codebase to a known working version. Ivy's API reference is generated automatically from the codebase and contains rendered schema references for all JSON files users interact with (configuration, local message archive, shared state).

# Author Contributions

MM: developed the sensor side of Hermes, wrote the Ivy boilerplate, wrote the manuscript, works on Pyra; JC (PI): initialized, co-developed, and supervises the GHG sensor networks driven by Hermes and Pyra, helped with her expertise in environmental sensing, reviewed the manuscript.

# Acknowledgement of Financial Support

This work is funded by the Horizon 2020 ICOS Cities PAUL Project under [grant no. 101037319](https://cordis.europa.eu/project/id/101037319), and the ERC Consolidator Grant CoSense4Climate under [grant no. 101089203](https://cordis.europa.eu/project/id/101089203).

# References
