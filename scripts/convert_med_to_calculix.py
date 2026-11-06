"""
Convert the L1-L2 MED mesh into a CalculiX-compatible INP file.

The converter preserves:
- L1 and L2 vertebral volume elements
- Intervertebral disc volume elements
- Superior L1 and inferior L2 boundary nodes

The original MED file remains unchanged.
"""

from pathlib import Path

import meshio
import numpy as np


# -------------------------------------------------------------
# FILE PATHS
# -------------------------------------------------------------

input_path = Path("mesh/L1-L2.med")
output_path = Path("mesh/L1-L2_calculix.inp")


# -------------------------------------------------------------
# READ ORIGINAL MESH
# -------------------------------------------------------------

mesh = meshio.read(input_path)

points = mesh.points

# Extract tetrahedral elements and their MED family identifiers
tetra_index = next(
    i for i, block in enumerate(mesh.cells)
    if block.type == "tetra"
)

tetra = mesh.cells[tetra_index].data.copy()

# -------------------------------------------------------------
# VALIDATE AND CORRECT TETRAHEDRAL ORIENTATION
# -------------------------------------------------------------

def signed_tetra_volumes(connectivity):
    vertices = points[connectivity]

    a = vertices[:, 0, :]
    b = vertices[:, 1, :]
    c = vertices[:, 2, :]
    d = vertices[:, 3, :]

    return np.einsum(
        "ij,ij->i",
        np.cross(b - a, c - a),
        d - a
    ) / 6.0


volumes = signed_tetra_volumes(tetra)

# Reject degenerate elements before attempting correction.
# The tolerance is relative to the characteristic mesh volume.
volume_tolerance = max(np.max(np.abs(volumes)) * 1e-12, 1e-15)

if np.any(np.abs(volumes) <= volume_tolerance):
    raise ValueError("Degenerate tetrahedral elements detected.")

# Reverse only elements with negative orientation.
negative = volumes < 0

tetra[negative, 1], tetra[negative, 2] = (
    tetra[negative, 2].copy(),
    tetra[negative, 1].copy()
)

# Verify the corrected connectivity.
corrected_volumes = signed_tetra_volumes(tetra)

if not np.all(corrected_volumes > volume_tolerance):
    raise ValueError("Tetrahedral orientation correction failed.")

print(
    "Orientation validation passed:",
    len(tetra),
    "positive-volume tetrahedra"
)

tetra_families = mesh.cell_data["cell_tags"][tetra_index]


# -------------------------------------------------------------
# DEFINE ANATOMICAL ELEMENT SETS
# -------------------------------------------------------------

element_sets = {
    "L1": -20,
    "L2": -21,
    "DISC": -19,
}

# Node families for loading and fixation
node_sets = {
    "L1_TOP": 8,
    "L2_BOTTOM": 7,
}

node_families = mesh.point_data["point_tags"]


# -------------------------------------------------------------
# WRITE CALCULIX INPUT FILE
# -------------------------------------------------------------

with output_path.open("w") as f:

    f.write("*HEADING\n")
    f.write("L1-L2 spinal finite element mesh\n")

    # Write nodes using 1-based indexing
    f.write("*NODE\n")

    for node_id, (x, y, z) in enumerate(points, start=1):
        f.write(
            f"{node_id}, {x:.9g}, {y:.9g}, {z:.9g}\n"
        )

    # Write 4-node tetrahedral elements
    f.write("*ELEMENT, TYPE=C3D4, ELSET=ALL_SOLIDS\n")

    for element_id, connectivity in enumerate(tetra, start=1):

        node_ids = connectivity + 1

        f.write(
            f"{element_id}, "
            + ", ".join(map(str, node_ids))
            + "\n"
        )

    # Write anatomical element sets
    for name, family_id in element_sets.items():

        element_ids = (
            np.where(tetra_families == family_id)[0] + 1
        )

        f.write(f"*ELSET, ELSET={name}\n")

        for start in range(0, len(element_ids), 12):
            chunk = element_ids[start:start + 12]
            f.write(
                ", ".join(map(str, chunk)) + "\n"
            )

    # Write boundary-condition node sets
    for name, family_id in node_sets.items():

        node_ids = (
            np.where(node_families == family_id)[0] + 1
        )

        f.write(f"*NSET, NSET={name}\n")

        for start in range(0, len(node_ids), 12):
            chunk = node_ids[start:start + 12]
            f.write(
                ", ".join(map(str, chunk)) + "\n"
            )


# -------------------------------------------------------------
# VERIFY CONVERSION SUMMARY
# -------------------------------------------------------------

print("Conversion complete.")
print("Output:", output_path)
print("Nodes:", len(points))
print("Tetrahedral elements:", len(tetra))

for name, family_id in element_sets.items():
    count = np.sum(tetra_families == family_id)
    print(f"Element set {name}: {count}")

for name, family_id in node_sets.items():
    count = np.sum(node_families == family_id)
    print(f"Node set {name}: {count}")
