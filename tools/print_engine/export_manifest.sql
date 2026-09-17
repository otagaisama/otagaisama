-- ① 事前チェック（lot番号の重複なし＝0行）
select lot_id, expires_at, created_at from bundles where lot_id in ('0001','0002','0003','0004');

-- ② 束を作る（1本ずつ実行。create_bundle_v2(p_lot_id, p_expires_at, p_count)。lot_no は関数が rooms に入れる）
-- select create_bundle_v2('0001', '2027-03-31 23:59:59+09', 100);
-- select create_bundle_v2('0002', '2027-03-31 23:59:59+09', 100);
-- select create_bundle_v2('0003', '2027-03-31 23:59:59+09', 100);
-- select create_bundle_v2('0004', '2027-03-31 23:59:59+09', 100);

-- ③ short_id が埋まっているか（0 であること）
select count(*) from rooms r join bundles b on b.id=r.bundle_id
where b.lot_id in ('0001','0002','0003','0004') and r.short_id is null;

-- ④ マニフェスト書き出し（結果セルをコピーして manifest.json に保存）。parent_token は出さない
select json_agg(json_build_object('short_id', r.short_id, 'global_no', r.global_no, 'lot_no', r.lot_no)
                order by b.lot_id, r.position) as manifest
from rooms r join bundles b on b.id = r.bundle_id
where b.lot_id in ('0001','0002','0003','0004');

-- 期限を延ばす／縮める
-- update bundles set expires_at = '2027-06-30 23:59:59+09' where lot_id in ('0001','0002','0003','0004');
