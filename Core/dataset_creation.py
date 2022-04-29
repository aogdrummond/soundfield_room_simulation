import sys

sys.path.append(r"C:\Users\aledr\Documents\GitHub\femder\\")

import femder as fd
import numpy as np
import matplotlib.pyplot as plt
import random
import os

from Core.utils.saving import save_sample
from Core.utils.discretization import room_discretization
from Core.utils.rooms_properties import (
    normalized_admitance,
    room_absorption,
)
from Core.utils.general import eu_dist, tup_to_array


def create_rectangular_sample(
    room_dim: list = [],
    source_position: list = [],
    view_soundfield: bool = False,
    freq_view: int = 100,
    save: bool = False,
    dataset_path: str = "",
    freqMin: int = 0,
    freqMax: int = 150,
    receiver_height: float = 1.0,
    source_Q: float = 0.01,
):

    """ """

    # SETTING ROOMs GEOMETRY

    if len(room_dim) != 0:
        l = room_dim[0]
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
        c0=343.0, rho0=1.21, temperature=20.0, humid=50.0, p_atm=101325.0
    )

    AC = fd.AlgControls(AP, freqMin, freqMax, freq_step=1)
    BC = fd.BC(AC, AP)  # Boundary Conditions
    alpha = room_absorption(Area, S, height)
    Y0 = normalized_admitance(alpha)
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

    grid = fd.GeometryGenerator(AP, fmax=freqMax, num_freq=6, plot=False)

    try:
        grid.generate_symmetric_polygon(pts, height)
    except:
        print("Coordinates cannot generate geometry!")

    # Geometries' discretization

    coord_x = grid.gen_pts[:, 0]
    coord_y = grid.gen_pts[:, 1]

    grid_coordinates = np.array(tuple(zip(coord_x, coord_y)))

    I = 32
    J = 32
    discrete_coord = room_discretization(grid_coordinates, I=I, J=J)

    # DEFINING ONE RECEPTOR PER EACH DISCRETE POINT

    receivers_coord = tup_to_array(discrete_coord, z=receiver_height)
    R = fd.receivers.Receiver()
    R.discretized_array(receivers_coord, I=I, J=J)

    if len(source_position) != 0:
        [coord_x, coord_y, coord_z] = source_position
    else:
        [coord_x, coord_y, coord_z] = random.choice(receivers_coord)

    S = fd.Source(wavetype="spherical", coord=[coord_x, coord_y, coord_z], q=[source_Q])

    F = fd.FEM_3D.FEM3D(Grid=grid, S=S, R=R, AP=AP, AC=AC, BC=BC)
    F.compute()
    F.evaluate(R)
    if view_soundfield == True:
        F.pressure_field(
            frequencies=freq_view,
            axis=["xy"],
            coord_axis={
                "xy": receiver_height,
                "yz": None,
                "xz": None,
                "boundary": None,
            },
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


def create_general_sample(
    room_dim=[],
    source_position: list = [],
    view_soundfield: list = True,
    freq_view: int = 150,
    save: bool = False,
    dataset_path: str = "",
    freqMin: int = 0,
    freqMax: int = 150,
    receiver_height: float = 1.0,
    source_Q: float = 0.01,
    view_geometry=False,
):

    if len(room_dim) != 0:

        pass

    else:

        Dim = generate_room_dimensions()
        while not (Dim["Area"] >= 10) & (Dim["Area"] <= 30):
            print("Looking for a feasible geometry.")
            Dim = generate_room_dimensions()
            continue

    AP = fd.AirProperties()
    AC = fd.AlgControls(AP, freqMin, freqMax, 1)
    BC = fd.BC(AC, AP)
    alpha = room_absorption(Dim["Area"], Dim["S"], Dim["height"])
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

    L = [Dim["Coordinate"]["H"], Dim["Coordinate"]["x3"], Dim["height"]]
    grid = fd.GeometryGenerator(AP, fmax=freqMax, num_freq=6, plot=False)
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

    receivers_coord = tup_to_array(discrete_coord, z=receiver_height)
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
        q=[source_Q],
    )

    AP = fd.AirProperties()
    AC = fd.AlgControls(AP, freqMin, freqMax, freq_step=1)
    F = fd.FEM_3D.FEM3D(Grid=grid, S=S, R=R, AP=AP, AC=AC, BC=BC)
    F.compute()
    F.evaluate(R)

    if view_geometry == True:

        y = []
        x = []
        for coord in discrete_coord:
            x.append(coord[0])
            y.append(coord[1])
        plt.scatter(x, y)
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
            hide_dots=True,
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
    freqMin: int = 0,
    freqMax: int = 150,
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
        create_sample = create_rectangular_sample
    elif geometry.lower() == "general":
        create_sample = create_general_sample
    else:
        raise Exception

    current_samples = len(os.listdir(dataset_path))

    while current_samples < n_samples:

        create_sample(
            dataset_path=dataset_path,
            save=True,
            freqMin=freqMin,
            freqMax=freqMax,
            receiver_height=1.2,
        )

        print(f"{len(os.listdir(dataset_path))}/{n_samples}")
    print("Dataset Criado!")


def generate_room_dimensions(height: float = 2.7):

    """
    Generates a dictionary containing the dimensions for the room,
    respecting the criteria adopted on the original work (CITAR)
    """

    H = random.uniform(3, 10)  # arger lenght
    h1 = random.uniform(0, H / 2)  # height lenght 1
    h2 = random.uniform(0, H / 2)  # height lenght 2
    l1 = random.uniform(H / 4, H)  # lateral lenght 1
    l2 = random.uniform(H / 4, H)  # lateral lenght 2
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
            "H": H,
        },
        "Area": Area,
        "S": S,
        "height": height,
    }

    return Dim
