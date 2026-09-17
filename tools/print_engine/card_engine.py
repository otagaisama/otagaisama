こころづて 印刷屋用カードエンジン v0.1（2026-09-17）
中身
card_engine.py … 本体（ReportLab＋qrcode。CMYK直指定・フォント埋め込み・QRベクター）
config.json … 寸法・色・文言・変種（4山＝lot 0001〜0004）。冠野の回答が来たら bleed_mm を差し替える
export_manifest.sql … Supabaseから400件を書き出すSQL／lot_no書き込みSQL
fonts/ … 無ければ実行時に Google Fonts（OFL）から自動取得
初回セットアップ（TAKAのPC・Claude Codeで）
    pip install reportlab qrcode pillow pdfrw
    python card_engine.py --make-dummy manifest_dummy.json
    python card_engine.py --manifest manifest_dummy.json --out test.pdf --sheets 1

毎バッチの手順
束を4本作る（SQL Editor で export_manifest.sql ①②。create_bundle_v2(lot_id, expires_at, 100)）
export_manifest.sql ③④を実行 → manifest.json に保存
`python card_engine.py --manifest manifest.json --out batch_0001.pdf`
→ NGなら止まる（件数・重複・旧文字 g i l o s z）。OKなら *_manifest_report.csv（c／sheet／k／lot_no／short_id／global_no／URL）が出る
表紙1シートを `--sheets 1` で出してコンビニ原寸100%で確認（幅91mm）
入稿（lot_no は create_bundle_v2 が rooms に入れるので後処理なし）
変えるとき
塗り足し／面付け … config.sheet（bleed_mm, gap_mm, cols, rows, page_w/h）。10丁にするなら cols=2 rows=5 と用紙寸法
文言 … config.text（日本語はShippori原本を埋め込むので字種の制約なし）
変種 … config.variants（sponsor: pdf（ベクター・CMYKのまま通る）/logo（PNG/JPG）/text/null、mono: 墨のみ）。ロゴは engine フォルダに置いてファイル名を指定。pdf の regions で部分抜き・詰めができる（現在は「株式会社」を除外）
裏面ミラー … config.sheet.mirror_back（冠野K3回答により現在 false）
表を変種で変えたい場合 … front_identical=false（表と裏の取り違え防止が効かなくなるので非推奨）
