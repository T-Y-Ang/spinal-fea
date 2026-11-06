# Spinal Finite Element Analysis (FEA)

**Status:** Work in Progress — Baseline Model Preparation

## Overview

An exploratory computational biomechanics project investigating vertebral loading, mechanical stresses, and spinal stability using finite element analysis (FEA).

The project aims to develop a reproducible workflow integrating medical imaging, anatomical reconstruction, finite element meshing, mechanical simulation, and visualisation.

The longer-term research objective is to investigate the mechanical behaviour of vertebral compression fractures, including stress distribution, deformation and potential contributors to progressive vertebral collapse.

This repository documents the development process, including dataset selection, mesh preparation, computational methods, technical challenges and simulation results.

## Research Objectives

1. Develop a functioning FEA simulation using an existing L1–L2 vertebral model.

2. Reconstruct pathological vertebral anatomy from publicly available CT imaging and investigate compression-fracture biomechanics.

3. Explore longitudinal changes in vertebral morphology, including progressive collapse and kyphotic deformity, subject to suitable serial imaging data being available.

## Current Progress

### Stage 1: Baseline L1–L2 Simulation — In Progress

**Source model:** [L1–L2 finite element model — Zenodo](https://zenodo.org/records/3961334)

The initial stage uses an existing anatomical model containing two lumbar vertebrae and the intervening intervertebral disc.

**Completed:**

- Established the Python and CalculiX computational environment under WSL Ubuntu.
- Downloaded and inspected the original MED-format finite element mesh.
- Identified the anatomical element groups representing L1, L2 and the intervertebral disc.
- Developed a Python script to convert the MED mesh into a CalculiX-compatible input file.
- Preserved the anatomical element sets and superior/inferior boundary node groups.
- Performed preliminary investigations of mesh connectivity and geometric proximity between anatomical structures.

**Mesh characteristics:**

| Component | Count |
|---|---:|
| Nodes | 17,513 |
| Tetrahedral elements | 62,247 |
| L1 elements | 29,430 |
| L2 elements | 28,756 |
| Intervertebral disc elements | 4,061 |
| L1 superior boundary nodes | 815 |
| L2 inferior boundary nodes | 929 |

**Preliminary connectivity findings:**

The L1 vertebra, L2 vertebra and intervertebral disc are represented by separate element groups without shared interface nodes.

Geometric proximity analysis identified closely positioned nodes between the vertebrae and disc, but no exactly coincident nodes.

These findings indicate that appropriate mechanical interface constraints must be established and validated before applying loads.

**Remaining tasks:**

- Verify mesh dimensions, coordinate units and anatomical orientation.
- Visualise and inspect the three-dimensional geometry.
- Validate mesh quality and identify vertebra–disc interface surfaces.
- Implement and test suitable interface constraints.
- Assign simplified material properties.
- Define boundary conditions and axial compression loading.
- Execute the first CalculiX simulation.
- Analyse displacement, stress and strain distributions.
- Investigate sensitivity to material properties and boundary conditions.

No completed FEA results are reported at this stage.

### Stage 2: Patient-Specific Compression Fracture Simulation — Planned

The second stage aims to develop an FEA model from an actual CT examination demonstrating vertebral compression fracture.

**Planned workflow:**

1. Identify a suitable CT scan demonstrating a non-instrumented vertebral compression fracture.
2. Segment the relevant vertebral anatomy.
3. Reconstruct the three-dimensional pathological geometry.
4. Generate a computational mesh.
5. Assign material properties and mechanical boundary conditions.
6. Simulate controlled loading.
7. Investigate stress concentrations, deformation and mechanical behaviour.

This stage will build on the computational workflow developed during the baseline simulation.

### Stage 3: Longitudinal Fracture Analysis — Conditional

If suitable serial CT examinations become available, the project may be extended to investigate progressive vertebral collapse.

Potential analyses include:

- Vertebral height loss.
- Changes in local kyphotic angulation.
- Differences in predicted mechanical stress and deformation.
- Relationships between observed morphological progression and simulated mechanical parameters.

This stage is conditional on identifying suitable longitudinal imaging with reliable patient matching and examination chronology.

## Dataset Investigation

### L1–L2 Finite Element Model

[Zenodo record](https://zenodo.org/records/3961334)

Selected as the initial baseline model because it provides an existing volumetric mesh containing L1, L2 and the intervening disc.

The original MED mesh is retained locally and converted into CalculiX format using the repository's Python conversion script.

### VerSe 2019/2020

[VerSe repository](https://github.com/anjany/verse)

A potential source of vertebral CT imaging and segmentation annotations for subsequent patient-specific modelling.

The availability of suitable, confirmed compression-fracture cases requires further assessment.

### UWSpineCT / BioMedIA

[Dataset source](https://biomedia.doc.ic.ac.uk/data/spine/)

An initial feasibility investigation was undertaken to identify suitable pathological spine CT examinations.

The screening encountered limitations including spinal instrumentation, imaging resolution and uncertainty regarding the availability of suitable serial non-instrumented compression-fracture cases.

The dataset has therefore not been selected for the first patient-specific simulation.

## Repository Structure

```text
spinal-fea/
├── data/               # Local imaging and derived data
├── mesh/               # Finite element mesh files
├── scripts/
│   ├── convert_med_to_calculix.py
│   └── screen_ct_scans.py
└── README.md
```

Additional directories and scripts will be documented as the simulation workflow develops.

Large imaging datasets, downloaded meshes and generated solver outputs are excluded from version control.

## Computational Environment

**Implemented:**

- Python 3.11
- NumPy
- SciPy
- NiBabel
- h5py
- meshio
- CalculiX 2.21
- WSL Ubuntu

**Planned or under consideration:**

- Gmsh
- 3D Slicer
- ParaView

## Reproducibility

The baseline mesh originates from the Zenodo record linked above and is not redistributed in this repository.

The conversion script can be executed after obtaining the source MED file:

```bash
python scripts/convert_med_to_calculix.py
```

The script reads `mesh/L1-L2.med` and produces `mesh/L1-L2_calculix.inp`, preserving the principal anatomical element groups and selected boundary node groups.

The generated file contains mesh geometry and sets; it is not yet a complete executable mechanical simulation.

Further documentation will be added for material assignments, interface constraints, loading conditions and solver execution.

## Limitations

This project is exploratory and intended for computational research and educational demonstration.

Finite element predictions are sensitive to assumptions regarding material properties, loading conditions, boundary constraints, mesh quality and anatomical reconstruction.

The initial model uses simplified anatomical regions and has not yet undergone mechanical verification or validation.

Results from future simulations must not be interpreted as validated clinical predictions of spinal instability, fracture progression or the need for surgical intervention.

## Data Availability and Licensing

Original medical imaging datasets, patient-level metadata and downloaded third-party meshes are not redistributed in this repository.

Users should obtain source datasets directly from their original providers and comply with applicable licensing and attribution requirements.

Any future redistribution of derived geometry or meshes will require review of the relevant source licences.

## Next Milestone

**Establish a functioning baseline L1–L2 axial compression simulation in CalculiX.**

The immediate priority is to verify the geometry and coordinate system, establish mechanically appropriate vertebra–disc interfaces, and validate the model before interpreting stress or displacement results.
