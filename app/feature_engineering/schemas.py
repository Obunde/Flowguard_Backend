"""The one definition of a model-ready feature vector.

`services` builds a `FeatureVector` and returns `.as_dict()`; consumers can
`FeatureVector.model_validate(vec)` to type-check. Field names map onto the
ETL Gold tables (`app/etl/gold/models.py`): sensor tier -> PumpFeatureWindow,
weather/risk tiers -> WeatherDailyRollup / StationRiskComposite via the
pump's station. Only columns that exist there are represented — the
proposal's *_min/*_max/*_trend, 30d cumulative rainfall and humidity have no
Gold column and are omitted.
"""
from pydantic import BaseModel, ConfigDict

# All-float so the vector round-trips through dict[str, float]. 0.0 fills a
# NULL column or an absent weather/risk join; the *_data_available flags
# distinguish "genuinely zero" from "not joined".
_ZERO = 0.0


class FeatureVector(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # sensor tier: PumpFeatureWindow
    vibration_mean: float = _ZERO
    vibration_std: float = _ZERO
    temperature_mean: float = _ZERO
    temperature_std: float = _ZERO
    pressure_mean: float = _ZERO
    pressure_std: float = _ZERO
    motor_current_mean: float = _ZERO
    sample_count: float = _ZERO  # raw readings behind the window

    # weather tier: WeatherDailyRollup
    weather_temperature_mean: float = _ZERO
    weather_precipitation_total_mm: float = _ZERO
    weather_wind_speed_max_m_s: float = _ZERO
    weather_data_available: float = _ZERO

    # regional risk tier: StationRiskComposite
    regional_risk_score: float = _ZERO
    risk_data_available: float = _ZERO

    def as_dict(self) -> dict[str, float]:
        return {key: float(value) for key, value in self.model_dump().items()}


FEATURE_KEYS: tuple[str, ...] = tuple(FeatureVector.model_fields.keys())
