バックアップ手順メモ(2026-07-12確立)
Supabaseバックアップ(DBいじった日の夜)

cmd を開く
cd C:\backup
node dump.js

→ supabase_backup_日付.sql ができたら完了(10秒)
GitHubバックアップ(月1 or 節目)

cmd を開く
cd C:\backup\otagaisama.git
git remote update

→ 完了(差分だけ取るので数秒)
トラブル時

cmd で claude を起動して「dump.js が動かん、直して」と依頼
DBパスワードを変えた時は dump.js の password: 行の書き換えが必要
(claudeに「パスワード変えた、新しいのは○○」と言えばやってくれる)

現在の接続構成(dump.js内)

host: aws-1-ap-northeast-1.pooler.supabase.com(Session pooler・東京)
port: 5432 / user: postgres.damussuizcfzqkfkpwwm
理由: 自宅回線がIPv4のみのため Direct接続(IPv6専用)は不可

保管

C:\backup を時々USBかクラウドにもコピー(PC故障対策)
DBパスワードは dump.js 内に平文である点に注意(このPC内限定の扱い)
