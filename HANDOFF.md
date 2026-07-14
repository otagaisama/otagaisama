# HANDOFF.md（現在地と次の一手）
最終更新: 2026-07-14

## 今どこ
- DB全行監査 完了（2026-07-13・再実施不要）
- profiles権限修正 完了（2026-07-14 revoke済み）
- SQLファイル置き場整理 完了（2026-07-14 sql/へ移動）
- docs/整理 進行中（5枚拾いのうち2枚済み：統合メモ・hikitsugi）
- 印刷エンジン（2,000枚・4-up）着手前
- 印刷屋 返信待ち（ケント180kg・100枚実測厚み）

## 次の一手
1. 残り3枚をdocs/へ（URLはdocs/MD台帳_2026-07-09.mdの各行に記載）
   - カード型/スタンプ → 台帳C欄【新】7/1の行
   - 3タブ設計 → 台帳E欄7/8の行 ※アップ後、実装(mypage.html)との照合をClaudeに依頼
   - sponsor契約スキーマ → 台帳G欄7/5の行
2. 5枚揃ったら「docs/全部読んで、重複・矛盾・古い記述を洗い出して」とClaudeに言う
3. 過去チャットの確定事項 洗い出し（台帳＋Claudeの記憶から docs/確定事項リスト.md に蒸留。
   Claudeの記憶にある設計決定のdocs/移植も同時に、TAKAと相談しながら仕分け）
4. 済んだら「HANDOFF更新して」とClaudeに言う（全文出力→丸ごと差し替え）
5. 印刷屋返信きたら→lot_no体系→印刷エンジン

## 後回しOK（急がん）
- redactedチャット(7/5)の目視確認・6/30命名mdの捜索（台帳の未走査欄参照）
- 集約チェックリスト.mdは役目終了後に削除

## リポジトリ内ファイル（本番HTML以外）
- BACKUP.md … バックアップ手順
- sql/ … SQLの保険置き場（下記ルール参照）
  - sql/discard_card_backup_20260711.sql … discard_card関数の原本（DB反映済み・復元用）
  - sql/migration_20260705_rls.sql … RLS定義の原本（DB反映済み・再現用）
- docs/ … テーマ別の正MD（運用ルール・NGルール・台帳・チェックリスト）
  - docs/カード状態遷移_統合メモ_2026-07-04.md … 状態遷移の正（claim3経路・期限・供養）
  - docs/hikitsugi_20260705.md … 経路A/B/C実装のcanonical handoff
- .github/workflows/keepalive.yml … Supabase休眠防止の毎日ping（触らない）

## SQL置き場ルール
DBが正。GitHubのsql/には再現用・復元用のみ置く（命名＝用途_日付.sql）。それ以外のSQLは保存しない。

## 書いたらあかんもの（要点）
鍵・トークン・parent_token・未修正脆弱性の詳細・個人情報・short_idと人物の対応
