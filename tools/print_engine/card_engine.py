#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
こころづて 印刷屋用カードエンジン v0.1（2026-09-17）
- ReportLab + qrcode。CMYK直指定・フォント埋め込み・QRはベクター直描画
- 4丁付け（既定）cut-and-stack: カードc(1..N) → シートn=((c-1)%B)+1, 面位置k=(c-1)//B
- 表は全数同一（表に可変データを置かない）。裏はQR/short_id/lot_no/協賛が可変
- 裏面ミラー無し（冠野K3: 版下は同方向でUP、刷版で調整）。config.sheet.mirror_back で切替可

使い方:
  python card_engine.py --make-dummy manifest_dummy.json      # ダミー400件を作る
  python card_engine.py --config config.json --manifest manifest.json --out batch_0001.pdf
  python card_engine.py ... --sheets 1                          # 先頭1シート分（表裏2ページ）だけ出す
"""
import argparse, json, os, sys, random, urllib.request, csv
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import CMYKColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
FONT_SRC = {  # Google Fonts (OFL) の原本。無ければ自動取得
    "ShipporiMincho-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/shipporimincho/ShipporiMincho-Regular.ttf",
    "ShipporiMincho-Bold.ttf":    "https://raw.githubusercontent.com/google/fonts/main/ofl/shipporimincho/ShipporiMincho-Bold.ttf",
    "ZenKakuGothicNew-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/zenkakugothicnew/ZenKakuGothicNew-Regular.ttf",
}
SHORT_ID_CHARSET = set("abcdefhjkmnpqrtuvwxy0123456789")  # 30文字セット（2026-08-07確定）
ECC = {"L": ERROR_CORRECT_L, "M": ERROR_CORRECT_M, "Q": ERROR_CORRECT_Q, "H": ERROR_CORRECT_H}


# ---------- 準備 ----------
def ensure_fonts():
    os.makedirs(FONT_DIR, exist_ok=True)
    for name, url in FONT_SRC.items():
        p = os.path.join(FONT_DIR, name)
        if not os.path.exists(p):
            print(f"[font] downloading {name}")
            urllib.request.urlretrieve(url, p)
    pdfmetrics.registerFont(TTFont("SMR", os.path.join(FONT_DIR, "ShipporiMincho-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("SMB", os.path.join(FONT_DIR, "ShipporiMincho-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("ZKG", os.path.join(FONT_DIR, "ZenKakuGothicNew-Regular.ttf")))


def cmyk(v):
    return CMYKColor(*v)


def load_manifest(path):
    """JSON: [{"short_id":..., "global_no":...}, ...] または CSV（ヘッダ short_id,global_no）。順序＝カード番号c"""
    if path.lower().endswith(".csv"):
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    else:
        with open(path, encoding="utf-8") as f:
            rows = json.load(f)
    return rows


def validate_manifest(rows, cfg):
    B = cfg["batch"]["cards_per_stack"]; S = cfg["batch"]["stacks"]; N = B * S
    errs = []
    if len(rows) != N:
        errs.append(f"件数 {len(rows)} ≠ {N}（{B}枚×{S}山）")
    ids = [r["short_id"] for r in rows]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        errs.append(f"short_id 重複: {sorted(dup)}")
    bad = [i for i in ids if not (isinstance(i, str) and len(i) == 6 and set(i) <= SHORT_ID_CHARSET)]
    if bad:
        errs.append(f"short_id 文字セット違反（旧文字 g i l o s z か桁違い）: {bad[:10]}{' …' if len(bad) > 10 else ''}")
    return errs


def make_dummy(path, cfg):
    B = cfg["batch"]["cards_per_stack"]; S = cfg["batch"]["stacks"]
    rnd = random.Random(20260917)
    chars = sorted(SHORT_ID_CHARSET); seen = set(); rows = []
    while len(rows) < B * S:
        s = "".join(rnd.choice(chars) for _ in range(6))
        if s in seen:
            continue
        seen.add(s); rows.append({"short_id": s, "global_no": 900000 + len(rows) + 1, "dummy": True})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=0)
    print(f"[dummy] {len(rows)} 件 → {path}")


# ---------- QR ----------
def qr_matrix(text, ecc):
    q = qrcode.QRCode(error_correction=ECC[ecc], border=0)
    q.add_data(text); q.make(fit=True)
    return q.get_matrix(), q.version


def draw_qr(c, x0, y0, size_mm, matrix, ink):
    """x0,y0 = 左下（mm）。行ごとに黒の連続区間を1本のrectにまとめる（オブジェクト数削減）"""
    n = len(matrix); cell = size_mm / n
    c.setFillColor(ink); c.setStrokeColor(ink); c.setLineWidth(0)
    p = c.beginPath()
    for r, row in enumerate(matrix):
        y = y0 + (n - 1 - r) * cell
        col = 0
        while col < n:
            if row[col]:
                start = col
                while col < n and row[col]:
                    col += 1
                p.rect((x0 + start * cell) * mm, y * mm, (col - start) * cell * mm, cell * mm)
            else:
                col += 1
    c.drawPath(p, stroke=0, fill=1)



# ---------- ベクターロゴ（PDF）埋め込み ----------
_XOBJ_CACHE = {}


def draw_pdf_logo(c, path, regions, x_mm, y_mm, box_w_mm, box_h_mm):
    """PDFロゴ1ページをフォームXObjectとして埋め込み、枠(box)に収める。色はロゴのまま（CMYKならCMYKのまま通る）。
    regions=[[x0,y0,x1,y1,dx], ...]（元PDFのpt座標。dx=横シフトpt）で部分だけ拾って詰められる。省略時はArtBox/MediaBox全体"""
    from pdfrw import PdfReader as _PR
    from pdfrw.buildxobj import pagexobj
    from pdfrw.toreportlab import makerl
    key = (id(c), path)
    if key not in _XOBJ_CACHE:
        pg = _PR(path).pages[0]
        for k in ("/PieceInfo", "/Thumb", "/LastModified", "/Metadata"):  # Illustratorの私物データはReportLabで落ちるので外す
            if k in pg: del pg[k]
        if pg.Resources and "/Properties" in pg.Resources: del pg.Resources["/Properties"]
        _XOBJ_CACHE[key] = (makerl(c, pagexobj(pg)), pg)
    form, pg = _XOBJ_CACHE[key]
    if not regions:
        box = pg.ArtBox or pg.MediaBox
        b = [float(v) for v in box]; regions = [[b[0], b[1], b[2], b[3], 0]]
    # 合成後の外接矩形
    minx = min(r[0] + r[4] for r in regions); maxx = max(r[2] + r[4] for r in regions)
    miny = min(r[1] for r in regions); maxy = max(r[3] for r in regions)
    cw, ch = maxx - minx, maxy - miny
    sc = min(box_w_mm * mm / cw, box_h_mm * mm / ch)
    ox = x_mm * mm; oy = (y_mm + box_h_mm) * mm - ch * sc  # 枠の上端に揃える
    for r in regions:
        c.saveState()
        c.translate(ox, oy); c.scale(sc, sc); c.translate(-minx, -miny)
        p = c.beginPath(); p.rect(r[0] + r[4], r[1], r[2] - r[0], r[3] - r[1]); c.clipPath(p, stroke=0, fill=0)
        c.translate(r[4], 0)
        c.doForm(form)
        c.restoreState()

# ---------- 文字ユーティリティ ----------
def _text(c, x_pt, y_pt, s, font, size, ink, charspace):
    t = c.beginText(); t.setTextOrigin(x_pt, y_pt); t.setFont(font, size)
    t.setFillColor(ink); t.setCharSpace(charspace); t.textOut(s); c.drawText(t)


def text_c(c, x_mm, y_mm, s, font, size, ink, charspace=0):
    w = pdfmetrics.stringWidth(s, font, size) + charspace * max(len(s) - 1, 0)
    _text(c, x_mm * mm - w / 2, y_mm * mm, s, font, size, ink, charspace)


def text_l(c, x_mm, y_mm, s, font, size, ink, charspace=0):
    _text(c, x_mm * mm, y_mm * mm, s, font, size, ink, charspace)


# ---------- カード面 ----------
def ink(cfg, name):
    """'sumi'/'shu'/'kin' か [c,m,y,k]"""
    C = cfg["colors"]
    return cmyk(C[name]) if isinstance(name, str) else cmyk(name)


def draw_front(c, cfg, variant):
    """原点＝トリム左下。単位mm。数値は config.layout.front"""
    L = cfg["layout"]["front"]; T = cfg["text"]
    mono = variant.get("mono", False) and not cfg.get("front_identical", True)
    W, H = cfg["card"]["w_mm"], cfg["card"]["h_mm"]
    col = lambda n: ink(cfg, "sumi" if mono else n)
    text_l(c, L["en_x"], H - L["en_y"], T["front_en"], "ZKG", L["en_size"], col(L["en_color"]), charspace=L["en_space"])
    text_c(c, W / 2, H - L["ja_y"], T["front_ja"], "SMB", L["ja_size"], col("sumi"), charspace=L["ja_space"])
    text_c(c, W / 2, H - L["tag_y"], T["front_tag"], "SMR", L["tag_size"], col(L["tag_color"]), charspace=L["tag_space"])
    if T.get("front_invite"):
        text_c(c, W / 2, H - L["invite_y"], T["front_invite"], "SMR", L["invite_size"], col(L["invite_color"]), charspace=L["invite_space"])


def draw_back(c, cfg, variant, card):
    L = cfg["layout"]["back"]; T = cfg["text"]; K = cfg["card"]
    mono = variant.get("mono", False)
    col = lambda n: ink(cfg, "sumi" if mono else n)
    sumi = ink(cfg, "sumi"); kin = col("kin")
    W, H, S = K["w_mm"], K["h_mm"], K["safe_mm"]
    # 左列：QR / short_id / lot_no
    qr_mm = K["qr_mm"]; lx = L["left_cx"]
    matrix, ver = qr_matrix(cfg["batch"]["url_base"] + card["short_id"], K["qr_ecc"])
    draw_qr(c, lx - qr_mm / 2, H - L["qr_top"] - qr_mm, qr_mm, matrix, sumi)
    text_c(c, lx, H - L["sid_y"], card["short_id"], "Courier-Bold", L["sid_size"], sumi, charspace=1.0)
    bw, bh = L["lot_box_w"], L["lot_box_h"]
    c.setStrokeColor(kin); c.setLineWidth(0.4)
    c.roundRect((lx - bw / 2) * mm, (H - L["lot_top"] - bh) * mm, bw * mm, bh * mm, 1.2 * mm, stroke=1, fill=0)
    text_c(c, lx, H - L["lot_top"] - bh + (bh - L["lot_size"] * 0.25) / 2 - 0.3, card["lot_no"], "Helvetica-Bold", L["lot_size"], sumi, charspace=0.6)
    # 右列：固定文（長い行は自動で折り返す）
    rx = L["right_x"]; rw = W - S - rx
    y = H - L["lines_top"]; fs = L["lines_size"]; cs = L["lines_space"]
    for line in T["back_lines"]:
        for seg in [x for part in line.split("\n") for x in wrap_jp(part, "SMR", fs, cs, rw * mm)]:  # \n で手動改行
            text_l(c, rx, y, seg, "SMR", fs, sumi, charspace=cs); y -= L["lines_lead"]
    sp = variant.get("sponsor")
    if sp:
        ry = H - L["sponsor_rule_top"]
        c.setStrokeColor(kin); c.setLineWidth(0.3); c.line(rx * mm, ry * mm, (rx + rw) * mm, ry * mm)
        text_l(c, rx, H - L["sponsor_lead_top"], T["sponsor_lead"], "SMR", L["sponsor_lead_size"], sumi, charspace=0.2)
        lf = os.path.join(HERE, sp.get("file") or "")
        box_top = H - L["logo_top"]; bh_ = L["logo_h"]; bw_ = min(rw, L["logo_w"])
        if sp.get("type") == "pdf" and os.path.exists(lf):
            draw_pdf_logo(c, lf, sp.get("regions"), rx, box_top - bh_, bw_, bh_)
        elif sp.get("type") == "logo" and os.path.exists(lf):
            from reportlab.lib.utils import ImageReader
            img = ImageReader(lf); iw, ih = img.getSize()
            sc = min(bw_ / iw, bh_ / ih); dw, dh = iw * sc, ih * sc
            c.drawImage(img, rx * mm, (box_top - dh) * mm, dw * mm, dh * mm, mask="auto")
        else:
            style = sp.get("style", "A"); name = sp.get("name", ""); ty = box_top - bh_ * 0.7
            if style == "A":    # 明朝ボールド・大きく・字間広め（ワードマーク風）
                text_l(c, rx, ty, name, "SMB", L["sponsor_text_size"], sumi, charspace=2.0)
            elif style == "B":  # ゴシック・大きく（ロゴ無しの店の看板文字に近い）
                text_l(c, rx, ty, name, "ZKG", L["sponsor_text_size"], sumi, charspace=1.2)
            elif style == "C":  # 金の枠に社名（lot_no枠と同じ意匠で揃える）
                tw = pdfmetrics.stringWidth(name, "SMB", L["sponsor_text_size"]) / mm + 8
                c.setStrokeColor(kin); c.setLineWidth(0.4)
                c.roundRect(rx * mm, (box_top - bh_) * mm, tw * mm, bh_ * mm, 1.2 * mm, stroke=1, fill=0)
                text_c(c, rx + tw / 2, ty, name, "SMB", L["sponsor_text_size"], sumi, charspace=1.0)
    # URL: variant.url_pos = right（右列下）/ left（左列・lot枠の下。判子用に右下を空ける）/ none
    pos = variant.get("url_pos", "right" if sp else "left")
    ft = T["footer_url"] + (f"    {cfg['date']}" if L.get("footer_show_date", False) else "")
    if pos == "right":
        text_l(c, rx, L["footer_y"], ft, "ZKG", L["footer_size"], kin, charspace=0.8)
    elif pos == "left":
        text_c(c, lx, L["footer_y"], ft, "ZKG", L["footer_size"], kin, charspace=0.8)


def wrap_jp(s, font, size, charspace, max_w_pt):
    """幅に収まらなければ文字単位で折り返す（句読点が行頭に来たら前行末へ）"""
    out, cur = [], ""
    for ch in s:
        trial = cur + ch
        w = pdfmetrics.stringWidth(trial, font, size) + charspace * max(len(trial) - 1, 0)
        if w > max_w_pt and cur:
            if ch in "、。」）":
                cur += ch; out.append(cur); cur = ""; continue
            out.append(cur); cur = ch
        else:
            cur = trial
    if cur: out.append(cur)
    return out


# ---------- 面付け ----------
def trim_marks(c, x, y, w, h, bleed, ink):
    """x,y=トリム左下(mm)。塗り足しの外側1〜5mmに日本式のコーナートンボ（トリム線＋塗り足し線）"""
    c.setStrokeColor(ink); c.setLineWidth(0.1)
    L0, L1 = bleed + 1.0, bleed + 5.0
    for (cx, sx) in ((x, -1), (x + w, 1)):
        for (cy, sy) in ((y, -1), (y + h, 1)):
            # 水平線（トリム位置・塗り足し位置）を外側へ
            for yy in (cy, cy + sy * bleed):
                c.line((cx + sx * L0) * mm, yy * mm, (cx + sx * L1) * mm, yy * mm)
            for xx in (cx, cx + sx * bleed):
                c.line(xx * mm, (cy + sy * L0) * mm, xx * mm, (cy + sy * L1) * mm)


def sheet_positions(cfg):
    sh = cfg["sheet"]; K = cfg["card"]
    pw, ph = sh["page_w_mm"], sh["page_h_mm"]
    cols, rows, gap, bleed = sh["cols"], sh["rows"], sh["gap_mm"], sh["bleed_mm"]
    bw, bh = K["w_mm"] + 2 * bleed, K["h_mm"] + 2 * bleed
    tw, th = cols * bw + (cols - 1) * gap, rows * bh + (rows - 1) * gap
    ox, oy = (pw - tw) / 2, (ph - th) / 2
    pos = []  # k=0 左上, 1 右上, 2 左下, 3 右下（読み順）
    for r in range(rows):
        for col in range(cols):
            x = ox + col * (bw + gap) + bleed
            y = oy + (rows - 1 - r) * (bh + gap) + bleed
            pos.append((x, y))
    return pos


def draw_sheet(c, cfg, cards_on_sheet, side, sheet_no, total_sheets):
    """cards_on_sheet: 面位置k順のカードdict（Noneは空き）"""
    sh = cfg["sheet"]; K = cfg["card"]; C = cfg["colors"]
    W, H, bleed = K["w_mm"], K["h_mm"], sh["bleed_mm"]
    pos = sheet_positions(cfg)
    if side == "back" and sh.get("mirror_back", False):
        cols = sh["cols"]; pos = [pos[r * cols + (cols - 1 - i)] for r in range(sh["rows"]) for i in range(cols)]
    sumi = cmyk(C["sumi"])
    for k, card in enumerate(cards_on_sheet):
        if card is None:
            continue
        x, y = pos[k]
        variant = card["_design"]
        trim_marks(c, x, y, W, H, bleed, sumi)
        c.saveState(); c.translate(x * mm, y * mm)
        if side == "front":
            draw_front(c, cfg, variant)
        else:
            draw_back(c, cfg, variant, card)
        c.restoreState()
    # シート外周のラベル（断裁で落ちる位置）
    lots = ", ".join((cd["lot"] if cd else "----") for cd in cards_on_sheet)
    label = f"{cfg['batch']['label']}  sheet {sheet_no:03d}/{total_sheets:03d}  {'表 FRONT' if side == 'front' else '裏 BACK'}  (lot {lots})"
    text_l(c, 10, sh["page_h_mm"] - 6, label, "ZKG", 7, sumi)
    # センタートンボ
    pw, ph = sh["page_w_mm"], sh["page_h_mm"]
    c.setStrokeColor(sumi); c.setLineWidth(0.1)
    for (x1, y1, x2, y2) in ((pw / 2, 2, pw / 2, 7), (pw / 2, ph - 2, pw / 2, ph - 7), (2, ph / 2, 7, ph / 2), (pw - 2, ph / 2, pw - 7, ph / 2)):
        c.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)



def lot_table(cfg, S, lps):
    """束ごとのデザイン表を返す（長さ S*lps）。config["lots"] があればそれ、無ければ variants（山ごと）を展開"""
    if "lots" in cfg:
        lots = cfg["lots"]
        assert len(lots) == S * lps, f"lots は {S * lps} 件必要（{S}山×{lps}束）、今 {len(lots)} 件"
        return lots
    out = []
    for k in range(S):
        v = cfg["variants"][k]
        for j in range(lps):
            out.append({**v, "lot": f"{int(v['lot']) + j:04d}"})
    return out


def build(cfg, rows, out_path, sheets_limit=None):
    B = cfg["batch"]["cards_per_stack"]; S = cfg["batch"]["stacks"]
    if "lots" not in cfg: assert len(cfg["variants"]) == S, "variants の数と stacks が一致しない"
    # カードc → (シートn, 面位置k) と lot_no
    # lot: 山k内で sheets_per_lot（既定100）シートごとに繰り上がる。config["lots"] は山0の束→山1の束…の順
    spl = cfg["batch"].get("sheets_per_lot", B); lps = -(-B // spl)  # 1山あたりの束数
    lots = lot_table(cfg, S, lps)
    cards = []
    for i, r in enumerate(rows):
        cnum = i + 1; n = (cnum - 1) % B + 1; k = (cnum - 1) // B
        li = k * lps + (n - 1) // spl; pos = (n - 1) % spl + 1
        lot_no = f"{lots[li]['lot']}-{pos:03d}"
        if r.get("lot_no"):  # DBの lot_no を正とし、並び順との食い違いは止める
            if r["lot_no"] != lot_no:
                raise SystemExit(f"[NG] c={cnum}: マニフェストの lot_no {r['lot_no']} ≠ 面付け計算 {lot_no}。manifest の並び（lot→position）か config.lots を確認")
        cards.append({**r, "c": cnum, "sheet": n, "k": k, "lot": lots[li]["lot"], "lot_no": lot_no, "_design": lots[li]})
    total = B if sheets_limit is None else min(B, sheets_limit)
    sh = cfg["sheet"]
    c = canvas.Canvas(out_path, pagesize=(sh["page_w_mm"] * mm, sh["page_h_mm"] * mm), pageCompression=1)
    c.setTitle(cfg["batch"]["label"]); c.setAuthor("HeartCloak Project")
    for n in range(1, total + 1):
        on_sheet = [next((cd for cd in cards if cd["sheet"] == n and cd["k"] == k), None) for k in range(S)]
        draw_sheet(c, cfg, on_sheet, "front", n, B); c.showPage()
        draw_sheet(c, cfg, on_sheet, "back", n, B); c.showPage()
    c.save()
    return cards


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "config.json"))
    ap.add_argument("--manifest")
    ap.add_argument("--out")
    ap.add_argument("--sheets", type=int, default=None, help="先頭nシートだけ出す（試し刷り用）")
    ap.add_argument("--make-dummy", metavar="PATH", help="ダミーマニフェストを書き出して終了")
    a = ap.parse_args()
    with open(a.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if a.make_dummy:
        make_dummy(a.make_dummy, cfg); return
    if not (a.manifest and a.out):
        ap.error("--manifest と --out が要る")
    ensure_fonts()
    rows = load_manifest(a.manifest)
    errs = validate_manifest(rows, cfg)
    if errs:
        print("[NG] マニフェスト検証失敗:"); [print("  -", e) for e in errs]; sys.exit(1)
    cards = build(cfg, rows, a.out, a.sheets)
    # 照合レポート（lot_no ↔ short_id ↔ global_no）
    rep = os.path.splitext(a.out)[0] + "_manifest_report.csv"
    with open(rep, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["c", "sheet", "k", "lot_no", "short_id", "global_no", "url", "sponsor", "mono"])
        for cd in cards:
            d = cd["_design"]; spn = (d.get("sponsor") or {}).get("name", "")
            w.writerow([cd["c"], cd["sheet"], cd["k"], cd["lot_no"], cd["short_id"], cd.get("global_no", ""), cfg["batch"]["url_base"] + cd["short_id"], spn, d.get("mono", False)])
    _, ver = qr_matrix(cfg["batch"]["url_base"] + rows[0]["short_id"], cfg["card"]["qr_ecc"])
    print(f"[OK] {a.out}  cards={len(cards)}  QR version={ver} ({17 + 4 * ver}x{17 + 4 * ver}, ECC {cfg['card']['qr_ecc']}, "
          f"{cfg['card']['qr_mm'] / (17 + 4 * ver):.3f} mm/module)  report={rep}")


if __name__ == "__main__":
    main()
