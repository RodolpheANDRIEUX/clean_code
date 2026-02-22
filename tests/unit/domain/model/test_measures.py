"""Tests for Measures domain model."""
from __future__ import annotations

import pytest

from src.domain.model.measures import (
    TemperatureC,
    HumidityPct,
    PressurePa,
    RainMm,
    RainIntensityMmH,
    WindSpeed,
    WindDirectionDeg,
    WindVector,
)


class TestTemperatureC:
    """Tests for TemperatureC value object."""

    def test_valid_temperature(self) -> None:
        temp = TemperatureC(value=20.5)
        assert temp.value == 20.5

    def test_temperature_immutable(self) -> None:
        temp = TemperatureC(value=20.5)
        with pytest.raises(AttributeError):
            temp.value = 25.0  # type: ignore

    def test_temperature_too_low(self) -> None:
        with pytest.raises(ValueError, match="Température hors bornes"):
            TemperatureC(value=-101.0)

    def test_temperature_too_high(self) -> None:
        with pytest.raises(ValueError, match="Température hors bornes"):
            TemperatureC(value=81.0)

    def test_temperature_boundary_values(self) -> None:
        TemperatureC(value=-100.0)
        TemperatureC(value=80.0)

    def test_temperature_from_int(self) -> None:
        temp = TemperatureC(value=20)
        assert temp.value == 20.0


class TestHumidityPct:
    """Tests for HumidityPct value object."""

    def test_valid_humidity(self) -> None:
        hum = HumidityPct(value=75.5)
        assert hum.value == 75.5

    def test_humidity_too_low(self) -> None:
        with pytest.raises(ValueError, match="Humidité hors bornes"):
            HumidityPct(value=-1.0)

    def test_humidity_too_high(self) -> None:
        with pytest.raises(ValueError, match="Humidité hors bornes"):
            HumidityPct(value=111.0)

    def test_humidity_boundary_values(self) -> None:
        HumidityPct(value=0.0)
        HumidityPct(value=110.0)

    def test_humidity_over_100(self) -> None:
        # Sensors can sometimes report > 100%
        hum = HumidityPct(value=105.0)
        assert hum.value == 105.0


class TestPressurePa:
    """Tests for PressurePa value object."""

    def test_valid_pressure(self) -> None:
        press = PressurePa(value=101325)
        assert press.value == 101325

    def test_pressure_to_hpa(self) -> None:
        press = PressurePa(value=101325)
        assert press.to_hpa() == 1013.25

    def test_pressure_too_low(self) -> None:
        with pytest.raises(ValueError, match="Pression hors bornes"):
            PressurePa(value=79999)

    def test_pressure_too_high(self) -> None:
        with pytest.raises(ValueError, match="Pression hors bornes"):
            PressurePa(value=110001)

    def test_pressure_boundary_values(self) -> None:
        PressurePa(value=80000)
        PressurePa(value=110000)

    def test_pressure_from_float(self) -> None:
        press = PressurePa(value=101325.7)
        assert press.value == 101326  # Rounded


class TestRainMm:
    """Tests for RainMm value object."""

    def test_valid_rain(self) -> None:
        rain = RainMm(value=10.5)
        assert rain.value == 10.5

    def test_rain_zero(self) -> None:
        rain = RainMm(value=0.0)
        assert rain.value == 0.0

    def test_rain_negative(self) -> None:
        with pytest.raises(ValueError, match="Pluie hors bornes"):
            RainMm(value=-1.0)

    def test_rain_too_high(self) -> None:
        with pytest.raises(ValueError, match="Pluie hors bornes"):
            RainMm(value=501.0)

    def test_rain_boundary_values(self) -> None:
        RainMm(value=0.0)
        RainMm(value=500.0)


class TestRainIntensityMmH:
    """Tests for RainIntensityMmH value object."""

    def test_valid_intensity(self) -> None:
        intensity = RainIntensityMmH(value=50.0)
        assert intensity.value == 50.0

    def test_intensity_zero(self) -> None:
        intensity = RainIntensityMmH(value=0.0)
        assert intensity.value == 0.0

    def test_intensity_negative(self) -> None:
        with pytest.raises(ValueError, match="Intensité pluie hors bornes"):
            RainIntensityMmH(value=-1.0)

    def test_intensity_too_high(self) -> None:
        with pytest.raises(ValueError, match="Intensité pluie hors bornes"):
            RainIntensityMmH(value=1001.0)

    def test_intensity_boundary_values(self) -> None:
        RainIntensityMmH(value=0.0)
        RainIntensityMmH(value=1000.0)


class TestWindSpeed:
    """Tests for WindSpeed value object."""

    def test_valid_wind_speed(self) -> None:
        speed = WindSpeed(value=15.5)
        assert speed.value == 15.5

    def test_wind_speed_zero(self) -> None:
        speed = WindSpeed(value=0.0)
        assert speed.value == 0.0

    def test_wind_speed_negative(self) -> None:
        with pytest.raises(ValueError, match="Vent hors bornes"):
            WindSpeed(value=-1.0)

    def test_wind_speed_too_high(self) -> None:
        with pytest.raises(ValueError, match="Vent hors bornes"):
            WindSpeed(value=81.0)

    def test_wind_speed_boundary_values(self) -> None:
        WindSpeed(value=0.0)
        WindSpeed(value=80.0)


class TestWindDirectionDeg:
    """Tests for WindDirectionDeg value object."""

    def test_valid_direction(self) -> None:
        direction = WindDirectionDeg(value=180)
        assert direction.value == 180

    def test_direction_north(self) -> None:
        direction = WindDirectionDeg(value=0)
        assert direction.value == 0

    def test_direction_full_circle(self) -> None:
        direction = WindDirectionDeg(value=360)
        assert direction.value == 360

    def test_direction_negative(self) -> None:
        with pytest.raises(ValueError, match="Direction vent invalide"):
            WindDirectionDeg(value=-1)

    def test_direction_too_high(self) -> None:
        with pytest.raises(ValueError, match="Direction vent invalide"):
            WindDirectionDeg(value=361)

    def test_direction_from_float(self) -> None:
        direction = WindDirectionDeg(value=180.7)
        assert direction.value == 181  # Rounded


class TestWindVector:
    """Tests for WindVector composite value object."""

    def test_valid_wind_vector_full(self) -> None:
        wind = WindVector(
            mean_speed=WindSpeed(10.0),
            mean_direction=WindDirectionDeg(180),
            max_gust=WindSpeed(15.0),
            max_direction=WindDirectionDeg(190),
        )
        assert wind.mean_speed.value == 10.0
        assert wind.mean_direction.value == 180
        assert wind.max_gust.value == 15.0
        assert wind.max_direction.value == 190

    def test_wind_vector_partial(self) -> None:
        wind = WindVector(
            mean_speed=WindSpeed(10.0),
            mean_direction=WindDirectionDeg(180),
        )
        assert wind.mean_speed.value == 10.0
        assert wind.mean_direction.value == 180
        assert wind.max_gust is None
        assert wind.max_direction is None

    def test_wind_vector_empty(self) -> None:
        wind = WindVector()
        assert wind.mean_speed is None
        assert wind.mean_direction is None
        assert wind.max_gust is None
        assert wind.max_direction is None

    def test_wind_vector_immutable(self) -> None:
        wind = WindVector(mean_speed=WindSpeed(10.0))
        with pytest.raises(AttributeError):
            wind.mean_speed = WindSpeed(20.0)  # type: ignore
