-- 2026-07-05 穴の総点検：フロント直書きテーブルのRLS締め
-- ③ room_posts INSERT（偽メッセージ/偽返信の改ざん封じ）
drop policy if exists "users can insert room_posts" on public.room_posts;
create policy "users can insert room_posts"
on public.room_posts for insert to authenticated
with check (
  auth.uid() = user_id
  and post_type in ('draft','message')
  and exists (select 1 from public.rooms r
              where r.room_id = room_posts.room_id and r.user_id = auth.uid())
);

-- ① rooms INSERT（他人名義の部屋乱造封じ）
drop policy if exists "users can insert rooms" on public.rooms;
create policy "users can insert rooms"
on public.rooms for insert to authenticated
with check ( auth.uid() = user_id );

-- ⑥ storage upload（他人フォルダへの画像割り込み封じ）
drop policy if exists "Authenticated upload room-images" on storage.objects;
create policy "Authenticated upload room-images"
on storage.objects for insert to authenticated
with check (
  bucket_id = 'room-images'
  and exists (select 1 from public.rooms r
              where r.room_id::text = split_part(objects.name, '/', 1)
                and r.user_id = auth.uid())
);
