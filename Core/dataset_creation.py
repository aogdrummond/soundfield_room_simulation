import femder.femder as fd
import numpy as np
import matplotlib.pyplot as plt
import random
import os

from Core.utils.saving import save_sample, save_properties, generate_folder_tree
from Core.utils.discretization import room_discretization
from Core.utils.rooms_properties import (
    normalized_admitance,
    room_absorption,
    initiate_properties,
)
from Core.utils.general import eu_dist, tup_to_array


def create_rectangular_room(
    room_dim: list = [],
    source_position: list = [],
    view_soundfield: bool = False,
    freq_view: int = 100,
    save: bool = False,
    dataset_path: str = "",
    **properties,
):

    """ """

    prop = initiate_properties(**properties)

    # SETTING ROOMs GEOMETRY

    if len(room_dim) != 0:
        l = room_dim[0] / 2
        w = room_dim[1]
        height = room_dim[2]
        Area = l * w

    else:
        l = 0
        w = 0
        height = 2.7
        Area = l * w

        while not (Area > 10) & (Area < 30):
            l = 2.83 + (4.87 - 2.83) * random.random()
            w = 1.1 * l + (4.5 * l - 9.6 - 1.1 * l) * random.random()
            Area = l * w
            print("Area does not correspond to criteria. Trying again.")

    S = 2 * (2 * Area + 2 * (l * height) + w * height)

    # SETTING ROOMs PROPERTIES

    AP = fd.AirProperties(
        c0=prop["c0"],
        rho0=prop["rho0"],
        temperature=prop["temperature"],
        humid=prop["humid"],
        p_atm=prop["p_atm"],
    )

    AC = fd.AlgControls(AP, prop["freqMin"], prop["freqMax"], freq_step=1)
    BC = fd.BC(AC, AP)  # Boundary Conditions
    alpha = room_absorption(S_floor=Area, S=S, height=height, T60=prop["T60"])
    Y0 = normalized_admitance(alfa_s=alpha)
    BC.normalized_admittance(2, Y0)
    pts = np.array(
        [
            [0, 0],  # Setting vertices from dimensions
            [l / 2, 0],
            [l, 0],
            [l, w / 2],
            [l, w],
            [l / 2, w],
            [0, w],
        ]
    )

    # CREATE MESH

    grid = fd.GeometryGenerator(AP, fmax=prop["freqMax"], num_freq=6, plot=False)

    try:
        grid.generate_symmetric_polygon(pts, height)
    except:
        print("Coordinates cannot generate geometry!")
        return

    # Geometries' discretization

    coord_x = grid.gen_pts[:, 0]
    coord_y = grid.gen_pts[:, 1]

    grid_coordinates = np.array(tuple(zip(coord_x, coord_y)))

    I = 32
    J = 32
    discrete_coord = room_discretization(grid_coordinates, I=I, J=J)

    # DEFINING ONE RECEPTOR PER EACH DISCRETE POINT

    receivers_coord = tup_to_array(discrete_coord, z=prop["receiver_height"])
    R = fd.receivers.Receiver()
    R.discretized_array(receivers_coord, I=I, J=J)

    if len(source_position) != 0:
        [coord_x, coord_y, coord_z] = source_position
    else:
        [coord_x, coord_y, coord_z] = random.choice(receivers_coord)

    S = fd.Source(
        wavetype="spherical", coord=[coord_x, coord_y, coord_z], q=[prop["source_Q"]]
    )

    F = fd.FEM_3D.FEM3D(Grid=grid, S=S, R=R, AP=AP, AC=AC, BC=BC)
    F.compute()
    F.evaluate(R)
    if view_soundfield == True:
        F.pressure_field(
            frequencies=freq_view,
            axis=["xy"],
            coord_axis={
                "xy": prop["receiver_height"],
                "yz": None,
                "xz": None,
                "boundary": None,
            },
            hide_dots=False,
        )

    if save == True:

        save_sample(
            l=l,
            w=w,
            height=height,
            S=S,
            R=R,
            F=F,
            receivers_coord=receivers_coord,
            dataset_path=dataset_path,
            I=I,
            J=J,
        )


def create_general_room(
    room_dim=[],
    source_position: list = [],
    view_soundfield: list = True,
    freq_view: int = 150,
    save: bool = False,
    dataset_path: str = "",
    view_geometry=False,
    **properties,
):

    prop = initiate_properties(**properties)

    if len(room_dim) != 0:
        Dim = get_room_dimensions(mode="inputed", vertex_coord=room_dim)

    else:
        Dim = get_room_dimensions(mode="generated")

        while not (Dim["Area"] >= 10) & (Dim["Area"] <= 30):
            print("Looking for a feasible geometry.")
            Dim = get_room_dimensions(mode="generated")
            continue

    AP = fd.AirProperties(
        c0=prop["c0"],
        rho0=prop["rho0"],
        temperature=prop["temperature"],
        humid=prop["humid"],
        p_atm=prop["p_atm"],
    )
    AC = fd.AlgControls(AP, prop["freqMin"], prop["freqMax"], 1)
    BC = fd.BC(AC, AP)
    alpha = room_absorption(Dim["Area"], Dim["S"], Dim["height"], T60=prop["T60"])
    Y0 = normalized_admitance(alpha)
    BC.normalized_admittance(domain_index=2, normalized_admittance=Y0)

    pts = np.array(
        [
            [Dim["Coordinate"]["x0"], Dim["Coordinate"]["y0"]],
            [Dim["Coordinate"]["x1"], Dim["Coordinate"]["y1"]],
            [Dim["Coordinate"]["x2"], Dim["Coordinate"]["y2"]],
            [Dim["Coordinate"]["x3"], Dim["Coordinate"]["y3"]],
            [Dim["Coordinate"]["x4"], Dim["Coordinate"]["y4"]],
            [Dim["Coordinate"]["x5"], Dim["Coordinate"]["y5"]],
            [Dim["Coordinate"]["x6"], Dim["Coordinate"]["y6"]],
        ]
    )

    grid = fd.GeometryGenerator(AP, fmax=prop["freqMax"], num_freq=6, plot=False)
    try:
        grid.generate_symmetric_polygon(pts, Dim["height"])
    except:
        print("Coordinates cannot generate geometry!")
    # CREATION OF RECEIVERS FROM ROOM'S SHAPE

    coord_x = grid.gen_pts[:, 0]
    coord_y = grid.gen_pts[:, 1]

    grid_coordinates = np.array(tuple(zip(coord_x, coord_y)))

    # Discretização

    I = 32
    J = 32

    discrete_coord = room_discretization(grid_coordinates, I=I, J=J)

    receivers_coord = tup_to_array(discrete_coord, z=prop["receiver_height"])
    R = fd.receivers.Receiver()
    R.discretized_array(receivers_coord, I=I, J=J)

    if len(source_position) != 0:
        [source_coord_x, source_coord_y, source_coord_z] = source_position
    else:
        [source_coord_x, source_coord_y, source_coord_z] = random.choice(
            receivers_coord
        )

    S = fd.Source(
        wavetype="spherical",
        coord=[source_coord_x, source_coord_y, source_coord_z],
        q=[prop["source_Q"]],
    )

    AP = fd.AirProperties()
    AC = fd.AlgControls(AP, prop["freqMin"], prop["freqMax"], freq_step=1)
    F = fd.FEM_3D.FEM3D(Grid=grid, S=S, R=R, AP=AP, AC=AC, BC=BC)
    F.compute()
    F.evaluate(R)

    if view_geometry == True:

        y = []
        x = []
        for coord in discrete_coord:
            x.append(coord[0])
            y.append(coord[1])
        plt.scatter(x, y, alpha=0.5)
        plt.title("Receivers' positions over the soundfield")
        plt.xlabel("[m]")
        plt.ylabel("[m]")
        plt.show()
        plt.scatter(pts[:, 0], pts[:, 1])
        plt.title("Vertices used to create the room")
        plt.xlabel("[m]")
        plt.ylabel("[m]")
        plt.show()

    if view_soundfield == True:

        F.pressure_field(
            frequencies=freq_view,
            axis=["xy"],
            coord_axis={"xy": source_coord_z, "yz": None, "xz": None, "boundary": None},
            hide_dots=False,
        )

    if save == True:

        save_sample(
            l=(Dim["Coordinate"]["x2"] - Dim["Coordinate"]["x0"]),
            w=(Dim["Coordinate"]["y6"] - Dim["Coordinate"]["y0"]),
            height=Dim["height"],
            S=S,
            R=R,
            F=F,
            receivers_coord=receivers_coord,
            dataset_path=dataset_path,
            I=I,
            J=J,
        )


def create_dataset(
    geometry: str,
    dataset_path: str,
    n_samples: int,
    **properties,
):

    """
    Function to create a dataset following certain criteria
    Args:
    geometry: the kind of geometry simulated either "rectangular" or "general"
    dataset_path (str): path to the folder where the dataset is being saved
    n_samples (int): dataset number of samples
    freqMin (int) : Smaller frequency calculated
    freqMax (int) : Higher frequency calculated
    """

    if geometry.lower() == "rectangular":
        create_sample = create_rectangular_room
    elif geometry.lower() == "general":
        create_sample = create_general_room
    else:
        raise Exception

    # Generate folder's structure
    if not os.path.exists(dataset_path):
        generate_folder_tree(dataset_path)

    dataset_path = "".join([dataset_path, "/simulated_soundfields/"])
    # Chech how many samples there are currently
    current_samples = len(
        [mat_file for mat_file in os.listdir(dataset_path) if mat_file.endswith(".mat")]
    )

    while current_samples < n_samples:

        create_sample(
            dataset_path=dataset_path,
            save=True,
            **properties,
        )

        current_samples = len(
            [
                mat_file
                for mat_file in os.listdir(dataset_path)
                if mat_file.endswith(".mat")
            ]
        )

        print(f"{current_samples}/{n_samples}")

    save_properties(dataset_path=dataset_path, properties=properties)
    print("Dataset created!")


def get_room_dimensions(mode: str, vertex_coord: list = [], height: float = 2.7):

    """
    Generates a dictionary containing the dimensions for the room,
    respecting the criteria adopted on the original work (CITAR)
    """

    if mode == "inputed":
        (
            (x0, x1, x2, x3, x4, x5, x6),
            (y0, y1, y2, y3, y4, y5, y6),
            height,
        ) = coordinates_from_vertices(vertex_coord)

    if mode == "generated":
        (
            (x0, x1, x2, x3, x4, x5, x6),
            (y0, y1, y2, y3, y4, y5, y6),
            height,
        ) = generate_room_coordinates()

    sum = (y0 * x1 + y1 * x2 + y2 * x3 + y3 * x4 + y4 * x5 + y5 * x6 + y6 * x0) - (
        x0 * y1 + x1 * y2 + x2 * y3 + x3 * y4 + x4 * y5 + x5 * y6 + x6 * y0
    )
    Area = abs(sum) / 2  # Floor's area
    S_parede_1 = eu_dist(x0, x1) * height
    S_parede_2 = eu_dist(x1, x2) * height
    S_parede_3 = eu_dist(x2, x3) * height
    S_parede_4 = eu_dist(x3, x4) * height
    S_parede_5 = eu_dist(x4, x5) * height
    S_parede_6 = eu_dist(x5, x6) * height
    S = 2 * (
        S_parede_1
        + S_parede_2
        + S_parede_3
        + S_parede_4
        + S_parede_5
        + S_parede_6
        + Area * 2
    )  # Total surface area

    Dim = {
        "Coordinate": {
            "x0": x0,
            "x1": x1,
            "x2": x2,
            "x3": x3,
            "x4": x4,
            "x5": x5,
            "x6": x6,
            "y0": y0,
            "y1": y1,
            "y2": y2,
            "y3": y3,
            "y4": y4,
            "y5": y5,
            "y6": y6,
        },
        "Area": Area,
        "S": S,
        "height": height,
    }

    return Dim


def receive_room_vertices(room_coordinates):

    Dim = {"Coordinate": {}}

    x0 = room_coordinates[0][0]
    y0 = room_coordinates[0][1]
    x1 = room_coordinates[1][0]
    y1 = room_coordinates[1][1]
    x2 = room_coordinates[2][0]
    y2 = room_coordinates[2][1]
    x3 = room_coordinates[3][0]
    y3 = room_coordinates[3][1]
    x4 = room_coordinates[4][0]
    y4 = room_coordinates[4][1]
    x5 = room_coordinates[5][0]
    y5 = room_coordinates[5][1]
    x6 = room_coordinates[6][0]
    y6 = room_coordinates[6][1]
    height = room_coordinates[7]

    sum = (y0 * x1 + y1 * x2 + y2 * x3 + y3 * x4 + y4 * x5 + y5 * x6 + y6 * x0) - (
        x0 * y1 + x1 * y2 + x2 * y3 + x3 * y4 + x4 * y5 + x5 * y6 + x6 * y0
    )

    Area = abs(sum) / 2
    S_parede_1 = eu_dist(x0, x1) * height
    S_parede_2 = eu_dist(x1, x2) * height
    S_parede_3 = eu_dist(x2, x3) * height
    S_parede_4 = eu_dist(x3, x4) * height
    S_parede_5 = eu_dist(x4, x5) * height
    S_parede_6 = eu_dist(x5, x6) * height
    S = 2 * (
        S_parede_1
        + S_parede_2
        + S_parede_3
        + S_parede_4
        + S_parede_5
        + S_parede_6
        + Area * 2
    )
    Dim = {
        "Coordinate": {
            "x0": x0,
            "x1": x1,
            "x2": x2,
            "x3": x3,
            "x4": x4,
            "x5": x5,
            "x6": x6,
            "y0": y0,
            "y1": y1,
            "y2": y2,
            "y3": y3,
            "y4": y4,
            "y5": y5,
            "y6": y6,
        },
        "Area": Area,
        "S": S,
        "height": height,
    }

    return Dim


def generate_room_coordinates(height: float = 2.7):

    H = random.uniform(3, 10)
    h1 = random.uniform(0, H / 2)
    h2 = random.uniform(0, H / 2)
    l1 = random.uniform(H / 4, H)
    l2 = random.uniform(H / 4, H)
    x0 = 0
    y0 = 0
    x2 = l1
    y2 = h1
    x6 = 0
    y6 = H
    x4 = l2
    y4 = H - h2
    x1 = (x0 + x2) / 2
    y1 = (y0 + y2) / 2
    x5 = (x4 + x6) / 2
    y5 = (y4 + y6) / 2
    x3 = random.uniform(x2, x4)
    y3 = random.uniform(y2, y4)
    height = height

    return (x0, x1, x2, x3, x4, x5, x6), (y0, y1, y2, y3, y4, y5, y6), height


def coordinates_from_vertices(vertex_coord: list, height: float = 2.7):

    x0 = vertex_coord[0][0]
    y0 = vertex_coord[0][1]
    x1 = vertex_coord[1][0]
    y1 = vertex_coord[1][1]
    x2 = vertex_coord[2][0]
    y2 = vertex_coord[2][1]
    x3 = vertex_coord[3][0]
    y3 = vertex_coord[3][1]
    x4 = vertex_coord[4][0]
    y4 = vertex_coord[4][1]
    x5 = vertex_coord[5][0]
    y5 = vertex_coord[5][1]
    x6 = vertex_coord[6][0]
    y6 = vertex_coord[6][1]

    height = height

    return (x0, x1, x2, x3, x4, x5, x6), (y0, y1, y2, y3, y4, y5, y6), height
