"""
Evidence mining — Venture Arena / Hướng A (VLearn AI Tutor)
==========================================================
Sinh toàn bộ con số trong spec §1-§2. Chạy lại được, không phụ thuộc state.

Chạy:   PYTHONIOENCODING=utf-8 python evidence_mining.py
Cần:    pandas
Data:   trỏ DATA_DIR về data/vlearn-pack (KHÔNG copy data vào repo nộp bài)

PHƯƠNG PHÁP ĐẾM (ghi vào spec §1 — R1 đòi "kiểm lại được"):
  - Đơn vị đếm = 1 turn = 1 cặp (student message, tutor message), khớp bằng turn_id.
    File có 2.522 dòng = 1.261 turn. Mọi tỉ lệ tính trên 1.261 turn.
  - "not-found" = câu trả lời của tutor khớp regex NOTFOUND (xem dưới). Đây là cách
    tutor tự khai nó không tìm được căn cứ trong tài liệu.
  - "pushback" = trong câu trả lời not-found, tutor yêu cầu học viên tự cung cấp
    nội dung / từ khoá / tiêu đề.
  - intent gán bằng regex theo thứ tự ưu tiên (summarize > explain_page > page_ref >
    logistics > noise > content_question). Regex có sai số → BẮT BUỘC soát tay 30 mẫu
    (hàm sample_for_manual_audit) và ghi kết quả soát vào spec.
"""
import os, re, io, glob, json, collections, math
import pandas as pd

# đường dẫn tương đối theo vị trí file này -> chạy được trên máy mọi thành viên
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'vlearn-pack')
CSV = os.path.join(DATA_DIR, 'chatlog', 'chat_history_anonymized_for_hackathon.csv')

# --------------------------------------------------------------------------- #
# 1. Dựng bảng turn
# --------------------------------------------------------------------------- #
SEL_PAT = re.compile(r'^\(Trang (\d+), đoạn được chọn: "(.*?)"\)\s*\n?(.*)$', re.S)

NOTFOUND = re.compile(
    r'(không tìm thấy|chưa tìm thấy|không thể truy (cập|xuất)|không có (trong|nội dung)'
    r'|không khớp|không bao gồm trang|không được hiển thị|không đề cập)', re.I)

REFUSAL = re.compile(
    r'(rất tiếc|xin lỗi|không tìm thấy|không thể truy (cập|xuất)|không có (quyền|thông tin)'
    r'|không khớp|chưa tìm thấy|không được (đề cập|hiển thị)|không bao gồm|không đề cập)', re.I)

PUSHBACK = re.compile(
    r'(cung cấp thêm|chia sẻ thêm|cho (tôi|mình) biết|bạn có thể (cho|cung cấp|chia sẻ)'
    r'|từ khoá|từ khóa|tiêu đề|nội dung (chính|của) trang|vui lòng cho biết)', re.I)


def load_turns(csv=CSV):
    df = pd.read_csv(csv)
    df['message_created_at'] = pd.to_datetime(df.message_created_at)

    piv = df.pivot_table(index='turn_id', columns='role', values='content', aggfunc='first')
    meta_cols = ['conversation_id', 'user_id', 'day_code', 'move_used', 'citations',
                 'rating', 'asked_check_question', 'avg_latency_ms', 'message_created_at']
    t = piv.join(df[df.role == 'tutor'].set_index('turn_id')[meta_cols])

    t['student'] = t.student.astype(str)
    t['tutor'] = t.tutor.astype(str)

    def parse(s):
        m = SEL_PAT.match(s)
        if m:
            return pd.Series({'page': int(m.group(1)), 'sel': m.group(2), 'q': m.group(3).strip()})
        return pd.Series({'page': None, 'sel': None, 'q': s.strip()})

    t = t.join(t.student.apply(parse))
    t['sel_len'] = t.sel.fillna('').str.len()
    t['q_words'] = t.q.str.split().str.len()
    t['t_words'] = t.tutor.str.split().str.len()
    t['n_cit'] = t.citations.fillna('[]').apply(
        lambda s: len(json.loads(s)) if isinstance(s, str) else 0)

    t['notfound'] = t.tutor.str.contains(NOTFOUND)
    t['refused'] = t.tutor.str.contains(REFUSAL)
    t['pushback'] = t.notfound & t.tutor.str.contains(PUSHBACK)
    t['intent'] = t.q.apply(classify_intent)

    t = t.sort_values(['conversation_id', 'message_created_at'])
    t['seq'] = t.groupby('conversation_id').cumcount() + 1
    t['is_last_turn'] = t.seq == t.groupby('conversation_id').seq.transform('max')
    return t


def classify_intent(q):
    """Ưu tiên từ trên xuống. Sai số ~5-10% -> soát tay 30 mẫu trước CP4."""
    ql = str(q).lower()
    if re.search(r'tóm tắt|tổng hợp|toàn bộ|tất cả nội dung|summar|note lại|ôn lại|những nội dung cần', ql):
        return 'summarize'
    if re.search(r'^\s*(giải thích|explain|làm rõ|nói rõ)', ql) and re.search(r'(trang|slide|page)\s*\d+', ql):
        return 'explain_page'
    if re.search(r'(trang|slide|page)\s*\d+', ql):
        return 'page_ref'
    if re.search(r'\b(tải|download|file|pdf|link|nộp|deadline|lab|bài tập|điểm|nhóm)\b', ql):
        return 'logistics'
    if re.search(r'^(hi+|hello|halo|alo|ok|hey|hú|ha+|ê|ủa|hả|test|yo)\b', ql.strip()) or len(ql.split()) <= 1:
        return 'noise'
    return 'content_question'


# --------------------------------------------------------------------------- #
# 2. Headline numbers (spec §1)
# --------------------------------------------------------------------------- #
def headline(t):
    nf = t[t.notfound]
    n = len(t)
    print('=' * 72)
    print('SPEC §1 — HEADLINE (mọi tỉ lệ trên', n, 'turn)')
    print('=' * 72)
    print(f'turn / user / conversation            : {n} / {t.user_id.nunique()} / {t.conversation_id.nunique()}')
    print(f'not-found turns                       : {len(nf)} = {len(nf)/n*100:.1f}%')
    print(f'  user bị ít nhất 1 lần               : {nf.user_id.nunique()} = {nf.user_id.nunique()/t.user_id.nunique()*100:.1f}%')
    print(f'  hội thoại bị ít nhất 1 lần          : {nf.conversation_id.nunique()} = {nf.conversation_id.nunique()/t.conversation_id.nunique()*100:.1f}%')
    print(f'  ĐẨY việc tra cứu về cho học viên    : {t.pushback.sum()}/{len(nf)} = {t.pushback.sum()/len(nf)*100:.1f}%')
    print(f'  là lượt CUỐI của hội thoại          : {nf.is_last_turn.sum()}/{len(nf)} = {nf.is_last_turn.mean()*100:.1f}%')
    print(f'    (đo được: hội thoại kết thúc tại đó — KHÔNG kết luận "học viên bỏ")')
    print(f'  rating                              : {(nf.rating=="down").sum()} down / {(nf.rating=="up").sum()} up')
    print(f'  payload ĐÃ CÓ số trang mà vẫn fail  : {nf.page.notna().sum()}/{len(nf)} = {nf.page.notna().mean()*100:.1f}%')
    print(f'  nói "không tìm thấy" nhưng vẫn cite : {(nf.n_cit>0).sum()}')
    s = t[t.intent == 'summarize']
    print(f'\nxin tóm tắt/ôn lại buổi               : {len(s)} turn = {len(s)/n*100:.1f}%')
    print(f'  số user khác nhau đã xin             : {s.user_id.nunique()}/{t.user_id.nunique()} = {s.user_id.nunique()/t.user_id.nunique()*100:.1f}%')
    print(f'  bị từ chối                          : {s.refused.sum()} = {s.refused.mean()*100:.1f}%')
    print(f'  rating trên nhóm bị từ chối         : {(s[s.refused].rating=="down").sum()} down / {(s[s.refused].rating=="up").sum()} up')
    print(f'\ntutor chủ động kiểm tra hiểu bài      : {(t.asked_check_question==True).sum()}/{n}')
    print(f'turn có rating (bất kỳ)               : {t.rating.notna().sum()} = {t.rating.notna().mean()*100:.1f}%')


# --------------------------------------------------------------------------- #
# 3. Bảng impact (spec §2) — 6 ứng viên, 1 chọn 5 loại
# --------------------------------------------------------------------------- #
def impact_table(t):
    n = len(t)
    cands = [
        ('CHỌN · Không có căn cứ -> đẩy việc về học viên', t.notfound),
        ('Loại · Recap cả buổi không làm được', (t.intent == 'summarize') & t.refused),
        ('Loại · Tutor không bao giờ kiểm tra hiểu bài', t.asked_check_question == False),
        ('Loại · Trả lời quá dài trong giờ học (>150 từ)', t.t_words > 150),
        ('Loại · Bôi đen rác (<=3 ký tự) vẫn được trả lời', t.sel_len.between(1, 3)),
        ('Loại · Latency > 5s', t.avg_latency_ms > 5000),
    ]
    rows = []
    for name, m in cands:
        sub = t[m]
        rows.append({
            'ứng viên': name,
            'turn': len(sub),
            '% turn': round(len(sub) / n * 100, 1),
            'user': sub.user_id.nunique(),
            '% user': round(sub.user_id.nunique() / t.user_id.nunique() * 100, 1),
            'hội thoại': sub.conversation_id.nunique(),
            '👎': int((sub.rating == 'down').sum()),
            '👍': int((sub.rating == 'up').sum()),
        })
    print('\n' + '=' * 72)
    print('SPEC §2 — BẢNG IMPACT')
    print('=' * 72)
    print(pd.DataFrame(rows).to_string(index=False))
    print('\nLý do chọn bằng số: ứng viên 1 có reach lớn nhất trong nhóm CÓ HẬU QUẢ ĐO ĐƯỢC')
    print('(👎/👍 = 18/1) và có hành vi thay thế rõ ràng. Ứng viên 3 reach 99.8% nhưng chỉ')
    print('chứng minh được "thiếu tính năng", không đo được thiệt hại mỗi lần -> loại.')
    print('Ứng viên 2 là một LỚP CASE của ứng viên 1 -> gộp vào golden set, không tách feature.')


# --------------------------------------------------------------------------- #
# 4. Golden set seeds — case thật, có turn_id để trích trong repo
# --------------------------------------------------------------------------- #
CLASS_SEEDS = {
    '① Nguồn sự thật (không có căn cứ)': ['T0036', 'T1157', 'T0819', 'T0418', 'T0352'],
    '② Mơ hồ / thiếu thông tin':         ['T0416', 'T0964', 'T0723', 'T0601', 'T0410'],
    '③ Ngoài phạm vi / thẩm quyền':      ['T0340', 'T0661', 'T1006', 'T0489', 'T0473'],
    '④ Đặc thù domain (cite sai/lệch)':  ['T0397', 'T1084', 'T1258', 'T0299', 'T1092'],
    'Thường · xin tóm tắt buổi':         ['T0932', 'T1119', 'T0258', 'T0443', 'T1164'],
    'Hiếm · nhiễu ngôn ngữ khác':        ['T0949', 'T0610'],
}


def golden_seeds(t):
    print('\n' + '=' * 72)
    print('SPEC §7 / eval/ — GOLDEN SET SEEDS (case thật, ghi bằng turn_id)')
    print('=' * 72)
    for cls, ids in CLASS_SEEDS.items():
        print(f'\n--- {cls}')
        for tid in ids:
            if tid not in t.index:
                print(f'  {tid}  [không có trong file]')
                continue
            r = t.loc[tid]
            base = 'FAIL' if r.notfound else ('cite' if r.n_cit else 'no-cite')
            print(f'  {tid} | intent={r.intent:16s} | baseline={base:7s} | rating={r.rating}')
            print(f'         HV : {r.q[:110]}')
            print(f'         cũ : {r.tutor[:130]}')


# --------------------------------------------------------------------------- #
# 5. Mẫu để soát tay (bắt buộc trước CP4)
# --------------------------------------------------------------------------- #
def sample_for_manual_audit(t, n=30, seed=42, out='audit_30_mau.csv'):
    """Xuất 30 turn để 2 người chấm độc lập: intent đúng chưa, notfound đúng chưa.
    Ghi tỉ lệ khớp vào spec §1 — đó là phần 'phương pháp đếm kiểm lại được'."""
    s = t.sample(n, random_state=seed)[['q', 'tutor', 'intent', 'notfound', 'pushback', 'rating']].copy()
    s['intent_nguoi_cham'] = ''
    s['notfound_nguoi_cham'] = ''
    s.to_csv(out, encoding='utf-8-sig')
    print(f'\n[✓] Đã xuất {n} mẫu soát tay -> {out}')


# --------------------------------------------------------------------------- #
# 6. Transcript corpus + BM25 (dùng cho retrieval của prototype)
# --------------------------------------------------------------------------- #
PARA_PAT = re.compile(r'\*\*\[(T\d\d-\d\d\d)\]\*\*\s*(.+?)(?=\n\n|\Z)', re.S)
STOP = set('là của và các một những cho được có trong với thì mà nếu này đó khi để không cũng '
           'ở về từ như sẽ đã rất bạn mình tôi chúng ta nó lại rồi hay nhưng vì nên ra vào lên '
           'trên dưới mỗi nào gì sao ai thế đây kia bởi tại do theo sau trước còn nữa hơn cả '
           'đều chỉ vẫn phải cần đang'.split())


def load_transcripts(data_dir=DATA_DIR):
    rows = []
    for f in sorted(glob.glob(data_dir + r'\transcript\transcript-0*-clean.md')):
        s = io.open(f, encoding='utf-8').read()
        for m in PARA_PAT.finditer(s):
            rows.append({'code': m.group(1),
                         'text': re.sub(r'\s+', ' ', m.group(2)).strip(),
                         'file': f.split('\\')[-1]})
    return pd.DataFrame(rows)


class BM25:
    """Retrieval tối giản cho prototype. Đủ tốt để demo; nâng lên embedding nếu còn giờ."""

    def __init__(self, texts, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.docs = [self._tok(x) for x in texts]
        self.N = len(self.docs)
        self.avgdl = sum(map(len, self.docs)) / self.N
        df = collections.Counter()
        for d in self.docs:
            df.update(set(d))
        self.idf = {w: math.log(1 + (self.N - c + .5) / (c + .5)) for w, c in df.items()}
        self.tf = [collections.Counter(d) for d in self.docs]

    @staticmethod
    def _tok(s):
        return [w for w in re.findall(r'[a-zà-ỹ0-9]+', str(s).lower())
                if w not in STOP and len(w) > 1]

    def search(self, q, k=5):
        qt = self._tok(q)
        sc = []
        for i, tf in enumerate(self.tf):
            dl = len(self.docs[i])
            s = sum(self.idf[w] * tf[w] * (self.k1 + 1) /
                    (tf[w] + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
                    for w in qt if w in tf)
            sc.append(s)
        top = sorted(range(self.N), key=lambda i: -sc[i])[:k]
        return [(i, round(sc[i], 2)) for i in top]


def transcript_report():
    P = load_transcripts()
    print('\n' + '=' * 72)
    print('CORPUS TRANSCRIPT (dùng làm nguồn sự thật cho prototype)')
    print('=' * 72)
    print(f'{len(P)} đoạn có mã trích dẫn · {P.text.str.len().sum():,} ký tự')
    print(P.file.value_counts().to_string())
    print('\nPhủ chủ đề (dùng để CHỌN case demo — đừng demo chủ đề không phủ):')
    for name, pat in [
        ('mức tự động hoá / augment', r'(mức tự động|tự động hoá|augment|con người giám sát)'),
        ('transformer / attention', r'(attention|transformer)'),
        ('agent / ReAct', r'(react|agent)'),
        ('evaluation / golden set', r'(evaluation|đánh giá mô hình|golden set|eval)'),
        ('problem statement', r'(phát biểu vấn đề|problem statement)'),
        ('token / chi phí', r'(token)'),
        ('hallucination / bịa', r'(bịa|hallucin)'),
        ('chính sách tải slide', r'(tải.{0,20}slide|bản quyền)'),
    ]:
        hits = P[P.text.str.contains(pat, case=False, regex=True)]
        print(f'  {name:28s}: {len(hits):3d} đoạn  {list(hits.code[:5])}')
    return P


# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    t = load_turns()
    headline(t)
    impact_table(t)
    golden_seeds(t)
    sample_for_manual_audit(t)
    P = transcript_report()

    # ví dụ retrieval cho prototype
    bm = BM25(P.text)
    print('\nVí dụ retrieval — "khi nào nên để con người giám sát AI":')
    for i, s in bm.search('khi nào nên để con người giám sát AI mức tự động hoá', 3):
        print(f'  [{P.code[i]}] score={s} :: {P.text[i][:140]}')
