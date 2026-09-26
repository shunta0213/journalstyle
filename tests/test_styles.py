import matplotlib.pyplot as plt
import pytest

import journalstyle as js
from journalstyle.specs import JOURNALS


def test_styles_are_registered():
    assert "journal" in plt.style.available
    assert "journal-latex" in plt.style.available
    assert "journal-latex-sans" in plt.style.available
    for key in JOURNALS:
        assert f"journal-{key}" in plt.style.available


def test_latex_styles_match_the_journal_family():
    with plt.style.context(["journal-aps", "latex"]):
        assert plt.rcParams["text.usetex"] is True
        assert "sfmath" not in plt.rcParams["text.latex.preamble"]
        assert plt.rcParams["xtick.direction"] == "in"
        assert plt.rcParams["figure.figsize"][0] == pytest.approx(3.375, abs=0.002)
    with plt.style.context(["journal-nature", "latex"]):
        assert plt.rcParams["text.usetex"] is True
        assert "sfmath" in plt.rcParams["text.latex.preamble"]
        assert plt.rcParams["font.family"][0] == "sans-serif"
        assert plt.rcParams["font.serif"][0] == "Computer Modern Roman"
    js.use("nature", latex=True)
    assert "sfmath" in plt.rcParams["text.latex.preamble"]


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


def test_panel_labels_follow_the_journal():
    assert js.format_panel("aps", 0) == "(a)"
    assert js.format_panel("nature", 1) == "b"
    assert js.format_panel("aaas", 0) == "A"
    assert js.get("aaas").panel_label_pt == 10
    assert js.get("nature").panel_label_pt == 8


def _legend_bbox(fig, leg):
    fig.draw_without_rendering()
    tight = leg.get_tightbbox(fig.canvas.get_renderer())
    return fig.transFigure.inverted().transform_bbox(tight)


def test_legend_below_keeps_the_axes_on_save(tmp_path):
    fig, ax = js.subplots("aps")
    for label in ("Experiment A", "Experiment B", "Experiment C", "Experiment D"):
        ax.plot([0, 1], [0, 1], label=label)
    ax.set_xlabel("x")
    leg = js.legend(ax, loc="below")
    fig.savefig(tmp_path / "below.pdf")
    assert fig.get_figwidth() == pytest.approx(3.375)
    assert ax.get_position().width > 0.7
    bbox = _legend_bbox(fig, leg)
    assert bbox.x0 >= -0.01
    assert bbox.x1 <= 1.01
    assert bbox.y1 < ax.get_position().y0
    plt.close(fig)


def test_legend_above_sits_under_the_title(tmp_path):
    fig, ax = js.subplots("aaas")
    ax.set_title("Head")
    for label in ("Experiment A", "Experiment B", "Experiment C", "Experiment D"):
        ax.plot([0, 1], [0, 1], label=label)
    leg = js.legend(ax, loc="above")
    fig.savefig(tmp_path / "above.pdf")
    assert leg.get_title().get_text() == "Head"
    assert ax.get_title() == ""
    assert ax.get_position().width > 0.7
    bbox = _legend_bbox(fig, leg)
    assert bbox.y0 > ax.get_position().y1
    assert bbox.x0 >= -0.01
    assert bbox.x1 <= 1.01
    plt.close(fig)


def test_legend_rejects_an_unknown_location():
    fig, ax = js.subplots("aps")
    ax.plot([0, 1], [0, 1], label="a")
    with pytest.raises(ValueError, match="below"):
        js.legend(ax, loc="best")
    plt.close(fig)


def test_bw_extra_overrides_colors():
    js.use("aps", extras=("journal-bw",))
    colors = [c["color"] for c in plt.rcParams["axes.prop_cycle"]]
    assert colors[0] == "#000000"
