# DEA Conflux

![GitHub](https://img.shields.io/github/license/GeoscienceAustralia/dea-conflux)
[![Test](https://github.com/GeoscienceAustralia/dea-conflux/actions/workflows/test.yml/badge.svg)](https://github.com/GeoscienceAustralia/dea-conflux/actions/workflows/test.yml) [![Lint](https://github.com/GeoscienceAustralia/dea-conflux/actions/workflows/lint.yml/badge.svg)](https://github.com/GeoscienceAustralia/dea-conflux/actions/workflows/lint.yml)

This is a prototype tool for processing bulk polygon drills.

- License: Apache 2.0
- Contact: matthew.alger@ga.gov.au

## Installation

Install with `pip`:

```bash
pip install git+https://github.com/GeoscienceAustralia/dea-conflux.git
```

Or clone the repository and install from the local version.

```bash
git clone https://github.com/GeoscienceAustralia/dea-conflux.git
cd dea-conflux
pip install -e .
```

## Usage

Conflux provides a command-line tool `dea-conflux` for running each step of the polygon drill. Descriptions of the commands are available with `dea-conflux --help`. Conflux requires a Datacube configuration to work.

To run Conflux on a single scene, give it a scene UUID present in the Datacube, a plugin describing the polygon drill, a place to put output files, and a shapefile defining the polygons:

```bash
dea-conflux run-one --uuid SCENE_ID --plugin PLUGIN_PATH -o OUTPUT_PATH -s SHAPEFILE_PATH
```

Conflux can also read from an AWS SQS queue. Messages must be the UUID of a scene.

```bash
dea-conflux run-from-queue --queue QUEUE_NAME --plugin PLUGIN_PATH -o OUTPUT_PATH -s SHAPEFILE_PATH
```

### Plugins

A plugin defines the inputs and outputs of a polygon drill. It is a Python file with the extensions `.conflux.py`. Examples are provided in the `examples/` directory.

Plugins must provide:

- a product name for the drill,
- a version string for the drill,
- the resampling method to use on input rasters,
- the CRS to project the input rasters into,
- the resolution to resample the input rasters into,
- a dictionary of input products and bands,
- a transform function, and
- a summarise function.

The transform is run to produce rasters to summarise and should contain operations like masking and band index calculation. The summarise function aggregates a dataset into a number of measurements that summarise a polygon, i.e. the outputs of the drill.
