import numpy as np
import pandas as pd

from bird_plot.cli import _safe_name_for_path, _sigmoid_scale


def test_safe_name_for_path_sanitizes() -> None:
    assert _safe_name_for_path("Alice/Bob..") == "Alice_Bob"
    assert _safe_name_for_path("   ") == "unnamed"
    assert _safe_name_for_path("Ok-Name_1") == "Ok-Name_1"


def test_sigmoid_scale_zero_series_returns_zero() -> None:
    series = pd.Series([0, 0, 0], dtype=float)
    scaled = _sigmoid_scale(series, max_value=25)
    assert np.allclose(scaled.to_numpy(), [0, 0, 0], equal_nan=False)
