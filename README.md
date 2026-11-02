# Spinal Finite Element Analysis (FEA)

**Status:** Work in Progress

## Overview

An exploratory computational biomechanics project investigating
vertebral loading, mechanical stresses, and spinal stability
using finite element analysis (FEA).

The project aims to develop a reproducible workflow combining
medical imaging, anatomical reconstruction, finite element
meshing, mechanical simulation, and visualisation.

## Research Objectives

1. Develop a functioning FEA simulation using an existing
   L1-L2 vertebral model.

2. Reconstruct pathological vertebral anatomy from publicly
   available CT imaging and investigate compression-fracture
   biomechanics.

3. Explore longitudinal changes in vertebral morphology,
   including progressive collapse and kyphotic deformity,
   subject to suitable serial imaging data being available.

## Planned Workflow

### Stage 1: Baseline Simulation

- Import an existing L1-L2 finite element model.
- Examine vertebral and intervertebral disc geometry.
- Define material properties and boundary conditions.
- Simulate axial compression and selected bending loads.
- Analyse stresses, strains, and displacement.

### Stage 2: Compression Fracture Simulation

- Select a suitable pathological CT scan.
- Segment vertebral anatomy.
- Reconstruct and mesh the fractured spinal segment.
- Apply controlled mechanical loading.
- Investigate stress concentrations and deformation.

### Stage 3: Longitudinal Fracture Analysis

- Identify serial CT examinations of the same patient.
- Assess vertebral height loss and kyphotic angulation.
- Compare mechanical behaviour across examinations.
- Investigate potential associations between simulated
  mechanical parameters and observed fracture progression.

This stage is conditional on obtaining suitable
longitudinal imaging data.

## Candidate Datasets

### L1-L2 Finite Element Model

https://zenodo.org/records/3961334

Existing finite element model for initial simulation.

### VerSe 2019/2020

https://github.com/anjany/verse

Public spine CT dataset containing vertebral segmentation
annotations and fracture-related information.

### UWSpineCT / BioMedIA

https://biomedia.doc.ic.ac.uk/data/spine/

Longitudinal pathological spine CT dataset containing
242 scans from 125 patients.

Availability of serial non-neoplastic compression-fracture
cases remains under investigation.

## Planned Software

- Python
- Gmsh
- CalculiX or another suitable open-source FEA solver
- 3D Slicer
- ParaView
- WSL Ubuntu

## Limitations

This project is exploratory and intended for computational
research and educational demonstration.

Mechanical simulations depend on assumptions regarding
material properties, loading, boundary conditions, and
anatomical reconstruction.

FEA results must not be interpreted as validated clinical
predictions of spinal instability or fracture progression.

## Data Availability and Licensing

Original medical imaging datasets and patient-level metadata
are not redistributed in this repository.

Users should obtain datasets from their original sources
and comply with the applicable licensing requirements.

## Project Status

Initial repository setup and dataset feasibility assessment
are in progress.
