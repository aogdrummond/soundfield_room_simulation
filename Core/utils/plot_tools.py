# Dependencies

import scipy
import scipy.io
import copy
from scipy import ndimage
from scipy.interpolate import griddata
import numpy as np
import matplotlib.pyplot as plt


def to_db(array: np.array, ref: float = 2 * (10**-5)) -> np.array:

    return 20 * np.log10(array / ref)


def general_room_sf(file_path: str, freq: int = 150) -> None:
    """
    Plots a scatter plot representing the soundfield on .mat file contained on
    "file_path"

    Parameters
    ----------
    file_path : TYPE
        DESCRIPTION.
    plot_receptors : boolean, optional
        DESCRIPTION. If you want the receptors position to be ploted instead of the soundfield
    freq: int, optional
        DESCRIPTION. The frequency which soundfield will be plotted
    cmap : str, optional
        DESCRIPTION. The colormap used to plot the soundfield
    Returns
    -------
    None.

    """
    mat = scipy.io.loadmat(file_path)
    frequency = mat["Frequency"][0]
    freq_idx = np.where(frequency == freq)[0]

    if len(freq_idx) == 0:
        raise IndexError(
            f"There is not information about {freq} Hz. Available frequencies: {frequency}"
        )

    f_response = mat["AbsFrequencyResponse"]
    soundfield = np.transpose(f_response, (1, 0, 2))
    sf_gt = np.expand_dims(copy.deepcopy(soundfield), axis=0)

    coordinates = mat["Receiver_Coord"]

    values = np.reshape(sf_gt[0, ..., freq_idx], (-1))
    fig, axs = plt.subplots(1, 1)
    max_x = coordinates[:, 0].max()
    max_y = coordinates[:, 1].max()
    aspect_ratio = max_y / (2 * max_x)
    fig.set_figwidth(4)
    fig.set_figheight(4 * aspect_ratio)
    sc = axs.scatter(coordinates[:, 0], coordinates[:, 1], c=to_db(values), cmap="jet")
    fig.colorbar(sc, label="SPL [dB]")
    axs.set_title(f"Sound Pressure along the room ({freq} Hz)")
    axs.set_xlabel("[m]")
    axs.set_ylabel("[m]")


def plot_square_sf(
    file_path: str,
    interpol_method: str = "cubic",
    freq: int = 150,
    resolution: int = 300,
    scatter: bool = False,
    cmap: str = "jet",
) -> None:
    """
    Plots the square projection of the sample contained on .mat file contained in the
    path "file_path"

    Parameters
    ----------
    file_path : TYPE
        DESCRIPTION.
    interpol_method : str, optional
        DESCRIPTION. The default is 'cubic'. One out of 'cubic', 'linear' or 'nearest'
    resolution : int, optional
        DESCRIPTION. The default is 300. The resolution (resolution x resolution) for the
        soundfield plot
    cmap : str, optional
        DESCRIPTION. The colormap used to plot the soundfield
    Returns
    -------
    None.

    """

    # Loading sample
    mat = scipy.io.loadmat(file_path)
    f_response = mat["AbsFrequencyResponse"]
    coordinates = mat["Receiver_Coord"]

    max_x = coordinates[:, 0].max()
    max_y = coordinates[:, 1].max()

    # Reshaping data

    soundfield = np.transpose(f_response, (1, 0, 2))
    sf_gt = np.expand_dims(copy.deepcopy(soundfield), axis=0)
    values = np.reshape(sf_gt[0, ..., freq], (-1))

    unique_y = np.unique(coordinates[:, 1])
    unique_x = np.linspace(-max_x, max_x, 32)

    coords_list = []
    for x in unique_x:
        for y in unique_y:
            coords_list.append((x, y))

    coordinates = np.array(coords_list)

    # Data interpolation

    grid_x, grid_y = np.mgrid[
        -max_x : max_x : complex(0, resolution), 0 : max_y : complex(0, resolution)
    ]
    img = griddata(coordinates, values, (grid_x, grid_y), method=interpol_method).T

    # Image Plotting
    fig, axs = plt.subplots(1, 1)

    if scatter == True:
        plt.scatter(coordinates[:, 0], coordinates[:, 1], c=to_db(values), cmap=cmap)
    else:
        fig.set_figwidth(3)
        fig.set_figheight(7)
        rotated_img = ndimage.rotate(img, 180)
        axs.imshow(rotated_img, origin="lower", aspect="equal")

        ticks = list(np.linspace(0, resolution, 7, dtype=int))
        list_size = len(ticks)
        idx_array = np.arange(0, list_size)
        y_ticks_indexes = np.multiply(idx_array, (max_y / 6))
        y_ticks_indexes = np.round(y_ticks_indexes, 1)
        y_labels = y_ticks_indexes.tolist()
        plt.yticks(ticks, y_labels)
        x_ticks_indexes = np.multiply(idx_array, (2 * max_x / 6))
        x_ticks_indexes = np.round(x_ticks_indexes, 1)
        x_labels = x_ticks_indexes.tolist()
        axs.set_title(f"Squared soundfield at {freq} Hz")
        plt.xticks(ticks, x_labels)
