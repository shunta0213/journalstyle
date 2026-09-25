"""Render every journal style on representative paper figure types.

Writes:
  examples/output/<plot>/<journal>.{pdf,png}   — one panel at journal size
  examples/output/gallery_<plot>.{pdf,png}     — all journals side by side
  examples/output/gallery_all.{pdf,png}        — full grid (journals × plots)
  examples/output/gallery_manifest.json        — paths + base64 for the canvas
  examples/GALLERY.md                          — markdown catalog of the PNGs
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

import journalstyle as js

OUT = Path(__file__).resolve().parent / "output"
RNG = np.random.default_rng(42)

# Science 1-column is only 5.7 cm; line plots need two columns.
COLUMNS = {key: (2 if key == "aaas" else 1) for key in js.journals()}

PLOT_TYPES = ("line", "scatter", "bar", "histogram", "heatmap")

PLOT_LABELS = {
    "line": "折れ線（複数系列）",
    "scatter": "散布図（誤差棒）",
    "bar": "グループ棒グラフ",
    "histogram": "ヒストグラム",
    "heatmap": "ヒートマップ",
}


def _draw_line(ax) -> None:
    x = np.linspace(0, 2 * np.pi, 200)
    for shift, label in (
        (0.0, r"$\sin x$"),
        (0.7, r"$\sin(x+0.7)$"),
        (1.4, r"$\sin(x+1.4)$"),
    ):
        ax.plot(x, np.sin(x + shift), label=label)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="upper right", frameon=False)


def _draw_scatter(ax) -> None:
    n = 18
    x = np.linspace(0.5, 5.0, n)
    for slope, label in ((0.8, "A"), (1.2, "B"), (1.6, "C")):
        y = slope * x + 0.4 * RNG.standard_normal(n)
        yerr = 0.25 + 0.1 * RNG.random(n)
        ax.errorbar(
            x,
            y,
            yerr=yerr,
            fmt="o",
            capsize=2,
            markersize=3.5,
            label=label,
        )
    ax.set_xlabel(r"$t$ (s)")
    ax.set_ylabel(r"$I$ (a.u.)")
    ax.legend(loc="upper left", frameon=False, ncol=3)


def _draw_bar(ax) -> None:
    categories = ["A", "B", "C", "D"]
    x = np.arange(len(categories))
    width = 0.28
    series = {
        "run 1": np.array([2.1, 3.4, 2.8, 4.0]),
        "run 2": np.array([1.8, 3.0, 3.2, 3.6]),
        "run 3": np.array([2.4, 2.9, 2.5, 3.8]),
    }
    for i, (name, values) in enumerate(series.items()):
        ax.bar(x + (i - 1) * width, values, width=width, label=name)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_xlabel("sample")
    ax.set_ylabel(r"$y$")
    ax.legend(loc="upper left", frameon=False, ncol=3)


def _draw_heatmap(ax) -> None:
    n = 64
    x = np.linspace(-2.0, 2.0, n)
    y = np.linspace(-1.5, 1.5, n)
    xx, yy = np.meshgrid(x, y)
    zz = np.exp(-(xx**2) / 2.0 - yy**2) * np.cos(2 * np.pi * xx)
    image = ax.imshow(
        zz,
        extent=(x[0], x[-1], y[0], y[-1]),
        origin="lower",
        aspect="auto",
        cmap="cividis",
    )
    colorbar = ax.figure.colorbar(image, ax=ax, fraction=0.046, pad=0.03)
    colorbar.set_label(r"$z$")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")


def _draw_histogram(ax) -> None:
    for mean, label in ((0.0, r"$\mu=0$"), (1.2, r"$\mu=1.2$"), (2.4, r"$\mu=2.4$")):
        data = RNG.normal(mean, 0.7, 400)
        ax.hist(data, bins=24, range=(-2.5, 5.0), histtype="step", density=True, label=label)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel("density")
    ax.legend(loc="upper right", frameon=False)


DRAWERS = {
    "line": _draw_line,
    "scatter": _draw_scatter,
    "bar": _draw_bar,
    "histogram": _draw_histogram,
    "heatmap": _draw_heatmap,
}


def _panel_title(journal: str) -> str:
    spec = js.get(journal)
    cols = COLUMNS[journal]
    col_label = f"{cols:g} col" if cols != int(cols) else f"{int(cols)} col"
    return f"{spec.title} · {col_label} · {spec.font_size:g} pt"


def render_single(journal: str, plot: str) -> tuple[Path, Path]:
    """Draw one journal-sized figure and save PDF + PNG."""
    columns = COLUMNS[journal]
    fig, ax = js.subplots(journal, columns=columns, latex=True)
    DRAWERS[plot](ax)
    ax.set_title(_panel_title(journal), pad=4)
    plot_dir = OUT / plot
    plot_dir.mkdir(parents=True, exist_ok=True)
    pdf = plot_dir / f"{journal}.pdf"
    png = plot_dir / f"{journal}.png"
    fig.savefig(pdf)
    fig.savefig(png, dpi=200)
    plt.close(fig)
    return pdf, png


def render_plot_row(plot: str) -> tuple[Path, Path]:
    """All journals for one plot type on a shared comparison figure."""
    journals = js.journals()
    n = len(journals)
    # Use a neutral canvas; each axes inherits style via context + redraw.
    fig_w = sum(js.figure_size(j, COLUMNS[j])[0] for j in journals) + 0.4 * (n - 1)
    fig_h = max(js.figure_size(j, COLUMNS[j])[1] for j in journals) + 0.55
    fig = plt.figure(figsize=(fig_w, fig_h), layout=None)
    widths = [js.figure_size(j, COLUMNS[j])[0] for j in journals]
    gs = GridSpec(1, n, figure=fig, width_ratios=widths, wspace=0.35)

    for i, journal in enumerate(journals):
        with js.context(journal, columns=COLUMNS[journal], latex=True):
            ax = fig.add_subplot(gs[0, i])
            DRAWERS[plot](ax)
            ax.set_title(_panel_title(journal), fontsize=plt.rcParams["font.size"], pad=4)

    pdf = OUT / f"gallery_{plot}.pdf"
    png = OUT / f"gallery_{plot}.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(png, dpi=160, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return pdf, png


def render_full_grid() -> tuple[Path, Path]:
    """Journals as columns, plot types as rows."""
    journals = js.journals()
    plots = list(PLOT_TYPES)
    n_col, n_row = len(journals), len(plots)
    col_w = [js.figure_size(j, COLUMNS[j])[0] for j in journals]
    row_h = 2.4
    fig = plt.figure(
        figsize=(sum(col_w) + 0.35 * (n_col - 1), row_h * n_row + 0.45 * n_row),
        layout=None,
    )
    gs = GridSpec(
        n_row,
        n_col,
        figure=fig,
        width_ratios=col_w,
        height_ratios=[1] * n_row,
        wspace=0.4,
        hspace=0.55,
    )

    for r, plot in enumerate(plots):
        for c, journal in enumerate(journals):
            with js.context(journal, columns=COLUMNS[journal], latex=True):
                ax = fig.add_subplot(gs[r, c])
                DRAWERS[plot](ax)
                title = f"{plot} · {_panel_title(journal)}"
                ax.set_title(title, fontsize=plt.rcParams["font.size"], pad=3)

    pdf = OUT / "gallery_all.pdf"
    png = OUT / "gallery_all.png"
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.1)
    fig.savefig(png, dpi=140, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return pdf, png


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def write_manifest(
    singles: dict[str, dict[str, dict[str, str]]],
    rows: dict[str, dict[str, str]],
    full: dict[str, str],
) -> Path:
    """Embed PNG base64 so the canvas can show figures without fetching files."""
    payload = {
        "journals": [
            {
                "key": key,
                "title": js.get(key).title,
                "columns": COLUMNS[key],
                "width_in": round(js.figure_size(key, COLUMNS[key])[0], 3),
                "font_size": js.get(key).font_size,
                "family": js.get(key).family,
                "source": js.get(key).source,
            }
            for key in js.journals()
        ],
        "plot_types": list(PLOT_TYPES),
        "singles": {
            plot: {
                journal: {
                    "pdf": paths["pdf"],
                    "png": paths["png"],
                    "png_b64": _b64(Path(paths["png"])),
                }
                for journal, paths in by_journal.items()
            }
            for plot, by_journal in singles.items()
        },
        "rows": {
            plot: {
                "pdf": paths["pdf"],
                "png": paths["png"],
                "png_b64": _b64(Path(paths["png"])),
            }
            for plot, paths in rows.items()
        },
        "full": {
            "pdf": full["pdf"],
            "png": full["png"],
            "png_b64": _b64(Path(full["png"])),
        },
        "output_dir": str(OUT),
    }
    path = OUT / "gallery_manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def write_gallery_markdown() -> Path:
    """Catalog every rendered PNG so the preview is a single markdown file."""
    lines = [
        "# journalstyle 見本",
        "",
        "各パネルは雑誌スタイルそのもので描いています。幅と文字サイズは出版社の規定です。Science は 2 段、文字は LaTeX です。セリフは Times、サンセリフは Helvetica です。ヒートマップのカラーマップは cividis です。",
        "",
        "再生成: `.venv/bin/python examples/make_gallery.py`",
        "",
        "## インストール",
        "",
        "```bash",
        "pip install git+https://github.com/shunta0213/journalstyle.git",
        "```",
        "",
        "```python",
        "import journalstyle as js",
        "",
        'fig, ax = js.subplots("aps")  # 1段、3.375 in',
        "ax.plot(x, y)",
        'fig.savefig("fig.pdf")',
        "```",
        "",
        "LaTeX で文字を組むときは `js.subplots(\"aps\", latex=True)` です。TeX が入っていない環境では `latex=False`（既定）のままにしてください。",
        "",
        "## 規定",
        "",
        "| key | 雑誌 | 段 | 幅 (in) | 文字 | 書体 |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for key in js.journals():
        spec = js.get(key)
        width = js.figure_size(key, COLUMNS[key])[0]
        lines.append(
            f"| `{key}` | {spec.title} | {COLUMNS[key]:g} | {width:.3f} | {spec.font_size:g} pt | {spec.family} |"
        )
    lines.append("")
    for plot in PLOT_TYPES:
        lines.extend(
            [
                f"## {PLOT_LABELS[plot]}",
                "",
                f"![{PLOT_LABELS[plot]} · 全雑誌](output/gallery_{plot}.png)",
                "",
            ]
        )
        for key in js.journals():
            spec = js.get(key)
            lines.extend(
                [
                    f"### {spec.title} (`{key}`)",
                    "",
                    f"![{spec.title} {PLOT_LABELS[plot]}](output/{plot}/{key}.png)",
                    "",
                ]
            )
    path = Path(__file__).resolve().parent / "GALLERY.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    singles: dict[str, dict[str, dict[str, str]]] = {}
    rows: dict[str, dict[str, str]] = {}

    for plot in PLOT_TYPES:
        singles[plot] = {}
        for journal in js.journals():
            pdf, png = render_single(journal, plot)
            singles[plot][journal] = {"pdf": str(pdf), "png": str(png)}
            print(f"{plot}/{journal}: {png.name}")
        row_pdf, row_png = render_plot_row(plot)
        rows[plot] = {"pdf": str(row_pdf), "png": str(row_png)}
        print(f"row {plot}: {row_png}")

    full_pdf, full_png = render_full_grid()
    full = {"pdf": str(full_pdf), "png": str(full_png)}
    print(f"full grid: {full_png}")

    manifest = write_manifest(singles, rows, full)
    print(f"manifest: {manifest}")

    catalog = write_gallery_markdown()
    print(f"catalog: {catalog}")

    # Emit canvas source with embedded images.
    emit_canvas(manifest)


def emit_canvas(manifest_path: Path) -> Path:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    canvas_path = Path(
        "/Users/shuntaide/.cursor/projects/"
        "Users-shuntaide-Documents-research-02-journal-research-graph-style/"
        "canvases/journal-style-gallery.canvas.tsx"
    )
    canvas_path.parent.mkdir(parents=True, exist_ok=True)

    # Keep the TSX readable: one data URL per plot-row comparison (compact).
    # Full grid is also included.
    journals_json = json.dumps(data["journals"], indent=2)
    rows_b64 = {plot: data["rows"][plot]["png_b64"] for plot in data["plot_types"]}
    full_b64 = data["full"]["png_b64"]
    out_dir = data["output_dir"]

    # Escape for template literal safety — we use JSON.stringify via python.
    rows_literal = json.dumps(rows_b64)
    full_literal = json.dumps(full_b64)
    out_literal = json.dumps(out_dir)
    plots_literal = json.dumps(data["plot_types"])

    source = f'''/**
 * Auto-generated by examples/make_gallery.py — do not edit by hand.
 * Re-run: .venv/bin/python examples/make_gallery.py
 */
import {{
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useHostTheme,
}} from "cursor/canvas";

const JOURNALS = {journals_json} as const;

const PLOT_TYPES: string[] = {plots_literal};

const ROW_PNG_B64: Record<string, string> = {rows_literal};

const FULL_PNG_B64: string = {full_literal};

const OUTPUT_DIR: string = {out_literal};

const PLOT_LABELS: Record<string, string> = {json.dumps(PLOT_LABELS, ensure_ascii=False)};

export default function JournalStyleGallery() {{
  const theme = useHostTheme();

  return (
    <Stack gap={{20}} style={{{{ padding: 20 }}}}>
      <Stack gap={{6}}>
        <H1>journalstyle gallery</H1>
        <Text tone="secondary">
          Each panel is drawn with the real Matplotlib style for that journal
          (column width, type size, and face). Science uses 2 columns. Text is
          set with LaTeX (Times for serif, Helvetica for sans). Source PNGs
          also live under examples/output/.
        </Text>
        <Text tone="tertiary" size="small">
          Output: {{OUTPUT_DIR}}
        </Text>
      </Stack>

      <Grid columns={{4}} gap={{12}}>
        <Stat value={{String(JOURNALS.length)}} label="Journals" />
        <Stat value={{String(PLOT_TYPES.length)}} label="Plot types" />
        <Stat value="1–2 col" label="Typical width" />
        <Stat value="7–9 pt" label="Type size" />
      </Grid>

      <H2>Journal specs</H2>
      <Table
        headers={{["Key", "Journal", "Columns", "Width (in)", "Type", "Family"]}}
        columnAlign={{["left", "left", "right", "right", "right", "left"]}}
        rows={{JOURNALS.map((j) => [
          j.key,
          j.title,
          String(j.columns),
          j.width_in.toFixed(3),
          `${{j.font_size}} pt`,
          j.family,
        ])}}
        striped
      />

      <H2>All journals × all plot types</H2>
      <Text tone="secondary" size="small">
        Rows are plot types; columns are journals (aps, ieee, nature, aaas, acs,
        elsevier, rsc). Open gallery_all.pdf for vector output.
      </Text>
      <Card>
        <CardHeader>gallery_all.png</CardHeader>
        <CardBody style={{{{ padding: 8 }}}}>
          <img
            src={{`data:image/png;base64,${{FULL_PNG_B64}}`}}
            alt="Full journal × plot-type gallery"
            style={{{{
              width: "100%",
              height: "auto",
              display: "block",
              background: theme.fill.tertiary,
            }}}}
          />
        </CardBody>
      </Card>

      <H2>By plot type</H2>
      {{PLOT_TYPES.map((plot) => (
        <Stack key={{plot}} gap={{8}}>
          <Row gap={{8}} align="center">
            <H3>{{PLOT_LABELS[plot] ?? plot}}</H3>
            <Pill tone="neutral" size="sm">
              {{plot}}
            </Pill>
          </Row>
          <Card>
            <CardHeader>gallery_{{plot}}.png</CardHeader>
            <CardBody style={{{{ padding: 8 }}}}>
              <img
                src={{`data:image/png;base64,${{ROW_PNG_B64[plot]}}`}}
                alt={{`${{plot}} across all journals`}}
                style={{{{
                  width: "100%",
                  height: "auto",
                  display: "block",
                  background: theme.fill.tertiary,
                }}}}
              />
            </CardBody>
          </Card>
          <Divider />
        </Stack>
      ))}}
    </Stack>
  );
}}
'''
    canvas_path.write_text(source, encoding="utf-8")
    print(f"canvas: {canvas_path}")
    return canvas_path


if __name__ == "__main__":
    main()
