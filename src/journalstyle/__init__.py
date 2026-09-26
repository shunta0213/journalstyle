"""Matplotlib styles sized to journal column widths.

SciencePlots composes a base style with a journal override. This package
does the same, and also picks the width from the publisher's column size:

    import journalstyle as js

    js.use("aps", columns=1)
    fig, ax = js.subplots()
"""

from __future__ import annotations

import warnings
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import rc_params_from_file

from .specs import JOURNALS, Journal

DEFAULT_ASPECT = 0.75
_FONT_KEYS = (
    "font.size",
    "axes.labelsize",
    "axes.titlesize",
    "xtick.labelsize",
    "ytick.labelsize",
    "legend.fontsize",
    "legend.title_fontsize",
)


def _register_styles() -> None:
    """Add the bundled stylesheets to ``plt.style.library``.

    Each ``journal-<name>`` already includes the shared ``journal`` settings,
    so ``plt.style.use("journal-aps")`` is enough.
    """
    styles_path = Path(__file__).resolve().parent / "styles"
    library = plt.style.library
    for path in styles_path.glob("*.mplstyle"):
        params = rc_params_from_file(path, use_default_template=False)
        library.setdefault(path.stem, {}).update(params)
    base = dict(library["journal"])
    for key in JOURNALS:
        name = f"journal-{key}"
        merged = dict(base)
        merged.update(library[name])
        library[name] = merged
    try:
        available = plt.style.available
    except AttributeError:  # matplotlib < 3.11
        available = plt.style.core.available
    available[:] = sorted(library.keys())


def _latex_style(style_names: list[str]) -> str:
    """Pick Times or Helvetica LaTeX from a journal name already in the list."""
    for name in reversed(style_names):
        key = name.removeprefix("journal-") if isinstance(name, str) else ""
        spec = JOURNALS.get(key)
        if spec is not None:
            return "journal-latex" if spec.family == "serif" else "journal-latex-sans"
    family = plt.rcParams["font.family"]
    family = family[0] if isinstance(family, (list, tuple)) else family
    if family == "sans-serif":
        return "journal-latex-sans"
    return "journal-latex"


def _expand_style(style):
    """Replace the name ``latex`` with the face that matches the journal."""
    if style == "latex":
        return _latex_style([])
    if isinstance(style, (str, dict)) or not isinstance(style, (list, tuple)):
        return style
    names = [item for item in style if isinstance(item, str)]
    return [_latex_style(names) if item == "latex" else item for item in style]


def _install_style_use() -> None:
    original = plt.style.use

    def use(style):
        return original(_expand_style(style))

    plt.style.use = use


_register_styles()
_install_style_use()


def journals() -> list[str]:
    """Return journal keys in a stable order."""
    return list(JOURNALS)


def get(journal: str) -> Journal:
    """Return the specification for ``journal``."""
    try:
        return JOURNALS[journal]
    except KeyError:
        known = ", ".join(JOURNALS)
        raise ValueError(f"Unknown journal {journal!r}. Known journals: {known}.") from None


def figure_size(
    journal: str,
    columns: float = 1,
    aspect: float = DEFAULT_ASPECT,
) -> tuple[float, float]:
    """Return ``(width, height)`` in inches for the journal column count.

    ``aspect`` is height / width. The default is 3/4.
    """
    spec = get(journal)
    if aspect <= 0:
        raise ValueError("aspect must be positive.")
    width = spec.width_in(columns)
    height = width * aspect
    if spec.max_height_mm is not None and height * 25.4 > spec.max_height_mm + 0.5:
        warnings.warn(
            f"{journal} figure height {height:.2f} in exceeds the page depth "
            f"({spec.max_height_mm:.0f} mm). Reduce aspect or split the figure.",
            stacklevel=2,
        )
    return (width, height)


def _layers(
    journal: str,
    *,
    columns: float,
    aspect: float,
    latex: bool,
    extras: Sequence[str],
) -> list:
    spec = get(journal)
    layers: list = ["journal", f"journal-{journal}"]
    if latex:
        style = "journal-latex" if spec.family == "serif" else "journal-latex-sans"
        layers.append(style)
    else:
        layers.append("journal-no-latex")
    layers.extend(extras)
    layers.append({"figure.figsize": figure_size(journal, columns, aspect)})
    return layers


def use(
    journal: str,
    *,
    columns: float = 1,
    aspect: float = DEFAULT_ASPECT,
    latex: bool = False,
    extras: Sequence[str] = (),
) -> None:
    """Apply the base style and a journal style.

    ``columns`` selects the publisher width (1, 1.5, 2, or 3 when that
    journal defines it). LaTeX is off unless ``latex=True``.
    """
    plt.style.use(_layers(journal, columns=columns, aspect=aspect, latex=latex, extras=extras))


@contextmanager
def context(
    journal: str,
    *,
    columns: float = 1,
    aspect: float = DEFAULT_ASPECT,
    latex: bool = False,
    extras: Sequence[str] = (),
) -> Iterator[None]:
    """Apply a journal style for the duration of a ``with`` block."""
    with plt.style.context(
        _layers(journal, columns=columns, aspect=aspect, latex=latex, extras=extras)
    ):
        yield


def subplots(
    journal: str | None = None,
    *args,
    columns: float = 1,
    aspect: float = DEFAULT_ASPECT,
    latex: bool = False,
    extras: Sequence[str] = (),
    **kwargs,
):
    """Create axes on a figure sized to ``journal``.

    Passing ``journal`` applies that style globally, same as :func:`use`.
    Omit it when :func:`use` was already called; the current
    ``figure.figsize`` is kept unless ``figsize`` is passed.
    """
    figsize = None
    if journal is not None:
        use(journal, columns=columns, aspect=aspect, latex=latex, extras=extras)
        figsize = kwargs.setdefault("figsize", figure_size(journal, columns, aspect))
    fig, ax = plt.subplots(*args, **kwargs)
    # macOS backends quantize the window to integer pixels and write that size
    # back onto the figure. Put the requested inches back so the PDF matches.
    if figsize is not None:
        fig.set_size_inches(figsize, forward=False)
    return fig, ax


def format_panel(journal: str, index: int) -> str:
    """Return the panel tag for ``journal``, such as ``(a)``, ``a``, or ``A``."""
    spec = get(journal)
    letter = chr(ord("a") + index)
    if spec.panel_case == "upper":
        letter = letter.upper()
    return spec.panel_form.format(letter=letter)


def label_panels(
    axes,
    journal: str | None = None,
    *,
    size: float | None = None,
    inside: bool | None = None,
) -> None:
    """Tag each axes with that journal's panel label.

    Physical Review puts ``(a)`` inside the axes, in the upper left. Nature
    and Science put line-plot labels just outside that corner. Pass
    ``inside=True`` for images and heatmaps. Science asks for those labels
    inside the frame.

    Nature uses 8 pt bold upright ``a``. Science uses 10 pt bold ``A``.
    The others use ``(a)``.
    """
    import numpy as np

    flat = np.atleast_1d(axes).ravel()
    spec = get(journal) if journal is not None else None
    if size is None and spec is not None:
        size = spec.panel_label_pt
    if size is None:
        size = plt.rcParams["font.size"]
    if inside is None:
        inside = bool(spec.panel_inside) if spec is not None else False
    for index, ax in enumerate(flat):
        if spec is None:
            label = f"({chr(ord('a') + index)})"
        else:
            label = format_panel(spec.key, index)
        if inside:
            xy, xytext, va = (0.02, 0.98), (0, 0), "top"
        else:
            xy, xytext, va = (0.0, 1.0), (0, 1), "bottom"
        text = ax.annotate(
            label,
            xy=xy,
            xycoords="axes fraction",
            xytext=xytext,
            textcoords="offset points",
            ha="left",
            va=va,
            fontsize=size,
            fontweight="bold",
            annotation_clip=False,
        )
        text.set_in_layout(True)


_LEGEND_LOC = {
    "below": "outside lower center",
    "above": "outside upper center",
}


def _axes_list(axes):
    import numpy as np

    if axes is None:
        return [plt.gca()]
    return list(np.atleast_1d(axes).ravel())


def _row_major(handles, labels, ncol):
    """Reorder so a figure legend reads left to right, then down.

    Matplotlib fills legend columns first. A wrapped legend would otherwise
    read down the first column.
    """
    pairs = list(zip(handles, labels))
    count = len(pairs)
    if ncol <= 1 or count <= ncol:
        return list(handles), list(labels)
    nrow = (count + ncol - 1) // ncol
    slots = [None] * (nrow * ncol)
    for index, pair in enumerate(pairs):
        slots[index] = pair
    ordered = [
        slots[row * ncol + col]
        for col in range(ncol)
        for row in range(nrow)
        if slots[row * ncol + col] is not None
    ]
    reordered_handles, reordered_labels = zip(*ordered)
    return list(reordered_handles), list(reordered_labels)


def _legend_gap_pt(fig, leg, axes) -> float:
    """Points of clear space between the legend entries and the axes."""
    renderer = fig.canvas.get_renderer()
    entries = leg._legend_handle_box.get_window_extent(renderer)
    spine = max(ax.get_window_extent(renderer).y1 for ax in axes)
    return (entries.y0 - spine) * 72 / renderer.dpi


def _open_above_legend(fig, leg, axes) -> None:
    """Leave about one em between an above-legend and the top spine.

    Constrained layout pins an outside legend against that spine. The
    built-in pad is only a couple of points, so the entries sit on the frame.
    """
    from matplotlib.offsetbox import DrawingArea

    target = float(leg._fontsize)
    spacer = DrawingArea(0, 0, 0, 0)
    leg._legend_box.get_children().append(spacer)
    fig.draw_without_rendering()
    gap = _legend_gap_pt(fig, leg, axes)
    spacer.height = min(max(0.0, target - gap), 2 * target)
    if spacer.height <= 0:
        leg._legend_box.get_children().remove(spacer)
    fig.draw_without_rendering()


def _legend_wider_than_figure(fig, leg) -> bool:
    """True when the legend sticks out of the left or right figure edge."""
    fig.draw_without_rendering()
    renderer = fig.canvas.get_renderer()
    tight = leg.get_tightbbox(renderer)
    if tight is None or tight.width <= 0:
        return False
    bbox = fig.transFigure.inverted().transform_bbox(tight)
    return bbox.x0 < -0.005 or bbox.x1 > 1.005


def legend(axes=None, *args, loc="below", ncol=None, **kwargs):
    """Place one legend outside the axes, keeping the axes at full width.

    ``loc="below"`` sits under the x-axis. ``loc="above"`` sits above the
    axes, with about one em between the entries and the top spine. On a
    single axes, a title already set on that axes becomes the legend title,
    so the entries sit directly under the heading.

    Do not place that legend with ``Axes.legend(..., bbox_to_anchor=...)``.
    Constrained layout counts an axes legend as part of the axes. A legend
    wider than the column then shrinks the axes, and ``savefig`` writes a
    sliver or an empty plot. A figure legend only reserves a horizontal band.

    ``ncol`` is the starting column count. It is reduced until the legend
    fits the column width. The default is a single row.
    """
    try:
        outside = _LEGEND_LOC[loc]
    except KeyError:
        known = ", ".join(_LEGEND_LOC)
        raise ValueError(f"loc must be one of {known}.") from None

    axs = _axes_list(axes)
    fig = axs[0].figure
    if args:
        handles = list(args[0])
        labels = list(args[1]) if len(args) > 1 else [h.get_label() for h in handles]
    else:
        handles, labels = [], []
        for ax in axs:
            found_handles, found_labels = ax.get_legend_handles_labels()
            handles.extend(found_handles)
            labels.extend(found_labels)
    for ax in axs:
        existing = ax.get_legend()
        if existing is not None:
            existing.remove()

    if loc == "above" and len(axs) == 1 and "title" not in kwargs:
        title = axs[0].get_title()
        if title:
            kwargs["title"] = title
            axs[0].set_title("")

    if ncol is None:
        ncol = kwargs.pop("ncols", None)
    else:
        kwargs.pop("ncols", None)
    if ncol is None:
        ncol = max(len(labels), 1)

    leg = None
    while True:
        if leg is not None:
            leg.remove()
        row_handles, row_labels = _row_major(handles, labels, ncol)
        leg = fig.legend(row_handles, row_labels, loc=outside, ncol=ncol, **kwargs)
        if ncol <= 1 or not _legend_wider_than_figure(fig, leg):
            break
        ncol -= 1
    if loc == "above":
        _open_above_legend(fig, leg, axs)
    return leg
