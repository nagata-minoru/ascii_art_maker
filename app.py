from pathlib import Path
from typing import Optional

import gradio as gr
import numpy as np
from PIL import Image

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
def load_asset(path: Path) -> str:
  """
  Read a text asset safely; fall back to an empty string if missing.
  """
  try:
    return path.read_text(encoding="utf-8")
  except OSError:
    return ""
CUSTOM_CSS = load_asset(STATIC_DIR / "styles.css")
COPY_JS = load_asset(STATIC_DIR / "copy.js")
def normalize_charset(charset: str) -> str:
  """
  ユーザーが入れた文字列から、重複と空白を取り除いた文字列を返す。
  左ほど「暗い」、右ほど「明るい」として使う。
  """
  # 改行などを除去
  charset = charset.replace("\n", "").replace("\r", "")
  # 空白のみはダメ
  charset = "".join(ch for ch in charset if not ch.isspace())
  # 重複削除(順序保持)
  seen = set()
  result = []
  for ch in charset:
    if ch not in seen:
      seen.add(ch)
      result.append(ch)
  if not result:
    return "@%#*+=-:. "
  return "".join(result)
def to_gray(img: Image.Image) -> Image.Image:
  """
  画像を 0〜255 の 8 ビットグレースケール画像に変換する。
  16 ビット PNG などの整数モード（I;16 系・I）は、Pillow の convert("L") だと
  255 を超える値が 255 に切り詰められて真っ白になるため、0〜65535 を 0〜255 に縮めてから変換する。

  引数:
    img: 変換する画像
  戻り値:
    モード "L" のグレースケール画像
  """
  if img.mode == "I" or img.mode.startswith("I;16"):
    arr = np.array(img).astype(np.float32) / 65535.0 * 255.0
    arr = np.clip(arr, 0.0, 255.0).round().astype(np.uint8)
    return Image.fromarray(arr, mode="L")
  return img.convert("L")
def adjust_contrast_gray(gray: Image.Image, contrast: float) -> Image.Image:
  """
  0〜255 のグレースケール画像に対してコントラストを調整。
  contrast = 1.0 で変更なし。
  1.0 より大きいとコントラスト強く、小さいと弱く。
  """
  arr = np.array(gray).astype(np.float32) / 255.0
  # 中心 0.5 を基準にコントラスト調整
  arr = (arr - 0.5) * contrast + 0.5
  arr = np.clip(arr, 0.0, 1.0)
  arr = (arr * 255.0).astype(np.uint8)
  return Image.fromarray(arr, mode="L")
def image_to_ascii(
  img: Image.Image,
  width: int = 80,
  charset: str = "@%#*+=-:. ",
  invert: bool = False,
  contrast: float = 1.0,
  vertical_scale: float = 0.5,
) -> str:
  """
  画像をASCIIアート文字列に変換。
  """
  if not img:
    return ""

  # 文字セット整形
  charset = normalize_charset(charset)
  if invert:
    charset = charset[::-1]
  n_chars = len(charset)

  # グレースケールに変換
  gray = to_gray(img)

  # 画像サイズからリサイズ後の高さを計算
  orig_w, orig_h = gray.size
  if width <= 0:
    width = 80
  aspect = orig_h / orig_w
  # フォントは縦長なので縦方向を少し圧縮する
  new_h = int(aspect * width * vertical_scale)
  new_h = max(1, new_h)

  gray_resized = gray.resize((width, new_h), resample=Image.Resampling.BICUBIC)

  # コントラスト調整
  if abs(contrast - 1.0) > 1e-3:
    gray_resized = adjust_contrast_gray(gray_resized, contrast)

  arr = np.array(gray_resized)  # shape: (H, W), 0〜255

  # 0〜255 を 0〜(n_chars-1) にマッピング
  indices = (arr.astype(np.float32) / 255.0) * (n_chars - 1)
  indices = indices.astype(np.int32)

  lines = []
  for row in indices:
    line_chars = [charset[i] for i in row]
    lines.append("".join(line_chars))

  ascii_art = "\n".join(lines)
  return ascii_art
def generate_ascii(
  img: Optional[Image.Image],
  width: int,
  charset: str,
  invert: bool,
  contrast: float,
  vertical_scale: float,
) -> str:
  if not img:
    return "画像がアップロードされていません。"

  try:
    ascii_art = image_to_ascii(
      img,
      width=width,
      charset=charset,
      invert=invert,
      contrast=contrast,
      vertical_scale=vertical_scale,
    )
    return ascii_art
  except Exception as e:
    return f"エラーが発生しました: {e}"
with gr.Blocks(title="ASCII Art Maker") as demo:
  gr.Markdown(
    """
# 🎨 ASCII Art Maker
画層を文字だけで描いた ** ASCIIアート** に変換するツール。

1. 左側で画像をアップロード
2. 幅や文字セットを調整
3. 「生成」を押すと右側にASCIIアートが出ます

生成されたテキストはコピーして、エディタやSlackなどに貼り付けて遊べます。
"""
  )

  with gr.Row():
    with gr.Column(scale=1):
      # 既定の image_mode="RGB" だと 16 ビット画像が gradio 側で切り詰められるので、元のモードのまま受け取る
      img_input = gr.Image(label="画像をアップロード", type="pil", image_mode=None)
      width_slider = gr.Slider(
        minimum=20, maximum=240, value=80, step=2, label="文字幅(横の文字数)"
      )

      charset_choice = gr.Dropdown(
        label="文字セット（プリセット）",
        choices=["@%#*+=-:. ", "█▓▒░ ", "10", "カスタム入力"],
        value="@%#*+=-:. ",
      )

      charset_text = gr.Textbox(
        label="カスタム文字セット", value="", lines=1, interactive=True, visible=False
      )

      def handle_charset_selection(choice, custom):
        if choice == "カスタム入力":
          return gr.update(visible=True), custom
        else:
          return gr.update(visible=False), choice

      invert_check = gr.Checkbox(label="明暗を反転する(ポジ/ネガ切り替え)", value=False)
      contrast_slider = gr.Slider(
        minimum=0.3, maximum=2.5, value=1.0, step=0.05, label="コントラスト"
      )
      vertical_slider = gr.Slider(
        minimum=0.3,
        maximum=1.5,
        value=0.5,
        step=0.05,
        label="縦方向のスケール(フォント縦長補正)",
      )

      run_button = gr.Button("生成", variant="primary")

    with gr.Column(scale=1):
      ascii_output = gr.Textbox(
        label="ASCIIアート出力",
        lines=30,
        interactive=True,
        elem_classes=["ascii-output"],
      )
      copy_button = gr.Button("クリップボードにコピー", variant="secondary")

  charset_choice.change(
    fn=handle_charset_selection,
    inputs=[charset_choice, charset_text],
    outputs=[charset_text, charset_text],
  )

  copy_button.click(fn=None, inputs=[ascii_output], outputs=[], js=COPY_JS)

  run_button.click(
    fn=generate_ascii,
    inputs=[
      img_input,
      width_slider,
      charset_text,
      invert_check,
      contrast_slider,
      vertical_slider,
    ],
    outputs=[ascii_output],
  )

if __name__ == "__main__":
  # Gradio 6 から css は Blocks ではなく launch() に渡す
  demo.launch(css=CUSTOM_CSS)
