"""Write one PDF per journal into examples/output."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import journalstyle as js

OUT = Path(__file__).resolve().parent / "output"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    x = np.linspace(0, 2 * np.pi, 200)
    for key in js.journals():
        columns = 2 if key == "aaas" else 1
        fig, ax = js.subplots(key, columns=columns)
        for shift in (0, 0.6, 1.2):
            ax.plot(x, np.sin(x + shift), label=rf"$\sin(x+{shift})$")
        spec = js.get(key)
        ax.set_xlabel(r"$x$")
        ax.set_ylabel(r"$y$")
        ax.legend(title=spec.title)
        fig.savefig(OUT / f"{key}.pdf")
        fig.savefig(OUT / f"{key}.png", dpi=150)
        plt.close(fig)
        print(f"{key}: {spec.width_in(columns):.3f} in, {spec.font_size:g} pt")


if __name__ == "__main__":
    main()
