"""Threadsにテキスト投稿する。承認済みの下書きだけに使うこと。

使い方:
  python3 scripts/threads_post.py "本文"            # 投稿する
  python3 scripts/threads_post.py --check            # アカウント確認だけ（投稿しない）
"""
import json
import sys
import time

from common import request

BASE = "https://graph.threads.net/v1.0"


def me():
    return request("GET", f"{BASE}/me", {"fields": "id,username"})


def post(text):
    if len(text) > 500:
        raise RuntimeError(f"Threadsの本文は500文字まで（今は{len(text)}文字）")
    container = request("POST", f"{BASE}/me/threads", {"media_type": "TEXT", "text": text})
    time.sleep(5)  # 公式の推奨: コンテナ作成から公開まで少し待つ
    published = request("POST", f"{BASE}/me/threads_publish", {"creation_id": container["id"]})
    return published["id"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--check":
        print(json.dumps(me(), ensure_ascii=False))
    else:
        print(json.dumps({"id": post(sys.argv[1])}))
