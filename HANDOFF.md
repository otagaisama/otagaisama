# HANDOFF.md（現在地と次の一手）
最終更新: 2026-07-14

## 今どこ
- DB全行監査 完了（2026-07-13・再実施不要）
- profiles権限修正 完了（2026-07-14 revoke済み）
- SQLファイル置き場整理 完了（2026-07-14 sql/へ移動）
- 印刷エンジン（2,000枚・4-up）着手前
- 印刷屋 返信待ち（ケント180kg・100枚実測厚み）
- docs/整理 進行中（引き継ぎMD5枚を順次アップ→Claudeがチェック）

## 次の一手
1. 引き継ぎMD 見つけた順にdocs/へ
2. 印刷屋返信きたら→lot_no体系→印刷エンジン

## リポジトリ内ファイル（本番HTML以外）
- BACKUP.md … バックアップ手順
- sql/ … SQLの保険置き場（下記ルール参照）
  - sql/discard_card_backup_20260711.sql … discard_card関数の原本（DB反映済み・復元用）
  - sql/migration_20260705_rls.sql … RLS定義の原本（DB反映済み・再現用）
- docs/ … テーマ別の正MD
  - docs/カード状態遷移_統合メモ_2026-07-04.md … 状態遷移の正（claim3経路・期限・供養）
- .github/workflows/keepalive.yml … Supabase休眠防止の毎日ping（触らない）

## SQL置き場ルール
DBが正。GitHubのsql/には再現用・復元用のみ置く（命名＝用途_日付.sql）。それ以外のSQLは保存しない。

## 書いたらあかんもの（要点）
鍵・トークン・parent_token・未修正脆弱性の詳細・個人情報・short_idと人物の対応
