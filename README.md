# 🎨 ASCII Art Maker

**ASCII Art Maker** は、画像を文字だけで描画する ASCIIアート に変換する Python × Gradio アプリです。

画像をアップロードし、幅や文字セットを調整するだけで、スタイリッシュな文字アートを簡単に生成できます。

---

## ✨ 主な機能

- 画像を ASCII アートへリアルタイム変換
- 文字幅（横の文字数）を自由に変更
- 使用する文字セットをカスタマイズ可能
- 明暗（ポジ/ネガ）の反転
- コントラスト調整
- フォントの縦長補正（vertical scale）
- 生成された ASCII アートはテキストとしてコピー可能

---

## 🖥️ デモ画面（イメージ）

```
+----------------+    +-------------------------------+
| 画像アップロード |    | ASCIIアート出力                |
| [ファイル選択]   | => | @@@%%%%#####++++===--...      |
| 文字幅: 80      |    | @@@%%%%#####++++===--...      |
| 文字セット: @%#* |    | ...                           |
+----------------+    +-------------------------------+
```

---

## 🚀 インストール方法

本プロジェクトは Python の仮想環境管理ツール（例: venv や pipenv）で動作します。ここでは汎用的な手順を示します。

### 1. プロジェクト取得

```bash
git clone https://github.com/nagata-minoru/ascii_art_maker.git
cd ascii_art_maker
```

### 2. 依存パッケージのインストール（例: pip を使用する場合）

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

※ uv を使う場合はプロジェクトで uv が定義されていることを確認してください。
代替例:
```bash
uv sync
uv add gradio pillow numpy
```

---

▶️ 起動方法

```bash
uv run python app.py    # uv 使用時
# または
python app.py           # 仮想環境で実行
```

実行後、ブラウザで以下にアクセスします：

http://127.0.0.1:7860

---

🛠️ 使用ライブラリ
- Gradio – Web UI フレームワーク
- Pillow (PIL) – 画像の読み込み・処理
- NumPy – 数値計算
- uv – （プロジェクトで使用する場合）仮想環境・依存管理ツール

---

📁 ディレクトリ構造（例）

```
ascii_art_maker/
├── app.py
├── README.md
├── requirements.txt
└── pyproject.toml
```

---

🧩 使い方のポイント
- 文字幅を大きくすると、より高解像度の ASCII アートになります
- "@%#*+=-:. " など、文字セットは自由にアレンジ可能
- "█▓▒░ " を使うとドットアート風になります
- "01" を使うとマトリックス風になります

---

📜 ライセンス

MIT License（必要に応じて変更してください）

---

🙌 貢献

バグ報告や改善提案は Issue / Pull Request にて歓迎します。

---

作者

永田

ASCIIアート生成ツールを Python で作りたくて始めたプロジェクトです。
