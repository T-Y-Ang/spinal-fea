
# -------------------------------------------------------------
# SPINAL FEA — INTERFACE TIE VISUALISATION
# -------------------------------------------------------------
#
# Purpose:
# Visualise the disc–vertebra interface geometry and identify
# nodes for which CalculiX could not generate tie constraints.
#
# This script reads existing mesh files without modifying them.
# -------------------------------------------------------------

from pathlib import Path
import re

import numpy as np
import pyvista as pv


# -------------------------------------------------------------
# FILE PATHS
# -------------------------------------------------------------

MESH_PATH = Path("mesh/L1-L2_calculix.inp")
SURFACE_PATH = Path("mesh/L1-L2_interfaces.inp")

LOG_PATH = Path(
    "cases/baseline_compression/baseline_tolerance_005.log"
)

OUTPUT_DIR = Path("outputs/figures")


# -------------------------------------------------------------
# LOAD NODE COORDINATES AND ELEMENT CONNECTIVITY
# -------------------------------------------------------------

coordinates = {}
elements = {}

mode = None

for raw_line in MESH_PATH.read_text().splitlines():

    line = raw_line.strip()

    if line.upper().startswith("*NODE"):
        mode = "nodes"
        continue

    if line.upper().startswith("*ELEMENT"):
        mode = "elements"
        continue

    if line.startswith("*"):
        mode = None
        continue

    if not line or line.startswith("**"):
        continue

    values = [value.strip() for value in line.split(",")]

    if mode == "nodes":
        node_id = int(values[0])

        coordinates[node_id] = np.array(
            [float(value) for value in values[1:4]]
        )

    elif mode == "elements":
        element_id = int(values[0])

        elements[element_id] = tuple(
            int(value) for value in values[1:5]
        )


# -------------------------------------------------------------
# VERIFY MESH LOADING
# -------------------------------------------------------------

print("MESH LOADING")
print("-" * 45)

print("Nodes loaded:", len(coordinates))
print("Tetrahedral elements loaded:", len(elements))

assert len(coordinates) == 17513, "Unexpected node count"
assert len(elements) == 62247, "Unexpected element count"

print("Mesh loading successful.")


# -------------------------------------------------------------
# RECONSTRUCT INTERFACE SURFACES
# -------------------------------------------------------------
#
# Each C3D4 tetrahedron has four triangular faces.
# CalculiX identifies these as S1, S2, S3 and S4.
#
# Convert each element-face reference into three node IDs.
# -------------------------------------------------------------

FACE_NODES = {
    "S1": (0, 1, 2),
    "S2": (0, 3, 1),
    "S3": (1, 3, 2),
    "S4": (2, 3, 0),
}

# Each surface will contain a list of triangular faces.
surface_faces = {}

current_surface = None

for raw_line in SURFACE_PATH.read_text().splitlines():

    line = raw_line.strip()

    if line.upper().startswith("*SURFACE"):

        match = re.search(
            r"NAME=([^,\s]+)",
            line,
            flags=re.I,
        )

        if match is None:
            raise ValueError(f"Surface name missing: {line}")

        current_surface = match.group(1).upper()
        surface_faces[current_surface] = []
        continue

    if not line or line.startswith("**"):
        continue

    if line.startswith("*"):
        current_surface = None
        continue

    if current_surface is None:
        continue

    element_text, face_id = [
        value.strip()
        for value in line.split(",")[:2]
    ]

    element_id = int(element_text)
    face_id = face_id.upper()

    element_nodes = elements[element_id]

    triangle = tuple(
        element_nodes[index]
        for index in FACE_NODES[face_id]
    )

    surface_faces[current_surface].append(triangle)


# -------------------------------------------------------------
# VERIFY SURFACE RECONSTRUCTION
# -------------------------------------------------------------

print()
print("INTERFACE SURFACE RECONSTRUCTION")
print("-" * 45)

for surface_name, faces in surface_faces.items():
    print(f"{surface_name:20s}: {len(faces):5d} faces")

assert len(surface_faces) == 6, "Expected six surfaces"

assert sum(
    len(faces) for faces in surface_faces.values()
) == 3999, "Unexpected total interface face count"

print("Surface reconstruction successful.")


# -------------------------------------------------------------
# EXTRACT REJECTED TIE NODES
# -------------------------------------------------------------

rejected_nodes = {
    int(node_id)
    for node_id in re.findall(
        r"no tied MPC\s+generated for node\s+(\d+)",
        LOG_PATH.read_text(),
        flags=re.I,
    )
}

l1_outer_nodes = {
    node_id
    for face in surface_faces["DISC_L1_OUTER"]
    for node_id in face
}

l1_rejected = sorted(rejected_nodes & l1_outer_nodes)

assert len(l1_rejected) == 29, "Unexpected L1 rejected-node count"


# -------------------------------------------------------------
# CONVERT TRIANGULAR SURFACES INTO PYVISTA MESHES
# -------------------------------------------------------------

def create_surface_mesh(faces):
    """Create a triangular PyVista mesh from node-ID faces."""

    unique_ids = sorted({
        node_id
        for face in faces
        for node_id in face
    })

    id_to_index = {
        node_id: index
        for index, node_id in enumerate(unique_ids)
    }

    points = np.array([
        coordinates[node_id]
        for node_id in unique_ids
    ])

    triangles = np.array([
        [3] + [id_to_index[node_id] for node_id in face]
        for face in faces
    ], dtype=np.int64)

    return pv.PolyData(points, triangles.ravel())


# Build the three surfaces.
l1_endplate = create_surface_mesh(
    surface_faces["L1_INFERIOR"]
)

disc_inner = create_surface_mesh(
    surface_faces["DISC_L1_INNER"]
)

disc_outer = create_surface_mesh(
    surface_faces["DISC_L1_OUTER"]
)

rejected_points = pv.PolyData(
    np.array([coordinates[node_id] for node_id in l1_rejected])
)


# -------------------------------------------------------------
# RENDER L1 INTERFACE
# -------------------------------------------------------------

plotter = pv.Plotter(
    off_screen=True,
    window_size=(1400, 1000),
)

plotter.set_background("white")

plotter.add_mesh(
    l1_endplate,
    color="lightgrey",
    opacity=0.45,
    show_edges=True,
    edge_color="grey",
    label="L1 inferior endplate",
)

plotter.add_mesh(
    disc_inner,
    color="seagreen",
    opacity=0.8,
    label="Disc inner interface",
)

plotter.add_mesh(
    disc_outer,
    color="orange",
    opacity=0.7,
    label="Disc outer interface",
)

plotter.add_mesh(
    rejected_points,
    color="red",
    point_size=16,
    render_points_as_spheres=True,
    label="29 rejected tie nodes",
)

plotter.add_axes()
plotter.add_legend()
plotter.view_isometric()

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_path = OUTPUT_DIR / "l1_interface_tie_failures.png"

plotter.screenshot(str(output_path))
plotter.close()

print()
print("L1 INTERFACE VISUALISATION")
print("-" * 45)
print("Rejected nodes:", len(l1_rejected))
print("Saved:", output_path)
print("File size:", output_path.stat().st_size, "bytes")


# -------------------------------------------------------------
# L2 INTERFACE VISUALISATION
# -------------------------------------------------------------

# Identify rejected nodes belonging to the L2 outer interface.
l2_outer_nodes = {
    node_id
    for face in surface_faces["DISC_L2_OUTER"]
    for node_id in face
}

l2_rejected = sorted(rejected_nodes & l2_outer_nodes)

assert len(l2_rejected) == 21, "Unexpected L2 rejected-node count"

# Reconstruct the L2 interface surfaces.
l2_endplate = create_surface_mesh(
    surface_faces["L2_SUPERIOR"]
)

l2_disc_inner = create_surface_mesh(
    surface_faces["DISC_L2_INNER"]
)

l2_disc_outer = create_surface_mesh(
    surface_faces["DISC_L2_OUTER"]
)

l2_rejected_points = pv.PolyData(
    np.array([coordinates[node_id] for node_id in l2_rejected])
)

# Create a separate figure for the L2 interface.
plotter = pv.Plotter(
    off_screen=True,
    window_size=(1400, 1000),
)

plotter.set_background("white")

plotter.add_mesh(
    l2_endplate,
    color="lightgrey",
    opacity=0.45,
    show_edges=True,
    edge_color="grey",
    label="L2 superior endplate",
)

plotter.add_mesh(
    l2_disc_inner,
    color="seagreen",
    opacity=0.8,
    label="Disc inner interface",
)

plotter.add_mesh(
    l2_disc_outer,
    color="orange",
    opacity=0.7,
    label="Disc outer interface",
)

plotter.add_mesh(
    l2_rejected_points,
    color="red",
    point_size=16,
    render_points_as_spheres=True,
    label="21 rejected tie nodes",
)

plotter.add_axes()
plotter.add_legend()
plotter.view_isometric()

output_path = OUTPUT_DIR / "l2_interface_tie_failures.png"

plotter.screenshot(str(output_path))
plotter.close()

print()
print("L2 INTERFACE VISUALISATION")
print("-" * 45)
print("Rejected nodes:", len(l2_rejected))
print("Saved:", output_path)
print("File size:", output_path.stat().st_size, "bytes")
