"""Threadsにテキスト投稿する。承認済みの下書きだけに使うこと。

使い方:
  python3 scripts/threads_post.py "本文"                         # 投稿する
  python3 scripts/threads_post.py "本文" "返信1" "返信2"          # 本文を出して、その下に返信をつなげる
  python3 scripts/threads_post.py --reply-to <投稿ID> "本文" ...  # 既存の投稿への返信として出す
  python3 scripts/threads_post.py --check                         # アカウント確認だけ（投稿しない）

出力は {"id": 最初の投稿のID, "replyIds": [返信のID...]}。
返信の途中で失敗したら、出せたところまでのIDと error を出して終了コード1で終わる（やり直さない）。
"""
import json
import sys
import time

from common import request

BASE = "https://graph.threads.net/v1.0"
LIMIT = 500


def me():
    return request("GET", f"{BASE}/me", {"fields": "id,username"})


def post(text, reply_to=None):
    if len(text) > LIMIT:
        raise RuntimeError(f"Threadsの本文は{LIMIT}文字まで（今は{len(text)}文字）")
    params = {"media_type": "TEXT", "text": text}
    if reply_to:
        params["reply_to_id"] = reply_to
    container = request("POST", f"{BASE}/me/threads", params)
    time.sleep(5)  # 公式の推奨: コンテナ作成から公開まで少し待つ
    published = request("POST", f"{BASE}/me/threads_publish", {"creation_id": container["id"]})
    return published["id"]


def post_chain(texts, reply_to=None):
    """texts[0] を出し、texts[1:] を1つ前の投稿への返信としてつなげる。"""
    for i, t in enumerate(texts):
        if len(t) > LIMIT:
            raise RuntimeError(f"{i + 1}本目が{LIMIT}文字を超えてる（{len(t)}文字）")
    first = post(texts[0], reply_to)
    result = {"id": first, "replyIds": []}
    parent = first
    for t in texts[1:]:
        try:
            parent = post(t, parent)
        except Exception as e:
            result["error"] = f"返信{len(result['replyIds']) + 1}本目で失敗: {e}"
            return result
        result["replyIds"].append(parent)
    return result


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--check":
        print(json.dumps(me(), ensure_ascii=False))
        sys.exit(0)
    reply_to = None
    if args[0] == "--reply-to":
        if len(args) < 3:
            sys.exit(__doc__)
        reply_to, args = args[1], args[2:]
    result = post_chain(args, reply_to)
    print(json.dumps(result, ensure_ascii=False))
    if "error" in result:
        sys.exit(1)
