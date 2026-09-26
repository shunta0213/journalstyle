"""Column widths and type sizes taken from publisher figure guides.

Widths are stored in millimeters and converted to inches, which is what
Matplotlib uses for ``figure.figsize``. A figure drawn at these sizes and
included in the manuscript at the same width keeps the point size below.
"""

from __future__ import annotations

from dataclasses import dataclass


def mm(width_mm: float) -> float:
    return width_mm / 25.4


@dataclass(frozen=True)
class Journal:
    key: str
    title: str
    family: str
    fonts: tuple[str, ...]
    font_size: float
    widths_mm: dict[float, float]
    source: str
    notes: str
    axes_linewidth: float = 0.6
    line_linewidth: float = 1.0
    marker_size: float = 4.0
    max_height_mm: float | None = None
    panel_label_pt: float | None = None
    # "{letter}" or "({letter})". letter is already cased.
    panel_form: str = "({letter})"
    panel_case: str = "lower"
    # Physical Review puts (a) inside the axes. Nature and Science keep
    # line-plot labels outside the frame.
    panel_inside: bool = False
    distinguish_in_grayscale: bool = False

    def width_in(self, columns: float) -> float:
        try:
            return mm(self.widths_mm[columns])
        except KeyError:
            choices = ", ".join(_column_label(c) for c in self.widths_mm)
            raise ValueError(
                f"{self.key} has no { _column_label(columns) } width. "
                f"Use one of: {choices}."
            ) from None

    @property
    def columns(self) -> tuple[float, ...]:
        return tuple(self.widths_mm)


def _column_label(columns: float) -> str:
    if columns == int(columns):
        n = int(columns)
        return f"{n} column" if n == 1 else f"{n} columns"
    return f"{columns:g} columns"


# Paul Tol bright, colorblind-safe. https://sronpersonalpages.nl/~pault/
TOL_BRIGHT = (
    "4477AA",
    "EE6677",
    "228833",
    "CCBB44",
    "66CCEE",
    "AA3377",
    "BBBBBB",
)

JOURNALS: dict[str, Journal] = {
    "aps": Journal(
        key="aps",
        title="APS Physical Review",
        family="serif",
        fonts=("STIXGeneral", "Times New Roman", "Times", "DejaVu Serif"),
        font_size=8,
        # APS states 3 3/8 in for one column. Full width is two columns plus
        # the inter-column gap, about 7 in. 1.5 columns is allowed but not
        # given as a separate measure, so it is the midpoint.
        widths_mm={1: 3.375 * 25.4, 1.5: 5.1875 * 25.4, 2: 7.0 * 25.4},
        source="https://journals.aps.org/authors/style-basics",
        notes=(
            "Smallest capitals must be at least 2 mm (~8 pt) and strokes at "
            "least 0.5 pt after reduction. REVTeX defaults to Times; STIX is "
            "the matching face when LaTeX is off. Multipart figures are "
            "cited as Fig. 1(a); put (a), (b) on the panels."
        ),
        max_height_mm=230,
        panel_label_pt=8,
        panel_inside=True,
    ),
    "ieee": Journal(
        key="ieee",
        title="IEEE journals",
        family="serif",
        fonts=("Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"),
        font_size=9,
        widths_mm={1: 3.5 * 25.4, 2: 7.16 * 25.4},
        source=(
            "https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/"
            "create-graphics-for-your-article/resolution-and-size/"
        ),
        notes=(
            "One column is 3.5 in and two columns are 7.16 in. Type should be "
            "about 9–10 pt at full size. Line art should stay readable in "
            "grayscale, so series differ by both color and line style. "
            "Multipart figures use (a), (b) on the panels and in the caption."
        ),
        max_height_mm=8.8 * 25.4,
        distinguish_in_grayscale=True,
    ),
    "nature": Journal(
        key="nature",
        title="Nature",
        family="sans-serif",
        fonts=("Arial", "Helvetica", "DejaVu Sans"),
        font_size=7,
        widths_mm={1: 89, 1.5: 128, 2: 183},
        source="https://www.nature.com/nature/for-authors/final-submission",
        notes=(
            "Sans serif, preferably Helvetica or Arial. Non-panel text is at "
            "most 7 pt; panel labels are 8 pt bold upright a, b, c with no "
            "parentheses. A column-and-a-half may be 120–136 mm; 128 mm is "
            "the midpoint. Strokes should be 0.25–1 pt."
        ),
        axes_linewidth=0.5,
        line_linewidth=0.8,
        marker_size=3.5,
        max_height_mm=247,
        panel_label_pt=8,
        panel_form="{letter}",
    ),
    "aaas": Journal(
        key="aaas",
        title="Science (AAAS)",
        family="sans-serif",
        fonts=("Helvetica", "Arial", "DejaVu Sans"),
        font_size=7,
        widths_mm={1: 57, 2: 121, 3: 184},
        source=(
            "https://www.science.org/content/page/instructions-preparing-initial-manuscript"
        ),
        notes=(
            "Printed widths are usually 5.7 cm, 12.1 cm, or 18.4 cm. Lettering "
            "should be about 7 pt and no smaller than 5 pt. Helvetica is preferred. "
            "Most line plots need the 2-column width; 1 column is narrow. "
            "Multipart panels are uppercase A, B at 10 pt bold in the upper left."
        ),
        max_height_mm=230,
        panel_label_pt=10,
        panel_form="{letter}",
        panel_case="upper",
    ),
    "acs": Journal(
        key="acs",
        title="ACS journals",
        family="sans-serif",
        fonts=("Arial", "Helvetica", "DejaVu Sans"),
        font_size=7,
        widths_mm={1: 3.25 * 25.4, 2: 7.0 * 25.4},
        source="https://pubs.acs.org/page/4authors/submission/graphics.html",
        notes=(
            "Article graphics are commonly produced at 3.25 in (one column) or "
            "7 in (two columns). Confirm the target journal; TOC graphics use "
            "a different box. Type should stay at or above about 6–7 pt."
        ),
    ),
    "elsevier": Journal(
        key="elsevier",
        title="Elsevier",
        family="sans-serif",
        fonts=("Arial", "Helvetica", "DejaVu Sans"),
        font_size=7,
        widths_mm={1: 90, 1.5: 140, 2: 190},
        source="https://www.elsevier.com/researcher/author/policies-and-guidelines/artwork-and-media-instructions",
        notes=(
            "Single column 90 mm, 1.5 columns 140 mm, double column 190 mm. "
            "Body lettering 7 pt, and subscripts no smaller than 6 pt."
        ),
    ),
    "rsc": Journal(
        key="rsc",
        title="RSC journals",
        family="sans-serif",
        fonts=("Arial", "Helvetica", "DejaVu Sans"),
        font_size=7,
        widths_mm={1: 83, 2: 171},
        source="https://www.rsc.org/journals-books-databases/journal-authors-reviewers/prepare-your-article/",
        notes=(
            "Standard RSC column widths are 8.3 cm and 17.1 cm. Minimum type "
            "size is 7 pt in Arial or Helvetica."
        ),
    ),
}
