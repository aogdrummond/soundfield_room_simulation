import femder.femder as fd
import numpy as np
import scipy.io
from Core.entities import Setup, Ambient, Room, Observation, Source


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

    scipy.io.savemat("".join([file_path, filename]), mat_file)


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
        zSample=1.2,
        xSamplingDistance=1,
        ySamplingDistance=1,
        zSamplingDistance=1.0,
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

    mat = mat_struct(
        Setup=setup,
        AbsFrequencyResponse=abs(FrequencyResponse),
        FreqLim=0,
        Frequency=np.array(
            (np.arange(0, (setup.Fs / 2 - 1 / setup.Duration), 1 / setup.Duration))
        ),
        FrequencyResponse=FrequencyResponse,
        i=0,
        j=0,
        Mu=np.zeros((17, 151)),
        Psi_r=np.zeros((1024, 17)),
        Psi_s=np.zeros((17, 1)),
        xCoor=np.arange(0, room.Dim[0] + 0.001, observation.xSamplingDistance),
        yCoor=np.arange(0, room.Dim[1] + 0.001, observation.ySamplingDistance),
        Receiver_Coord=R.coord[:, 0:2],
    )

    save_mat(mat_dict=mat, file_path=dataset_path)
