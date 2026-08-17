# Changelog — Nhặt Chữ

Chantiers 1–19, moved out of CLAUDE.md (2026-08-17) to keep session startup lean. Chantiers 20+ live in CLAUDE.md itself (most recent 3 kept inline for immediate context, older ones roll off the bottom of this file's counterpart section into here as the project continues).

## Chantiers completed so far

1. Ported from a Claude.ai artifact to a standalone static site: `window.storage`
   → `localStorage`, Haiku check disabled, GitHub Pages deployment, PWA
   manifest/icons/service worker, Export/Import.
2. Vocabulary restructured for multi-book support: `data/connect1.json`
   extracted from inline code, `BOOKS` catalog, per-lesson active-scope
   filtering, new Settings screen (sources / data / reset).
3. Settings UI redesign: bigger home menu buttons, 3-entry Settings menu,
   vertical lesson checklist, disabled Connect 2 preview, mobile viewport
   fix (`svh`).
4. Connect 2 vocabulary added: `data/connect2.json` (410 words, lessons 1-6)
   extracted from the source PDFs (see "Known constraints" for how), `BOOKS`
   catalog entry added, the now-obsolete "COMING SOON" preview block removed
   from Settings → Vocabulary sources, `sw.js` cache updated. Lessons default
   to inactive, same as any newly-added book.
5. Add-word verification redesigned around a reference dictionary instead of
   the disabled Haiku check (see "Data model" for the mechanics). Went
   through two iterations before landing: (1) hard-blocked Save on a raw
   not-found/duplicate word, using the FVDP/OVDP dictionary (GNU GPL) —
   replaced after catching a real bug, typing "meo" got silently saved
   as-is just because it matched "mèo" once diacritics were stripped, since
   Save trusted whatever was literally typed; (2) switched to an Apply-only
   flow (type roughly → "Check word" → pick the exact dictionary spelling →
   Save only appears once applied) and, separately, swapped the dictionary
   source to Wiktionary data (CC BY-SA) after the FVDP source's ~20-year-old,
   unpunctuated glosses turned out to combine multiple senses into one messy
   blob (e.g. "chó"/dog rendered as "Dog spaniel boxer saluki") — fixed by
   showing each sense as its own Apply row instead of joining them. Also
   fixed `findVnDuplicate()`'s exact-match to require literal spelling
   equality (was flagging unrelated words like "chó" dog and "chỗ" place as
   duplicates just for sharing a bare spelling). "Report an issue" popup
   generalized to also cover not-yet-saved words, surfaced inline instead of
   a separate modal.
6. Settings polish: **Vocabulary sources** rebuilt as a 3-column lesson grid
   per book (see "UI structure") so it fits without scrolling with 2 books;
   **Reset Progression** split into its own **Reset** sub-screen with 2
   separate actions instead of one button — resetting learning progress
   (unchanged) is conceptually different from deleting user-created content,
   so "Reset manually added words" got its own entry, its own destructive-
   sounding wording, and a confirmation that names the exact word count
   before deleting (plus cleans up their now-orphaned `progress` entries).
7. "Report an issue" redesigned around a single persistent floating icon
   (`#floatingIssueBtn`, see "UI structure") instead of two separate entry
   points (session-only button, home-only menu row). Every `issueReports`
   entry now also records `page` (the screen it was opened from), captured
   automatically — no category picker was added (considered, then dropped
   as too heavy per the user). The `issues` screen gained a "+ New report"
   button (for reports with no specific word) and status filter pills
   (Unresolved/Resolved/All, mirroring the Vocabulary list's filter pattern).
   `sw.js` cache bumped to `nhat-chu-v6`. Still open: how to periodically
   surface unresolved reports to a Claude Code chat for review — deliberately
   left unsolved this chantier (see "Planned next").
8. Dictionary source switched from FVDP/OVDP (GPL, 1997-2007, unmaintained)
   to Wiktionary-derived data (CC BY-SA, actively maintained) after real
   words surfaced garbled glosses from the old source's ambiguous markup
   (see "Data model" for the "chó"/dog example). Check-word results now
   show each dictionary sense as its own row with its own Apply button
   (`dictSenseRows()`, capped at `MAX_SENSES_SHOWN` = 2 + "+N more senses"),
   instead of one Apply per headword that joined every sense into one
   string — so picking "dog" applies exactly "dog". `findVnDuplicate()`'s
   exact-match fixed to require literal spelling equality instead of
   diacritic-stripped equality, which had been wrongly flagging unrelated
   words sharing a bare spelling (e.g. "chó" dog vs "chỗ" place) as
   duplicates. `.check-result` capped at a `max-height` with internal
   scroll so a long sense list doesn't push Save far down the screen.
   Settings → Data credit line updated to Wiktionary/CC BY-SA. Also: the
   "Quick notes" scratchpad (bottom of "Add a word") removed entirely per
   the user — markup, CSS, the `quick-notes` localStorage key, and its
   Export/Import handling are all gone; `sw.js` cache bumped to
   `nhat-chu-v8`.
9. Two rounds of real-usage bug reports against the new dictionary, both
   fixed as build-script rules rather than one-off data edits (see "Data
   model" for `trim_gloss()`/`strip_verbose_paren()`): first "chó" showing
   both its senses squashed into one Apply, then "máy in" → "printer; a
   device, usually attached to a computer..." and "cua" → "crab (a
   crustacean of the infraorder Brachyura)" — short terms polluted with a
   long trailing explanation. The "+N more senses" note in `dictSenseRows()`
   was also just static text with no way to actually see those senses —
   turned into a real `<button>` that reveals them in place and removes
   itself. Separately: "Add a word" moved off `home` entirely, now opened
   via a small "+" icon button in the `wordlist` screen's header (see "UI
   structure"), whose header was also made to stay fixed while the list
   scrolls (previously the whole page scrolled the filters away).
10. Learning-memory system replaced end to end: the old last-outcome-only
    known/review/new categorization became a signed streak (-3..-1/1..3,
    skip zero) tracked independently per direction, with an exact-where-
    possible migration for existing progress and a redesigned draw
    algorithm (see "Data model" for all the mechanics). Also fixed a real
    bug caught during this chantier's own testing: the home stat bar's
    minimum-segment-width guarantee was drawing a visible colored sliver
    labeled "0%" for a category that rounded down to nothing, and applying
    the width correction sequentially could shrink an already-boosted
    segment back below its own minimum — `renderStatBar()` now hides any
    category that rounds to 0% and corrects all undersized segments in a
    single non-sequential pass. New UI: streak badges/pips in the
    Vocabulary list and its per-word popup, the home Vocabulary card's
    two-direction percentage bars, and a Settings → Learning method screen
    (4 named presets, no percentages shown — see "UI structure"). The
    visible `--red` was also brightened from `#9A3323` to `#D6412C`
    everywhere it's used (a single CSS variable, so one change cascades to
    the session "needs work" stamp, buttons, badges, etc.) — the old value
    read as too muted for something meant to draw attention. `sw.js` cache
    bumped to `nhat-chu-v16`.

11. New **Grammar** tab added (`grammar`/`grammarDetail` screens, home
    Grammar card — see "UI structure") with all 22 grammar rules from
    Connect 1 (Bài 1-6), extracted from the source lesson-body PDFs (not the
    vocabulary appendix used before — grammar boxes are scattered through
    each lesson under a "Conversational Phrase" / "Câu giao tiếp" heading,
    found by searching each PDF page's text for that marker rather than
    reading a structured appendix). Deliberately **not** a flashcard system —
    no streak, no session draws, pure consultation (see "Data model" for the
    full card shape and the active-scope reuse that unlocks rules per
    lesson). Went through several rounds of visual iteration before landing
    on the final design, all driven by user feedback on live mockups
    (published as Artifacts, since local file:// previews and the sandboxed
    render panel both turned out unable to run JS or even plain `<a href=
    "#...">` CSS `:target` navigation — the working mockup technique ended
    up being pure-CSS `:target` page-switching with no JS at all, later
    ported to real `showScreen()` calls for the actual app): detail view
    moved from a popup to a full page for room to breathe; rule keywords
    highlighted in bold red text (no background — an earlier gold-highlight
    version was rejected as "too busy"); a placeholder-word convention
    settled on (`[noun]`/`[verb]`/etc. — italic, lowercase, not bold, always
    bracketed — vs. the rule's own literal words in plain bold); textbook
    examples get a thin gold left border to distinguish them from the
    examples written for this app to reach 5 per rule; and one rule ("Degrees
    of liking", Bài 1) got a custom red→gold→jade gradient scale graphic
    (mirrors the app's existing streak colors) after two failed attempts —
    first a same-direction angled-label layout that overflowed and looked
    cluttered, replaced by shrinking the bar to ~76% width (which both frees
    room for the labels to lean into and pulls the ticks closer together)
    with every label at the same rotation angle, then centered. Also caught
    and fixed a real correctness bug during review: an early draft added
    "(only)" to every English translation of "mới" examples, but "only"
    actually comes from a *different* word ("thôi", which pairs with "mới"
    in speech per the textbook's own note) — kept only on the one example
    that actually contains "thôi" in the Vietnamese, and left uncolored
    (not red) there since it isn't really "mới"'s own meaning. `sw.js` cache
    bumped to `nhat-chu-v17`.

12. Home screen's Vocabulary card stat bars (`renderStatBar()`) got
    magnitude shading: the solid-green "known" segment and solid-red
    "review" segment are now each subdivided into 3 inner shades matching
    streak magnitude 1/2/3 (see "Data model" for the streak model) —
    magnitude 3 darkest, magnitude 1 lightest. `computeDirStats()` gained
    `knownByMag`/`reviewByMag` (additive, existing keys untouched) to feed
    this. Purely cosmetic: the outer known/review/new percentages, widths,
    and the `MIN_SEG_PCT` minimum-width legibility guarantee are all
    unchanged — the magnitude sub-shading only divides up the width a
    segment already got. Left-to-right order is deliberately different per
    color: green goes dark→light (most solid first), red goes light→dark
    (builds toward full "needs review") — chosen by the user, not
    symmetric. Added `text-shadow` to the known/review percentage labels
    since a lone light shade under the text is no longer guaranteed to have
    the old flat dark background. `sw.js` cache bumped to `nhat-chu-v25`.

13. Grammar extended to Connect 2: `data/grammar-connect2.json` (21 rules
    across Bài 1-5; Bài 6 is a review lesson with no new structures — see
    "Data model" for how the extraction marker differs from Connect 1's and
    why Bài 6 has zero cards), `BOOKS`' connect2 entry gained a `grammarFile`
    field, `sw.js` `ASSETS` gained the new file. Several Connect 2 rules
    revisit ground Connect 1 already covers with more depth or nuance
    (`Trong khi ... thì ...` vs. Connect 1's `khi / trong khi`; `Tuy ...
    nhưng ...` vs. `Mặc dù ... nhưng ...` within Connect 2 itself) — each
    such card's explanation cross-references the earlier one instead of
    silently duplicating it, per the project's one-word/one-concept
    cross-check convention (see "Data model"). Also added a per-lesson
    accordion to the Grammar list (see "UI structure" for the mechanics):
    each `.lesson-group` header is now clickable, shows a rule count in
    parentheses, and independently expands/collapses its rows — open by
    default, multiple groups can stay open at once (user's explicit
    preference, confirmed before building). Fixed a real staleness bug this
    surfaced: `refreshGrammarCard()`'s home-screen summary hardcoded "·
    Connect 1", which would have quietly misrepresented the count once a
    second book started contributing rules — removed rather than made
    dynamic, since the count itself was already book-agnostic and a second
    book name would have made the line noisy. `sw.js` cache bumped to
    `nhat-chu-v26`.

14. Vocabulary list search + badge polish: a free-text search box added
    below the language toggle (`#wlSearchInput`), diacritic-insensitive
    (reuses `normalizeVn()`) and scoped to whichever language is currently
    selected — see "UI structure" for the mechanics. The per-row `.wl-badge`
    streak indicator, previously a flat jade/red circle, now shades by
    magnitude with the exact same 6 hex values as the home Vocabulary card's
    stat-bar gradient from chantier 12, so the two known/review color scales
    read as one consistent system across the app. Also removed the
    `wordlistTitle` live rewrite ("Vocabulary | Status (DIR→DIR)") per the
    user — the header is now always a plain static "Vocabulary" regardless
    of the status/language filters. `sw.js` cache bumped to `nhat-chu-v27`.

15. Settings reorganized around Data/Reset. `exportIssues()` added in
    Settings → Data ("Export data (issues only)"): downloads only
    `issueReports` entries with `resolved: false` as
    `issues_YYYY-MM-DD.json` — a lighter counterpart to the existing full
    `exportData()` backup (renamed "Export data (all)" for contrast), reusing
    the same `Blob`+anchor download pattern. Settings → "Vocabulary sources"
    renamed to just "Sources" (menu entry, screen header, and the Grammar
    empty-state hint) now that it gates both vocabulary *and* grammar
    lessons via the same active-scope. Settings main menu reordered to
    Sources → Learning method → Data → Reset → Test mode; Data screen
    reordered to Export data (all) → Export data (issues only) → Import
    data. Settings → Reset → "Reset manually added words" no longer deletes
    everything in one tap: it now opens a new picker screen
    (`settingsResetVocab`, reusing the wordlist screen's sticky-header +
    scroll pattern) listing every custom word with an individually tappable
    checkmark (`.picker-row`/`.picker-toggle`, styled after the Issues
    list's resolved-toggle circle) plus a "Select all" row that toggles
    every word at once; the existing confirm-delete popup is reused as-is,
    its message now reporting the actual selected count instead of always
    "all". Deleting down to zero words auto-returns to the Reset screen;
    a partial delete just re-renders the picker with the remainder.
    `sw.js` cache bumped to `nhat-chu-v29`.

16. End-of-session "Results" recap card. Finishing a full session (deck
    exhausted, `deckPos >= deck.length` inside `renderCard()`) no longer
    tosses a generic toast and jumps to `home` — it now routes to a new
    `sessionResults` screen (see "UI structure") built around a card that
    reuses the flashcard's exact flip mechanic. Front face is static:
    "Results" / *Kết quả* (italic, below), same "tap to reveal" convention.
    Back face is **two independent columns**, ✅ (correct answers) and 🧠
    (wrong answers, mirroring the session buttons' own emoji) — each row
    is fully self-contained (`[before pastille] → [after pastille] × N`,
    both badges live in every row, no shared middle column). A word can
    only ever start a session from one of 7 pastilles (`null`/new, `-3`..
    `-1`, `1`..`3` — see `stepStreak()`, "Data model"), each with exactly
    one correct-answer destination and one wrong-answer destination
    (computed live via `stepStreak(pos, correct)`, never hardcoded), so
    each column always shows exactly those same 7 rows — fixed, so no
    scrolling is ever needed. A row whose count is `0` still shows its
    `[before] → [after]` pastilles (the point of the column is to make
    every reachable transition visible, not just what happened) — only the
    `× N` count text itself is omitted for that row, never printed as
    `×0`. The two columns deliberately run in **opposite directions**:
    `RESULTS_LADDER_CORRECT` (`[-3,-2,-1,null,1,2,3]`) reads worst-review-
    first, top to bottom, matching the ladder order used elsewhere (e.g.
    `renderStreakPips`); `RESULTS_LADDER_WRONG` is the reverse
    (`[3,2,1,null,-1,-2,-3]`) so the 🧠 column reads least-bad-first,
    ending on the single worst possible outcome — 🔴3 answered wrong again
    (`-3` "staying" `-3`) — at the very bottom. A "maintained" row (🟢3
    correct again, or 🔴3 wrong again) needs no special-casing: its
    destination badge is simply identical to its own starting pastille,
    which already reads as "stayed here." This is the *second* design
    pass — the very first version (a single shared-position 7×3 grid) was
    rejected by the user for burying the "worst" outcome in the middle of
    the grid instead of at a clear end, and for having no obvious reason
    the grid couldn't show an impossible transition; this two-column,
    opposite-direction, zero-omitted layout was specified directly by the
    user and validated by them before being built. Both design passes were
    proposed and confirmed with the user *before* code was written for
    either — worth preserving as the pattern for any future
    visually-driven feature request. Data capture (unchanged across both
    passes): `markCard()` reads the pre-answer streak via the existing
    `getStreak()` before calling `applyAnswer()`, and pushes
    `{prevStreak, newStreak, correct}` into a session-scoped
    `sessionResults` array (reset at the top of `buildDeck()`); for a
    merged VN-homonym card, only the first id's streak is recorded — one
    entry per card *drawn*, not per underlying id, same "representative
    sense" convention `mergeVnCard` already uses elsewhere. The results
    card's own front/back faces deliberately do **not** reuse the session
    card's `.face` class (new `.rs-face` instead) — `flipCard()`/
    `renderCard()` grab `.face.front`/`.face.back` via a bare
    `document.querySelector()`, and since every screen's markup stays in
    the DOM at once (only hidden via CSS), a shared class name would have
    let the wrong card answer that query depending on source order; the
    results screen gets its own small `flipResultsCard()` instead.
    `#sessionResults.screen` was still added to the existing
    `#wordlist.screen`-style `max-height:100svh` selector (see "Known
    constraints") as a safety net even though this bounded layout no
    longer strictly needs it to avoid overflow. `sw.js` cache bumped to
    `nhat-chu-v33`.

17. New **Statistics** tab (`statistics` screen, home card — see "Data
    model" for the full `dailyStats`/`stuckCards` mechanics and "UI
    structure" for the screen). Three sections: 3 metric cards (cards today,
    success rate, day streak), a rolling-7-day activity histogram (green
    correct / red wrong segments, bar width proportional to that day's card
    count), and a top-5 "stuck cards" list. Two new localStorage keys
    (`daily-stats`, `stuck-cards`), both additive — `progress` and every
    other existing key untouched. Two design decisions were confirmed with
    the user before/during the build rather than assumed: stuck-card
    tracking is **independent per direction** (a word can be stuck VN→EN
    without being stuck EN→VN — the initial proposal of a single combined
    entry per word id was corrected by the user), and the 7-day window is a
    **rolling** window (today always last) rather than a Mon-Sun calendar
    week, chosen for simplicity and confirmed before implementation. "End of
    session" for the streak/histogram reuses the exact same natural-
    deck-exhaustion point `renderCard()` already uses for the `sessionResults`
    screen (chantier 16) — exiting early via `#exitBtn` does not count.
    Caught and fixed during this chantier's own browser-based verification:
    an `ensureTodayStats()` helper was referenced (in comments and in both
    `markCard()` and `renderCard()`) but never actually defined — a
    `ReferenceError` that silently broke every "Got it"/"Needs work" button
    in the session screen. Found by driving a real session in the browser
    preview (flip → answer → check `dailyStats`) rather than only unit-
    testing the data functions in isolation — worth remembering as a reason
    to always exercise the real click path, not just the underlying logic,
    before calling a feature done. `sw.js` cache bumped to `nhat-chu-v38`.

18. Statistics polish, from live-usage feedback right after chantier 17
    shipped (see "Data model" for the exact mechanics touched):
    - **No-scroll layout**: stuck-card rows condensed from 3 lines to 2
      (word+direction on one line, gloss on the next, ellipsis-truncated so
      a long gloss can never force a 3rd line), and every Statistics
      spacing value (card padding, section margins, row gaps) tightened —
      specifically so all 3 sections (today / 7-day histogram / top-5 stuck
      cards) fit on one screen with zero scrolling on a small phone
      (verified at 375×667, iPhone SE-class, the smallest common target).
    - **Day counts on the histogram**: each of the 7 daily bars now shows
      its raw `cardsFlipped` count to the right, alongside the success-rate
      % already inside the green segment — volume and rate were previously
      conflated into a single number.
    - **"Today" grouping**: the 3 metric cards got their own section title,
      matching "Last 7 days"/"Stuck cards" — and "Cards today" was renamed
      to "Cards reviewed" since "today" is now redundant with the title.
    - **Flags instead of text everywhere**: "VN → EN"/"EN → VN" replaced by
      `🇻🇳 → 🇬🇧`/`🇬🇧 → 🇻🇳` app-wide (Statistics stuck cards, the home
      Vocabulary card, the per-word popup, the report popup) via one shared
      `dirFlags(dir)` helper — a global visual-consistency pass, not
      Statistics-specific, done in the same chantier because the stuck-card
      compaction already needed a compact direction indicator.
    Also folds in a same-day standalone fix that shipped between chantier 17
    and this one: the floating report/issues icon (top-right on every
    screen) had a permanently-empty label `<span>` still reserving
    line-height space beneath it, visibly pushing the icon above the
    header text next to it — removed, and the button's `top` offset
    retuned to center on that text now that the dead space is gone.
    `sw.js` cache bumped to `nhat-chu-v39` (icon fix) then `nhat-chu-v40`
    (this chantier).

19. Statistics tweaks from testing chantier 18 on the user's actual phone
    (see "Data model" for the exact mechanics touched):
    - **Sizing recalibrated**: chantier 18's no-scroll layout had been
      tuned against the smallest phone on the market (iPhone-SE-class,
      375×667) and read as too cramped on the user's own, more typical
      phone — every Statistics size bumped back up moderately, now
      calibrated against a common current phone (~390×844) instead. Still
      fits with zero scroll there; the smallest phones may now need a
      little scroll, judged the better tradeoff.
    - **Stuck-card word order fixed to the direction, not to Vietnamese**:
      the bold/primary word used to always be the Vietnamese one regardless
      of direction, which read backwards for an EN→VN row (you're being
      shown the English word first in practice). Now `vn2en` shows VN bold
      with the EN gloss as subtitle, `en2vn` shows EN bold with the VN word
      as subtitle — matches what's actually prompted in that direction.
    - **Stuck-card row re-laid-out**: direction flags moved to their own
      column on the far left (previously inline next to the word), then
      the word pair, then the streak count pinned to the far right —
      clearer scanning order than the chantier 18 layout.
    `sw.js` cache bumped to `nhat-chu-v41`.

