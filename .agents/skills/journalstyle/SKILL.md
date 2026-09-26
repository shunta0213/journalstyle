---
name: journalstyle
description: >
  Draw Matplotlib figures at publisher column widths for APS, IEEE, Nature,
  Science (AAAS), ACS, Elsevier, and RSC. Use this skill whenever the user
  asks for a paper figure, journal figure, matplotlib style, 論文の図,
  グラフ, APS, IEEE, Nature, Science, ACS, Elsevier, or RSC, even if they
  do not name the journalstyle package.
---

# journalstyle

Matplotlib styles sized to journal column widths. The package must be installed first:

```bash
pip install git+https://github.com/shunta0213/journalstyle.git
```

## Draw a figure

```python
import journalstyle as js

fig, ax = js.subplots("aps")  # 1 column, 3.375 in, 8 pt
ax.plot(x, y)
ax.set_xlabel(r"$x$")
fig.savefig("fig.pdf")  # page size is the print size
```

Do not pass `bbox_inches="tight"`. Cropping changes the width, so the point size no longer matches the journal.

Place a legend outside the axes with `js.legend`, not `Axes.legend(..., bbox_to_anchor=...)`. Constrained layout treats an axes legend as part of the axes, so a legend wider than the column shrinks the axes and `savefig` writes a sliver or a blank plot. `loc="above"` sits under the axes title. `loc="below"` sits under the x-axis. Entries wrap to the column width.

```python
ax.set_title("Head")
js.legend(ax, loc="above")
fig.savefig("fig.pdf")
```

LaTeX is off unless the user asks for it and TeX is installed. Then pass `plt.style.use(["journal-aps", "latex"])` or `["journal-nature", "latex"]`. The single name `latex` picks Times or Helvetica from the journal. See `docs/usage.md`. Keep subfigure prose in the manuscript `\caption`, and put only the panel tag on the figure.

```python
fig, ax = js.subplots("nature", columns=2, latex=True)
```

## Multipanel figures

Size the whole figure, not each panel. Two panels side by side in one column:

```python
fig, axes = js.subplots("aps", 1, 2, columns=1, aspect=0.72)
js.label_panels(axes, journal="aps")
fig.savefig("fig.pdf")
```

`label_panels` follows the journal: `(a)` for APS, IEEE, ACS, Elsevier, and RSC; upright bold `a` at 8 pt for Nature; bold `A` at 10 pt for Science. Physical Review places `(a)` inside the axes at the upper left, in a corner clear of the data. Nature and Science place line-plot labels just outside that corner. Widen the whole figure with `columns=2` when the pair should span two columns. For images and heatmaps pass `inside=True`. For Science, prefer `columns=2` or `columns=3` rather than one column when the panels are wide.

## Journals

| key | columns | single width | type |
| --- | --- | --- | --- |
| `aps` | 1, 1.5, 2 | 3.375 in | 8 pt serif |
| `ieee` | 1, 2 | 3.5 in | 9 pt serif |
| `nature` | 1, 1.5, 2 | 89 mm | 7 pt sans |
| `aaas` | 1, 2, 3 | 57 mm | 7 pt sans |
| `acs` | 1, 2 | 3.25 in | 7 pt sans |
| `elsevier` | 1, 1.5, 2 | 90 mm | 7 pt sans |
| `rsc` | 1, 2 | 83 mm | 7 pt sans |

Science (`aaas`) one-column figures are only 5.7 cm. Use `columns=2` for line plots unless the user wants a narrow panel.

Grayscale-safe series: `js.use("aps", extras=("journal-bw",))`. IEEE already varies both color and linestyle.

`js.journals()` lists the keys. `js.get("aps")` returns the written specification and its source URL.
