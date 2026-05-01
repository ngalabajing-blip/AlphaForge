from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from alphaforge_shared.settings import CommonSettings
from pydantic import Field


class MLSettings(CommonSettings):
    model_dir: Path = Field(default=Path("/var/lib/alphaforge/ml"), alias="ML_MODEL_DIR")
    feature_window: int = Field(default=120, alias="ML_FEATURE_WINDOW")
    anomaly_contamination: float = Field(default=0.02, alias="ML_ANOMALY_CONTAMINATION")
    sentiment_max_length: int = Field(default=160, alias="ML_SENTIMENT_MAX_LENGTH")
    use_torch: bool = Field(default=False, alias="ML_USE_TORCH")
    sentiment_backend: str = Field(
        default="lexicon", alias="ML_SENTIMENT_BACKEND"
    )  # "lexicon" | "transformer"


@lru_cache(maxsize=1)
def get_settings() -> MLSettings:
    return MLSettings()
