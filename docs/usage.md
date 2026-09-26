# journalstyle の使い方

`import journalstyle` したあと、雑誌名を `plt.style.use` に渡します。共通の体裁（内向き目盛り、余白、保存 600 dpi）は `journal-aps` などの中に入っています。

```python
import matplotlib.pyplot as plt
import journalstyle

plt.style.use("journal-aps")
```

LaTeX を使うときは、リストの最後に `latex` を足します。セリフかサンセリフかは雑誌名から選ばれます。APS と IEEE は Times、それ以外は Helvetica です。

```python
plt.style.use(["journal-aps", "latex"])
plt.style.use(["journal-nature", "latex"])
```

TeX が入っていない環境では `latex` を付けないでください。

## 1段の図

雑誌スタイルに書いてある `figure.figsize` は1段幅です。`plt.subplots()` はそれを使います。

```python
import matplotlib.pyplot as plt
import journalstyle

plt.style.use(["journal-aps", "latex"])

fig, ax = plt.subplots()          # 3.375 in × 2.531 in、8 pt
ax.plot(x, y)
ax.set_xlabel(r"$x$")
ax.set_ylabel(r"$y$")
fig.savefig("fig.pdf")            # bbox_inches="tight" は付けない
```

`bbox_inches="tight"` で余白を切ると、PDF の幅が段幅より小さくなります。原稿で `\columnwidth` に引き伸ばすと、ポイント数が指定より大きくなります。

凡例を軸の外に置くときは `js.legend` を使います。`loc="above"` はタイトルの直下、`loc="below"` は横軸の下です。

```python
ax.set_title("Head")
js.legend(ax, loc="above")
# js.legend(ax, loc="below")
fig.savefig("fig.pdf")
```

`ax.legend(..., bbox_to_anchor=...)` で軸の外に出すと、constrained layout が凡例を軸の一部として数えます。凡例が段幅より広いと軸が潰れて、`savefig` の図が細い帯か空白になります。`js.legend` は図の凡例なので、高さだけを空けて軸の幅は残します。列に収まらないときは行を折り返します。

保存時の解像度は `savefig.dpi` の 600 です。画面表示用の `figure.dpi` は上げていません。

## 2段、1.5段

段数はスタイルファイルには入っていません。`figsize` を自分で渡すか、`journalstyle.figure_size` を使います。

```python
import journalstyle as js

width, height = js.figure_size("aps", columns=2, aspect=0.6)
fig, ax = plt.subplots(figsize=(width, height))
```

`aspect` は図全体の高さ / 幅です。既定は 0.75 です。

| キー | 選べる段 | 1段の幅 |
| --- | --- | --- |
| `aps` | 1, 1.5, 2 | 3.375 in |
| `ieee` | 1, 2 | 3.5 in |
| `nature` | 1, 1.5, 2 | 89 mm |
| `aaas` | 1, 2, 3 | 57 mm |
| `acs` | 1, 2 | 3.25 in |
| `elsevier` | 1, 1.5, 2 | 90 mm |
| `rsc` | 1, 2 | 83 mm |

Science（`aaas`）の1段は 5.7 cm しかありません。折れ線を1段に入れると読みにくくなります。広い図は `columns=2`（12.1 cm）か `columns=3`（18.4 cm）にしてください。

一時的にだけ適用するときは `plt.style.context` です。

```python
with plt.style.context(["journal-nature", "latex"]):
    fig, ax = plt.subplots()
```

## LaTeX

`latex` は直前の雑誌に合わせて中身を切り替えます。自分で `journal-latex` と `journal-latex-sans` を選ぶ必要はありません。

```python
plt.style.use(["journal-ieee", "latex"])    # Times
plt.style.use(["journal-nature", "latex"])  # Helvetica
```

`journalstyle.use("aps", latex=True)` も同じです。`latex=False`（既定）のときは LaTeX を使いません。

数式はいつも `r"$...$"` で書きます。LaTeX がオンのとき、この文字列は TeX に渡されます。オフのときは Matplotlib の mathtext です。

## 複数パネルの記号

記号は図の中の (a) や a や A です。

```python
import journalstyle as js

plt.style.use(["journal-aps", "latex"])
width, height = js.figure_size("aps", columns=1, aspect=0.72)
fig, axes = plt.subplots(1, 2, figsize=(width, height))
axes[0].plot(x, y1)
axes[1].plot(x, y2)
js.label_panels(axes, journal="aps")
fig.savefig("panels.pdf")
```

`label_panels` は雑誌ごとの形と位置を使います。

| 雑誌 | 記号 | 折れ線での位置 |
| --- | --- | --- |
| APS | (a), (b)、8 pt 太字 | 軸の内側、左上。データと重ならない角 |
| IEEE, ACS, Elsevier, RSC | (a), (b)、本文と同じ大きさ | 軸の外、左上 |
| Nature | a, b。括弧なし、8 pt の立体太字 | 軸の外、左上 |
| Science | A, B。10 pt 太字 | 軸の外、左上。画像は `inside=True` で枠の内側 |

画像とヒートマップは枠の外に出すと余白だけが増えます。Science も画像は枠内を指定しています。

```python
js.label_panels(axes, journal="aaas", inside=True)
```

## そのほかのスタイル

白黒印刷で系列を線種でも分けるとき:

```python
plt.style.use(["journal-aps", "latex", "journal-bw"])
```

IEEE の `journal-ieee` は、最初から色と線種の両方を変えます。`journal-bw` はさらに色をグレーにします。

## スタイル一覧

| 名前 | 役割 |
| --- | --- |
| `journal-aps` `journal-ieee` `journal-nature` `journal-aaas` `journal-acs` `journal-elsevier` `journal-rsc` | 雑誌。共通設定込み。figsize は1段 |
| `latex` | その雑誌に合う LaTeX。リストの最後に足す |
| `journal-bw` | グレー＋線種 |
