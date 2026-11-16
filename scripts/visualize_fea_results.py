
from pathlib import Path

import pyvista as pv


# ---------------------------------------------------------
# LOAD THE EXISTING FINITE ELEMENT RESULTS
# ---------------------------------------------------------

mesh = pv.read("outputs/baseline_tolerance_005.vtu")

print("Nodes:", mesh.n_points)
print("Elements:", mesh.n_cells)


# ---------------------------------------------------------
# EXTRACT THE EXTERNAL SURFACE
# ---------------------------------------------------------

# The surface is easier to visualise than the complete volumetric tetrahedral mesh.

surface = mesh.extract_surface(algorithm="dataset_surface")

# ---------------------------------------------------------
# CREATE A 3D DISPLACEMENT VISUALISATION
# ---------------------------------------------------------

plotter = pv.Plotter(off_screen=True, window_size=(1400, 1000))

plotter.add_mesh(
    surface,
    scalars="Displacement Magnitude",
    cmap="viridis",
    show_edges=False,
    scalar_bar_args={
        "title": "Displacement (mm)",
        "vertical": True,
        "position_x": 0.82,
        "position_y": 0.15,
        "height": 0.65,
    }
)

# ---------------------------------------------------------
# ANATOMICAL CAMERA ORIENTATION
# ---------------------------------------------------------
#
# The mesh uses positive Z as anatomically inferior.
# Set negative Z as the camera's upward direction so that L1 appears above L2 in the rendered image.
#
# This changes only the visualisation, not the mesh or the underlying finite element results.

plotter.add_axes()

plotter.camera_position = [
    (
        mesh.center[0] + 180,
        mesh.center[1] + 220,
        mesh.center[2] + 70,
    ),
    mesh.center,
    (0, 0, -1),
]

plotter.add_text(
    "L1-L2 Axial Compression: Displacement Magnitude",
    font_size=12,
)

plotter.set_background("white")


# ---------------------------------------------------------
# SAVE THE FIGURE
# ---------------------------------------------------------

output_path = Path(
    "outputs/figures/baseline_tolerance_005_displacement.png"
)

output_path.parent.mkdir(parents=True, exist_ok=True)

plotter.screenshot(str(output_path))
plotter.close()

print("Saved figure:", output_path)


# ---------------------------------------------------------
# VON MISES STRESS VISUALISATION
# ---------------------------------------------------------

stress_plotter = pv.Plotter(
    off_screen=True,
    window_size=(1400, 1000)
)

# Display the original, undeformed mesh coloured by stress.
stress_plotter.add_mesh(
    surface,
    scalars="Von Mises Stress",
    cmap="plasma",
    clim=[0, 1.6],
    show_edges=False,
    # ---------------------------------------------------------
    # STRESS COLOUR BAR POSITIONING
    # ---------------------------------------------------------
    #
    # Move the colour bar inward to prevent its title
    # from being clipped at the right edge.
    #
    # Use the same positioning as the displacement figure
    # for a consistent presentation.

    scalar_bar_args={
        "title": "Von Mises stress (MPa)",
        "vertical": True,
        "position_x": 0.82,
        "position_y": 0.15,
        "height": 0.65,
    }
)

# ---------------------------------------------------------
# ANATOMICAL CAMERA ORIENTATION
# ---------------------------------------------------------
#
# Match the displacement visualisation camera.
# Negative Z points upward on screen, placing L1 above L2.
#
# Using the same camera makes displacement and stress distributions easier to compare.

stress_plotter.add_axes()

stress_plotter.camera_position = [
    (
        mesh.center[0] + 180,
        mesh.center[1] + 220,
        mesh.center[2] + 70,
    ),
    mesh.center,
    (0, 0, -1),
]

stress_plotter.add_text(
    "L1-L2 Axial Compression: Von Mises Stress",
    font_size=12,
)

stress_plotter.set_background("white")

# Save the stress figure separately from displacement.
stress_output = Path(
    "outputs/figures/baseline_tolerance_005_von_mises.png"
)

stress_plotter.screenshot(str(stress_output))
stress_plotter.close()

print("Saved stress figure:", stress_output)


# ---------------------------------------------------------
# LOCATE THE MAXIMUM VON MISES STRESS NODE
# ---------------------------------------------------------

import numpy as np

# Find node 10200 using its original CalculiX node ID.
node_ids = mesh.point_data["Node ID"]
node_index = np.where(node_ids == 10200)[0][0]

maximum_stress_position = mesh.points[node_index]

# Create a diagnostic plot.
diagnostic_plotter = pv.Plotter(
    off_screen=True,
    window_size=(1400, 1000)
)

# ---------------------------------------------------------
# TRANSLUCENT SURFACE FOR INTERNAL NODE VISUALISATION
# ---------------------------------------------------------
#
# The maximum-stress node may be located inside the mesh.
# A translucent surface allows the red location marker
# to remain visible through the surrounding anatomy.

diagnostic_plotter.add_mesh(
    surface,
    scalars="Von Mises Stress",
    cmap="plasma",
    clim=[0, 1.6],
    opacity=0.35,
    show_scalar_bar=False,
)

# Mark the maximum-stress node with a red sphere.
marker = pv.Sphere(
    radius=2.0,
    center=maximum_stress_position,
)

diagnostic_plotter.add_mesh(
    marker,
    color="red",
    opacity=1.0,
)

# ---------------------------------------------------------
# ANATOMICAL CAMERA ORIENTATION
# ---------------------------------------------------------
#
# Match the displacement and von Mises stress figures.
# Positive Z is anatomically inferior in this mesh.
# Using negative Z as the camera-up vector places L1 above L2 without changing the simulation geometry.

diagnostic_plotter.add_axes()

diagnostic_plotter.camera_position = [
    (
        mesh.center[0] + 180,
        mesh.center[1] + 220,
        mesh.center[2] + 70,
    ),
    mesh.center,
    (0, 0, -1),
]

diagnostic_plotter.set_background("white")

diagnostic_plotter.add_text(
    "Maximum Von Mises Stress: Node 10200",
    font_size=12,
)

diagnostic_output = Path(
    "outputs/figures/maximum_stress_node_location.png"
)

diagnostic_plotter.screenshot(str(diagnostic_output))
diagnostic_plotter.close()

print("Saved diagnostic figure:", diagnostic_output)


# ---------------------------------------------------------
# SAGITTAL CROSS-SECTION: VON MISES STRESS
# ---------------------------------------------------------

# Start with a central plane perpendicular to the X-axis.
# This is an exploratory section; anatomical orientation will be confirmed against our existing orientation reference.

#section = mesh.slice(
#    normal=(1, 0, 0),
#    origin=mesh.center,
#)
# ---------------------------------------------------------
# CROSS-SECTION THROUGH THE MAXIMUM-STRESS NODE
# ---------------------------------------------------------

# Locate node 10200 using its original CalculiX node ID.
node_index = np.where(
    mesh["Node ID"] == 10200
)[0][0]

maximum_stress_position = mesh.points[node_index]

# Create a YZ cross-section through that node.
section = mesh.slice(
    normal=(1, 0, 0),
    origin=maximum_stress_position,
)

print("Section X-coordinate:", maximum_stress_position[0])
print("Section maximum stress:", section["Von Mises Stress"].max())

section_plotter = pv.Plotter(
    off_screen=True,
    window_size=(1400, 1000)
)

section_plotter.add_mesh(
    section,
    scalars="Von Mises Stress",
    cmap="plasma",
    clim=[0, 1.6],
    show_edges=False,
    scalar_bar_args={
        "title": "Von Mises stress (MPa)",
        "vertical": True,
        "position_x": 0.82,
        "position_y": 0.15,
        "height": 0.65,
    },
)

# ---------------------------------------------------------
# ANATOMICAL CAMERA ORIENTATION — YZ CROSS-SECTION
# ---------------------------------------------------------
#
# The section is perpendicular to the X-axis.
# Position the camera along positive X, looking toward the centre of the section.
#
# Negative Z is anatomically superior in this mesh.
# Setting camera-up to negative Z places L1 above L2.
#
# This changes only the viewing orientation.

section_plotter.camera_position = [
    (
        section.center[0] + 200,
        section.center[1],
        section.center[2],
    ),
    section.center,
    (0, 0, -1),
]

section_plotter.reset_camera()
section_plotter.set_background("white")

#section_plotter.add_text(
#    "L1-L2: Central Cross-Section - Von Mises Stress",
#    font_size=12,
#)
section_plotter.add_text(
    "L1-L2: Cross-Section Through Maximum-Stress Node",
    font_size=12,
)

#section_output = Path(
#    "outputs/figures/baseline_tolerance_005_stress_section.png"
#)
section_output = Path(
    "outputs/figures/baseline_tolerance_005_max_stress_section.png"
)

section_plotter.screenshot(str(section_output))
section_plotter.close()

print("Saved cross-sectional figure:", section_output)
