# -*- coding: utf-8 -*-
"""문제 은행 마크다운(제한된 부분집합) → 블록 구조 → Qt 리치텍스트용 HTML. 표준 라이브러리만 사용.

지원: 제목(#), 문단, 펜스 코드 블록(목록 안 들여쓴 것·`1. ```python` 꼴 포함), 번호/글머리 목록(중첩),
      인용(>), 표(| a | b |, 셀 안 <br>, \\| 이스케이프), 인라인 `코드`·``코드``·**굵게**.
지원하지 않는 것(은행에 없음): 링크, 이미지, 기울임, 취소선, HTML 태그(문자 그대로 보여 줌).
"""
import html
import re

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([\w+-]*)\s*$")
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
OL_RE = re.compile(r"^(\s*)(\d+)([.)])(\s+)(.*)$")
UL_RE = re.compile(r"^(\s*)([-*+])(\s+)(.*)$")
SEP_RE = re.compile(r"^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$")
INLINE_RE = re.compile(r"(``.+?``|`[^`\n]*`|\*\*.+?\*\*|<br\s*/?>|\\[\\`*_|<>#\[\]()-])")


def indent_of(line):
    return len(line) - len(line.lstrip(" "))


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells = re.split(r"(?<!\\)\|", line)
    return [c.strip().replace("\\|", "|") for c in cells]


def parse(text):
    """블록 목록을 돌려줌. 블록: dict(t=..., ...)
    heading(level, text) · para(text) · code(lang, text) · ol(start, items[[blocks]]) · ul(items) · quote(blocks) · table(head, rows)"""
    return _blocks(text.replace("\r\n", "\n").replace("\t", "    ").split("\n"))


def _blocks(lines):
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = FENCE_RE.match(line)
        if m:
            ind, mark, lang = len(m.group(1)), m.group(2), m.group(3)
            body, i = [], i + 1
            while i < n and not re.match(r"^\s*%s+\s*$" % re.escape(mark[0] * 3), lines[i]):
                body.append(lines[i][min(ind, indent_of(lines[i])):])
                i += 1
            i += 1  # 닫는 펜스
            out.append({"t": "code", "lang": lang, "text": "\n".join(body)})
            continue
        m = HEAD_RE.match(line)
        if m:
            out.append({"t": "heading", "level": len(m.group(1)), "text": m.group(2)})
            i += 1
            continue
        if line.lstrip().startswith(">"):
            body = []
            while i < n and lines[i].lstrip().startswith(">"):
                body.append(re.sub(r"^\s*> ?", "", lines[i]))
                i += 1
            out.append({"t": "quote", "blocks": _blocks(body)})
            continue
        if line.lstrip().startswith("|") and i + 1 < n and SEP_RE.match(lines[i + 1]) and "-" in lines[i + 1]:
            head = split_row(line)
            rows, i = [], i + 2
            while i < n and lines[i].lstrip().startswith("|"):
                row = split_row(lines[i])
                rows.append((row + [""] * len(head))[:len(head)])
                i += 1
            out.append({"t": "table", "head": head, "rows": rows})
            continue
        m = OL_RE.match(line) or UL_RE.match(line)
        if m:
            ordered = bool(OL_RE.match(line))
            pat = OL_RE if ordered else UL_RE
            base = indent_of(line)
            items, start = [], None
            while i < n:
                m = pat.match(lines[i])
                if not m or indent_of(lines[i]) != base:
                    break
                if ordered:
                    width = base + len(m.group(2)) + 1 + len(m.group(4))
                    first = m.group(5)
                    if start is None:
                        start = int(m.group(2))
                else:
                    width = base + 1 + len(m.group(3))
                    first = m.group(4)
                body, i = [first], i + 1
                in_fence = bool(FENCE_RE.match(first))
                while i < n:
                    ln = lines[i]
                    if in_fence:
                        body.append(ln[min(width, indent_of(ln)):])
                        if re.match(r"^\s*(`{3,}|~{3,})\s*$", ln):
                            in_fence = False
                        i += 1
                        continue
                    if not ln.strip():  # 빈 줄 다음 줄이 이 항목에 속해야 항목이 이어짐
                        j = i
                        while j < n and not lines[j].strip():
                            j += 1
                        if j < n and indent_of(lines[j]) >= width:
                            body.append("")
                            i += 1
                            continue
                        break
                    if indent_of(ln) >= width:
                        piece = ln[width:]
                        if FENCE_RE.match(piece):
                            in_fence = True
                        body.append(piece)
                        i += 1
                        continue
                    if indent_of(ln) > base and (OL_RE.match(ln) or UL_RE.match(ln)):  # 덜 들여쓴 중첩 목록
                        body.append(ln[min(width, indent_of(ln)):])
                        i += 1
                        continue
                    if _starts_block(ln):
                        break
                    body.append(ln.strip())  # 게으른 이어쓰기
                    i += 1
                items.append(_blocks(body))
                while i < n and not lines[i].strip():  # 항목 사이 빈 줄
                    j = i
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and pat.match(lines[j]) and indent_of(lines[j]) == base:
                        i = j
                    else:
                        break
            out.append({"t": "ol" if ordered else "ul", "start": start or 1, "items": items})
            continue
        body = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not _starts_block(lines[i]):
            body.append(lines[i].strip())
            i += 1
        out.append({"t": "para", "text": " ".join(body)})
    return out


def _starts_block(line):
    return bool(FENCE_RE.match(line) or HEAD_RE.match(line) or OL_RE.match(line) or UL_RE.match(line)
                or line.lstrip().startswith(">") or line.lstrip().startswith("|"))


# 인라인

def inline_tokens(text):
    """[(kind, text)] kind: text | code | bold | br. 굵게 안의 코드는 ('bold', [tokens]) 로 중첩."""
    out = []
    for part in INLINE_RE.split(text):
        if not part:
            continue
        if part.startswith("``") and part.endswith("``") and len(part) > 4:
            out.append(("code", part[2:-2].strip()))
        elif part.startswith("`") and part.endswith("`") and len(part) >= 2:
            out.append(("code", part[1:-1]))
        elif part.startswith("**") and part.endswith("**") and len(part) > 4:
            out.append(("bold", inline_tokens(part[2:-2])))
        elif re.fullmatch(r"<br\s*/?>", part):
            out.append(("br", ""))
        elif len(part) == 2 and part[0] == "\\":
            out.append(("text", part[1]))
        else:
            out.append(("text", part))
    return out


def inline_html(text):
    def render(tokens):
        buf = []
        for kind, val in tokens:
            if kind == "code":
                buf.append("<code>%s</code>" % html.escape(val, quote=False))
            elif kind == "bold":
                buf.append("<b>%s</b>" % render(val))
            elif kind == "br":
                buf.append("<br/>")
            else:
                buf.append(html.escape(val, quote=False))
        return "".join(buf)
    return render(inline_tokens(text))


def inline_plain(text):
    def render(tokens):
        return "".join("\n" if k == "br" else (render(v) if k == "bold" else v) for k, v in tokens)
    return render(inline_tokens(text))


# HTML (Qt 리치텍스트 부분집합)

CSS = """
body { font-size: 14px; color: #1f2328; }
p { margin-top: 0px; margin-bottom: 10px; }
h1 { font-size: 20px; margin-top: 14px; margin-bottom: 8px; }
h2 { font-size: 16px; margin-top: 16px; margin-bottom: 6px; color: #0b3d91; }
h3 { font-size: 14px; margin-top: 12px; margin-bottom: 4px; }
code { font-family: 'Menlo', 'Consolas', 'D2Coding', 'Courier New', monospace; font-size: 13px; background-color: #eef0f3; color: #1f2328; white-space: pre-wrap; }
pre { font-family: 'Menlo', 'Consolas', 'D2Coding', 'Courier New', monospace; font-size: 13px; margin: 0px; color: #1f2328; }
td.codebox { background-color: #f3f4f6; border: 1px solid #d0d7de; }
td.quote { background-color: #fff8e1; border: 1px solid #f0d98c; }
table.grid { border-collapse: collapse; margin-top: 4px; margin-bottom: 10px; }
table.grid th { background-color: #eaeef2; font-weight: bold; padding: 6px 10px; border: 1px solid #c8d1da; }
table.grid td { padding: 6px 10px; border: 1px solid #c8d1da; }
li { margin-bottom: 6px; }
"""


def to_html(text):
    return "<body>%s</body>" % _html(parse(text))


def _html(blocks, tight=False):
    out = []
    for b in blocks:
        t = b["t"]
        if t == "heading":
            level = min(3, max(1, b["level"]))
            out.append("<h%d>%s</h%d>" % (level, inline_html(b["text"]), level))
        elif t == "para":
            out.append("<p>%s</p>" % inline_html(b["text"]))
        elif t == "code":
            out.append('<table width="100%%" cellspacing="0" cellpadding="8" border="0" style="margin-top:2px; margin-bottom:10px;">'
                       '<tr><td class="codebox"><pre>%s</pre></td></tr></table>' % html.escape(b["text"], quote=False))
        elif t == "quote":
            out.append('<table width="100%%" cellspacing="0" cellpadding="8" border="0" style="margin-bottom:10px;">'
                       '<tr><td class="quote">%s</td></tr></table>' % _html(b["blocks"]))
        elif t == "table":
            head = "".join("<th>%s</th>" % inline_html(c) for c in b["head"])
            rows = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline_html(c) for c in r) for r in b["rows"])
            out.append('<table class="grid" border="1" cellspacing="0" cellpadding="6"><tr>%s</tr>%s</table>' % (head, rows))
        elif t in ("ol", "ul"):
            items = "".join("<li>%s</li>" % _html(it, tight=True) for it in b["items"])
            if t == "ol":
                out.append('<ol start="%d">%s</ol>' % (b["start"], items))
            else:
                out.append("<ul>%s</ul>" % items)
    return "".join(out)


# 감사(audit)용 기대값

def expected(text):
    """렌더링 결과와 대조할 기대 구조: 코드 줄, 표, 번호 목록의 번호, 인라인 코드, 굵게, 전체 글자."""
    exp = {"code_lines": [], "tables": [], "ol_numbers": [], "inline_code": [], "bold": [], "plain": []}

    def walk_inline(text, in_heading=False, in_th=False):
        def rec(tokens, bold=False):
            for kind, val in tokens:
                if kind == "code":
                    exp["inline_code"].append(val)
                    exp["plain"].append(val)
                elif kind == "bold":
                    if not in_heading and not in_th:
                        exp["bold"].append(inline_plain_tokens(val))
                    rec(val, True)
                elif kind == "text":
                    exp["plain"].append(val)
        rec(inline_tokens(text))

    def inline_plain_tokens(tokens):
        return "".join(v if k in ("text", "code") else "" for k, v in tokens)

    def walk(blocks):
        for b in blocks:
            t = b["t"]
            if t == "heading":
                walk_inline(b["text"], in_heading=True)
            elif t == "para":
                walk_inline(b["text"])
            elif t == "code":
                exp["code_lines"] += b["text"].split("\n")
                exp["plain"].append(b["text"])
            elif t == "quote":
                walk(b["blocks"])
            elif t == "table":
                exp["tables"].append([[inline_plain(c) for c in b["head"]]] + [[inline_plain(c) for c in r] for r in b["rows"]])
                for c in b["head"]:
                    walk_inline(c, in_th=True)
                for r in b["rows"]:
                    for c in r:
                        walk_inline(c)
            elif t in ("ol", "ul"):
                for k, item in enumerate(b["items"]):
                    if t == "ol":
                        exp["ol_numbers"].append(b["start"] + k)
                    walk(item)
    walk(parse(text))
    return exp
