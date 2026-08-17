# Data Model — Nhặt Chữ

Full mechanics for the vocabulary/grammar/progress/statistics data layer. Moved out of CLAUDE.md (2026-08-17) to keep session startup lean — see CLAUDE.md's "Data model" summary for the short version and when to come here.

## Data model

- **Vocabulary catalog**: `BOOKS` array in `index.html` (near the top of the
  `<script>`), e.g. `{ id, title, file, lessonsCount }`. `loadBooksData()`
  fetches every book's JSON file and tags each entry with `book: bookDef.id`,
  filling the global `baseVocab` array.
- **Recipe to add a new book** (e.g. Connect 3): drop `data/connect3.json`
  (same shape as `data/connect1.json`) → add one line to `BOOKS` → add the
  file path to `ASSETS` in `sw.js` and bump `CACHE_NAME` → done. Lessons
  default to **inactive** until the user turns them on (see active-scope).
  Before finalizing the new book's JSON, compare its `vn` words against every
  existing book's and report findings to the user (count + full list, split
  into "identical word+translation" vs "same word, different sense") — this
  check can be run automatically, but **never delete or keep an entry without
  the user explicitly deciding**, one at a time or via a rule they approve.
  (Connect 1 vs Connect 2 had 7 words in common; only 1 — "bữa tiệc" — was an
  exact duplicate and was removed after confirmation; the other 6 were the
  same word with a different sense, kept as-is.)
- **Active scope** (`active-scope` localStorage key): `{ [bookId]: { [lesson]:
  true|false } }`. Drives `activeVocab()`, which feeds session draws, the
  Vocabulary screen, and home stats. `allVocab()` (unfiltered) is used ONLY by
  the duplicate check in "Add a word" — a word must be catchable as a
  duplicate even if its lesson isn't active yet. Connect 1 lessons default to
  active (pre-existing content); anything added later defaults to inactive.
- **Custom vocab** (`custom-vocab` localStorage key): user-added words,
  `{id, vn, en, lesson:null}`, always included in `activeVocab()` regardless
  of active-scope — no toggle for these.
- **Regional-variant convention** (chantier 21, e.g. "bao tay" vs "găng
  tay" — same meaning, Southern vs Northern Vietnam spelling): merged into
  a **single** vocab entry rather than kept as two cards or two glosses —
  `vn` becomes `"<southern> (S) / <northern> (N)"`, `en` stays the plain
  shared meaning (e.g. `"bao tay (S) / găng tay (N)"` → `"glove"`). The
  redundant second entry is deleted rather than kept alongside it. This is
  a **different** mechanism from the VN-homonym auto-merge (`mergeVnCard()`,
  see the streak/session-draw notes below) — that one only ever triggers
  for two entries sharing the *exact same spelling* with different senses
  (e.g. "chỉ"); a regional variant is two *different* spellings for the
  *same* sense, authored as one entry by hand, not merged automatically at
  runtime. Apply this same pattern any time a future review session turns
  up another true regional-variant pair.
- **`alwaysActive` books** (chantier 21): a `BOOKS` entry can set
  `alwaysActive: true` (currently only `custom`, `data/custom.json`) to mean
  "same treatment as custom-vocab" — no Settings → Sources entry, no lesson
  toggle, unconditionally included. `ALWAYS_ACTIVE_BOOKS` (a `Set` built once
  from `BOOKS`) is checked in both `activeVocab()` (bypasses the normal
  `scope[book][lesson]` filter) and `renderSettingsSources()` (skips the book
  entirely when rendering the per-lesson grid) — `getActiveScope()` needs no
  change since `lessonsCount: 0` already makes its per-lesson loop a no-op.
- **Vocab-review workflow** (chantier 21) — the answer to "custom-vocab lives
  only in the user's phone localStorage, Claude Code can't see or edit it
  directly, so how does a word ever get corrected or made permanent?" Words
  typed into "Add a word" still land in `custom-vocab` exactly as before —
  nothing changes day to day. Periodically the user exports **"Export data
  (issues + vocab)"** (Settings → Data → `exportVocabReview()`) — a bundle of
  `{customVocab, issueReports (unresolved only)}`, deliberately **without**
  `progress`, and brings the file into a Claude Code session. This single
  button also **replaced** the older, narrower "Export data (issues only)"
  from chantier 15 — that one only ever downloaded unresolved
  `issueReports`, a strict subset of what this export already carries, so
  keeping both was redundant; `exportIssues()` was deleted rather than kept
  alongside it. Claude reviews
  each word (cross-referencing any tied `issueReports` note for translation
  nuance — see the "rủ" vs "mời" example worked through when this workflow
  was designed) and, for whichever words are judged ready, writes them
  **directly into `data/custom.json`** (a normal file edit, committed and
  pushed like any other code change) — this is the "graduation" moment. The
  critical rule making this safe: **a promoted word keeps its exact original
  `custom-vocab` id**. Progress (`progress[id]`) is keyed purely by id and
  lives in its own separate localStorage key untouched by any of this, so a
  promoted word's learning streak carries over automatically with zero
  migration — nothing about `progress` ever needs to move. The now-redundant
  copy still sitting in the user's `custom-vocab` is **not** deleted by
  hand — `livingCustomVocab()` (used by both `allVocab()` and
  `activeVocab()`) filters out any `customVocab` entry whose id already
  exists in `baseVocab`, so the moment `data/custom.json` ships and the app
  reloads, the old copy simply stops being shown; it sits inert in
  localStorage indefinitely (harmless, tiny) rather than needing a cleanup
  step. This was a deliberate correction mid-design: an earlier version of
  this plan had the user manually delete graduated words via "Reset manually
  added words" — rejected because that screen intentionally also deletes
  the matching `progress` entries (built for "I don't want this word
  anymore", not "this word moved to a permanent file"), which would have
  silently reset the streak on every graduated word. The export is
  **one-way** (phone → Claude Code session) — it is never re-imported, so it
  carries none of the snapshot/staleness risk that a full "Export data
  (all)" → edit → re-import round-trip would (re-importing an old `progress`
  snapshot can overwrite any progress made in the meantime; this workflow
  never touches `progress` at all, so that risk doesn't apply here). Fixing
  a word that's already in `connect1.json`/`connect2.json` (not
  custom-vocab) is simpler still: Claude just edits that file directly, no
  export/import of any kind needed, since it's already a tracked repo file.
- **Progress** (`progress` localStorage key): per-direction learning memory,
  `{ [wordId]: { vn2en: {correct, wrong, last, streak}, en2vn: {...} } }`.
  `correct`/`wrong` are cumulative counters kept for reference only; `last`
  is kept for backward compatibility with pre-streak data (see migration
  below). The live value driving everything is `streak` — a signed integer
  that is **always -3..-1 or 1..3, never 0** — computed by `stepStreak()` in
  `index.html`: a correct answer moves it one step toward +3 (jumping
  straight from -1 to +1, skipping 0 — the two are the *same* pivot point,
  just colored differently), a wrong answer moves it one step toward -3
  (jumping from +1 to -1). Both directions are tracked fully independently —
  knowing a word VN→EN says nothing about EN→VN. `isKnownInDir()` /
  `isNeedsReviewInDir()` just check the sign (`streak > 0` / `streak < 0`);
  the magnitude (1/2/3) is extra detail, not a separate category, everywhere
  except the weighted draw (see below). **Migration**: progress saved before
  `streak` existed is upgraded lazily (`migratedStreak()`, run once at
  startup by `migrateProgressStreaks()` in `loadState()`) — if a word was
  never missed (`wrong === 0`), its streak is reconstructed *exactly* as
  `+min(correct, 3)` (nothing could have broken the run), symmetrically for
  never-succeeded words; a genuinely mixed history (both `correct` and
  `wrong` > 0) can't be reconstructed exactly since the order of past
  answers was never recorded, so it restarts at `±1` from `last`.
  **Weighted session draw** (`buildDeck()`): candidates fall into 7 buckets —
  `new` (never seen) plus one per streak value (`-3`..`3`, skipping 0) — and
  `LEARNING_MODES` (in `index.html`, selected in Settings → Learning method,
  `learning-mode` localStorage key, default `balanced`) supplies the quota
  table: `discovery` 60/30/10, `balanced` 40/40/20, `review` 20/50/30,
  `consolidation` 0/70/30 (new / review-total / maintenance-total — always
  multiples of ten so a 10-word session divides evenly). The review total is
  split across `-3`/`-2`/`-1` weighted toward the worse end, and the
  maintenance total across `1`/`2`/`3` weighted toward the fresher end —
  these finer splits are internal only, never shown in the UI. Fallback
  cascade: a bucket short on words hands its shortfall to the next bucket in
  `BUCKET_ORDER` (`new`→`-3`→`-2`→`-1`→`1`→`2`→`3`); if `new` is completely
  empty its whole share is redistributed proportionally across the other 6
  (same shape, scaled up to still sum to 100). A merged VN-homonym card (see
  `mergeVnCard()`) is represented by whichever underlying sense has the
  lowest streak (most negative wins, `new` wins over everything).
  **`buildDeck()` rolls the 'mix'-mode direction coin flip once per VN-
  spelling group, not once per word** (chantier 20) — true homonyms sharing
  one spelling (e.g. "chỉ" = "only" vs "chỉ" = "to guide", 5 such pairs
  currently: "bộ phận", "chỉ", "mới", "nên", "trả") must land on the same
  direction together, otherwise one sense could roll vn2en while the other
  rolled en2vn independently, which used to make the merge into "chỉ (2)"
  happen only ~25% of the times both were drawn — the other ~75% split them
  into a vn2en card and an unrelated-looking en2vn card, reported by the
  user as the merge "randomly" not working. Grouping by spelling before the
  coin flip makes it deterministic per session: the whole group is either
  vn2en (merges into one card) or en2vn (each sense shows separately with
  its own distinct English prompt — no merge needed there, fronts already
  differ, so no visual ambiguity either way).
- **`mergeEnCard()` (chantier 22)** — the mirror of `mergeVnCard()`, for
  true synonyms: two+ vocab entries with a *different* `vn` spelling but the
  exact same `en` gloss text (e.g. "xài" / "sử dụng", both "to use") merge
  into one en2vn card (one English prompt, every VN spelling listed on the
  back) but stay fully separate on vn2en — seeing two pre-paired VN
  spellings there would give the answer away, and that split needs no code
  at all since keeping them as distinct JSON entries already produces
  separate cards. This is the fix for a real gap: two *intended* merge
  patterns had been conflated under one hand-authored `vn: "X / Y"` JSON
  convention. **Type 1** — one spelling contains/extends the other (e.g.
  "cảm"/"cảm lạnh", "mang"/"mang theo") — correctly merges both directions
  today via `mergeVnCard()` alone; no `en`-side counterpart needed since
  these were never meant to split. **Type 2** — genuinely different
  spellings, true synonyms (e.g. "thoải mái"/"dễ chịu", "xài"/"sử dụng")
  — needed `mergeEnCard()`, since merging both directions was wrong: seeing
  two independent VN spellings pre-paired on a VN-front card isn't a real
  recognition test. `candidateCategory()` (weighted-draw bucket) and the
  merged-card render/mark-answer code in `renderCard()`/`markCard()` are
  shared between both merge directions — `candidateCategory()` reads
  `c.dir` instead of hardcoding `'vn2en'`, and `renderCard()`'s merged
  branch picks `currentCard.vn`/`s.en` vs `currentCard.en`/`s.vn` based on
  `isVnFirst`, exactly mirroring the unmerged-card branch beside it.
  **The 'mix'-mode coin-flip grouping (previous bullet) generalizes to a
  union-find** over "same `vn`" OR "same `en`" — any words that could end up
  on a merged card, either direction, must share one coin flip, or a
  synonym pair would suffer the exact same ~25%-of-the-time problem chantier
  20 fixed for homonyms. Every past `vn: "X / Y"` merge was re-classified
  (see `VOCAB_CLEANUP_LOG.md`, 2026-08-17 entry, for the full list and the
  git-history-verified original ids used to split each Type 2 pair back into
  two JSON entries with identical `en` text). Two entries were deliberately
  left as judgment calls rather than mechanically reclassified: "mùa hè
  (casu.) / mùa hạ (litt.)" stays merged both directions (its register tag
  lives in `vn`, not `en`, so neither merge mechanism would touch it anyway
  — user chose not to change its shape), and "ngừng / ngưng" (Bắc/Nam
  regional variant) was retagged to `"ngưng (S) / ngừng (N)"` to match the
  established Regional-variant convention (S/N order, "bao tay (S) / găng
  tay (N)") — cosmetic only, still one merged entry.
- **Other localStorage keys**: `issue-reports` (user-flagged
  translation/spelling/app-behavior issues),
  each `{id, wordId, vn, en, dir, page, note, resolved, createdAt}` — `page`
  is the screen id (`home`/`session`/`add`/`wordlist`/`issues`/`settings*`)
  active when the report was opened, always recorded; `vn`/`en`/`dir` are
  only set when the report is tied to a specific word (a session card or a
  not-found "Add a word" entry) — see "UI structure" for how it's created.
- **All storage is `localStorage`** — per-device, per-browser, never synced,
  never sent anywhere. Export/Import (Settings → Data) is the only way to
  move data across devices/browsers.
- **Reference dictionary** (`data/dictionary.json`, ~4.5MB raw / ~1.4MB
  gzip): `{ _license, vn: {...}, en: {...} }`, built by
  `scripts/build-dictionary.py` from Vietnamese-language Wiktionary entries
  (CC BY-SA 3.0, actively maintained — chosen over an earlier FVDP/OVDP-based
  version after that ~20-year-old, no-longer-updated source turned out to
  have real data-quality problems: e.g. its gloss for "chó" (dog) came out
  as the unpunctuated blob "Dog spaniel boxer saluki" because its markup
  couldn't be parsed unambiguously). `vn` is keyed by `normalizeVn(headword)`
  → array of `{vn, gl}` variants sharing that diacritic-stripped spelling
  (usually 1, sometimes many — e.g. "ban" groups with "bàn", "bạn", "bản",
  etc., 12 in total). `gl` is a list of individual senses (Wiktionary's
  numbered definitions, one gloss string per sense — e.g. "chó" → `["dog",
  "(little) (son of a) bitch"]`), not one combined string; each sense is
  also run through `trim_gloss()` in the build script, which drops a
  trailing long explanatory clause after a short term (e.g. Wiktionary's
  "printer; a device, usually attached to a computer, used to print text
  or images onto paper" becomes just `"printer"`) while leaving genuine
  multi-synonym lists like "to save; to glean; to collect; to lay up"
  intact — it keeps semicolon-separated segments (parenthesis-aware, so
  "smack (a loud kiss; a quick noise)" isn't split mid-parenthetical) only
  while each one stays under 40 characters, stopping at the first long
  one. Same function also strips a trailing verbose parenthetical off an
  otherwise-short segment (`strip_verbose_paren()`) — e.g. "crab (a
  crustacean of the infraorder Brachyura)" becomes just `"crab"` — but
  leaves a short clarifying parenthetical alone ("to save (every bit of)")
  and leaves a segment that *starts* with "(" alone (no lead text to fall
  back to, e.g. "(little) (son of a) bitch"). Affects ~1.3% of senses for
  the semicolon case and ~10% for the trailing-parenthetical case — real
  volume, which is why this is a build-script rule rather than a per-word
  fix. `en` is keyed by
  an English gloss phrase → array of matching Vietnamese headwords. Lazily
  fetched by `loadDictionaryData()` only when "Add a word" opens (not at app
  startup — a one-time download, cached by the service worker afterward).
  `lookupVnInDictionary()`/`lookupEnInDictionary()` query it.
  **The user can never type a word straight into Save** — "Check word"
  (`checkDuplicates()`) renders every matching entry via `dictSenseRows()`:
  the headword once, then **each individual sense as its own row with its
  own Apply button** (capped at `MAX_SENSES_SHOWN` = 2, "+N more senses"
  beyond that) — so picking "dog" applies exactly "dog", not every sense of
  "chó" glued together. Clicking Apply calls `applyDictionaryEntry(vn, en)`,
  which overwrites both inputs with that exact spelling + single gloss,
  re-runs `findVnDuplicate()` against it, and only then reveals the Save
  button (`#saveWordBtn` is `.hidden` by default and after every edit — see
  `clearCheckResult()`). This exists specifically to stop a typed-but-
  uncorrected spelling (e.g. "meo") from being saved just because it happens
  to match a real word ("mèo") once diacritics are stripped —
  matching-for-the-check and what-gets-saved used to be the same string,
  which was the bug. `.check-result` has a `max-height` with internal
  scroll so a long sense list (e.g. "ban"'s 11 senses across 12 headwords)
  doesn't push Save far down the screen. A not-found entry shows an inline
  "Report this word" row (`reportRow()`) instead of an Apply button, calling
  `openReportPopup({vn, en})` directly (no separate modal) so it lands on
  the Issues screen for later review. **`findVnDuplicate()`'s "exact" match
  requires literal string equality** (`w.vn === vn`), not just same-after-
  normalizeVn — two different accented words that only share their bare
  spelling (e.g. "chó" dog vs "chỗ" place) fall through to the non-blocking
  "near" warning instead of being wrongly treated as the same word already
  in the list. This only became safe to tighten because Apply always writes
  a real dictionary headword's exact spelling into the VN field before Save
  is ever reachable — free-typed near-misses like "meo" can no longer reach
  this check at all. Regenerate the dictionary file with `python3
  scripts/build-dictionary.py` if the upstream source ever needs
  refreshing.

- **Grammar** (`data/grammar-<bookId>.json`, e.g. `data/grammar-connect1.json`):
  an array of card objects `{id, lesson, title, structure, explanation,
  examples: [{vn, en, book}], scaleHtml?}`. `structure`/`explanation`/`vn`/`en`
  are **pre-rendered HTML strings**, not plain text — they already contain
  `<mark class="hl">...</mark>` around the rule's own literal keywords (styled
  red, see CSS) and `<span class="gd-ph">[...]</span>` around placeholder
  words (`[subject]`, `[verb]`, `[degree word]`..., always lower-case,
  bracketed, italic, never bold — this convention is deliberate, keep it
  consistent for any new rule added later). Storing HTML directly (instead of
  structured segments a JS renderer would assemble) matches this project's
  no-build-step, single-file philosophy — same pragmatic tradeoff as the
  reference dictionary's pre-trimmed glosses. `examples[].book: true` marks a
  sentence taken verbatim from the textbook (rendered with a gold left
  border, `.gd-example.book`) vs. one written for this app to fill out to
  **5 examples per rule**; every rule was checked for one-word-two-meanings
  clashes across lessons before being written (e.g. "mới" means "just did X"
  in Bài 1 but "not until X, later than expected" in Bài 3 — both cards
  cross-reference each other in their explanation text so the two senses
  don't get confused). `scaleHtml` is optional, set on exactly one card so
  far (Bài 1 "Degrees of liking") — a full `<div class="gd-scale">` block (a
  red→gold→jade gradient bar, one tick per level, each level's label angled
  underneath its own tick) injected as-is into `#gdScaleContainer`; add the
  same field to any future rule that similarly benefits from a visual scale.
  Loaded via `loadGrammarData()` (eager, alongside `loadBooksData()` at
  startup — these files are small, unlike the reference dictionary — tags
  each card with `book: bookDef.id`, filling the global `grammarData` array)
  and filtered by `activeGrammar()`, which reuses the **exact same
  active-scope** that gates vocabulary (`getActiveScope()` — a grammar rule's
  `lesson` number is checked against `scope[card.book][card.lesson]`, so
  toggling a lesson on/off in Settings → Vocabulary sources unlocks/hides its
  grammar rules too, no separate toggle). Grammar has **no learning-memory
  tracking** — no streak, no session draws, pure consultation, deliberately
  separate from the flashcard system; the home screen's Grammar card just
  shows a live count (`refreshGrammarCard()`, called from `refreshStats()`)
  instead of the Vocabulary card's known/review bars — deliberately
  book-agnostic text (just "N rules unlocked"), since it now sums rules
  across every book with a `grammarFile`, not just Connect 1.
  `data/grammar-connect2.json` (21 cards, chantier 13) extracts from a
  **different heading marker** than Connect 1's PDFs — Connect 2's grammar
  boxes are tagged "Cấu trúc" (Structure) / "Ngữ dụng" (Language Usage)
  instead of "Câu giao tiếp" — found by searching each page's text for
  either string. Connect 2 Bài 6 is a pure review/capstone lesson (recycles
  earlier structures like `vừa...vừa`/`tuy...nhưng` in new exercises) and
  genuinely introduces no new grammar box of its own — confirmed by
  exhausting every marker search on that PDF, not a missed extraction — so
  it has zero cards and never appears as a group in the Grammar tab.

- **Statistics** (`daily-stats` and `stuck-cards` localStorage keys, chantier
  17): `dailyStats[YYYY-MM-DD]` (local calendar day, via `todayKey()`) =
  `{cardsFlipped, correctAnswers, incorrectAnswers, sessionCompleted}` —
  created lazily on the day's first flip (`ensureTodayStats()`, called from
  `markCard()`), never eagerly at startup, so a day with no activity simply
  has no key (the histogram/streak logic tell "no session" apart from "0
  cards" this way). Counted **once per card drawn**, not per underlying id —
  same convention as `sessionResults` (chantier 16): a merged VN-homonym
  card is one flip. `sessionCompleted` is set at the exact point
  `renderCard()` detects `deckPos >= deck.length` (natural deck exhaustion)
  — deliberately **not** set on an early exit via `#exitBtn`, mirroring the
  sessionResults screen's own "only on full completion" rule. The home
  Statistics card's "🔥 N-day streak" and the Statistics screen's own streak
  metric (`computeStreakDays()`) walk backward from today counting
  consecutive `sessionCompleted` days; if today has no completed session yet
  that alone doesn't break the streak — the walk just starts from yesterday
  instead (finishing later today still keeps it, same as most habit-tracker
  apps). The 7-day activity histogram uses a **rolling 7-day window**
  (`last7DaysKeys()`, today always last), not a Mon-Sun calendar week —
  chosen for simplicity over calendar-week alignment, confirmed with the
  user. `stuckCards[id][dir]` = `{consecutiveAttempts, lastSeen}` — tracked
  **independently per direction** (confirmed with the user: a word can be
  stuck VN→EN without being stuck EN→VN), populated by `updateStuckCard()`
  inside `applyAnswer()`. A word/direction becomes "stuck" only when it was
  *already* at streak -3 on a previous appearance and stays at -3 after this
  answer too (`prevStreak === -3 && newStreak === -3`) — first reaching -3
  doesn't count yet. Climbing back above -3 clears only that direction's own
  entry; the other direction (if also stuck) is untouched. The Statistics
  screen's "Stuck cards" section flattens `stuckCards` into one list of
  `{id, dir, consecutiveAttempts, lastSeen}` instances (so a word stuck both
  ways appears twice, once per direction), sorted **worst offenders first**
  (`consecutiveAttempts` desc, ties broken by `lastSeen` desc — chantier
  20, changed from a pure recency sort so the cards that have been wrong
  the most times in a row while stuck float to the top), top 5 shown as a
  **2-line row** each — condensed from an initial 3-line design
  (chantier 18) specifically so all 3 sections fit one screen with no
  scroll on a typical current phone. Row layout, left to right (chantier
  19): direction flags, then the word pair, then the streak count pinned to
  the far right. **Which word is bold/primary is not fixed to Vietnamese**
  — it follows the direction actually being tested (`vn2en` prompts VN
  first → VN bold with the EN gloss as subtitle; `en2vn` prompts EN first →
  EN bold with the VN word as subtitle), matching the flag order from
  `dirFlags(dir)` right next to it; the subtitle is ellipsis-truncated
  (`text-overflow:ellipsis`) so a long gloss can never force a 3rd line.
  Entry point: a 3rd home-screen `.vocab-card` ("📊 Statistics", same style
  as Vocabulary/Grammar) → `renderStatisticsScreen()`, rebuilt fresh every
  time the screen opens (cheap enough — 7 days + up to 5 rows — that
  there's no need to cache or diff it). The metric-card row sits under its
  own "Today" section title (same style as "Last 7 days"/"Stuck cards"),
  and each histogram row shows that day's raw `cardsFlipped` count to the
  right of the bar, in addition to the success-rate % already inside the
  green segment — the % is a rate, the count is a volume, chantier 18 added
  the count so both are visible at once. Every VN↔EN direction label
  anywhere in the app (this screen, the home Vocabulary card, the per-word
  popup, the report popup) is rendered by the single `dirFlags(dir)` helper
  — `🇻🇳 → 🇬🇧` / `🇬🇧 → 🇻🇳` — instead of "VN → EN"/"EN → VN" text
  (chantier 18). Statistics' CSS sizing was calibrated **twice**: chantier
  18 squeezed everything down to fit the smallest phone on the market
  (iPhone-SE-class, 375×667) with no scroll at all; live use on the user's
  own (larger, more typical) phone found that read as cramped, so chantier
  19 backed the sizing off to target a common current phone instead
  (~390×844, e.g. iPhone 13/14) — comfortably fits there with zero scroll,
  and only needs a small scroll on the smallest phones, which was judged
  the better tradeoff.

