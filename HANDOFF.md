# HANDOFF.md（現在地と次の一手）
最終更新: 2026-07-22

## 今どこ
- セキュリティ監査: 第1次（2026-07-18〜19・22項目）＋第2次（2026-07-20・
  RPCのEXECUTE権限×内部ガード層）完了。第2次でcreate_bundle系のanon直叩き穴を
  発見→同日修正済み。詳細はdocs/監査マトリクス（7/20更新版）
- 適用済み: profiles対策一式（権限整理＋自動作成トリガー・配線確認済・
  2026-07-19 DB検証でanon/authenticatedはSELECTのみ確認）／
  room_posts DELETEポリシー／discard_card整備版／claimed_at埋め戻し／
  RPC権限最小化（2026-07-20: create_bundle v1封鎖・v2 anon剥奪・
  内部専用2本剥奪・delete_room等のanon剥奪）／
  レガシーposts緩いINSERTポリシー撤去（旧・軽微件①を前倒し消化）
- docs/整理: 正MD6枚アップ済み（監査マトリクス／電気通信事業法判断地図／
  規約プラポリ骨子／印刷エンジン実行指示書v1.3／大掃除リスト／
  rlsautotest実行指示書）・NGスキャン通過
- 印刷エンジン: 実行指示書v1.3確定（400枚バッチ×5回・4丁付け・両面・
  束100=山=1bundle・合紙不要）。冠野K1/K3/K4の返信待ちのみ
- 冠野栄興社: 確認メール送信済み（2026-07-20）・返信待ち
- 法務: 現状（収益ゼロ）は届出不要の公算。スポンサー収益開始の直前に届出。
  詳細はdocs/判断地図
- Netlify: 削除完了（2026-07-22）
- rlsautotest（RLSの自動実測検証・Supabaseニュースレター発）: 導入検証済み。
  公開前チェックの任意候補。本番直当て禁止＝使い捨てコピー必須。
  指示書はdocs/rlsautotest実行指示書_2026-07-19.md
- HANDOFF読込の注意: raw素読みはキャッシュで古い版が返ることがある。
  ?cb=タイムスタンプ付きで取得（Claudeメモリにルール化済み）

## 次の一手
1. 冠野返信きたら → K1/K3/K4を指示書v1.3に記入 → 実装チャット（Sonnet／
   Claude Code）へv1.3を渡して印刷エンジン実装
2. 実装後: 第1バッチPDF検品（QR読取・番号ズレ）→ 発注
3. mypage表示改修: global_no＋lot_no（「1-3」形式）表示（Sonnet向け・実装は1と前後可）
4. （任意・急がず）公開前チェックでrlsautotest実行（docs/指示書参照）

## 新規確定事項（2026-07-18〜20監査）
- admin系操作はoperator限定ポリシーで防御済み（クライアント判定は飾りでよい）
- XSS: ユーザー入力の出力箇所 全16箇所エスケープ済み・シロ
- 関数: SECURITY DEFINER 17本すべてsearch_path固定済み
- RPC権限層（7/20第2次）: 全18本のEXECUTE×内部ガード判定完了・穴は同日修正済み
- 教訓: 「auth.uid() is null＝SQL Editor」は誤り（anonキーREST直叩きでもnull）。
  definer関数の管理者ガードはEXECUTE権限側で絞る。新RPC作成時は
  revoke→必要ロールにgrantを儀式化
- card_access_log: 稼働中（列名はaccessed_at）。デバッグタスクは廃止
- claim_bundle現行版は正常（claimed_at記入あり）。空欄は旧版時代の痕跡で埋め戻し済み
- draft+message併存の原因はDELETEポリシー欠落→追加済みで再発防止。
  既存分（F点呼: 22件・2026-07-19時点）は大掃除リストへ集約
- lot_no採番は「バッチ-山」形式（例「1-3」）。「H」始まりは自家印刷用に予約・使用禁止
- bundles.lot_id列とadmin手動割当UIは既存。残りはmypage表示改修のみ
- mypage「お役目終了」ボタンは実装済み
- auth.htmlのprofiles書き込みはデッドコード化（トリガー方式に移行）→大掃除リストへ
- 軽微な堅牢化 残1件（非公開管理・詳細は監査チャット）→大掃除リストと同時に実施
  ※①は2026-07-20に前倒し消化済み
- 掃除系タスクはすべてdocs/大掃除リストに集約済み。実行は本番公開直前・前倒し禁止
- Supabase側仕様変更（2026-07）: log_connections新デフォルトoffへ自動移行・対応不要
- .nojekyll追加（2026-07-20）: Pages のJekyll処理を無効化。日本語ファイル名等による
  ビルド事故の恒久対策。削除禁止

## リポジトリ内ファイル（本番HTML以外）
- BACKUP.md … バックアップ手順
- .nojekyll … Pagesビルド設定（中身空で正常・削除禁止）
- sql/discard_card_backup_20260711.sql … discard_card原本（整備版適用前の控え）
- sql/migration_20260705_rls.sql … RLS定義原本
- docs/ … テーマ別の正MD（2026-07-20時点で新6枚を含む）

## 書いたらあかんもの（要点）
鍵・トークン・parent_token・未修正脆弱性の詳細・個人情報・short_idと人物の対応
