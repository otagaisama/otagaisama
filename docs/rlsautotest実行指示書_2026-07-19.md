# rlsautotest実行指示書（Claude Code用・B方式）
出所: Claude（Fable）／ 初版: 2026-07-19 ／ 実行タイミング: 公開前チェック時（急ぎでない）

## 前提確認（順に。無ければそこで報告して停止）
1. Docker Desktopが起動するか（無ければ導入相談に戻す）
2. pg_dumpが使えるか: `pg_dump --version`（無ければ `winget install PostgreSQL.PostgreSQL.17` のクライアントのみで可）

## 手順（本番には一切書き込まない。dumpは読み取りのみ）
1. バックアップ兼素材取得（Session pooler経由・パスワードはTAKAが入力）:
   pg_dump "postgresql://postgres.damussuizcfzqkfkpwwm:【PW】@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres" --schema=public --no-owner -F c -f rls_copy.dump
2. 使い捨てDB起動:
   docker run -d --name rlstest -e POSTGRES_PASSWORD=test -p 55432:5432 postgres:17
3. 復元:
   pg_restore -d "postgresql://postgres:test@localhost:55432/postgres" --no-owner rls_copy.dump
   ※auth.usersが無い等のエラーは想定内。roles(anon/authenticated)作成が要る場合:
   psql同URLで CREATE ROLE anon NOLOGIN; CREATE ROLE authenticated NOLOGIN; CREATE ROLE service_role NOLOGIN; を先に実行して再restore
4. 実行:
   pip install rlsautotest
   rlsautotest --db-url "postgresql://postgres:test@localhost:55432/postgres" --schema public --html rls-report.html
5. rls-report.htmlを開き、監査マトリクス（docs/監査マトリクス_2026-07-18.md）の22項目と突き合わせ
6. 後片付け: docker rm -f rlstest ／ rls_copy.dumpは C:\backup へ移動（バックアップ兼用）

## 禁止事項
- 本番URL（pooler含む）を --db-url に渡さない
- 生成物にパスワードを書き残さない
