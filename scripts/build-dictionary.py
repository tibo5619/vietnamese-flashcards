#!/usr/bin/env python3
"""
One-off data-prep tool: turns the FVDP/OVDP Vietnamese-English dictionary
(GNU GPL v2-or-later) into data/dictionary.json, the static asset the app
fetches at runtime to power the "Check for duplicates" verification.

Source: https://raw.githubusercontent.com/iamstevendao/superfast-dictionary/
        master/app/src/main/assets/vietanh.json
(a JSON-ish export of the Free Vietnamese Dictionary Project + Open
Vietnamese Dictionary Project data; not shipped to the browser, only this
script's *output* is).

Not run automatically — re-run manually (python3 scripts/build-dictionary.py)
if the upstream source ever needs to be refreshed.

Output shape:
  {
    "_license": "<verbatim FVDP/OVDP GPL notice>",
    "vn": { "<diacritic-stripped spelling>": [ {"vn": "<headword>", "gl": ["<gloss>", ...]}, ... ], ... },
    "en": { "<english phrase>": ["<vn headword>", ...], ... }
  }
"""
import re
import json
import unicodedata
import urllib.request
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/iamstevendao/superfast-dictionary/master/app/src/main/assets/vietanh.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "dictionary.json"
META_KEYS = {"00-database-info", "00-database-short", "00-database-url"}

# The source file isn't strictly valid JSON (some values contain unescaped
# inner quotes; a few entries have a literal newline inside a [pronunciation]
# bracket), so it's parsed line-by-line: buffer lines until one matches a
# complete "key": "value" pair, using a greedy value match so the *last*
# quote on the buffered text is treated as the closing delimiter.
LINE_RE = re.compile(r'^\s*"(.*?)":\s*"(.*)"\s*,?\s*$', re.DOTALL)
SKIP_RE = re.compile(r'^\s*[{}]\s*,?\s*$')


def unescape(s):
    return (s.replace('\\r', '')
             .replace('\\n', ' ')
             .replace('\\t', ' ')
             .replace('\\/', '/')
             .replace('\\"', '"')
             .replace('\\\\', '\\'))


def parse_entries(raw_text):
    entries = {}
    buf = []
    for line in raw_text.split('\n'):
        if not buf and SKIP_RE.match(line):
            continue
        buf.append(line)
        candidate = '\n'.join(buf)
        m = LINE_RE.match(candidate)
        if m:
            entries[unescape(m.group(1))] = unescape(m.group(2))
            buf = []
    return entries


# Markup per entry: "@headword [pron]* POS- gloss1- gloss2=vn_ex+en_ex..."
# repeated per POS block (blocks separated by "*"). We only need the
# glosses (not POS labels, which mix English/Vietnamese inconsistently in
# the source, or the worked examples), so:
#  - strip the leading "@headword [pronunciation]" echo
#  - split into POS blocks on "*"
#  - within each block, drop the POS label (text before the first "-")
#  - split remaining text into sub-senses on a hyphen followed by an
#    uppercase letter or "(" (distinguishes sub-sense separators like
#    "daylight- Rash" from mid-word hyphens like "hold-up")
#  - for each sub-sense, keep only the text before its first "=" (drops
#    the VN/EN example pair that follows)
POS_PREFIX_RE = re.compile(r'^[^\-=]{0,25}-\s*(.*)$', re.DOTALL)
SUBSENSE_SPLIT_RE = re.compile(r'-(?=\s*[A-ZÀ-Ỹ(])')


def extract_glosses(headword, value):
    s = value[1:] if value.startswith('@') else value
    if s.lower().startswith(headword.lower()):
        s = s[len(headword):]
    s = re.sub(r'^\s*\[[^\]]*\]', '', s)  # drop leading [pronunciation]

    glosses = []
    for seg in s.split('*'):
        seg = seg.strip()
        if not seg:
            continue
        m = POS_PREFIX_RE.match(seg)
        text = m.group(1) if m else seg
        for chunk in SUBSENSE_SPLIT_RE.split(text):
            gloss = chunk.split('=')[0].strip(' -;,.')
            if gloss and len(gloss) < 200:
                glosses.append(gloss)

    seen, out = set(), []
    for g in glosses:
        key = g.lower()
        if key not in seen:
            seen.add(key)
            out.append(g)
    return out


def normalize_vn(s):
    """Mirrors index.html's normalizeVn(): NFD-strip diacritics, đ -> d."""
    s = s.lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if not (0x0300 <= ord(ch) <= 0x036f))
    s = s.replace('đ', 'd')
    return s.strip()


STOP_PREFIXES = ('to ', 'a ', 'an ', 'the ')


def en_phrases(gloss):
    for part in re.split(r'[,;]', gloss):
        p = re.sub(r'\([^)]*\)', '', part).strip().lower()
        if not p:
            continue
        for pre in STOP_PREFIXES:
            if p.startswith(pre):
                p = p[len(pre):].strip()
                break
        if p and len(p) < 60:
            yield p


def main():
    print(f"Fetching {SOURCE_URL} ...")
    with urllib.request.urlopen(SOURCE_URL) as resp:
        raw_text = resp.read().decode('utf-8')

    entries = parse_entries(raw_text)
    license_text = entries.pop("00-database-info", "").strip()
    for k in META_KEYS - {"00-database-info"}:
        entries.pop(k, None)
    print(f"Parsed {len(entries)} dictionary entries.")

    vn_index, en_index = {}, {}
    for headword, raw in entries.items():
        glosses = extract_glosses(headword, raw)
        norm = normalize_vn(headword)
        vn_index.setdefault(norm, []).append({"vn": headword, "gl": glosses})
        for gloss in glosses:
            for phrase in en_phrases(gloss):
                bucket = en_index.setdefault(phrase, [])
                if headword not in bucket:
                    bucket.append(headword)

    out = {"_license": license_text, "vn": vn_index, "en": en_index}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

    size = OUT_PATH.stat().st_size
    print(f"Wrote {OUT_PATH} ({size / 1024 / 1024:.2f} MB raw, "
          f"{len(vn_index)} VN groups, {len(en_index)} EN phrases).")


if __name__ == "__main__":
    main()
