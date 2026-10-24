import sys
from pathlib import Path

# ASCIIアート変換の主要ロジックを直接 import するため、リポジトリルートをパスに追加

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from app import (
  adjust_contrast_gray,
  generate_ascii,
  image_to_ascii,
  normalize_charset,
  to_gray,
)
def test_normalize_charset_strips_whitespace_and_duplicates():
  # 空白と重複文字を取り除けること
  result = normalize_charset(" A A\nB\tB  ")
  assert result == "AB"
def test_normalize_charset_falls_back_when_empty():
  # 入力が空の場合にデフォルト文字セットへフォールバックすること
  assert normalize_charset(" \n\t") == "@%#*+=-:. "
def test_adjust_contrast_gray_scales_around_midpoint():
  # コントラスト強調で0/255に張り付くか（中心0.5を基準に伸長）
  gray = Image.fromarray(np.array([[64, 192]], dtype=np.uint8), mode="L")

  adjusted = adjust_contrast_gray(gray, contrast=2.0)

  np.testing.assert_array_equal(
    np.array(adjusted), np.array([[0, 255]], dtype=np.uint8)
  )
def test_to_gray_scales_16bit_image_to_8bit():
  # 16 ビット画像は 255 で切り詰めず、0〜65535 を 0〜255 に縮めること
  img = Image.fromarray(np.array([[0, 257, 32896, 65535]], dtype=np.uint16))
  assert img.mode == "I;16"

  gray = to_gray(img)

  assert gray.mode == "L"
  np.testing.assert_array_equal(
    np.array(gray), np.array([[0, 1, 128, 255]], dtype=np.uint8)
  )
def test_to_gray_scales_32bit_integer_image_to_8bit():
  # 32 ビット整数（I）の画像も 16 ビットの範囲として縮め、範囲外は切り詰めること
  img = Image.fromarray(np.array([[0, 32896, 65535, 70000]], dtype=np.int32))
  assert img.mode == "I"

  np.testing.assert_array_equal(
    np.array(to_gray(img)), np.array([[0, 128, 255, 255]], dtype=np.uint8)
  )
def test_image_to_ascii_handles_16bit_gradient():
  # 16 ビットのグラデーションでも暗い文字から明るい文字まで使われること
  img = Image.fromarray(np.array([[0, 21845, 43690, 65535]], dtype=np.uint16))

  ascii_art = image_to_ascii(
    img, width=4, charset="ABCD", invert=False, contrast=1.0, vertical_scale=1.0
  )

  assert ascii_art == "ABCD"
def test_image_to_ascii_maps_pixels_with_given_charset():
  # 指定した文字セットを使ってピクセルがマッピングされること
  img = Image.fromarray(np.array([[0, 255]], dtype=np.uint8), mode="L")

  ascii_art = image_to_ascii(
    img,
    width=2,
    charset="AB",
    invert=False,
    contrast=1.0,
    vertical_scale=1.0,
  )

  assert ascii_art == "AB"
def test_image_to_ascii_uses_default_charset_and_inverts_when_requested():
  # 空白のみの文字セットはデフォルトに置き換わり、invertで反転されること
  img = Image.fromarray(np.array([[0, 255]], dtype=np.uint8), mode="L")

  ascii_art = image_to_ascii(
    img,
    width=2,
    charset="  ",  # normalization should drop whitespace and use default
    invert=True,
    contrast=1.0,
    vertical_scale=1.0,
  )

  assert ascii_art == " @"
def test_generate_ascii_handles_missing_or_invalid_input_gracefully():
  # 入力なし・不正入力で適切なメッセージを返すこと
  assert (
    generate_ascii(
      None,
      width=80,
      charset="@%#*+=-:. ",
      invert=False,
      contrast=1.0,
      vertical_scale=0.5,
    )
    == "画像がアップロードされていません。"
  )

  error_message = generate_ascii(
    "not-an-image",
    width=10,
    charset="@%",
    invert=False,
    contrast=1.0,
    vertical_scale=0.5,
  )
  assert "エラーが発生しました" in error_message
