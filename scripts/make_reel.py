"""photos/ のカード画像（1080x1350）から、Instagramリール用の縦動画（1080x1920, 8秒, 無音）を作る。
フィードの画像投稿はフォロワーにしか届かないので、IGはリールで出す（おすすめ・リールタブに載る）。
カードの上下はカードの背景色で埋め、ゆっくりズームさせる。

使い方:
  python3 scripts/make_reel.py                 # photos/card-*.jpg のうち、まだ動画がないもの全部
  python3 scripts/make_reel.py card-toy-01.jpg # 1枚だけ
出力: photos/reels/<カード名>.mp4
"""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTOS = os.path.join(ROOT, "photos")
OUT = os.path.join(PHOTOS, "reels")
BG = "0xF6EFE6"
SECONDS = 8
FPS = 30


def make(card):
    src = os.path.join(PHOTOS, card)
    out = os.path.join(OUT, os.path.splitext(card)[0] + ".mp4")
    frames = SECONDS * FPS
    # 1.0倍→1.06倍にゆっくりズーム。zoompan は入力より大きく拡大してから縮めると揺れにくい
    vf = (
        f"scale=2160:-1,zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={frames}:s=1080x1350:fps={FPS},"
        f"pad=1080:1920:0:285:color={BG},format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-loop", "1", "-i", src,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vf", vf, "-frames:v", str(frames),
        "-c:v", "libx264", "-profile:v", "high", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-movflags", "+faststart", out,
    ]
    subprocess.run(cmd, check=True)
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if len(sys.argv) > 1:
        cards = sys.argv[1:]
    else:
        cards = [
            os.path.basename(p) for p in sorted(glob.glob(os.path.join(PHOTOS, "card-*.jpg")))
            if not os.path.exists(os.path.join(OUT, os.path.basename(p)[:-4] + ".mp4"))
        ]
    for c in cards:
        print(make(c))
