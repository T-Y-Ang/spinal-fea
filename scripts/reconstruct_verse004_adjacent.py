"""
Reconstruct T12 and L2 vertebral surfaces from VerSe 2019 subject 004.

The original segmentation geometry is preserved without smoothing.
Vertices are transformed into physical coordinates in millimetres.
"""

from pathlib import Path

import nibabel as nib
import numpy as np
import pyvista as pv
from skimage.measure import marching_cubes


# -------------------------------------------------------------
# 1. INPUT AND OUTPUT PATHS
# -------------------------------------------------------------

mask_path = Path(
    "data/raw/verse2019/sub-verse004/"
    "sub-verse004_seg-vert_msk.nii.gz"
)

output_dir = Path("mesh/verse004")
output_dir.mkdir(parents=True, exist_ok=True)

# VerSe vertebral labels:
# 19 = T12, 20 = L1, 21 = L2.
target_vertebrae = {
    19: "t12",
    21: "l2",
}


# -------------------------------------------------------------
# 2. LOAD SEGMENTATION
# -------------------------------------------------------------

image = nib.load(mask_path)
segmentation = np.asarray(image.dataobj)


# -------------------------------------------------------------
# 3. RECONSTRUCT EACH VERTEBRA
# -------------------------------------------------------------

for label, name in target_vertebrae.items():

    # Extract the binary mask for the selected vertebra.
    mask = segmentation == label

    # Padding prevents clipping at the image boundaries.
    padded_mask = np.pad(
        mask.astype(np.uint8),
        pad_width=1,
        mode="constant",
    )

    # Extract the triangular surface using marching cubes.
    vertices, faces, _, _ = marching_cubes(
        padded_mask,
        level=0.5,
    )

    # Remove the padding offset.
    vertices -= 1

    # Transform voxel coordinates into NIfTI world coordinates.
    world_vertices = nib.affines.apply_affine(
        image.affine,
        vertices,
    )

    # Convert triangle indices to PyVista's face format.
    pv_faces = np.column_stack(
        [
            np.full(len(faces), 3, dtype=np.int64),
            faces,
        ]
    ).ravel()

    surface = pv.PolyData(
        world_vertices,
        pv_faces,
    )

    # Recalculate normals without changing vertex positions.
    surface = surface.compute_normals(
        point_normals=True,
        cell_normals=True,
        consistent_normals=True,
        auto_orient_normals=True,
        inplace=False,
    )

    # Save the unsmoothed triangular surface.
    output_path = output_dir / f"{name}_surface_raw.vtp"
    surface.save(output_path)

    # Report basic geometry and topology.
    problem_edges = surface.extract_feature_edges(
        boundary_edges=True,
        non_manifold_edges=True,
        feature_edges=False,
        manifold_edges=False,
    )

    print(f"\n{name.upper()}")
    print("Segmented voxels:", np.count_nonzero(mask))
    print("Surface vertices:", surface.n_points)
    print("Surface triangles:", surface.n_cells)
    print("Boundary/non-manifold edges:", problem_edges.n_cells)
    print("Manifold:", surface.is_manifold)
    print("Enclosed volume (mm³):", round(surface.volume, 2))
    print("Saved:", output_path)
