# journalstyle

論文の列幅に合わせた Matplotlib スタイルです。構成は [SciencePlots](https://github.com/garrettj403/SciencePlots) と同じで、共通の `journal` の上に雑誌ごとの差分を重ねます。

SciencePlots との違いは次の3点です。

- 幅は雑誌が公開している段組寸法から選びます。`columns=1`、`2`、雑誌によっては `1.5` や `3` です。
- LaTeX は既定で使いません。TeX が無い環境でもそのまま描画できます。
- `figure.dpi` は上げません。`savefig.dpi` だけ 600 です。画面上のプレビューが巨大になりません。保存した PDF のインチ寸法が、原稿に挿入する寸法です。`bbox_inches="tight"` は使いません。余白で縮むと、ポイント数が指定より大きくなります。

## インストール

```bash
pip install -e .
```

## 使い方

```python
import journalstyle as js

fig, ax = js.subplots("aps")          # 1段、3.375 in
ax.plot(x, y)
ax.set_xlabel(r"$x$")
fig.savefig("fig.pdf")                # 幅 3.375 in の PDF
```

```python
js.use("ieee", columns=2)
fig, ax = plt.subplots()              # 7.16 in

with js.context("nature", columns=1.5):
    fig, ax = plt.subplots()
```

スタイル名を直接指定することもできます。

```python
import journalstyle  # 読み込むとスタイルが登録される
import matplotlib.pyplot as plt

plt.style.use(["journal", "journal-aps"])
```

`journalstyle` を import してから `plt.style.use` してください。SciencePlots と同じ手順です。

白黒印刷で系列を分けるときは `extras=("journal-bw",)` を渡します。IEEE は色と線種の両方で分かれるようにしてあります。

パネル記号は `js.label_panels(axes, journal="nature")` です。Nature では 8 pt の太字になります。

LaTeX で文字を組む場合だけ `latex=True` にします。このときは書体が Computer Modern になり、スタイル側の Times や Arial は効きません。APS の既定（Times）に近づけるなら LaTeX はオフのままにしてください。STIX が Times の代わりになります。

## 収録している雑誌

| キー | 雑誌 | 幅 | 文字 | 書体 |
| --- | --- | --- | --- | --- |
| `aps` | APS Physical Review | 3.375 in / 5.19 in / 7 in | 8 pt | serif (STIX) |
| `ieee` | IEEE | 3.5 in / 7.16 in | 9 pt | serif (Times) |
| `nature` | Nature | 89 mm / 128 mm / 183 mm | 7 pt | sans (Arial) |
| `aaas` | Science | 57 mm / 121 mm / 184 mm | 7 pt | sans (Helvetica) |
| `acs` | ACS | 3.25 in / 7 in | 7 pt | sans (Arial) |
| `elsevier` | Elsevier | 90 mm / 140 mm / 190 mm | 7 pt | sans (Arial) |
| `rsc` | RSC | 83 mm / 171 mm | 7 pt | sans (Arial) |

高さは幅の 0.75 倍です。`aspect` で変えられます。Science の1段は 5.7 cm しかないので、折れ線は `columns=2` を使ってください。`js.subplots("aaas")` の既定は1段のままです。

数値の出典は `src/journalstyle/specs.py` の各 `source` です。雑誌を足すときは、そこに幅と文字サイズを書き、`styles/journal-<key>.mplstyle` に1段幅の `figure.figsize` と書体を追加してください。高さは幅の 0.75 倍、小数3桁です。

```bash
.venv/bin/python examples/make_gallery.py
.venv/bin/pytest
```

`make_gallery.py` は代表的な図（折れ線・誤差付き散布図・棒・ヒストグラム・ヒートマップ）を LaTeX で全雑誌スタイルに描き、次を書き出します。一覧は `examples/GALLERY.md` です。

- `examples/output/gallery_all.{pdf,png}` — 雑誌×図種別の全体グリッド
- `examples/output/gallery_<plot>.{pdf,png}` — 図種別ごとの横並び比較
- `examples/output/<plot>/<journal>.{pdf,png}` — 雑誌寸法どおりの単独図
- Cursor 用ギャラリー canvas（スクリプトが更新）
