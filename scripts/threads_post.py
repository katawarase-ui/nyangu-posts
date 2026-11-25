"""Threadsにテキスト投稿する。承認済みの下書きだけに使うこと。

使い方:
  python3 scripts/threads_post.py "本文"                         # 投稿する
  python3 scripts/threads_post.py "本文" "返信1" "返信2"          # 本文を出して、その下に返信をつなげる
  python3 scripts/threads_post.py --reply-to <投稿ID> "本文" ...  # 既存の投稿への返信として出す
  python3 scripts/threads_post.py --topic 猫トイレ "本文" ...     # トピックを指定する（省略時は「猫」）
  python3 scripts/threads_post.py --check                         # アカウント確認だけ（投稿しない）

最初の投稿には必ずトピック（topic_tag）を付ける。付けないと本文の最初のハッシュタグがトピックになり、
「#PR」が入っていると「PR」トピックに分類されて猫好きに届かない（11/1〜11/25 の商品投稿が全部そうだった）。

投稿の前に /me の username が nyanguichiba か確かめて、違えば何も出さずに止める。
出力は {"id": 最初の投稿のID, "replyIds": [返信のID...]}。
返信の途中で失敗したら、出せたところまでのIDと error を出して終了コード1で終わる（やり直さない）。
"""
import json
import sys
import time

from common import ensure_account, request

BASE = "https://graph.threads.net/v1.0"
LIMIT = 500
DEFAULT_TOPIC = "猫"


def me():
    return request("GET", f"{BASE}/me", {"fields": "id,username"})


def post(text, reply_to=None, topic=None):
    if len(text) > LIMIT:
        raise RuntimeError(f"Threadsの本文は{LIMIT}文字まで（今は{len(text)}文字）")
    params = {"media_type": "TEXT", "text": text}
    if reply_to:
        params["reply_to_id"] = reply_to
    if topic:
        params["topic_tag"] = topic
    container = request("POST", f"{BASE}/me/threads", params)
    time.sleep(5)  # 公式の推奨: コンテナ作成から公開まで少し待つ
    published = request("POST", f"{BASE}/me/threads_publish", {"creation_id": container["id"]})
    return published["id"]


def post_chain(texts, reply_to=None, topic=DEFAULT_TOPIC):
    """texts[0] を出し、texts[1:] を1つ前の投稿への返信としてつなげる。"""
    for i, t in enumerate(texts):
        if len(t) > LIMIT:
            raise RuntimeError(f"{i + 1}本目が{LIMIT}文字を超えてる（{len(t)}文字）")
    first = post(texts[0], reply_to, topic)
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
    topic = DEFAULT_TOPIC
    while args and args[0] in ("--reply-to", "--topic"):
        if len(args) < 3:
            sys.exit(__doc__)
        if args[0] == "--reply-to":
            reply_to = args[1]
        else:
            topic = args[1].lstrip("#") or DEFAULT_TOPIC
        args = args[2:]
    ensure_account(me(), "Threads")
    result = post_chain(args, reply_to, topic)
    print(json.dumps(result, ensure_ascii=False))
    if "error" in result:
        sys.exit(1)
