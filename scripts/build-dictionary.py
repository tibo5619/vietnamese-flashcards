#!/usr/bin/env python3
"""
One-off data-prep tool: turns Wiktionary's Vietnamese-language entries
(extracted from en.wiktionary.org, CC BY-SA 3.0) into data/dictionary.json,
the static asset the app fetches at runtime to power "Check word" on the
Add-a-word screen.

Source: https://raw.githubusercontent.com/Trannosaur/published_dicts/
        master/vi2enwikitxt.txt
(a tab-separated dump of Vietnamese Wiktionary entries: headword, blank,
numbered senses joined by "<br />" with POS tags and examples, tags).
Chosen over the older FVDP/OVDP dictionary (used until this script's
previous version) because FVDP was compiled 1997-2007 and never updated
since, and some of its glosses are garbled from ambiguous legacy markup
(e.g. "chó" (dog) came out as "Dog spaniel boxer saluki" with no
punctuation). This Wiktionary-derived source is actively maintained and
its numbered-sense format parses unambiguously.

Not run automatically — re-run manually (python3 scripts/build-dictionary.py)
if the upstream source ever needs to be refreshed.

Output shape (unchanged from the previous FVDP-based version, so no
runtime code in index.html needs to change):
  {
    "_license": "<attribution text>",
    "vn": { "<diacritic-stripped spelling>": [ {"vn": "<headword>", "gl": ["<gloss>", ...]}, ... ], ... },
    "en": { "<english phrase>": ["<vn headword>", ...], ... }
  }
"""
import re
import json
import unicodedata
import urllib.request
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/Trannosaur/published_dicts/master/vi2enwikitxt.txt"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "dictionary.json"
LICENSE_TEXT = (
    "Vietnamese-English glosses derived from English Wiktionary "
    "(https://en.wiktionary.org) contributor content, via the "
    "vi2enwikitxt.txt extract at "
    "https://github.com/Trannosaur/published_dicts. "
    "Licensed under Creative Commons Attribution-ShareAlike 3.0 Unported "
    "(https://creativecommons.org/licenses/by-sa/3.0/)."
)

# Each source line is 4 tab-separated fields: "<n>[:-]<headword>", "",
# "<numbered senses joined by <br />>", "<space-separated tags>".
SENSE_RE = re.compile(r'^(\d+)\.\s*(?:\(([^)]*)\)\s*)?(.*)$')


def extract_senses(definition_field):
    """Splits a Wiktionary-style '1. (pos) gloss<br />> example: ...<br />2. ...'
    field into a flat list of gloss strings, dropping example/meaning lines
    (prefixed '>') and POS tags — only the gloss text itself is kept."""
    glosses = []
    for line in definition_field.split('<br />'):
        line = line.strip()
        if not line or line.startswith('>'):
            continue
        m = SENSE_RE.match(line)
        text = m.group(3).strip() if m else line
        if text:
            glosses.append(text)
    return glosses


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

    entries = {}
    for line in raw_text.split('\n'):
        parts = line.rstrip('\n').split('\t')
        if len(parts) != 4:
            continue
        headword = re.sub(r'^\d+[:-]', '', parts[0])
        glosses = extract_senses(parts[2])
        if not glosses:
            continue
        entries.setdefault(headword, []).extend(glosses)
    print(f"Parsed {len(entries)} dictionary entries.")

    vn_index, en_index = {}, {}
    for headword, glosses in entries.items():
        norm = normalize_vn(headword)
        vn_index.setdefault(norm, []).append({"vn": headword, "gl": glosses})
        for gloss in glosses:
            for phrase in en_phrases(gloss):
                bucket = en_index.setdefault(phrase, [])
                if headword not in bucket:
                    bucket.append(headword)

    out = {"_license": LICENSE_TEXT, "vn": vn_index, "en": en_index}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

    size = OUT_PATH.stat().st_size
    print(f"Wrote {OUT_PATH} ({size / 1024 / 1024:.2f} MB raw, "
          f"{len(vn_index)} VN groups, {len(en_index)} EN phrases).")


if __name__ == "__main__":
    main()
