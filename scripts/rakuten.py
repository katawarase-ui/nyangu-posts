"""楽天市場のランキングと商品検索。アフィリエイトID付きのリンクが返る。

使い方:
  python3 scripts/rakuten.py ranking [genreId]     # 既定はペット 101213
  python3 scripts/rakuten.py search "猫 トイレ"
"""
import json
import sys

from common import env, request

HEADERS = {"Referer": "https://room.rakuten.co.jp/", "Origin": "https://room.rakuten.co.jp"}
BASE = "https://openapi.rakuten.co.jp"


def _params(extra):
    params = {
        "applicationId": env("RAKUTEN_APP_ID"),
        "accessKey": env("RAKUTEN_ACCESS_KEY"),
        "format": "json",
        "formatVersion": 2,
    }
    affiliate_id = env("RAKUTEN_AFFILIATE_ID", required=False)
    if affiliate_id:
        params["affiliateId"] = affiliate_id
    params.update(extra)
    return params


def _item(raw):
    images = raw.get("mediumImageUrls") or []
    return {
        "rank": raw.get("rank"),
        "name": raw.get("itemName"),
        "price": raw.get("itemPrice"),
        "shop": raw.get("shopName"),
        "url": raw.get("affiliateUrl") or raw.get("itemUrl"),
        "reviewAverage": raw.get("reviewAverage"),
        "reviewCount": raw.get("reviewCount"),
        "image": images[0] if images else None,
        "caption": (raw.get("itemCaption") or "")[:300],
    }


def ranking(genre_id="101213"):
    data = request("GET", f"{BASE}/ichibaranking/api/IchibaItem/Ranking/20220601",
                   _params({"genreId": genre_id}), HEADERS)
    items = [_item(i) for i in data.get("Items", [])]
    # 並びが逆順で返ることがあるので rank で並べ直す
    return sorted(items, key=lambda i: i["rank"] or 999)


def search(keyword, hits=10):
    data = request("GET", f"{BASE}/ichibams/api/IchibaItem/Search/20220601",
                   _params({"keyword": keyword, "hits": hits, "sort": "-reviewCount"}), HEADERS)
    return [_item(i) for i in data.get("Items", [])]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ranking"
    if cmd == "ranking":
        result = ranking(sys.argv[2] if len(sys.argv) > 2 else "101213")
    elif cmd == "search":
        result = search(sys.argv[2])
    else:
        sys.exit(__doc__)
    print(json.dumps(result, ensure_ascii=False, indent=2))
