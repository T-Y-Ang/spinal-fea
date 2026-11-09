# Spinal FEA — Validation Progress

**Status:** Baseline simulations completed; numerical and interface validation ongoing.

**Last completed:** Step 217 — Confirmed availability of baseline CalculiX result files.

**Next:** Generate displacement and von Mises stress visualisations for both baseline simulations.

## Model

- Anatomy: L1, L2 and intervertebral disc
- Mesh: 17,513 nodes, 62,247 tetrahedral elements
- Solver: CalculiX
- Loading: Displacement-controlled
- L2 inferior surface: Fixed in X, Y and Z
- L1 superior surface: +0.1 displacement along Z
- Loading direction: Confirmed to produce compression

## Simulations

1. `baseline_test` — default tie tolerance
2. `baseline_tolerance_005` — tie tolerance 0.05

Both simulations completed successfully.

## Interface validation

- Default tolerance: 228 untied disc nodes
- Tolerance 0.05: 50 untied disc nodes
- Reduction: 78.1%

Some remaining untied nodes are located near the outer boundaries of the disc interfaces.

## Displacement comparison

- Maximum displacement, original: 0.133626
- Maximum displacement, tolerance 0.05: 0.132768
- Difference: approximately −0.64%

## Von Mises stress comparison

| Region | Original mean | Tolerance 0.05 mean |
|---|---:|---:|
| L1 | 0.133818 | 0.194720 |
| L2 | 0.139232 | 0.200127 |
| Disc | 0.078437 | 0.100023 |

Global maximum von Mises stress:
- Original: 0.987775 at node 10388 (L2)
- Tolerance 0.05: 1.579123 at node 10200 (L2)

Increasing the tie tolerance substantially changes the calculated stress field.

**Important:** Stress units, material properties, boundary-condition effects and mesh convergence have not yet been fully validated. Results are exploratory and should not be interpreted as clinically validated biomechanics.

## Additional validation — Steps 132–143

### Peak-stress location

The maximum von Mises stress in both simulations occurs in L2, near its superior endplate rather than at the fixed inferior surface.

- Original tolerance: node 10388
- Tolerance 0.05: node 10200

This reduces concern that the peak is located directly at the fixed boundary, but does not exclude stress concentrations caused by the tie constraints, element formulation or mesh geometry.

### Material properties

Both simulations use simplified, homogeneous, isotropic, linear-elastic materials.

| Material | Young's modulus | Poisson's ratio |
|---|---:|---:|
| Vertebral bone | 1000 MPa | 0.30 |
| Intervertebral disc | 10 MPa | 0.45 |

These are exploratory modelling assumptions, not a validated representation of the heterogeneous vertebral bodies or disc.

The model does not separately represent cortical bone, cancellous bone, annulus fibrosus or nucleus pulposus.

### Reaction-force equilibrium

Reaction forces were extracted from CalculiX FRD output using the FORC data block.

| Measurement | Original tolerance | Tolerance 0.05 |
|---|---:|---:|
| L1 superior Fz | +397.320062 | +556.540011 |
| L2 inferior Fz | -397.320065 | -556.539988 |
| Net Fz residual | approximately -0.000002 | +0.000024 |

Force values are in N, assuming consistent N-mm-MPa units.

Both simulations demonstrate negligible global force imbalance relative to their axial reaction forces.

### Effective axial stiffness

The prescribed L1 superior displacement is +0.1 mm along Z.

Effective axial stiffness was calculated as:

k = abs(total L2 inferior Fz) / 0.1 mm

| Measurement | Original tolerance | Tolerance 0.05 |
|---|---:|---:|
| Reaction-force magnitude | 397.320 N | 556.540 N |
| Axial stiffness | 3973.201 N/mm | 5565.400 N/mm |
| Untied disc nodes | 228 | 50 |

Increasing the tie tolerance from the CalculiX default (approximately 0.01206) to 0.05 increased the calculated axial stiffness by 40.07%.

This demonstrates substantial sensitivity of the global mechanical response to the disc-vertebra interface constraints.

The modified model is not automatically more physiologically accurate simply because more nodes were successfully tied.

### Outstanding limitations

- 50 disc interface nodes remain untied at tolerance 0.05.
- The influence of interface gaps and tie constraints remains unresolved.
- Mesh convergence has not been demonstrated.
- First-order tetrahedral elements and the nearly incompressible disc material may introduce artificial numerical stiffness.
- The simplified materials and boundary conditions are not physiologically validated.
- The model does not include facets, ligaments or muscle forces.
- Results are suitable for an exploratory FEA demonstration, not clinical inference.

## Additional interface investigation — Steps 145–213

### Original mesh surface definitions

The original `mesh/L1-L2.med` file was inspected using HDF5 metadata.

The MED mesh contains four separately defined intervertebral disc interface surface families:

| Original MED family | CalculiX surface |
|---|---|
| `IVD_L1L2_L1_Inner_Face` | `DISC_L1_INNER` |
| `IVD_L1L2_L1_Outer_Face` | `DISC_L1_OUTER` |
| `IVD_L1L2_L2_Inner_Face` | `DISC_L2_INNER` |
| `IVD_L1L2_L2_Outer_Face` | `DISC_L2_OUTER` |

The inner/outer distinction is present in the original source mesh and was not introduced during conversion to CalculiX.

### Spatial distribution

The interface node coordinates were analysed to compare central and peripheral surface geometry.

| Surface | Nodes | Median radial distance (mm) | Maximum radial distance (mm) |
|---|---:|---:|---:|
| L1 inner | 153 | 11.24 | 18.39 |
| L1 outer | 168 | 20.44 | 26.90 |
| L2 inner | 159 | 11.64 | 18.32 |
| L2 outer | 173 | 21.16 | 26.28 |

Radial distances were calculated relative to a common XY centroid for each interface.

The outer surfaces occupy more peripheral regions than the inner surfaces.

### Surface topology

Surface connectivity and boundary topology were examined using PyVista.

| Surface | Triangles | Connected regions | Closed boundary loops |
|---|---:|---:|---:|
| L1 inner | 264 | 1 | 1 |
| L1 outer | 231 | 1 | 2 |
| L2 inner | 276 | 1 | 1 |
| L2 outer | 240 | 1 | 2 |

All boundary vertices had degree two.

These findings establish that the original interface mesh contains connected central surface patches and surrounding annular surfaces.

Although this geometry is consistent with central and peripheral anatomical disc regions, the original MED metadata does not independently establish the tissue composition or intended mechanical attachment conditions.

### Rejected tie-node investigation

At a tie position tolerance of 0.05 mm:

- 29 nodes remained untied at the L1–disc interface.
- 21 nodes remained untied at the L2–disc interface.
- All 50 rejected nodes belonged to the outer disc interface surfaces.

The rejected nodes were visualised in three dimensions and were concentrated around the peripheral disc–vertebra interfaces.

Distances to the finite triangular vertebral endplate surfaces were evaluated using VTK/PyVista.

All 50 rejected nodes were farther than 0.05 mm from their respective master surfaces.

An additional XY-projected endplate footprint analysis identified:

- 7 L1 rejected nodes outside the projected endplate footprint.
- 3 L2 rejected nodes outside the projected endplate footprint.
- 40 remaining rejected nodes inside their respective projected footprints.

The XY footprint analysis is a geometric screening method, not a definitive three-dimensional anatomical classification.

Several peripheral nodes also showed discrepancies between CalculiX-reported distances and finite-triangle closest-point distances. These discrepancies were associated with nodes outside the projected endplate footprints and may reflect differences in projection methodology.

### Interpretation

The original MED mesh has coherent central and annular interface topology.

The remaining tie failures are concentrated in peripheral annular regions, where disc–vertebra geometry and surface alignment require careful interpretation.

Peripheral extension beyond a vertebral endplate is not automatically a mesh defect. Conversely, a geometrically coherent annular surface does not establish that all its nodes are correctly attached.

The existing 40.07% change in calculated axial stiffness between tie configurations demonstrates that interface treatment materially affects the mechanical response.

Consequently:

- The original mesh geometry has been preserved.
- Tie tolerance has not been increased beyond the investigated 0.05 mm configuration.
- No rejected nodes have been removed or artificially repositioned.
- The mechanical significance of the remaining untied nodes remains unresolved.
- Further validation is required before interpreting the results as physiologically representative.

### Visualisation and next validation priority

The following interface figures have been generated:

- `outputs/figures/l1_interface_tie_failures.png`
- `outputs/figures/l2_interface_tie_failures.png`
- `outputs/figures/rejected_tie_nodes_3d.png`
- `outputs/figures/rejected_tie_nodes_by_interface.png`
- `outputs/figures/spinal_fea_anatomical_orientation.png`

CalculiX result files are available for both baseline simulations:

- `cases/baseline_compression/baseline_test.frd`
- `cases/baseline_compression/baseline_tolerance_005.frd`

The next priority is to visualise displacement magnitude and von Mises stress for both simulations, investigate potential interface-related stress concentrations, and assess the implications for numerical verification.

The model remains an exploratory computational demonstration rather than a validated biomechanical predictor.

## Next steps

1. Prepare three-dimensional geometry and field visualisations.
2. Compare displacement and von Mises stress distributions.
3. Inspect interface regions and possible numerical artefacts.
4. Consider targeted interface repair and mesh refinement.
5. Document model limitations and sensitivity findings.
6. Prepare the GitHub portfolio report.
