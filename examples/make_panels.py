"""Two-panel figures for every journal, plus examples/PANELS.md."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import journalstyle as js

OUT = Path(__file__).resolve().parent / "output" / "panels"
DOC = Path(__file__).resolve().parent / "PANELS.md"
# One journal column, two panels side by side.
COLUMNS = 1
ASPECT = 0.72


def _draw(ax, phase: float, *, labeled: bool = False) -> None:
    x = np.linspace(0, 2 * np.pi, 200)
    # Stay clear of the upper-left corner, where an inside label sits.
    ax.plot(
        x,
        0.65 * np.sin(x + phase) - 0.2,
        label=r"$\sin$" if labeled else None,
    )
    ax.plot(
        x,
        0.65 * np.cos(x + phase) - 0.35,
        label=r"$\cos$" if labeled else None,
    )
    ax.set_ylim(-1.35, 1.15)
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")


def render(journal: str) -> Path:
    fig, axes = js.subplots(
        journal, 1, 2, columns=COLUMNS, aspect=ASPECT, latex=True
    )
    _draw(axes[0], 0.0)
    _draw(axes[1], 0.6)
    js.label_panels(axes, journal=journal)
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / f"{journal}.png"
    pdf = OUT / f"{journal}.pdf"
    fig.savefig(pdf)
    fig.savefig(png, dpi=200)
    plt.close(fig)
    return png


def render_legend() -> Path:
    """One shared legend above both panels. Labels come from the first axes."""
    fig, axes = js.subplots(
        "aps", 1, 2, columns=COLUMNS, aspect=ASPECT, latex=True
    )
    _draw(axes[0], 0.0, labeled=True)
    _draw(axes[1], 0.6)
    js.label_panels(axes, journal="aps")
    js.legend(axes[0], loc="above")
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / "aps-legend.png"
    fig.savefig(OUT / "aps-legend.pdf")
    fig.savefig(png, dpi=200)
    plt.close(fig)
    return png


def write_doc(paths: dict[str, Path]) -> None:
    lines = [
        "# 複数パネル",
        "",
        "この見本は 1 段幅で、パネルは横に 2 枚です。図全体を 2 段にするときは `columns=2` にします。",
        "",
        "Physical Review の (a) は軸の内側、左上です。空いている角に置きます。Nature と Science の折れ線は軸の外、左上です。画像とヒートマップは `inside=True` で枠の内側に入れます。",
        "",
        "| 雑誌 | パネル記号 | サイズ | 折れ線での位置 |",
        "| --- | --- | --- | --- |",
        "| APS | (a), (b) | 8 pt | 軸の内側、左上 |",
        "| IEEE, ACS, Elsevier, RSC | (a), (b) | 本文と同じ | 軸の外、左上 |",
        "| Nature | a, b（括弧なし、立体の太字） | 8 pt | 軸の外、左上 |",
        "| Science | A, B（大文字の太字） | 10 pt | 軸の外、左上。画像は枠内 |",
        "",
        "```python",
        "import journalstyle as js",
        "",
        'fig, axes = js.subplots("aps", 1, 2, columns=1, aspect=0.72)',
        "axes[0].plot(x, y1)",
        "axes[1].plot(x, y2)",
        'js.label_panels(axes, journal="aps")  # (a) inside the axes',
        'fig.savefig("fig.pdf")',
        "```",
        "",
        "`aspect` は図全体の高さ / 幅です。",
        "",
        "## 凡例",
        "",
        "系列の名前は `js.legend` でパネルの外に置きます。`loc=\"above\"` はパネルの上、`loc=\"below\"` は横軸の下です。2 枚で線種が同じときは、ラベルを付けた側だけを渡します。",
        "",
        "```python",
        'fig, axes = js.subplots("aps", 1, 2, columns=1, aspect=0.72)',
        'axes[0].plot(x, y1, label=r"$\\sin$")',
        'axes[0].plot(x, y2, label=r"$\\cos$")',
        "axes[1].plot(x, y3)",
        "axes[1].plot(x, y4)",
        'js.label_panels(axes, journal="aps")',
        'js.legend(axes[0], loc="above")',
        'fig.savefig("fig.pdf")',
        "```",
        "",
        "![APS two panels with a legend above](output/panels/aps-legend.png)",
        "",
    ]
    for key, path in paths.items():
        spec = js.get(key)
        tag = js.format_panel(key, 0)
        lines.extend(
            [
                f"## {spec.title} (`{key}`)",
                "",
                f"記号 `{tag}`、図の幅 {js.figure_size(key, COLUMNS)[0]:.3f} in（{COLUMNS:g} 段）。",
                "",
                f"![{spec.title} two panels](output/panels/{path.name})",
                "",
            ]
        )
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    paths = {}
    for key in js.journals():
        png = render(key)
        paths[key] = png
        print(png)
    print(render_legend())
    write_doc(paths)
    print(DOC)


if __name__ == "__main__":
    main()
