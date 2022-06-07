import numpy as np

# Definir corretamente os sampling distance!
class Observation:
    def __init__(
        self,
        xSample,
        ySample,
        zSample,
        xSamplingDistance,
        ySamplingDistance,
        zSamplingDistance,
        Center,
        Point,
    ):

        self.xSample = xSample  # N of points on x axis
        self.ySample = ySample  # N of points on y axis
        self.zSample = zSample  # N of points on z axis

        self.xSamplingDistance = xSamplingDistance
        self.ySamplingDistance = ySamplingDistance
        self.zSamplingDistance = zSamplingDistance

        self.Center = Center  # Center of microphone array
        self.Point = Point  # 3D coordinate for each discrete point


"""
Highpass: The cutoff frequency for the high-pass filter applied
Lowpass: The cutoff frequency for the low-pass filter applied
Position: The position of the source
ScrNum: Number of sources
"""


class Source:
    def __init__(self, Highpass: int, Lowpass: int, Position: np.array, ScrNum: int):

        self.Highpass = Highpass  # Source lower cutoff frequency [Hz]
        self.Lowpass = Lowpass  # Source higher cutoff frequency [Hz]
        self.Position = Position  # Source position
        self.ScrNum = ScrNum  # Number of sources


class Room:
    def __init__(self, Dim: np.array, Dim2: np.array, ReverbTime: float):

        self.Dim = Dim
        self.Dim2 = Dim2
        self.ReverbTime = ReverbTime


class Ambient:
    def __init__(self, Temp: int, Pressure: int):

        self.Temp = Temp  # Ambient temperature
        self.Pressure = Pressure  # Ambient pressure
        self.R_ = 287  # Ideal gases constant
        self.rho = self.Pressure / (self.R_ * (self.Temp + 273.15))  # Air density
        self.cp = 29.07  # Isobaric molar heat capacity
        self.cv = 20.7643  # Isochore molar heat capacity
        self.gamma = self.cp / self.cv  # Ratio of specific heats
        self.c = np.sqrt(self.gamma * self.Pressure * self.rho)  # Speed of Sound


class Setup:
    def __init__(
        self,
        Fs: int,
        Duration: int,
        Ambient: Ambient,
        Room: Room,
        Source: Source,
        Observation: Observation,
    ):

        self.Fs = Fs
        self.Duration = Duration
        self.Ambient = Ambient
        self.Room = Room
        self.Source = Source
        self.Observation = Observation
