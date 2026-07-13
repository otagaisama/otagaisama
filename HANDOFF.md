# HANDOFF.md（現在地と次の一手）
最終更新: 2026-07-14

## 今どこ
- DB全行監査 完了（2026-07-13・再実施不要）
- profiles権限の修正SQL 未実行 ★最優先
- 印刷エンジン（2,000枚・4-up）着手前
- 冠野栄興社 返信待ち（ケント180kg・100枚実測厚み）
- docs/整理 進行中（引き継ぎMD5枚を順次アップ→Claudeがチェック）

## 次の一手
1. profiles権限修正SQL実行（anon/authenticatedからINSERT/UPDATE/DELETEをrevoke）
2. 引き継ぎMD 見つけた順にdocs/へ
3. 冠野返信きたら→lot_no体系→印刷エンジン

## リポジトリ内ファイル（本番HTML以外）
- BACKUP.md … バックアップ手順
- discard_card_backup_20260711.sql … discard_card関数の原本（DB反映済み）
- migration_20260705_rls.sql … RLS定義の原本（DB反映済み）
- docs/ … テーマ別の正MD

## 書いたらあかんもの（要点）
鍵・トークン・parent_token・未修正脆弱性の詳細・個人情報・short_idと人物の対応
