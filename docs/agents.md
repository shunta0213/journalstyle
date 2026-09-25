# Claude Code と Codex に journalstyle を渡す

図を描く手順は skill にまとめてあります。本体は [`.agents/skills/journalstyle/SKILL.md`](../.agents/skills/journalstyle/SKILL.md) です。Claude Code 用の [`.claude/skills/journalstyle`](../.claude/skills/journalstyle) は同じディレクトリへのシンボリックリンクです。

先にパッケージを入れてください。

```bash
pip install git+https://github.com/shunta0213/journalstyle.git
```

## このリポジトリで使う

クローンしたディレクトリで Claude Code または Codex を開くと、それぞれの skill ディレクトリが読まれます。追加のコピーは要りません。

- Claude Code は `.claude/skills/<name>/SKILL.md` を読み、`/journalstyle` で呼び出せます。
- Codex は `.agents/skills/<name>/SKILL.md` を、作業ディレクトリからリポジトリルートまでさかのぼって読みます。`$journalstyle` または `/skills` から選べます。

## ほかのプロジェクトで使う

skill だけをユーザー領域に置きます。パッケージのインストールとは別です。

Claude Code:

```bash
mkdir -p ~/.claude/skills
ln -sfn /path/to/journalstyle/.agents/skills/journalstyle ~/.claude/skills/journalstyle
```

Codex:

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/journalstyle/.agents/skills/journalstyle ~/.agents/skills/journalstyle
```

`/path/to/journalstyle` は、このリポジトリをクローンした場所に置き換えてください。Codex にすぐ出ないときは再起動してください。Codex の `$skill-installer` に、このリポジトリの `.agents/skills/journalstyle` を入れるよう頼む方法もあります。

出典:

- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Codex agent skills](https://developers.openai.com/codex/skills)
