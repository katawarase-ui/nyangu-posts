"""Instagramに画像1枚の投稿をする。承認済みの下書きだけに使うこと。
画像は公開URL（このリポジトリの photos/ を raw.githubusercontent.com で）である必要がある。

使い方:
  python3 scripts/ig_post.py <画像URL> "キャプション"
  python3 scripts/ig_post.py --check
"""
import json
import sys
import time

from common import request

BASE = "https://graph.instagram.com/v23.0"


def me():
    return request("GET", f"{BASE}/me", {"fields": "user_id,username,account_type"})


def post(image_url, caption):
    if len(caption) > 2200:
        raise RuntimeError(f"キャプションは2200文字まで（今は{len(caption)}文字）")
    container = request("POST", f"{BASE}/me/media", {"image_url": image_url, "caption": caption})
    for _ in range(12):
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
    elif len(sys.argv) == 3:
        print(json.dumps({"id": post(sys.argv[1], sys.argv[2])}))
    else:
        sys.exit(__doc__)
