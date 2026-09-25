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

LaTeX is off unless the user asks for it and TeX is installed. Then pass `latex=True`. Serif journals use Times; sans-serif journals use Helvetica.

```python
fig, ax = js.subplots("nature", columns=2, latex=True)
```

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
