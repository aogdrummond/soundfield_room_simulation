import numpy as np
import math

def calculate_Zs(
    alfa_s: float,
    Temp: int = 20,
    Pressure: float = 1000e2,
    R_: int = 287,
    cp: float = 29.07,
    cv: float = 20.7643,
    normalized=False,
) -> float:
    """
    Calculates surface's acoustic impedance based
    on its absorption

    ARGUMENTS:
        alfa_s: The mean absorption of the wall
        Temp: Ambient Temperature
        Pressure: Ambient Pressure
        R_: Ideal gases constant
        cp: isobaric molar heat capacity
        cv: isochore molar heat capacity
    RETURNS:
        Zs: Surface's acoustic impedance
    """

    rho0 = Pressure / (R_ * Temp + 237.15)
    gamma = cp / cv
    c0 = np.sqrt(gamma * Pressure * rho0)
    Zs = ((rho0 * c0) / (np.cos(55 * np.pi / 180))) * (
        1 + (np.sqrt(1 - alfa_s)) / (1 - np.sqrt(1 - alfa_s))
    )

    if normalized == True:
        return Zs / (rho0 * c0)

    else:
        return Zs


def normalized_admitance(
    alfa_s: float,
    Temp: int = 20,
    Pressure: float = 1000e2,
    R_: int = 287,
    cp: float = 29.07,
    cv: float = 20.7643,
) -> float:
    """
    Calculates mean wall's acoustic admittance for room
    based on its absorption an normalized by characteristic
    impedance (Z0)
    Args:
        alfa_s: The mean absorption of the wall
        Temp: Ambient Temperature
        Pressure: Ambient Pressure
        R_: Ideal gases constant
        cp: isobaric molar heat capacity
        cv: isochore molar heat capacity
    Returns:
        Y0: room's normalized admittance
    """
    Zs = calculate_Zs(
        alfa_s=alfa_s,
        Temp=Temp,
        Pressure=Pressure,
        R_=R_,
        cp=cp,
        cv=cv,
        normalized=True,
    )

    return 1 / Zs


def room_absorption(S_floor: float, S: float, height: float, T60=0.6) -> float:
    """
    Calculates expected properties for the room based on its dimensions.
    Alpha is calculated according to Eyring's formula and considering
    reverberation time T60
    Args:
        S_planta: Transversal area (floors)
        S: Whole room's area
        height: Room's ceiling height
    Returns:
        alpha: room's mean coeficient of absorption

    """
    V = S_floor * height
    alpha = 1 - math.exp(0.161 * V / (-S * T60))

    return alpha
