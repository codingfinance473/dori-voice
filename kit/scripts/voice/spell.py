"""받아쓰기 대조용 표기 규칙. 받아쓰기는 숫자를 아라비아 숫자로, 소수점을 '점·쩜'으로 적고, 소리 나는 대로('일억'→'이럭') 적을 때가 있다.
편마다 voice/spell.json 의 "alt"(핵심어 → 같은 말로 볼 표기 목록)·"num_form"(원문 읽기 → 받아쓰기 표기)을 더한다."""
import json, re
from pathlib import Path

ALT = {  # 지금까지 편에서 확인한 같은 말
    "1등": ["1등", "일등"], "2등": ["2등", "이등"], "3등": ["3등", "삼등"],
    "1억": ["1억", "일억", "이럭", "이력"], "2억": ["2억", "이억"], "3억": ["3억", "삼억"], "7억": ["7억", "칠억"], "11억": ["11억", "십일억"],
    "2010": ["2010", "이천십"], "2024": ["2024", "이천이십사"], "2025": ["2025", "이천이십오"], "2026": ["2026", "이천이십육"],
    "30": ["30", "삼십"], "95": ["95", "구십오"], "4병": ["4병", "네병", "내병", "사병"], "열": ["열", "10"], "여덟": ["여덟", "8"],
    "7월": ["7월", "칠월"], "11월": ["11월", "십일월"], "82.7": ["827", "82점7", "82쩜7", "80이쩜칠", "80이점칠"],
    "30.2": ["302", "30점2", "30쩜2", "30점이", "30쩜이"],
}
NUM_FORM = {  # 원문(한글 읽기) → 받아쓰기 표기, 비슷한 정도를 잴 때만 쓴다
    "이천이십사 년": "2024년", "이천이십오 년": "2025년", "이천십 년": "2010년", "일 등": "1등", "이 등": "2등", "삼 등": "3등",
    "일억": "1억", "이억": "2억", "삼십 퍼센트": "30퍼센트", "칠월": "7월", "십일월": "11월",
}


def load(folder="voice"):
    p = Path(folder) / "spell.json"
    alt, nf = dict(ALT), dict(NUM_FORM)
    if p.exists():
        j = json.loads(p.read_text(encoding="utf-8"))
        alt.update(j.get("alt", {})); nf.update(j.get("num_form", {}))
    return alt, nf


def norm(s):
    for c in " .,!?…~": s = s.replace(c, "")
    return s.replace("%", "퍼센트")


def ko_num(n):
    """한자어 수 읽기: 2924 → 이천구백이십사, 12900 → 만이천구백 (가격 검산 대사·받아쓰기 대조용)."""
    if n == 0: return "영"
    D, out = "영일이삼사오육칠팔구", ""
    for big, name in ((10 ** 8, "억"), (10 ** 4, "만"), (1, "")):
        q, n = divmod(n, big)
        if not q: continue
        part = ""
        for unit, un in ((1000, "천"), (100, "백"), (10, "십"), (1, "")):
            d, q = divmod(q, unit)
            if d: part += ("" if d == 1 and un else D[d]) + un
        out += ("" if part == "일" and name == "만" else part) + name
    return out


def ko(t):
    """숫자를 한글 읽기로 바꾼 꼴 — 받아쓰기가 숫자로 적든 한글로 적든 같은 말로 본다."""
    return re.sub(r"\d+", lambda m: ko_num(int(m.group())), t)


def variants(k, alt):
    v = list(alt.get(k, [k]))
    if re.fullmatch(r"\d+\.\d+", k):  # 소수: 점 빼기·'점'·'쩜'
        a, b = k.split(".")
        v += [a + b, f"{a}점{b}", f"{a}쩜{b}"]
    return [norm(x) for x in v]


def ko_text(text):
    """받아쓰기 원문 → 한글 읽기 꼴. 천 단위 쉼표(1,290)만 숫자로 잇고 '59,8' 같은 쉼표는 끊어 읽는다(가격 검산 voice.py 와 같은 기준)."""
    t = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", text)
    t = re.sub(r"(?<=\d)\.(?=\d)", "점", t)   # 소수점: 1.5 → 1점5 → 일점오 (변형 '1점5' 와 같은 꼴)
    return norm(ko(t))


def ok(text, keys, alt):
    t = norm(text); tk = ko_text(text)
    return all(any((a in t and not re.search(r"\d", a)) or ko(a) in tk for a in variants(k, alt)) for k in keys)


def num_form(s, nf):
    for a, b in nf.items(): s = s.replace(a, b)
    return norm(s)
