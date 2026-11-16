"""
Reconstruct the L1 vertebral surface from VerSe 2019 subject 004.

The original segmentation is preserved without smoothing.
Output coordinates are in millimetres in the NIfTI world space.
"""

from pathlib import Path

import nibabel as nib
import numpy as np
import pyvista as pv
from skimage.measure import marching_cubes


# -------------------------------------------------------------
# 1. INPUT AND OUTPUT PATHS
# -------------------------------------------------------------

data_dir = Path("data/raw/verse2019/sub-verse004")
output_dir = Path("mesh/verse004")
output_dir.mkdir(parents=True, exist_ok=True)

mask_path = data_dir / "sub-verse004_seg-vert_msk.nii.gz"
output_path = output_dir / "l1_surface_raw.vtp"


# -------------------------------------------------------------
# 2. LOAD L1 SEGMENTATION
# -------------------------------------------------------------

image = nib.load(mask_path)

# VerSe label 20 corresponds to L1.
mask = np.asarray(image.dataobj) == 20

print("L1 voxels:", np.count_nonzero(mask))


# -------------------------------------------------------------
# 3. EXTRACT TRIANGULAR SURFACE
# -------------------------------------------------------------

# Padding ensures that a surface can be extracted even if the
# segmented vertebra touches the image boundary.
padded_mask = np.pad(
    mask.astype(np.uint8),
    pad_width=1,
    mode="constant",
)

# Marching cubes returns vertices in padded voxel coordinates.
vertices, faces, _, _ = marching_cubes(
    padded_mask,
    level=0.5,
)

# Remove the one-voxel padding offset.
vertices -= 1


# -------------------------------------------------------------
# 4. CONVERT TO PHYSICAL COORDINATES
# -------------------------------------------------------------

# The NIfTI affine accounts for voxel spacing, rotation and
# translation, including the slightly oblique CT acquisition.
world_vertices = nib.affines.apply_affine(
    image.affine,
    vertices,
)


# -------------------------------------------------------------
# 5. CREATE AND SAVE PYVISTA SURFACE
# -------------------------------------------------------------

# PyVista expects each triangular face in the form:
# [3, vertex_1, vertex_2, vertex_3].
pv_faces = np.column_stack(
    [
        np.full(len(faces), 3, dtype=np.int64),
        faces,
    ]
).ravel()

surface = pv.PolyData(world_vertices, pv_faces)

# Fix triangle orientation without smoothing the geometry.
surface = surface.compute_normals(
    auto_orient_normals=True,
    consistent_normals=True,
    inplace=False,
)

surface.save(output_path)


# -------------------------------------------------------------
# 6. REPORT INITIAL SURFACE PROPERTIES
# -------------------------------------------------------------

print("Surface vertices:", surface.n_points)
print("Surface triangles:", surface.n_cells)
print("Bounds (mm):", surface.bounds)
print("Surface area (mm²):", round(surface.area, 2))
print("Saved:", output_path)
