"""Instagramに投稿する（画像1枚 or リール）。承認済みの下書きだけに使うこと。
画像・動画は公開URL（このリポジトリの photos/ を raw.githubusercontent.com で）である必要がある。
投稿の前に /me の username が nyanguichiba か確かめて、違えば何も出さずに止める。
フィードの画像投稿はフォロワーにしか届かないので、基本はリール（photos/reels/*.mp4）で出す。

使い方:
  python3 scripts/ig_post.py --reel <動画URL> "キャプション"
  python3 scripts/ig_post.py <画像URL> "キャプション"
  python3 scripts/ig_post.py --check
"""
import json
import sys
import time

from common import ensure_account, request

BASE = "https://graph.instagram.com/v23.0"


def me():
    return request("GET", f"{BASE}/me", {"fields": "user_id,username,account_type"})


def post(image_url, caption, reel=False):
    if len(caption) > 2200:
        raise RuntimeError(f"キャプションは2200文字まで（今は{len(caption)}文字）")
    if reel:
        params = {"media_type": "REELS", "video_url": image_url, "caption": caption, "share_to_feed": "true"}
    else:
        params = {"image_url": image_url, "caption": caption}
    container = request("POST", f"{BASE}/me/media", params)
    for _ in range(36 if reel else 12):
        status = request("GET", f"{BASE}/{container['id']}", {"fields": "status_code"})
        if status.get("status_code") == "FINISHED":
            break
        if status.get("status_code") == "ERROR":
            raise RuntimeError(f"画像の処理に失敗: {status}")
        time.sleep(5)
    published = request("POST", f"{BASE}/me/media_publish", {"creation_id": container["id"]})
    return published["id"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--check":
        print(json.dumps(me(), ensure_ascii=False))
        sys.exit(0)
    if len(sys.argv) != (4 if sys.argv[1] == "--reel" else 3):
        sys.exit(__doc__)
    ensure_account(me(), "Instagram")
    if sys.argv[1] == "--reel":
        print(json.dumps({"id": post(sys.argv[2], sys.argv[3], reel=True)}))
    else:
        print(json.dumps({"id": post(sys.argv[1], sys.argv[2])}))
