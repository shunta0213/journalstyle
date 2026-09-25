import matplotlib.pyplot as plt
import pytest

import journalstyle as js
from journalstyle.specs import JOURNALS


def test_styles_are_registered():
    assert "journal" in plt.style.available
    for key in JOURNALS:
        assert f"journal-{key}" in plt.style.available


def test_single_column_width_matches_spec():
    for key, spec in JOURNALS.items():
        with plt.style.context(["journal", f"journal-{key}"]):
            width, height = plt.rcParams["figure.figsize"]
            assert width == pytest.approx(spec.width_in(1), abs=0.002)
            assert height == pytest.approx(spec.width_in(1) * 0.75, abs=0.002)
            assert plt.rcParams["font.size"] == spec.font_size


def test_use_sets_font_and_double_column():
    js.use("ieee", columns=2)
    width, height = plt.rcParams["figure.figsize"]
    assert width == pytest.approx(JOURNALS["ieee"].width_in(2))
    assert height == pytest.approx(width * 0.75)
    assert plt.rcParams["font.size"] == 9
    assert plt.rcParams["text.usetex"] is False
    assert plt.rcParams["savefig.dpi"] == 600
    assert plt.rcParams["figure.dpi"] != 600


def test_unknown_journal_and_column():
    with pytest.raises(ValueError, match="Unknown journal"):
        js.use("prl")
    with pytest.raises(ValueError, match="1.5"):
        js.figure_size("ieee", columns=1.5)


def test_nature_one_and_a_half():
    width, _ = js.figure_size("nature", columns=1.5)
    assert width == pytest.approx(128 / 25.4)


def test_subplots_keeps_style_for_later_artists():
    fig, ax = js.subplots("aps", columns=1)
    assert fig.get_figwidth() == pytest.approx(3.375)
    line = ax.plot([0, 1], [0, 1])[0]
    assert line.get_linewidth() == pytest.approx(1.0)
    plt.close(fig)


def test_context_restores_previous_style():
    js.use("aps")
    with js.context("nature"):
        assert plt.rcParams["font.family"][0] == "sans-serif"
    assert plt.rcParams["font.family"][0] == "serif"


def test_aaas_three_columns():
    width, _ = js.figure_size("aaas", columns=3)
    assert width == pytest.approx(184 / 25.4)


def test_bw_extra_overrides_colors():
    js.use("aps", extras=("journal-bw",))
    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
    assert colors[0] == "#000000"
