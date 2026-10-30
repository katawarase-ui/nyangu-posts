"""共通処理。トークンは環境のネットワークシークレットがAuthorizationヘッダーに自動で付けるので、コードには持たない。"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request


def request(method, url, params=None, headers=None):
    if params:
        query = urllib.parse.urlencode(params)
        if method == "GET":
            url = f"{url}?{query}"
            data = None
        else:
            data = query.encode()
    else:
        data = None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} {url.split('?')[0]}: {body}") from None


def env(name, required=True):
    value = os.environ.get(name, "")
    if required and not value:
        raise RuntimeError(f"環境変数 {name} が設定されていない")
    return value
