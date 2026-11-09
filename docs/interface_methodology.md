# Vertebra–Disc Interface Methodology

**Project:** L1–L2 Spinal Finite Element Analysis
**Status:** Interface investigation in progress
**Solver:** CalculiX 2.21

## 1. Purpose

This document records the investigation of vertebra–disc
interface constraints in the baseline L1–L2 finite element model.

The objective is to establish mechanically appropriate load
transfer between the vertebral bodies and intervertebral disc
before interpreting stress distributions or attempting
biomechanical validation.

## 2. Baseline model

The model comprises:

- L1 vertebral body
- L2 vertebral body
- Intervertebral disc
- 17,513 nodes
- 62,247 first-order tetrahedral elements

The L2 inferior surface is fixed in all translational directions.

A prescribed displacement of +0.1 mm along the Z-axis is
applied to the L1 superior surface, producing compression.

The vertebrae and disc are connected using four CalculiX
surface-based tie constraints.

## 3. Identified interface problem

The original simulation used the automatically calculated
tie tolerance of approximately 0.01206 mm.

Inspection of the solver warnings identified 228 unique
disc nodes for which the intended tie constraints were
not generated.

A second simulation increased the tie tolerance to 0.05 mm.

This reduced the number of untied disc nodes to 50,
a reduction of approximately 78.1%.

However, the change also substantially altered the
mechanical response.

## 4. Quantitative comparison

| Measurement | Original tolerance | 0.05 mm tolerance |
|---|---:|---:|
| Untied disc nodes | 228 | 50 |
| Axial reaction force | 397.320 N | 556.540 N |
| Effective axial stiffness | 3973.201 N/mm | 5565.400 N/mm |
| Maximum nodal displacement | 0.133626 mm | 0.132768 mm |
| Maximum nodal von Mises stress | 0.987775 MPa | 1.579123 MPa |

Increasing the tie tolerance produced:

- A 40.07% increase in effective axial stiffness.
- An approximately 59.9% increase in maximum nodal
  von Mises stress.
- A relatively small change in maximum nodal displacement.

Both simulations achieved negligible global axial
force-equilibrium residuals.

## 5. Interpretation

The substantial change in axial stiffness indicates that
the calculated mechanical response is sensitive to the
interface constraint configuration.

Increasing the tie tolerance causes additional disc nodes
to become mechanically constrained to the vertebral surfaces.

This changes the load-transfer pathways within the model.

The improved force balance and reduced number of untied
nodes do not independently establish physiological accuracy.

The observed stiffness difference must therefore be treated
as an interface sensitivity finding rather than evidence
that either simulation is biomechanically validated.

## 6. Outstanding questions

1. Are the untied nodes caused by geometric gaps,
   nonconforming meshes or incorrectly defined surfaces?
2. Can the disc–endplate interfaces be made geometrically
   congruent without distorting the anatomy?
3. Would conforming shared-node meshes eliminate the need
   for surface-based tie constraints?
4. How much of the predicted stiffness is attributable
   to interface constraints versus material properties?
5. Does the use of first-order tetrahedral elements with
   a nearly incompressible disc introduce volumetric locking?
6. Are the peak stresses influenced by interface or
   mesh-related numerical artefacts?

## 7. Provisional modelling decision

Further increases in tie tolerance will not be used as
the primary strategy for correcting the interface.

The next investigation will focus on geometric congruency,
surface definitions and the feasibility of conforming meshes.

The preferred approach will be selected after inspecting
the existing mesh and considering published spinal finite
element modelling methodologies.

This decision remains provisional pending further testing.

## 8. Validation limitations

The current model is exploratory.

It uses simplified homogeneous linear-elastic materials,
first-order tetrahedral elements and idealised boundary
conditions.

Mesh convergence, experimental calibration and
physiological validation have not yet been established.

No clinical conclusions should be drawn from the current
stress or stiffness predictions.

## 9. Supporting literature

The proposed interface investigation is informed by published
lumbar finite element modelling studies:

- Ibarz et al. (2013): Geometrically congruent interfaces
  and tied connections between vertebrae and discs.
- Warren et al. (2020): Simplified lumbar modelling
  and computational efficiency.
- Wiczenbach et al. (2023): Shared-node connections
  and interface-specific contact formulations.
- Schmidt et al. (2007): Model calibration and validation.

These publications provide methodological context but do not
validate our particular interface geometry, tie tolerance,
material properties or stiffness predictions.

See [Literature References](references.md) for citations,
DOI links and study-specific limitations.
