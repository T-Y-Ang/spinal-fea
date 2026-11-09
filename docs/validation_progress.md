# Spinal FEA — Validation Progress

**Status:** Validation in progress
**Last completed:** Step 144
**Next:** Step 146 — Prepare 3D visualisation of the baseline simulations.

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

The maximum von Mises stress in both simulations occurs in L2,
near its superior endplate rather than at the fixed inferior surface.

- Original tolerance: node 10388
- Tolerance 0.05: node 10200

This reduces concern that the peak is located directly at the fixed
boundary, but does not exclude stress concentrations caused by the
tie constraints, element formulation or mesh geometry.

### Material properties

Both simulations use simplified, homogeneous, isotropic,
linear-elastic materials.

| Material | Young's modulus | Poisson's ratio |
|---|---:|---:|
| Vertebral bone | 1000 MPa | 0.30 |
| Intervertebral disc | 10 MPa | 0.45 |

These are exploratory modelling assumptions, not a validated
representation of the heterogeneous vertebral bodies or disc.

The model does not separately represent cortical bone, cancellous
bone, annulus fibrosus or nucleus pulposus.

### Reaction-force equilibrium

Reaction forces were extracted from CalculiX FRD output using
the FORC data block.

| Measurement | Original tolerance | Tolerance 0.05 |
|---|---:|---:|
| L1 superior Fz | +397.320062 | +556.540011 |
| L2 inferior Fz | -397.320065 | -556.539988 |
| Net Fz residual | approximately -0.000002 | +0.000024 |

Force values are in N, assuming consistent N-mm-MPa units.

Both simulations demonstrate negligible global force imbalance
relative to their axial reaction forces.

### Effective axial stiffness

The prescribed L1 superior displacement is +0.1 mm along Z.

Effective axial stiffness was calculated as:

k = abs(total L2 inferior Fz) / 0.1 mm

| Measurement | Original tolerance | Tolerance 0.05 |
|---|---:|---:|
| Reaction-force magnitude | 397.320 N | 556.540 N |
| Axial stiffness | 3973.201 N/mm | 5565.400 N/mm |
| Untied disc nodes | 228 | 50 |

Increasing the tie tolerance from the CalculiX default
(approximately 0.01206) to 0.05 increased the calculated
axial stiffness by 40.07%.

This demonstrates substantial sensitivity of the global mechanical
response to the disc-vertebra interface constraints.

The modified model is not automatically more physiologically
accurate simply because more nodes were successfully tied.

### Outstanding limitations

- 50 disc interface nodes remain untied at tolerance 0.05.
- The influence of interface gaps and tie constraints remains unresolved.
- Mesh convergence has not been demonstrated.
- First-order tetrahedral elements and the nearly incompressible
  disc material may introduce artificial numerical stiffness.
- The simplified materials and boundary conditions are not
  physiologically validated.
- The model does not include facets, ligaments or muscle forces.
- Results are suitable for an exploratory FEA demonstration,
  not clinical inference.

## Next steps

1. Prepare three-dimensional geometry and field visualisations.
2. Compare displacement and von Mises stress distributions.
3. Inspect interface regions and possible numerical artefacts.
4. Consider targeted interface repair and mesh refinement.
5. Document model limitations and sensitivity findings.
6. Prepare the GitHub portfolio report.
