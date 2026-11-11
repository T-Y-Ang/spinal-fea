# Spinal FEA — Visualisation Progress

**Checkpoint date:** 12 November 2026  
**Project:** L1–L2 axial compression finite element analysis  
**Status:** Baseline simulations completed; post-processing and visualisation ongoing.

## 1. Completed simulations

Two CalculiX simulations have been completed using the same L1–L2 anatomical mesh with different vertebra–disc tie tolerances.

| Parameter | Original tolerance | 0.05 mm tolerance |
|---|---:|---:|
| Axial reaction force | 397.320 N | 556.540 N |
| Calculated stiffness | 3,973.201 N/mm | 5,565.400 N/mm |
| Maximum nodal displacement | 0.133626 mm | 0.132768 mm |
| Maximum nodal von Mises stress | 0.987775 MPa | 1.579123 MPa |
| Untied disc nodes | 228 | 50 |

Changing the tie tolerance increased calculated stiffness by approximately 40.07%, demonstrating substantial sensitivity to the interface formulation.

The model uses 62,247 first-order tetrahedral elements. The CalculiX FRD results contain 17,511 referenced nodes.

## 2. Completed post-processing

The script `scripts/read_calculix_frd.py` has been developed to extract:

- Node coordinates and identifiers.
- Tetrahedral element connectivity.
- Three-dimensional nodal displacement vectors.
- Six nodal stress tensor components.
- Calculated nodal von Mises stress.

The extracted results can be assembled into a PyVista unstructured grid and exported to VTK format.

The 0.05 mm tolerance simulation has been exported to:

`outputs/baseline_tolerance_005.vtu`

Available fields:

- Node ID
- Displacement
- Displacement Magnitude
- Von Mises Stress

The VTK file is excluded from Git tracking.

## 3. Completed visualisations

The script `scripts/visualize_fea_results.py` generates:

1. `outputs/figures/baseline_tolerance_005_displacement.png`
2. `outputs/figures/baseline_tolerance_005_von_mises.png`
3. `outputs/figures/maximum_stress_node_location.png`
4. `outputs/figures/baseline_tolerance_005_max_stress_section.png`

A central cross-sectional stress figure was also generated earlier:

`outputs/figures/baseline_tolerance_005_stress_section.png`

The visualisations are preliminary and require improved anatomical labels and presentation before inclusion in the portfolio report.

## 4. Anatomical orientation and boundary conditions

The mesh uses a coordinate convention in which positive Z points anatomically inferiorly.

Boundary conditions:

- L2 inferior surface: fixed in X, Y and Z.
- L1 superior surface: prescribed +0.1 mm displacement along Z.

The observed displacement distribution is consistent with these boundary conditions.

## 5. Maximum-stress investigation

The maximum nodal von Mises stress occurs at node 10200.

**Node coordinates (mm):**

- X = 189.187
- Y = 170.912
- Z = 385.422

**Stress results:**

- Von Mises stress: 1.579123 MPa
- Axial normal stress (SZZ): −1.52658 MPa

Node 10200 has both the greatest calculated von Mises stress and the most negative axial normal stress in the model.

A YZ cross-section at X = 189.187 mm reveals a localised high-stress region near a vertebral endplate–disc interface.

The central section at X = 202.3995 mm has a maximum interpolated von Mises stress of approximately 0.6602 MPa, compared with 1.5791 MPa in the section through node 10200.

These findings suggest localised stress concentration near an interface, but the underlying cause has not been established.

## 6. Scientific limitations

The model remains an exploratory computational demonstration.

Important limitations include:

- Simplified isotropic, linear-elastic material properties.
- First-order tetrahedral elements.
- Sensitivity to vertebra–disc tie tolerance.
- Unmatched interface nodes.
- Potential stress extrapolation and mesh-dependent peak values.
- No experimental or clinical validation.

Von Mises stress is not equivalent to compressive pressure. Axial normal stress (SZZ) is a separate quantity, with negative values indicating compression.

The present results should not be used to infer clinical fracture thresholds.

## 7. Next steps

**Immediate next task — Step 332:**

Add the optional `stresses` argument to `attach_frd_results()` in `scripts/read_calculix_frd.py`, allowing axial normal stress (SZZ) to be attached to the PyVista mesh.

Then:

1. Verify that SZZ ranges from −1.52658 to +0.0503111 MPa.
2. Re-export the VTU file with the SZZ field.
3. Generate an axial stress cross-section through node 10200.
4. Improve anatomical orientation, labels and colour bars.
5. Compare stress distributions between the original and 0.05 mm tie-tolerance simulations.
6. Update the spinal FEA README and central GitHub portfolio report.

No additional CalculiX simulation is currently required for these post-processing tasks.

## 8. Resume instructions

Activate the environment:

```bash
conda activate spinal-fea
cd /mnt/c/GitHub/spinal-fea
```

Resume at **Step 332 — Add axial normal stress (SZZ) to the PyVista results**.

The original FRD simulation files remain stored locally under `cases/baseline_compression/` and should not be committed to GitHub.