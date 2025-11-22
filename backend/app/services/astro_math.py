import math

# Physical constants (SI units)
G = 6.67430e-11            # gravitational constant, m^3 kg^-1 s^-2
C = 2.99792458e8           # speed of light, m/s
M_SUN = 1.98847e30         # mass of the Sun, kg
AU = 1.495978707e11        # astronomical unit, m
YEAR_SEC = 365.25 * 24 * 3600  # seconds in a year


def schwarzschild_radius_solar_masses(mass_solar: float) -> float:
    """
    Compute Schwarzschild radius (event horizon radius) for a non-rotating black hole.

    Rs = 2GM / c^2

    :param mass_solar: mass in units of solar masses
    :return: radius in meters
    """
    mass_kg = mass_solar * M_SUN
    rs = 2 * G * mass_kg / (C ** 2)
    return rs


def schwarzschild_radius_km(mass_solar: float) -> float:
    """
    Convenience wrapper: Schwarzschild radius in kilometers.
    """
    return schwarzschild_radius_solar_masses(mass_solar) / 1000.0


def kepler_orbital_period_years(a_au: float, star_mass_solar: float = 1.0) -> float:
    """
    Approximate orbital period using Kepler's 3rd law in astrophysical units:

        P^2 = a^3 / M

    where:
      - P is in years
      - a is semi-major axis in AU
      - M is star mass in solar masses

    :param a_au: semi-major axis in AU
    :param star_mass_solar: star mass in solar masses (default: 1 solar mass)
    :return: orbital period in years
    """
    if star_mass_solar <= 0:
        raise ValueError("Star mass must be positive")

    p_years = math.sqrt((a_au ** 3) / star_mass_solar)
    return p_years


def kepler_orbital_period_days(a_au: float, star_mass_solar: float = 1.0) -> float:
    """
    Orbital period in days, convenience wrapper.
    """
    p_years = kepler_orbital_period_years(a_au, star_mass_solar)
    return p_years * 365.25
