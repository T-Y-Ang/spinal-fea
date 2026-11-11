
from pathlib import Path


def read_frd_nodes(file_path):
    """
    Extract node IDs and XYZ coordinates from a CalculiX FRD file.

    Returns
    -------
    dict
        Node ID -> (x, y, z), in millimetres.
    """

    nodes = {}
    reading_nodes = False

    with open(file_path, "r") as file:
        for line in file:

            # The 2C record marks the start of node coordinates.
            if line.lstrip().startswith("2C"):
                reading_nodes = True
                continue

            if not reading_nodes:
                continue

            # The -3 record marks the end of this section.
            if line.strip() == "-3":
                break

            # Only process node-coordinate records.
            if line.startswith(" -1"):
                node_id = int(line[3:13])

                # CalculiX uses fixed-width scientific notation.
                x = float(line[13:25])
                y = float(line[25:37])
                z = float(line[37:49])

                nodes[node_id] = (x, y, z)

    return nodes


def read_frd_elements(file_path):
    """
    Extract four-node tetrahedral elements from a CalculiX FRD file.

    Returns
    -------
    dict
        Element ID -> tuple of four node IDs.
    """

    elements = {}
    reading_elements = False
    current_element_id = None

    with open(file_path, "r") as file:
        for line in file:

            # The 3C record marks the element-connectivity section.
            if line.lstrip().startswith("3C"):
                reading_elements = True
                continue

            if not reading_elements:
                continue

            # End of the element section.
            if line.strip() == "-3":
                break

            # Element definition: extract its ID and type.
            if line.startswith(" -1"):
                fields = line.split()

                current_element_id = int(fields[1])
                element_type = int(fields[2])

                # FRD type 3 represents a four-node tetrahedron.
                if element_type != 3:
                    raise ValueError(
                        f"Unexpected element type: {element_type}"
                    )

            # Connectivity: four node IDs forming the tetrahedron.
            elif line.startswith(" -2"):
                node_ids = tuple(map(int, line.split()[1:]))

                if len(node_ids) != 4:
                    raise ValueError(
                        f"Element {current_element_id} has "
                        f"{len(node_ids)} nodes instead of 4."
                    )

                elements[current_element_id] = node_ids

    return elements


def read_frd_displacements(file_path):
    """
    Extract nodal displacement vectors from a CalculiX FRD file.

    Returns
    -------
    dict
        Node ID -> (D1, D2, D3), in millimetres.
    """

    displacements = {}
    reading_displacements = False

    with open(file_path, "r") as file:
        for line in file:

            # Locate the displacement dataset.
            if line.startswith(" -4") and line[5:17].strip() == "DISP":
                reading_displacements = True
                continue

            if not reading_displacements:
                continue

            # End of displacement dataset.
            if line.strip() == "-3":
                break

            # Ignore component definitions and metadata.
            if not line.startswith(" -1"):
                continue

            # FRD nodal results use a 10-character node ID field
            # followed by 12-character scientific notation fields.
            node_id = int(line[3:13])

            d1 = float(line[13:25])
            d2 = float(line[25:37])
            d3 = float(line[37:49])

            displacements[node_id] = (d1, d2, d3)

    return displacements


def read_frd_stresses(file_path):
    """
    Extract the six nodal stress tensor components from an FRD file.

    Returns
    -------
    dict
        Node ID -> (SXX, SYY, SZZ, SXY, SYZ, SZX).
        Stress units are MPa for our N-mm model.
    """

    stresses = {}
    reading_stresses = False

    with open(file_path, "r") as file:
        for line in file:

            # Locate the stress dataset.
            if line.startswith(" -4") and line[5:17].strip() == "STRESS":
                reading_stresses = True
                continue

            if not reading_stresses:
                continue

            # End of stress dataset.
            if line.strip() == "-3":
                break

            # Ignore component definitions and metadata.
            if not line.startswith(" -1"):
                continue

            # Extract the original node ID.
            node_id = int(line[3:13])

            # Read six fixed-width stress components.
            components = tuple(
                float(line[13 + 12*i : 25 + 12*i])
                for i in range(6)
            )

            stresses[node_id] = components

    return stresses


def calculate_von_mises(stresses):
    """
    Calculate nodal von Mises stress from six stress components.

    Parameters
    ----------
    stresses : dict
        Node ID -> (SXX, SYY, SZZ, SXY, SYZ, SZX).

    Returns
    -------
    dict
        Node ID -> von Mises stress, in MPa.
    """

    import numpy as np

    von_mises = {}

    for node_id, components in stresses.items():

        sxx, syy, szz, sxy, syz, szx = components

        # Three-dimensional von Mises equivalent stress.
        vm = np.sqrt(
            0.5 * (
                (sxx - syy)**2
                + (syy - szz)**2
                + (szz - sxx)**2
            )
            + 3.0 * (
                sxy**2 + syz**2 + szx**2
            )
        )

        von_mises[node_id] = float(vm)

    return von_mises


def build_pyvista_mesh(nodes, elements):
    """
    Construct a PyVista tetrahedral mesh from FRD geometry.

    Preserves the original CalculiX node and element IDs.
    """

    import numpy as np
    import pyvista as pv

    # Preserve the original node IDs and their coordinates.
    node_ids = list(nodes)
    points = np.array(
        [nodes[node_id] for node_id in node_ids],
        dtype=float
    )

    # Map CalculiX node IDs to zero-based PyVista indices.
    node_index = {
        node_id: index
        for index, node_id in enumerate(node_ids)
    }

    # Each tetrahedron has four nodes.
    # PyVista expects [4, node0, node1, node2, node3].
    connectivity = []

    for element_nodes in elements.values():
        connectivity.extend(
            [4] + [node_index[n] for n in element_nodes]
        )

    cells = np.array(connectivity, dtype=np.int64)

    cell_types = np.full(
        len(elements),
        pv.CellType.TETRA,
        dtype=np.uint8
    )

    mesh = pv.UnstructuredGrid(cells, cell_types, points)
    mesh.point_data["Node ID"] = np.array(node_ids)
    mesh.cell_data["Element ID"] = np.array(list(elements))

    return mesh

def attach_frd_results(mesh, displacements, von_mises, stresses=None):
    """
    Attach CalculiX displacement and von Mises stress results
    to a PyVista mesh using the original node IDs.
    """

    import numpy as np

    # Retrieve node IDs in the exact order used by PyVista.
    node_ids = mesh.point_data["Node ID"]

    # Align displacement vectors with the mesh node ordering.
    displacement_array = np.array(
        [displacements[int(node_id)] for node_id in node_ids],
        dtype=float
    )

    # Align nodal von Mises stresses with the same ordering.
    stress_array = np.array(
        [von_mises[int(node_id)] for node_id in node_ids],
        dtype=float
    )

    # Calculate the magnitude of each displacement vector.
    displacement_magnitude = np.linalg.norm(
        displacement_array,
        axis=1
    )

    # Attach the results as PyVista point data.
    mesh.point_data["Displacement"] = displacement_array
    mesh.point_data["Displacement Magnitude"] = displacement_magnitude
    mesh.point_data["Von Mises Stress"] = stress_array


    # ---------------------------------------------------------
    # OPTIONAL AXIAL NORMAL STRESS
    # ---------------------------------------------------------

    if stresses is not None:

        # SZZ is the third component of the CalculiX
        # stress tensor: (SXX, SYY, SZZ, SXY, SYZ, SZX).
        axial_stress = np.array(
            [stresses[int(node_id)][2] for node_id in node_ids],
            dtype=float
        )

        # Negative SZZ indicates compression under the
        # conventional stress sign convention.
        mesh.point_data["Axial Stress SZZ"] = axial_stress


    return mesh


# Test the coordinate reader using our completed simulation.
if __name__ == "__main__":

    frd_path = Path(
        "cases/baseline_compression/baseline_tolerance_005.frd"
    )

    nodes = read_frd_nodes(frd_path)

    print("Nodes extracted:", len(nodes))
    print("First five node IDs:", list(nodes)[:5])
    print("Node 1 coordinates:", nodes.get(1))
    print("Highest node ID:", max(nodes))
