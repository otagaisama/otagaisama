-- discard_card 差し替え前の原本（2026-07-11 取得）
-- 戻したいときはこの中身をSupabase SQL Editorに貼ってRunすれば復元できる

CREATE OR REPLACE FUNCTION public.discard_card(p_key text, p_reason text DEFAULT NULL::text)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
DECLARE
  v_old rooms%ROWTYPE;
  v_uid uuid := auth.uid();
  v_allowed boolean := false;
BEGIN
  IF v_uid IS NULL THEN
    RETURN jsonb_build_object('ok', false, 'error', 'login_required');
  END IF;

  -- カード特定（short_id 優先、なければ room_id として解釈）
  SELECT * INTO v_old FROM rooms WHERE short_id = p_key FOR UPDATE;
  IF NOT FOUND THEN
    BEGIN
      SELECT * INTO v_old FROM rooms WHERE room_id = p_key::uuid FOR UPDATE;
    EXCEPTION WHEN invalid_text_representation THEN NULL;
    END;
  END IF;

  IF v_old.id IS NULL THEN
    RETURN jsonb_build_object('ok', false, 'error', 'not_found');
  END IF;
  IF v_old.closed_at IS NOT NULL THEN
    RETURN jsonb_build_object('ok', false, 'error', 'card_closed');
  END IF;
  IF v_old.short_id IS NULL THEN
    RETURN jsonb_build_object('ok', false, 'error', 'no_short_id');
  END IF;

  -- ★完結保護：往復成立（reply あり）は誰も終了できない
  IF EXISTS (
    SELECT 1 FROM room_posts
    WHERE room_id = v_old.room_id AND post_type = 'reply'
  ) THEN
    RETURN jsonb_build_object('ok', false, 'error', 'completed_locked');
  END IF;

  -- 権限1：現所有者/作成者による「お役目終了」（白紙・書きかけ・送信済みのうち未完結のみ）
  IF v_old.user_id = v_uid THEN
    v_allowed := true;
  -- 権限2：レガシー救済（移行前の完成カード＝確定済み部屋の返信者）
  ELSIF v_old.is_confirmed AND EXISTS (
    SELECT 1 FROM room_posts
    WHERE room_id = v_old.room_id AND user_id = v_uid AND post_type = 'reply'
  ) THEN
    v_allowed := true;
  END IF;

  IF NOT v_allowed THEN
    RETURN jsonb_build_object('ok', false, 'error', 'not_owner');
  END IF;

  -- カードを閉じる（short_id は残す＝お役目終了表示・番号再利用なし）
  UPDATE rooms SET closed_at = now() WHERE id = v_old.id;

  INSERT INTO room_transfers (room_id, from_user, to_user, transferred_at, transfer_type, reason)
  VALUES (v_old.id, COALESCE(v_old.owner_user_id, v_old.user_id), v_uid, now(), 'discard', NULLIF(trim(p_reason), ''));

  RETURN jsonb_build_object('ok', true);
END;
$function$;
