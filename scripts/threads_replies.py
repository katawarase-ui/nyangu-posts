"""Threadsの返信を読む（読むだけ。投稿はしない）。

使い方:
  python3 scripts/threads_replies.py recent [日数]   # 自分の投稿で返信がついたものを返信数の多い順に（既定3日）
  python3 scripts/threads_replies.py <投稿ID>        # その投稿についた返信の本文（最大300件）

返信した人のユーザー名は出さない（下書きに個人名を書かないため）。
"""
import json
import sys
import time
from datetime import datetime, timedelta, timezone

from common import request

BASE = "https://graph.threads.net/v1.0"


def recent(days=3):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    data = request("GET", f"{BASE}/me/threads",
                   {"fields": "id,timestamp,text,link_attachment_url", "limit": 50})
    out = []
    for p in data.get("data", []):
        ts = datetime.fromisoformat(p["timestamp"].replace("+0000", "+00:00"))
        if ts < since:
            continue
        ins = request("GET", f"{BASE}/{p['id']}/insights", {"metric": "views,likes,replies"})
        m = {x["name"]: x["values"][0]["value"] for x in ins.get("data", [])}
        out.append({
            "id": p["id"],
            "timestamp": p["timestamp"],
            "hasLink": bool(p.get("link_attachment_url")),
            "text": (p.get("text") or "")[:80],
            **m,
        })
    return sorted(out, key=lambda x: x.get("replies", 0), reverse=True)


def replies(post_id, max_items=300):
    texts = []
    params = {"fields": "text", "limit": 100}
    url = f"{BASE}/{post_id}/replies"
    while url and len(texts) < max_items:
        data = request("GET", url, params)
        texts += [r["text"] for r in data.get("data", []) if r.get("text")]
        after = data.get("paging", {}).get("cursors", {}).get("after")
        if not after or not data.get("paging", {}).get("next"):
            break
        params = {"fields": "text", "limit": 100, "after": after}
        time.sleep(0.5)
    return texts[:max_items]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "recent":
        result = recent(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    else:
        result = replies(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
