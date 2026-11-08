# Spinal FEA — Validation Progress

**Status:** Validation in progress  
**Last completed:** Step 131  
**Next:** Step 132 — Investigate peak-stress locations relative to the fixed L2 boundary.

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

## Next steps

1. Step 132: Determine whether the maximum-stress nodes are close to the fixed inferior L2 boundary.
2. Examine stress concentrations and potential boundary-condition artefacts.
3. Verify material properties and physical units.
4. Extract reaction forces and calculate effective axial stiffness.
5. Generate displacement and von Mises stress visualisations in ParaView.
6. Compare simulations and document limitations.
7. Prepare the GitHub portfolio report.