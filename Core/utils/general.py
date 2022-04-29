import numpy as np


def eu_dist(a, b):
    """
    Calculates Euclidian distance between a and b
    """
    dist = np.sqrt((a - b) ** 2)

    return dist


def appropriate_size(pts):

    """
    Function that checks wether geometries'
    area is within the recommended dimensions
    (40m² <= A <=60m²)
    """

    # Base and top lenght calculation
    y_dim_1 = np.unique(pts[:, 1])[0]
    y_dim_2 = np.unique(pts[:, 1])[1]
    pts_base = np.array([coord for coord in pts if coord[1] == y_dim_1])
    pts_top = np.array([coord for coord in pts if coord[1] == y_dim_2])

    top_lenght = pts_top[:, 0].max() - pts_top[:, 0].min()
    base_lenght = pts_base[:, 0].max() - pts_base[:, 0].min()
    height = abs(y_dim_1 - y_dim_2)
    Area = ((top_lenght + base_lenght) / 2) * height

    if (Area >= 20) & (Area <= 60):
        return True, Area
    else:
        return False, Area

def tup_to_array(list_of_tuple, z=None):

    """
    Transforma uma lista de tuplas 2D em um array 2D, ou um array 3D com altura fixa z
    """

    if z == None:  # Caso não seja dada altura
        line0 = []
        line1 = []
        for pair in list_of_tuple:
            line0.append(pair[0])
            line1.append(pair[1])

        array_ = np.array((line0, line1))
        array_ = array_.reshape((-1, 2))

    else:  # Caso altura seja fornecida

        line0 = []
        line1 = []
        line2 = []

        for couple in list_of_tuple:
            line0.append(couple[0])
            line1.append(couple[1])
            line2.append(z)

        line0 = np.array(line0)
        line1 = np.array(line1)
        line2 = np.array(line2)
        line0 = line0.reshape((-1, 1))
        line1 = line1.reshape((-1, 1))
        line2 = line2.reshape((-1, 1))

        array_ = np.concatenate((line0, line1, line2), axis=1)

    return array_
