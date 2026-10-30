# nyangu-posts

楽天Room「にゃん具市場」（猫グッズ）の集客用に、Threads と Instagram（どちらも @nyanguichiba）の投稿を下書き→承認→公開する仕組み。持ち主はふくなが。日本語・タメ口で話す。

## 絶対のルール

- **承認されていない下書きは絶対に公開しない。** 承認ボードで `status` が `approved` のものだけを公開する。
- トークンやキーをコード、ファイル、コミット、チャットに書かない。Threads と Instagram のトークンは環境「nyangu」のネットワークシークレットが Authorization ヘッダーに自動で付ける。楽天の値は環境変数 `RAKUTEN_APP_ID` `RAKUTEN_ACCESS_KEY` `RAKUTEN_AFFILIATE_ID`。
- アフィリエイトリンクを含む投稿には必ず「#PR」を入れる（ステマ規制）。
- 使っていない商品を使った風に書かない。実際に使った商品は `data/used_items.md` に載っているものだけ。それ以外は「気になってる」「レビューが多い」「売れてる」という書き方にする。
- ショップの商品画像を Instagram に転載しない。Instagram は `photos/` にある自分の写真だけを使う。写真がなければ Instagram の下書きは作らない。

## 承認ボード

- URL: data/board_url.txt に書いてある Artifact。`ArtifactData` ツールで読み書きする。
- コレクション `drafts`。ドキュメントIDは `YYYY-MM-DD-<slot>-<platform>`（slot は am / pm、platform は threads / instagram）。
- フィールド: `date`（YYYY-MM-DD）, `slot`, `platform`, `type`（reaction / compare / problem / review / question / sale）, `text`（本文）, `image`（Instagram の画像URL。Threads は空）, `product`（`{name, price, url}`。問いかけ型は空でよい）, `status`（pending / approved / rejected / posted / failed）, `postId`, `error`, `createdAt`, `postedAt`。
- 書き込むときは読んだ `version` を `if_version` に必ず渡す。

## 毎朝の下書き作成（6時台）

1. `python3 scripts/rakuten.py ranking` でペットの売れ筋を取る（`rank` 順）。猫用のものだけ候補にする。過去の売れ筋（猫トイレ・砂の飛び散り防止、消臭スプレー、電動の魚おもちゃ、シニア猫フード、猫柄雑貨）に近いものを優先し、直近7日の下書きと同じ商品は避ける。キーワードで探すときは `python3 scripts/rakuten.py search "猫 トイレ"`。
2. 曜日の型で、その日の朝(am)と夜(pm)の Threads 下書きを1本ずつ作る。月・土=問いかけ（リンクなし）、火=猫の反応、木=比較・結論、金=正直レビュー、水・日=日常か悩み解決。リンク付きとリンクなしがだいたい2対1になるようにする。
3. Threads は500文字以内、1行目で結論か問いかけ。最後にリンクと「#PR」。
4. Instagram は `photos/` に未使用の写真があるとき（`data/used_photos.txt` に載っていないもの）だけ、週3本を上限に下書きを作る。画像URLは `https://raw.githubusercontent.com/katawarase-ui/nyangu-posts/main/photos/<ファイル名>`。キャプション末尾に「商品はプロフィールの楽天Roomにまとめてるよ」と「#PR #猫のいる暮らし #猫グッズ #楽天room」。
5. 下書きを `status: pending` で承認ボードに書き込む。

## 公開（7時半と21時）

1. 承認ボードの `drafts` から、今日の該当 slot（朝は am、夜は pm）で `status == approved` のものを読む。
2. Threads は `python3 scripts/threads_post.py "<text>"`、Instagram は `python3 scripts/ig_post.py "<image>" "<text>"`。
3. 成功したら `status: posted`, `postId`, `postedAt` を書く。Instagram で使った写真は `data/used_photos.txt` に追記してコミット。失敗したら `status: failed` と `error` を書いて、勝手にやり直さない。

## 毎週日曜の振り返り

投稿ごとの反応（Threads は `/v1.0/<id>/insights`、Instagram は `/<id>/insights`）を集めて、伸びた型と商品をボードの `reports` コレクションに1件書く。楽天の売上は API がないので書かない。
