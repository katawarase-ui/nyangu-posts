"""フリー素材の猫写真に文字を載せて、Instagram用のカード画像（1080x1350）を作る。
素材の元画像は公開リポジトリに置かない（再配布になるため）。元画像はリポジトリの外のフォルダに置いて指定する。
カードの文字と出典は data/photo_sources.csv に書く。

使い方:
  python3 scripts/make_card.py <元画像フォルダ> [出力フォルダ]   # 出力の既定は photos/
  python3 scripts/make_card.py <元画像フォルダ> photos card-toy-01.jpg  # 1枚だけ
"""
import csv
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = os.path.join(ROOT, "data", "photo_sources.csv")
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"

W, H = 1080, 1350
PHOTO_H = 780
BG = "#F6EFE6"
INK = "#3B2F25"
ACCENT = "#C2603C"
SUB = "#8A7A66"


def font(size):
    return ImageFont.truetype(FONT, size)


def make(row, raw_dir, out_dir):
    photo = Image.open(os.path.join(raw_dir, row["raw_file"])).convert("RGB")
    photo = ImageOps.fit(photo, (W, PHOTO_H), centering=(0.5, float(row.get("focus_y") or 0.45)))
    im = Image.new("RGB", (W, H), BG)
    im.paste(photo, (0, 0))
    d = ImageDraw.Draw(im)
    d.text((80, PHOTO_H + 50), row["title"], font=font(76), fill=INK)
    d.text((80, PHOTO_H + 145), row["subtitle"], font=font(46), fill=ACCENT)
    y = PHOTO_H + 225
    for i, key in enumerate(["point1", "point2", "point3"]):
        d.ellipse((80, y + 4, 124, y + 48), fill=ACCENT)
        d.text((102, y + 26), str(i + 1), font=font(30), fill="white", anchor="mm")
        d.text((145, y + 2), row[key], font=font(42), fill=INK)
        y += 70
    d.text((W - 40, H - 28), "にゃん具市場", font=font(28), fill=SUB, anchor="rd")
    out = os.path.join(out_dir, row["file"])
    im.save(out, quality=90)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    raw_dir = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "photos")
    only = sys.argv[3] if len(sys.argv) > 3 else None
    os.makedirs(out_dir, exist_ok=True)
    with open(SOURCES, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if only and row["file"] != only:
                continue
            print(make(row, raw_dir, out_dir))
