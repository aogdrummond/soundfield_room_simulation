import femder.femder as fd
import numpy as np
import scipy.io
from Core.entities import Setup, Ambient, Room, Observation, Source
from datetime import datetime
import json
import os


def mat_struct(
    Setup: Setup,
    AbsFrequencyResponse=np.zeros((32, 32, 300)),
    FreqLim=int(),
    Frequency=np.zeros((1, 600)),
    FrequencyResponse=np.zeros((32, 32, 300)),
    i=int(),
    j=int(),
    Mu=np.zeros((17, 151)),
    Psi_r=np.zeros((1024, 17)),
    Psi_s=np.zeros((1024, 17)),
    xCoor=np.zeros((1, 32)),
    yCoor=np.zeros((1, 32)),
    Receiver_Coord=np.zeros((1, 1024)),
):

    mat_file_dict = {
        "Setup": Setup,
        "AbsFrequencyResponse": AbsFrequencyResponse,
        "FreqLim": FreqLim,
        "Frequency": Frequency,
        "FrequencyResponse": FrequencyResponse,
        "i": i,
        "j": j,
        "Mu": Mu,
        "Psi_r": Psi_r,
        "Psi_s": Psi_s,
        "xCoord": xCoor,
        "yCoord": yCoor,
        "Receiver_Coord": Receiver_Coord,
    }

    return mat_file_dict


def save_sample(
    l: float,
    w: float,
    height: float,
    S: fd.Source,
    R: fd.receivers.Receiver,
    F: fd.FEM_3D.FEM3D,
    receivers_coord: np.array,
    dataset_path: str,
    I: int,
    J: int,
):

    """ """
    ambient = Ambient(Temp=20, Pressure=1000e2)
    room = Room(Dim=[l, w, height], Dim2=2 * l * w, ReverbTime=0.6)
    source = Source(Highpass=10, Lowpass=150, Position=S.coord, ScrNum=len(S.coord[0]))
    observation = Observation(
        xSample=I,
        ySample=J,
        zSample=1,
        xSamplingDistance=1,
        ySamplingDistance=1,
        zSamplingDistance=1,
        Center=0,
        Point=receivers_coord,
    )
    setup = Setup(
        Fs=1200,
        Duration=1,
        Ambient=ambient,
        Room=room,
        Source=source,
        Observation=observation,
    )

    FrequencyResponse = F.evaluate(R)
    FrequencyResponse = np.reshape(FrequencyResponse, (-1, I, J))
    FrequencyResponse = np.transpose(FrequencyResponse, (1, 2, 0))

    n_sample = len(
        [sample for sample in os.listdir(dataset_path) if sample.endswith(".mat")]
    )

    mat = mat_struct(
        Setup=setup,
        AbsFrequencyResponse=abs(FrequencyResponse),
        FreqLim=0,
        Frequency=np.array(
            (np.arange(0, (setup.Fs / 2 - 1 / setup.Duration), 1 / setup.Duration))
        ),
        FrequencyResponse=FrequencyResponse,
        i=0,
        j=n_sample,
        Mu=np.zeros((17, 151)),
        Psi_r=np.zeros((1024, 17)),
        Psi_s=np.zeros((17, 1)),
        xCoor=np.arange(0, room.Dim[0] + 0.001, observation.xSamplingDistance),
        yCoor=np.arange(0, room.Dim[1] + 0.001, observation.ySamplingDistance),
        Receiver_Coord=R.coord[:, 0:2],
    )

    save_mat(mat_dict=mat, file_path=dataset_path)


def save_mat(mat_dict: dict, file_path: str):

    "Function to save the file as .mat"

    def create_filename(mat_dict: dict) -> str:
        """
        Creates the string with file's name according the standard addopted on the original
        work, from the attributes of .mat file.
        """

        filename = "".join(
            [
                str(mat_dict["j"]),
                "_d_",
                str(mat_dict["Setup"].Room.Dim[0]),
                "_",
                str(mat_dict["Setup"].Room.Dim[1]),
                "_",
                str(mat_dict["Setup"].Room.Dim2),
                "_s_",
                str(mat_dict["Setup"].Source.Position[0][0]),
                "_",
                str(mat_dict["Setup"].Source.Position[0][1]),
                "_.mat",
            ]
        )

        return filename

    mat_file = {
        "Setup": mat_dict["Setup"],
        "AbsFrequencyResponse": mat_dict["AbsFrequencyResponse"],
        "FreqLim": mat_dict["FreqLim"],
        "Frequency": mat_dict["Frequency"],
        "FrequencyResponse": mat_dict["FrequencyResponse"],
        "i": mat_dict["i"],
        "j": mat_dict["j"],
        "Mu": mat_dict["Mu"],
        "Psi_r": mat_dict["Psi_r"],
        "Psi_s": mat_dict["Psi_s"],
        "xCoord": mat_dict["xCoord"],
        "yCoord": mat_dict["yCoord"],
        "Receiver_Coord": mat_dict["Receiver_Coord"],
    }

    filename = create_filename(mat_dict)

    scipy.io.savemat(os.path.join(file_path, filename), mat_file)


def unwraps_mat_file(mat_file: dict) -> dict:
    """
    Formats loaded mat_file as an understandable
    dictionary, since the original structure changes
    during saving.
    """

    Ambient = {
        "Temp": int(mat_file["Setup"][0][0][2][0][0][0]),
        "Pressure": int(mat_file["Setup"][0][0][2][0][0][1]),
        "R_": int(mat_file["Setup"][0][0][2][0][0][2]),
        "rho": float(mat_file["Setup"][0][0][2][0][0][3]),
        "cp": float(mat_file["Setup"][0][0][2][0][0][4]),
        "cv": float(mat_file["Setup"][0][0][2][0][0][5]),
        "gamma": float(mat_file["Setup"][0][0][2][0][0][6]),
        "c": float(mat_file["Setup"][0][0][2][0][0][7]),
    }

    Room = {
        "Dim": mat_file["Setup"][0][0][3][0][0][0].ravel(),
        "Dim2": float(mat_file["Setup"][0][0][3][0][0][1]),
        "ReverbTime": float(mat_file["Setup"][0][0][3][0][0][2]),
    }

    Source = {
        "Highpass": int(mat_file["Setup"][0][0][4][0][0][0]),
        "Lowpass": int(mat_file["Setup"][0][0][4][0][0][1]),
        "Position": mat_file["Setup"][0][0][4][0][0][2].ravel(),
        "ScrNum": int(mat_file["Setup"][0][0][4][0][0][3]),
    }

    Observation = {
        "xSample": int(mat_file["Setup"][0][0][5][0][0][0]),
        "ySample": int(mat_file["Setup"][0][0][5][0][0][1]),
        "zSample": int(mat_file["Setup"][0][0][5][0][0][2]),
        "xSamplingDistance": int(mat_file["Setup"][0][0][5][0][0][3]),
        "ySamplingDistance": float(mat_file["Setup"][0][0][5][0][0][4]),
        "zSamplingDistance": float(mat_file["Setup"][0][0][5][0][0][5]),
        "Center": float(mat_file["Setup"][0][0][5][0][0][6]),
        "Point": mat_file["Setup"][0][0][5][0][0][7],
    }

    Setup = {
        "Fs": int(mat_file["Setup"][0][0][0]),
        "Duration": int(mat_file["Setup"][0][0][1]),
        "Ambient": Ambient,
        "Room": Room,
        "Source": Source,
        "Observation": Observation,
    }

    mat_dict = {
        "Setup": Setup,
        "AbsFrequencyResponse": mat_file["AbsFrequencyResponse"],
        "FreqLim": mat_file["FreqLim"],
        "Frequency": mat_file["Frequency"],
        "FrequencyResponse": mat_file["FrequencyResponse"],
        "i": mat_file["i"],
        "j": mat_file["j"],
        "Mu": mat_file["Mu"],
        "Psi_r": mat_file["Psi_r"],
        "Psi_s": mat_file["Psi_s"],
        "xCoord": mat_file["xCoord"],
        "yCoord": mat_file["yCoord"],
        "Receiver_Coord": mat_file["Receiver_Coord"],
    }

    return mat_dict


def save_properties(dataset_path: str, properties: dict):

    date = datetime.now().isoformat()[: datetime.now().isoformat().rfind(".")]

    settings_file = {
        "date": date,
        "c0": properties.get("c0", 343.0),
        "rho0": properties.get("rho0", 1.21),
        "temperature": properties.get("temperature", 20.0),
        "humid": properties.get("humid", 50.0),
        "p_atm": properties.get("p_atm", 101325.0),
        "T60": properties.get("T60", 0.6),
        "source_Q": properties.get("source_Q", 0.01),
        "receiver_height": properties.get("receiver_height", 1.0),
        "freqMin": properties.get("freqMin", 0),
        "freqMax": properties.get("freqMax", 150),
    }
    settings_file_path = os.path.join(dataset_path, "dataset_settings.json")
    with open(settings_file_path, "w") as f:
        json.dump(settings_file, f)

    print("Settings saved")


def generate_folder_tree(dataset_path: str):
    """
    Generates the folder tree as required to fit to the rest of the repo
    in "dataset_path" if it still does not existe
    """
    os.mkdir(os.path.join(dataset_path, "simulated_soundfields"))
    for subset in ["train", "test", "val"]:
        os.mkdir(os.path.join(dataset_path, "simulated_soundfields", subset))

    print("Dataset folder tree generated")
