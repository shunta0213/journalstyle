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
    """Add the bundled stylesheets to ``plt.style.library``."""
    styles_path = Path(__file__).resolve().parent / "styles"
    library = plt.style.library
    for path in styles_path.glob("*.mplstyle"):
        params = rc_params_from_file(path, use_default_template=False)
        library.setdefault(path.stem, {}).update(params)
    try:
        available = plt.style.available
    except AttributeError:  # matplotlib < 3.11
        available = plt.style.core.available
    available[:] = sorted(library.keys())


_register_styles()


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
    get(journal)
    layers: list = ["journal", f"journal-{journal}"]
    layers.append("journal-latex" if latex else "journal-no-latex")
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


def label_panels(axes, journal: str | None = None, *, size: float | None = None) -> None:
    """Tag axes ``(a)``, ``(b)``, ... in the upper left.

    Nature specifies 8 pt bold panel labels. Other journals use the current
    font size in bold.
    """
    import numpy as np

    flat = np.atleast_1d(axes).ravel()
    if size is None and journal is not None:
        size = get(journal).panel_label_pt
    if size is None:
        size = plt.rcParams["font.size"]
    for index, ax in enumerate(flat):
        ax.text(
            0.02,
            0.98,
            f"({chr(ord('a') + index)})",
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=size,
            fontweight="bold",
        )
