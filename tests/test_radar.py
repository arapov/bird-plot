import numpy as np

from bird_plot.plots.radar import _format_title


def test_format_title_without_note() -> None:
    data = {"Name": "Grace", "Note": ""}
    assert _format_title(data) == "Grace"


def test_format_title_with_note() -> None:
    data = {"Name": "Grace", "Note": "P/D"}
    assert _format_title(data) == "Grace, P/D"


def test_format_title_with_nan_note() -> None:
    data = {"Name": "Grace", "Note": np.nan}
    assert _format_title(data) == "Grace"
