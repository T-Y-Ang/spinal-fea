
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


# -------------------------------------------------------------
# MASTER SURFACE BOUNDARY ANALYSIS
# -------------------------------------------------------------
#
# Identify the boundary edges of the vertebral endplate
# surfaces and calculate the nearest boundary distance
# for each rejected disc node.
#
# This is a preliminary geometric diagnostic.
# -------------------------------------------------------------

from scipy.spatial import cKDTree


def analyse_boundary_distances(master_surface, rejected_ids, label):
    """Measure distances from rejected nodes to master boundary vertices."""

    # Extract boundary edges from the triangular master surface.
    boundary = master_surface.extract_feature_edges(
        boundary_edges=True,
        feature_edges=False,
        manifold_edges=False,
        non_manifold_edges=False,
    )

    boundary_points = np.asarray(boundary.points)

    if len(boundary_points) == 0:
        raise ValueError(f"No boundary points found for {label}")

    tree = cKDTree(boundary_points)

    rejected_xyz = np.array([
        coordinates[node_id] for node_id in rejected_ids
    ])

    distances, _ = tree.query(rejected_xyz)

    print()
    print(f"{label} MASTER BOUNDARY DISTANCES")
    print("-" * 45)
    print("Rejected nodes:", len(rejected_ids))
    print("Boundary vertices:", len(boundary_points))
    print(f"Minimum distance: {distances.min():.4f} mm")
    print(f"Median distance:  {np.median(distances):.4f} mm")
    print(f"Maximum distance: {distances.max():.4f} mm")


analyse_boundary_distances(
    l1_endplate,
    l1_rejected,
    "L1",
)

analyse_boundary_distances(
    l2_endplate,
    l2_rejected,
    "L2",
)


# -------------------------------------------------------------
# CLOSEST MASTER SURFACE POINT ANALYSIS
# -------------------------------------------------------------
#
# Find the closest point on the actual triangulated vertebral
# endplate surface for each rejected disc node.
#
# Unlike nearest-vertex distances, this calculation considers
# the interiors and edges of the surface triangles.
# -------------------------------------------------------------

import vtk


def analyse_closest_surface_points(master_surface, rejected_ids, label):

    locator = vtk.vtkStaticCellLocator()
    locator.SetDataSet(master_surface)
    locator.BuildLocator()

    distances = []

    for node_id in rejected_ids:

        point = coordinates[node_id]

        closest_point = [0.0, 0.0, 0.0]
        cell_id = vtk.mutable(0)
        sub_id = vtk.mutable(0)
        distance_squared = vtk.mutable(0.0)

        locator.FindClosestPoint(
            point,
            closest_point,
            cell_id,
            sub_id,
            distance_squared,
        )

        distances.append(np.sqrt(float(distance_squared)))

    distances = np.array(distances)

    print()
    print(f"{label} CLOSEST MASTER SURFACE DISTANCES")
    print("-" * 45)
    print("Rejected nodes:", len(rejected_ids))
    print(f"Minimum distance: {distances.min():.4f} mm")
    print(f"Median distance:  {np.median(distances):.4f} mm")
    print(f"Maximum distance: {distances.max():.4f} mm")

    print(
        "Nodes within 0.05 mm:",
        int(np.sum(distances <= 0.05)),
    )


analyse_closest_surface_points(
    l1_endplate,
    l1_rejected,
    "L1",
)

analyse_closest_surface_points(
    l2_endplate,
    l2_rejected,
    "L2",
)


# -------------------------------------------------------------
# COMPARE CALCULIX AND PYVISTA DISTANCES
# -------------------------------------------------------------

# Extract rejected-node distances reported by CalculiX.
solver_distances = {
    int(node): float(distance)
    for node, distance in re.findall(
        r"no tied MPC\s+generated for node\s+(\d+)"
        r".*?distance:\s*([0-9.Ee+-]+)",
        LOG_PATH.read_text(),
        flags=re.I | re.S,
    )
}


def compare_surface_distances(master_surface, rejected_ids, label):

    locator = vtk.vtkStaticCellLocator()
    locator.SetDataSet(master_surface)
    locator.BuildLocator()

    comparisons = []

    for node_id in rejected_ids:

        point = coordinates[node_id]

        closest_point = [0.0, 0.0, 0.0]
        cell_id = vtk.mutable(0)
        sub_id = vtk.mutable(0)
        distance_squared = vtk.mutable(0.0)

        locator.FindClosestPoint(
            point,
            closest_point,
            cell_id,
            sub_id,
            distance_squared,
        )

        vtk_distance = np.sqrt(float(distance_squared))
        solver_distance = solver_distances[node_id]

        comparisons.append((
            node_id,
            solver_distance,
            vtk_distance,
            vtk_distance - solver_distance,
        ))

    comparisons.sort(
        key=lambda row: abs(row[3]),
        reverse=True,
    )

    print()
    print(f"{label} CALCULIX–PYVISTA DISTANCE COMPARISON")
    print("-" * 65)
    print("Node    CalculiX    PyVista     Difference (mm)")

    for node, solver, vtk_dist, difference in comparisons[:10]:
        print(
            f"{node:5d}   {solver:9.4f}   "
            f"{vtk_dist:9.4f}   {difference:+10.4f}"
        )


compare_surface_distances(
    l1_endplate,
    l1_rejected,
    "L1",
)

compare_surface_distances(
    l2_endplate,
    l2_rejected,
    "L2",
)


# -------------------------------------------------------------
# TRIANGLE PROJECTION ANALYSIS
# -------------------------------------------------------------
#
# Determine whether discrepant nodes project inside or
# outside their nearest master-surface triangle.
#
# This tests the geometry independently of CalculiX's
# internal tie-constraint search algorithm.
# -------------------------------------------------------------

def analyse_triangle_projection(master_surface, node_ids, label):

    locator = vtk.vtkStaticCellLocator()
    locator.SetDataSet(master_surface)
    locator.BuildLocator()

    print()
    print(f"{label} TRIANGLE PROJECTION ANALYSIS")
    print("-" * 65)
    print("Node    Surface distance    Projection")

    for node_id in node_ids:

        point = coordinates[node_id]

        closest_point = [0.0, 0.0, 0.0]
        cell_id = vtk.mutable(0)
        sub_id = vtk.mutable(0)
        distance_squared = vtk.mutable(0.0)

        locator.FindClosestPoint(
            point,
            closest_point,
            cell_id,
            sub_id,
            distance_squared,
        )

        # Obtain the vertices of the closest triangle.
        cell = master_surface.GetCell(int(cell_id))

        vertices = np.array([
            cell.GetPoints().GetPoint(i)
            for i in range(3)
        ])

        a, b, c = vertices

        # Calculate the orthogonal projection onto the
        # infinite plane containing the triangle.
        normal = np.cross(b - a, c - a)
        normal /= np.linalg.norm(normal)

        projected = point - np.dot(point - a, normal) * normal

        # Compute barycentric coordinates.
        v0 = b - a
        v1 = c - a
        v2 = projected - a

        d00 = np.dot(v0, v0)
        d01 = np.dot(v0, v1)
        d11 = np.dot(v1, v1)
        d20 = np.dot(v2, v0)
        d21 = np.dot(v2, v1)

        denominator = d00 * d11 - d01 * d01

        v = (d11 * d20 - d01 * d21) / denominator
        w = (d00 * d21 - d01 * d20) / denominator
        u = 1.0 - v - w

        tolerance = 1e-8

        inside = (
            u >= -tolerance
            and v >= -tolerance
            and w >= -tolerance
        )

        distance = np.sqrt(float(distance_squared))

        print(
            f"{node_id:5d}   "
            f"{distance:12.4f} mm    "
            f"{'INSIDE' if inside else 'OUTSIDE'}"
        )


# Nodes with the largest CalculiX–PyVista discrepancies.
analyse_triangle_projection(
    l1_endplate,
    [191, 81, 188, 194, 21, 80, 23],
    "L1",
)

analyse_triangle_projection(
    l2_endplate,
    [264, 262],
    "L2",
)


# -------------------------------------------------------------
# ENDPLATE FOOTPRINT ANALYSIS
# -------------------------------------------------------------
#
# Test whether the XY projection of each discrepant disc
# node falls inside any master-surface triangle.
#
# This distinguishes an individual triangle-edge effect
# from potential overhang beyond the overall footprint.
# -------------------------------------------------------------

def point_inside_triangle_2d(point, triangle, tolerance=1e-8):
    """Check whether a 2D point lies inside a 2D triangle."""

    a, b, c = triangle

    v0 = b - a
    v1 = c - a
    v2 = point - a

    denominator = (
        v0[0] * v1[1] - v1[0] * v0[1]
    )

    if abs(denominator) < 1e-12:
        return False

    u = (
        v2[0] * v1[1] - v1[0] * v2[1]
    ) / denominator

    v = (
        v0[0] * v2[1] - v2[0] * v0[1]
    ) / denominator

    return (
        u >= -tolerance
        and v >= -tolerance
        and u + v <= 1.0 + tolerance
    )


def analyse_endplate_footprint(master_surface, node_ids, label):

    print()
    print(f"{label} ENDPLATE FOOTPRINT ANALYSIS")
    print("-" * 55)
    print("Node    XY footprint")

    for node_id in node_ids:

        point_xy = np.asarray(coordinates[node_id])[:2]

        inside_any = False

        for cell_id in range(master_surface.n_cells):

            cell = master_surface.GetCell(cell_id)

            triangle_xy = np.array([
                cell.GetPoints().GetPoint(i)[:2]
                for i in range(3)
            ])

            if point_inside_triangle_2d(point_xy, triangle_xy):
                inside_any = True
                break

        print(
            f"{node_id:5d}   "
            f"{'INSIDE' if inside_any else 'OUTSIDE'}"
        )


analyse_endplate_footprint(
    l1_endplate,
    [191, 81, 188, 194, 21, 80, 23],
    "L1",
)

analyse_endplate_footprint(
    l2_endplate,
    [264, 262],
    "L2",
)

# Classify every rejected disc node against its
# corresponding vertebral endplate XY footprint.

analyse_endplate_footprint(
    l1_endplate,
    sorted(l1_rejected),
    "L1 — ALL REJECTED NODES",
)

analyse_endplate_footprint(
    l2_endplate,
    sorted(l2_rejected),
    "L2 — ALL REJECTED NODES",
)

# -------------------------------------------------------------
# DISC INTERFACE SPATIAL SUMMARY
# -------------------------------------------------------------
#
# Compare the spatial extent of the original MED disc
# surface families using their reconstructed mesh nodes.
# -------------------------------------------------------------

for name in (
    "DISC_L1_INNER",
    "DISC_L1_OUTER",
    "DISC_L2_INNER",
    "DISC_L2_OUTER",
):
    node_ids = sorted({
        node_id
        for face in surface_faces[name]
        for node_id in face
    })

    xyz = np.array([
        coordinates[node_id] for node_id in node_ids
    ])

    print(f"\n{name}")
    print(f"Nodes: {len(node_ids)}")
    print(f"Centroid: {np.mean(xyz, axis=0).round(3)}")
    print(f"Minimum XYZ: {np.min(xyz, axis=0).round(3)}")
    print(f"Maximum XYZ: {np.max(xyz, axis=0).round(3)}")

# -------------------------------------------------------------
# INNER VERSUS OUTER DISC RADIAL DISTRIBUTION
# -------------------------------------------------------------
#
# Compare radial distances from a common XY centroid
# at each vertebral interface.
# -------------------------------------------------------------

for level in ("L1", "L2"):

    inner_name = f"DISC_{level}_INNER"
    outer_name = f"DISC_{level}_OUTER"

    def get_surface_xyz(name):
        node_ids = {
            node_id
            for face in surface_faces[name]
            for node_id in face
        }
        return np.array([
            coordinates[node_id] for node_id in sorted(node_ids)
        ])

    inner_xyz = get_surface_xyz(inner_name)
    outer_xyz = get_surface_xyz(outer_name)

    # Use the combined surface centroid as a common reference.
    centre_xy = np.vstack(
        (inner_xyz[:, :2], outer_xyz[:, :2])
    ).mean(axis=0)

    print(f"\n{level} RADIAL DISTRIBUTION")
    print("-" * 45)

    for name, xyz in (
        ("INNER", inner_xyz),
        ("OUTER", outer_xyz),
    ):
        radii = np.linalg.norm(
            xyz[:, :2] - centre_xy,
            axis=1,
        )

        print(
            f"{name}: "
            f"min={radii.min():.2f}, "
            f"median={np.median(radii):.2f}, "
            f"max={radii.max():.2f} mm"
        )

# -------------------------------------------------------------
# DISC INTERFACE SURFACE TOPOLOGY
# -------------------------------------------------------------
#
# Determine how many connected components and boundary edges exist in each original MED disc interface surface.
#
# A connected annular surface typically has two closed boundary loops: an inner loop and an outer loop.
# -------------------------------------------------------------

for name in (
    "DISC_L1_INNER",
    "DISC_L1_OUTER",
    "DISC_L2_INNER",
    "DISC_L2_OUTER",
):

    # Reconstruct the triangular interface surface.
    surface = create_surface_mesh(surface_faces[name])

    # Identify disconnected surface components.
    connected = surface.connectivity()
    region_count = len(np.unique(connected["RegionId"]))

    # Extract boundary edges only.
    boundary = surface.extract_feature_edges(
        boundary_edges=True,
        feature_edges=False,
        manifold_edges=False,
        non_manifold_edges=False,
    )

    print(f"\n{name} TOPOLOGY")
    print("-" * 45)
    print("Surface triangles:", surface.n_cells)
    print("Connected regions:", region_count)
    print("Boundary edges:", boundary.n_cells)

# -------------------------------------------------------------
# DISC INTERFACE BOUNDARY COMPONENTS
# -------------------------------------------------------------
#
# Count connected boundary components and check whether
# each boundary vertex has exactly two incident edges.
# -------------------------------------------------------------

from collections import Counter

for name in (
    "DISC_L1_INNER",
    "DISC_L1_OUTER",
    "DISC_L2_INNER",
    "DISC_L2_OUTER",
):
    surface = create_surface_mesh(surface_faces[name])

    boundary = surface.extract_feature_edges(
        boundary_edges=True,
        feature_edges=False,
        manifold_edges=False,
        non_manifold_edges=False,
    )

    components = boundary.connectivity()
    region_ids = np.unique(components["RegionId"])

    # Each boundary line contributes two vertex endpoints.
    endpoint_counts = Counter()
    for cell in boundary.lines.reshape(-1, 3):
        endpoint_counts[int(cell[1])] += 1
        endpoint_counts[int(cell[2])] += 1

    irregular_vertices = sum(
        degree != 2 for degree in endpoint_counts.values()
    )

    print(f"\n{name} BOUNDARY ANALYSIS")
    print("-" * 45)
    print("Boundary components:", len(region_ids))
    print("Boundary edges:", boundary.n_cells)
    print("Vertices with degree != 2:", irregular_vertices)