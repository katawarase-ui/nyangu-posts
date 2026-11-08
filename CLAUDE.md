# nyangu-posts

楽天Room「にゃん具市場」（猫グッズ）の集客用に、Threads と Instagram（どちらも @nyanguichiba）の投稿を下書き→承認→公開する仕組み。持ち主はふくなが。日本語・タメ口で話す。

## 絶対のルール

- **承認されていない下書きは絶対に公開しない。** 承認ボードで `status` が `approved` のものだけを公開する。
- トークンやキーをコード、ファイル、コミット、チャットに書かない。Threads と Instagram のトークンは環境「nyangu」のネットワークシークレットが Authorization ヘッダーに自動で付ける。楽天の値は環境変数 `RAKUTEN_APP_ID` `RAKUTEN_ACCESS_KEY` `RAKUTEN_AFFILIATE_ID`。
- アフィリエイトリンクを含む投稿には必ず「#PR」を入れる（ステマ規制）。
- 使っていない商品を使った風に書かない。実際に使った商品は `data/used_items.md` に載っているものだけ。それ以外は「気になってる」「レビューが多い」「売れてる」という書き方にする。
- ショップの商品画像を Instagram に転載しない。Instagram は `photos/` にある画像だけを使う。写真がなければ Instagram の下書きは作らない。
- `photos/` の `card-*.jpg` はフリー素材（Pexels など商用OKのもの）の猫写真に文字を載せたカード。出典は `data/photo_sources.csv` に1行ずつ記録し、`python3 scripts/make_card.py <元画像フォルダ>` で作る。素材の元画像はそのまま再配布になるのでリポジトリに置かない（`/mnt/project-files/nyangu/stock-raw/` に保管）。
- 素材の猫は自分の猫ではない。キャプションで「うちの子」「この子が使ってる」のように書かない。カードの内容（対策・コツ）に沿ったキャプションにする。人の顔やブランドロゴが目立つ素材は使わない。

## 承認ボード

- URL: data/board_url.txt に書いてある Artifact。`ArtifactData` ツールで読み書きする。
- コレクション `drafts`。ドキュメントIDは `YYYY-MM-DD-<slot>-<platform>`（slot は am / pm、platform は threads / instagram）。同じ枠に2本目を入れるときは末尾に `-2` を付ける（例: `2026-11-06-pm-threads-2`）。
- フィールド: `date`（YYYY-MM-DD）, `slot`, `platform`, `type`（reaction / compare / problem / review / question / sale / roundup）, `text`（本文）, `image`（Instagram の画像URL。ボードの表示用。Threads は空）, `video`（Instagram のリール動画URL。あればリールで出す）, `product`（`{name, price, url}`。問いかけ型は空でよい）, `status`（pending / approved / rejected / posted / failed）, `postId`, `error`, `createdAt`, `postedAt`。
- 返信のつながり（Threads だけ）: `replies`（本文の下に自分でつなげる返信の本文の配列。2〜3本）, `replyIds`（公開後の返信のID）。既存の投稿の下に返信として出すときは `replyTo`（相手の投稿ID）, `replyToLabel`（ボードに出す説明）, `replyToUrl`（その投稿のURL）。承認はボードで本文と返信をまとめて1回。
- 書き込むときは読んだ `version` を `if_version` に必ず渡す。

## 前日夜の下書き作成（19時台、翌日分）

下書きは投稿の前日夜に作り、ふくながが前日22時ごろに承認する。作る下書きの `date` は**明日（日本時間）**。

1. `python3 scripts/rakuten.py ranking` でペットの売れ筋を取る（`rank` 順）。猫用のものだけ候補にする。過去の売れ筋（猫トイレ・砂の飛び散り防止、消臭スプレー、電動の魚おもちゃ、シニア猫フード、猫柄雑貨）に近いものを優先し、直近7日の下書きと同じ商品は避ける。キーワードで探すときは `python3 scripts/rakuten.py search "猫 トイレ"`。
2. 曜日の型で、明日の朝(am)と夜(pm)の Threads 下書き（曜日は明日の曜日で決める）を1本ずつ作る。月・土=問いかけ（リンクなし）、火=猫の反応、木=比較・結論、金=正直レビュー、水・日=日常か悩み解決。リンク付きとリンクなしがだいたい2対1になるようにする。
3. Threads は500文字以内、1行目で結論か問いかけ。最後にリンクと「#PR」。
4. Instagram は `photos/` に未使用の写真があるとき（`data/used_photos.txt` に載っていないもの）だけ、週3本を上限に下書きを作る。**リールで出す**（画像1枚のフィード投稿はフォロワー以外に届かず、10/31〜11/4の5本はリーチ0だった。7月のリールはフォロワー7人でも毎回リーチ約100）。`photos/reels/<カード名>.mp4` がなければ `python3 scripts/make_reel.py <カード名>.jpg` で作ってコミットしてから下書きにする。`image` は `https://raw.githubusercontent.com/katawarase-ui/nyangu-posts/main/photos/<ファイル名>`、`video` は `https://raw.githubusercontent.com/katawarase-ui/nyangu-posts/main/photos/reels/<カード名>.mp4`。
   キャプションの1行目は悩みの言葉で始める（例「猫砂が飛び散るの、地味にストレスじゃない？」）。最後に「保存して見直してね」と「商品はプロフィールの楽天Roomにまとめてるよ」、ハッシュタグは「#PR」＋内容に合うもの4〜5個（例 #猫のいる暮らし #猫好きさんと繋がりたい #ねこ #猫トイレ #猫のおもちゃ）。#楽天room は付けない（猫好きは検索しないので）。
5. 「みんなの声まとめ」（type: roundup）: `python3 scripts/threads_replies.py recent 4` で、2〜4日前の自分の問いかけ投稿に返信が5件以上ついていたら、明日の pm 枠の Threads をこれにする（その日の曜日の型より優先）。作り方は下の「みんなの声まとめ」。
6. 下書きを `status: pending` で承認ボードに書き込む。

### みんなの声まとめ（返信のつながりで商品リンクを並べる）

問いかけで集まった答えを集計して、多かったものを紹介する。リンクは本文に入れず、本文の下に自分でつなげる返信に1本ずつ入れる（Threads はリンク付きの本文が表示されにくいため）。Room のコレクションは使わない。

1. `python3 scripts/threads_replies.py <問いかけの投稿ID>` で返信を全部読み、出てきた商品・ジャンルを数える。返信した人の名前や文章をそのまま引用しない。
2. 多かったものに近い商品を楽天のジャンル別ランキングから探す: `python3 scripts/rakuten.py ranking <genreId>`。猫用品 507524、猫のおもちゃ 206264、猫じゃらし 215363、ねずみのおもちゃ 404161、猫砂 204174、療法食 404149（ほかはペット全体 101213）。商品ページのURLがわかっていてランキングにないときは `python3 scripts/rakuten.py link "<item.rakuten.co.jp のURL>"` でリンクを作る。ランキングにも見つからないものは紹介しない（100均や家にあるものは本文で「タダで遊べる派も多かった」と触れるだけ）。
3. `text`（本文）: 1行目で「◯件の答えで多かったのは…」と結論。TOP3の名前と、手作り派・100均派が多かった話など。リンクは入れず、最後に「商品は返信につなげたよ👇」と「#PR」。
4. `replies`: 商品1つにつき1本、2〜3本。商品名・価格・レビュー件数と平均・「回答でも名前が多かった」などの理由、リンク、最後に「#PR」。どれも500文字以内。使ってない商品なので「使ってる」「うちの子が」とは書かない。
5. `product` には1本目の返信の商品を入れる。元の問いかけの投稿にぶら下げたいとき（投稿がまだ見られているとき）は `replyTo` にその投稿IDを入れる。

## 公開（7時半と21時）

1. 承認ボードの `drafts` から、今日の該当 slot（朝は am、夜は pm）で `status == approved` のものを読む。
2. Threads は `python3 scripts/threads_post.py "<text>"`、Instagram は `video` があれば `python3 scripts/ig_post.py --reel "<video>" "<text>"`、なければ `python3 scripts/ig_post.py "<image>" "<text>"`。`replies` があるときは `python3 scripts/threads_post.py "<text>" "<replies[0]>" "<replies[1]>" ...`、`replyTo` があるときは先頭に `--reply-to <replyTo>` を付ける。本文と返信は承認されたものをそのまま渡す。
3. 成功したら `status: posted`, `postId`, `postedAt`（返信があれば `replyIds` も）を書く。返信の途中で失敗したら、出せた `postId` / `replyIds` と `status: failed`, `error` を書いて、残りを勝手に出さない。Instagram で使った写真は `data/used_photos.txt` に追記してコミット。失敗したら `status: failed` と `error` を書いて、勝手にやり直さない。

## 毎週日曜の振り返り

投稿ごとの反応（Threads は `/v1.0/<id>/insights`、Instagram は `/<id>/insights`）を集めて、伸びた型と商品をボードの `reports` コレクションに1件書く。楽天の売上は API がないので書かない。
