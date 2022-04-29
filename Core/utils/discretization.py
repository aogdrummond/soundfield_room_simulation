class GridPoint_Generico:
    def __init__(self, x, y, Lx=0, Ly=0, I=8, J=3):

        self.x = x  # número do ponto no eixo x [0 a I-1]
        self.y = y  # número do ponto no eixo y [0 a J-1]
        self.Lx = Lx  # Lx é a dimensão variável
        self.Ly = Ly  # Por convenção, Ly é a dimensão constante
        self.coord_x = (x / (I - 1)) * Lx  # coordenada no sistema cartesiano
        self.coord_y = (y / (J - 1)) * Ly

    """Classe definida para armazenar as coordenadas"""


class coordinate:
    def __init__(self, x, y):

        self.x = x
        self.y = y


#%% Required Functions


def values(coordinates, axis):
    """
    Creates a vector "values" containing all the diferent values that the coordinate
    "axis" (x/y) may assume
    """

    values = []
    for coord in coordinates:
        if axis == "x":
            if coord[0] not in values:
                values.append(coord[0])
        if axis == "y":
            if coord[1] not in values:
                values.append(coord[1])
    return values


def get_Ly(coordinates):
    """
    Gets Ly value (larger difference between y points with the same x) from coordinates
    """
    y_original = values(coordinates, "y")
    Ly = max(y_original) - min(y_original)

    return Ly


def y_discretization(coordinates, J):
    """
    Discretize "coordinates" in relation to y axis, containing J different "y" elements
    for each "x" value
    """

    y_new_values = []
    Ly = get_Ly(coordinates)
    # y_original = values(coord_pontos,'y')
    for y in range(J):
        y_new_values.append(GridPoint_Generico(0, y, Ly=Ly, J=J).coord_y)

    return y_new_values


def current_lx(coord_points, y_coord):
    """
    Gets Lx value for a given "y_coord" point (required in the irregular figures cases, with
    variable width)
    Gets "x" coordinate initial value (required to keep original shape)
    """
    x_coord = []

    for coord in coord_points:
        if (
            coord[1] == y_coord
        ):  # Verifica, para todos os pares, quais os valores de x que possuem
            # y_coord como coordenada y
            x_coord.append(coord[0])

    if x_coord != []:
        lx = abs(max(x_coord) - min(x_coord))  # obtém o lx
    else:
        ValueError("Could not find correspondent value!")

    beggining_x = min(x_coord)

    return lx, beggining_x


def close_values(new_value, original_values):
    """
    Obtaining the values immediately above and below those to be interpolated
    """
    upper_value = max(original_values)
    lower_value = min(original_values)

    for value in original_values:
        if value < new_value and value >= lower_value:
            lower_value = value
        if value > new_value and value <= upper_value:
            upper_value = value

    return lower_value, upper_value


def interpolation(coordinates, new_value, original_values):
    """
    Realiza interpolação para obter um par ordenado (x,y) com base no novo valor
    y = new_value, nos valores originais de y, original_values, e nas coordenadas
    originais de x e y coordinates

    Interpolates to get an ordered pair (x,y) based on the new value y=new_value,
    on y original values and on the original coordinates x and y
    """

    lower_value, upper_value = close_values(new_value, original_values)

    lower_y_x = []  # Armazenará os valores de x que já estão presentes para o y abaixo
    upper_y_x = []
    for coord in coordinates:
    
        if lower_value == coord[1]:
            lower_y_x.append(coord[0])
        if upper_value == coord[1]:
            upper_y_x.append(coord[0])

    y = new_value

    x1 = min(lower_y_x)
    x2 = min(upper_y_x)
    y1 = lower_value
    y2 = upper_value

    if (x2 - x1) != 0 and (y2 - y1) != 0:
        derivative_1 = (y2 - y1) / (x2 - x1)
        x_first = x1 + ((y - y1) / derivative_1)

    else:
        x_first = x1

    x1 = max(lower_y_x)
    x2 = max(upper_y_x)
    y1 = lower_value
    y2 = upper_value

    if (x2 - x1) != 0 and (y2 - y1) != 0:
        derivative_2 = (y2 - y1) / (x2 - x1)
        x_last = x1 + ((y - y1) / derivative_2)

    else:
        x_last = x1

    return (x_first, y), (x_last, y)


def room_discretization(coord_original, I, J):

    """
    Utiliza as funções declaradas anteriormente para obter as novas coordenadas
    da geometria já discretizada, com I elementos no eixo x e J no eixo y, com base
    na coordenada original genérica coord_original

    Uses the functions declared above to get the new geometry coordinates, discretized
    already, with "I" elements on x axis and "J" on y axis, based on original coordinates
    coord_original

    """

    y_original = values(coord_original, "y")

    Ly = get_Ly(coord_original)
    y_discretizado = y_discretization(coord_original, J)

    pontos_discretizados = []

    for y in y_discretizado:

        # Caso y esteja no conjunto original, apenas crio os pontos de x naquelas
        # coordenadas (não é necessário interpolação)
        if y in y_original:
            lx, beggining_x = current_lx(coord_original, y)
            for x in range(I):
                # set_trace()
                pontos_discretizados.append(
                    (
                        beggining_x
                        + GridPoint_Generico(x, y, Lx=lx, Ly=Ly, I=I, J=J).coord_x,
                        y,
                    )
                )

        # Interpolação
        else:
            first_pair, last_pair = interpolation(coord_original, y, y_original)
            first_x = first_pair[0]
            last_x = last_pair[0]
            lx = last_x - first_x
            beggining_x = first_x
            for x in range(I):
                pontos_discretizados.append(
                    (
                        beggining_x
                        + GridPoint_Generico(x, y, Lx=lx, Ly=Ly, I=I, J=J).coord_x,
                        y,
                    )
                )

    return pontos_discretizados


# Funções utilizadas para encontrar o receptor mais próximo da coordenada da fonte, para criar um mask com a info da posição!


# def euclidian_distance(coord1, coord2):
#     """
#     Calculates the euclidian distance between coord1 and coord2, that are two arrays
#     """
#     import math

#     distance = np.sqrt(
#         (coord2[0] - coord1[0]) ** 2
#         + (coord2[1] - coord1[1]) ** 2
#         + (coord2[2] - coord1[2]) ** 2
#     )

#     return distance


# def index_closest_rec(S, R):

#     rec_coordinates = R.coord
#     source_coordinate = S.coord[0]

#     distance = [
#         euclidian_distance(source_coordinate, coord) for coord in rec_coordinates
#     ]
#     min_distance = min(distance)
#     rec_index = distance.index(min_distance)

#     return rec_index
#     "Obtém a coordenada de R mais próxima da coordenada de S"
