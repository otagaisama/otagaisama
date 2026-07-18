# HANDOFF.md（現在地と次の一手）
最終更新: 2026-07-19

## 今どこ
- セキュリティ監査: 全項目完了（2026-07-19）。admin権限・profiles・XSS・
  関数search_path・アクセスログ、すべて決着。詳細は監査チャット（Fable 2026-07-18〜19）
- 適用済み: profiles対策一式（権限整理＋自動作成トリガー・配線確認済）／
  room_posts DELETEポリシー／discard_card整備版／claimed_at埋め戻し
- 印刷エンジン: 実行指示書v0.9作成済み。TAKA決定点D1〜D3が未決
- 冠野栄興社: 確認メール文面作成済み（3点整理版）・送信待ち
- 法務: 現状（収益ゼロ）は届出不要の公算。スポンサー収益開始の直前に届出。
  規約・プラポリ骨子v0.1あり（監査チャット内）

## 次の一手
1. 冠野メール送信（スマホ可・最重要リマインダー）
2. D1〜D3決定 → 印刷エンジン指示書v1.0確定 → Sonnet実装へ
3. lot_no採番ルール決定（「H」始まり禁止が確定制約）→ mypage表示改修
4. docs/へ3枚アップ: 監査マトリクス／印刷指示書v0.9／規約・プラポリ骨子v0.1

## 新規確定事項（2026-07-18〜19監査）
- admin系操作はoperator限定ポリシーで防御済み（クライアント判定は飾りでよい）
- XSS: ユーザー入力の出力箇所 全16箇所エスケープ済み・シロ
- 関数: SECURITY DEFINER 17本すべてsearch_path固定済み
- card_access_log: 稼働中（列名はaccessed_at）。デバッグタスクは不要につき廃止
- claim_bundle現行版は正常（claimed_at記入あり）。空欄は旧版時代の痕跡で埋め戻し済み
- draft+message併存の原因はDELETEポリシー欠落→追加済みで再発防止。
  既存分（F点呼: 22件・2026-07-19時点）は本番前の大掃除で削除
- lot_no採番は「H」始まり禁止（mypageが自家印刷判定に使用）
- bundles.lot_id列とadmin手動割当UIは既存。残りは採番ルール＋mypage表示のみ
- mypage「お役目終了」ボタンは実装済み
- auth.htmlのprofiles書き込みはデッドコード化（トリガー方式に移行）→後日掃除
- 公開前リスト: rooms自己更新の列制限（RPC化）／レガシーpostsテーブルの緩いポリシー撤去

## リポジトリ内ファイル（本番HTML以外）
- BACKUP.md … バックアップ手順
- sql/discard_card_backup_20260711.sql … discard_card原本（整備版適用前の控え）
- sql/migration_20260705_rls.sql … RLS定義原本
- docs/ … テーマ別の正MD

## 書いたらあかんもの（要点）
鍵・トークン・parent_token・未修正脆弱性の詳細・個人情報・short_idと人物の対応

## SQL置き場ルール
DBが正。GitHubのsql/には再現用・復元用のみ置く（命名＝用途_日付.sql）。それ以外のSQLは保存しない。

## 書いたらあかんもの（要点）
鍵・トークン・parent_token・未修正脆弱性の詳細・個人情報・short_idと人物の対応
