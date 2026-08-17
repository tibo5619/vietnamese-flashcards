# UI Structure — Nhặt Chữ

Full screen graph and layout mechanics. Moved out of CLAUDE.md (2026-08-17) to keep session startup lean — see CLAUDE.md's "UI structure" summary for the short version and when to come here.

## UI structure

Screens (each a `<section class="screen">`, shown via `showScreen(id)`):
`home` → `session` / `add` / `wordlist` / `grammar` / `statistics` /
`issues` / `settings`.
`session` → `sessionResults` once the deck is exhausted (see "Data model" for
what it shows and how) — only on full completion; exiting early via `#exitBtn`
still goes straight to `home` as before, unchanged.
`grammar` (list, tapped from the home screen's Grammar card, styled like the
Vocabulary card but with a plain "N rules unlocked" count instead of
known/review bars) → `grammarDetail` (one rule, full page — not a popup,
deliberately, to leave room for the examples list — via `openGrammarDetail
(cardId)`, back button returns to `grammar` via `showScreen('grammar')`).
Both reuse the wordlist screen's established layout patterns rather than
introducing new ones: `.wl-sticky-header` / `max-height:100svh` + `.wordlist-
scroll` for the list (rows grouped into `.lesson-group`s, one per book+lesson,
title-only `.gram-row`s — the full rule only renders once opened, on
`grammarDetail`), and the same `max-height` + inner-scroll split on the
detail screen itself: `.gd-sticky` (title/structure/explanation, and the
optional scale graphic) stays fixed, only `.gd-examples` scrolls, so a rule
with many examples never pushes the explanation off-screen.
Each `.lesson-group` is a self-contained accordion (chantier 13): its
`.lesson-group-header` (the "Connect 1 — Bài 1 (5)" row, count from
`groups[key].length`) toggles the `open` class on its own `.lesson-group`
only, independent of every other group — plain `classList.toggle()`, no
persisted JS state, since `renderGrammarList()` only re-runs on a fresh
Home→Grammar entry (always starts every group `open` by default) and
`backFromGrammarDetail` returns to `grammar` without re-rendering, so
manually-collapsed groups stay collapsed across a detail-view round trip
for free. `.lesson-group-rows` (wraps the `.gram-row`s) collapses via a
`max-height` CSS transition rather than `display:none`, matching the app's
no-animation-library convention; the chevron rotates 90° and turns gold
when its group is open.
`showScreen()` tracks the active screen in `currentScreenId` and calls
`updateFloatingIcon()`, which drives `#floatingIssueBtn` — a single button
positioned outside all `.screen` sections (direct child of `#app`, `position:
absolute`, top-right) so it stays visible across every screen, including
mid-session. It has two modes, switched purely by CSS class/click-handler in
`updateFloatingIcon()`, not by separate markup: on `home` it shows a badge
(unresolved `issueReports` count, hidden at 0) and opens the `issues` screen
— the only way to reach the list; on every other screen except `issues`
itself (where it's hidden — the list has its own "+ New report" button) it
opens the report popup directly (`openReportPopup()`), capturing the current
session card if there is one, else just the page. This replaced two older
entry points: the session-only "Report an issue" button and the home-only
"Reported issues" menu row.
`settings` is a 4-entry menu (`.menu-btn` rows): **Vocabulary sources**
(→ `settingsSources`, per-book `.lesson-grid` of 3-column `.lesson-tile`s
instead of stacked rows — compact enough that Connect 1 + Connect 2 (12
lessons) fit on one screen with no scroll; the container still scrolls once a
3rd book is added) / **Data** (→ `settingsData`, Export/Import) / **Reset**
(→ `settingsReset`, a 2-entry sub-screen: **Reset learning progress**, opens
the pre-existing confirm popup — `progress = {}` — and **Reset manually added
words**, opens a confirm popup naming the exact word count, then clears
`customVocab` and deletes only the `progress` entries for those word ids;
if there are 0 custom words it shows a toast instead of opening the popup)
/ **Learning method** (→ `settingsLearningMode`, see "Data model" for what
each mode actually changes) — a single-choice list of `.method-row`s built
by `renderLearningModeList()`, one per key in `LEARNING_MODES`, each row a
fixed `min-height` (so "Consolidation"'s two-line subtitle doesn't make that
row taller than the others) showing only a title + plain-language subtitle,
deliberately no percentages.
The Vocabulary list (`wordlist`) and its per-word popup (`wlPopupBackdrop`)
show the streak from "Data model" two ways: `renderWordList()` draws a
compact `.wl-badge` per row (18px circle, the magnitude 1-3 as a digit
inside, empty outline if never seen) for whichever single direction the
`wlLangGroup` pill has selected — never both, since the list already shows
one direction at a time. The badge fill color is magnitude-shaded to match
the home Vocabulary card's stat-bar gradient exactly (chantier 12's
`known-mag1/2/3` / `review-mag1/2/3` hex values, `wl-badge.on-known.mag1/2/3`
/ `.on-review.mag1/2/3` in the CSS) rather than a flat jade/red — same
darker-is-more-entrenched convention, same two light shades needing a dark
text color override for legibility. A free-text search box
(`#wlSearchInput`, chantier 14) sits below the language pill: it filters
`words` against only the field for whichever language is currently
selected (`wordlistLang` doubles as the word object's own field name, `vn`
or `en`) via `wordlistSearchFilter()`, reusing `normalizeVn()` (see "Data
model") so an unaccented query like "chao" still matches "chào" — the query
never matches the other language's field, and it resets to empty every time
the screen is reopened from `home` (`statDirectoryBtn`'s click handler,
alongside the existing reset-to-"All" behavior). The header title
(`#wordlistTitle`) is a plain static "Vocabulary" — an earlier version
rewrote it live to "Vocabulary | Status (DIR→DIR)" on every filter change,
removed per the user as unnecessary noise. Tapping a row calls
`openWordPopup(w)` (takes the whole word object,
not just display strings, so it can look up both directions), which renders
the full detail via `renderStreakPips()`: a 5-pip `.wl-popup-pip` row per
direction, pivot at the middle pip (magnitude 1, colored by sign), extending
outward to the two pips on either side for magnitude 2/3 — never seen shows
all 5 empty. The home screen's Vocabulary card (`#vocabStats`, built by
`refreshStats()`) shows the same per-direction split as two compact rows
(`computeDirStats()` for the numbers), each a segmented `.vocab-stat-bar`
with all 3 percentages (known/review/never-seen, no decimals) centered
inside their own segment — deliberately not a single merged known/review
total across both directions, since a word known in one direction and not
the other used to make "known + review" over- or under-shoot the real word
count. `renderStatBar()` guarantees each shown segment (skipping any that
rounds to 0%) a minimum visual width so its own number stays legible,
borrowing the difference from the other segments in one non-sequential pass
(so boosting one small segment can never undercut another back below the
minimum — the two "small" segments can't both need it beyond what the one
guaranteed "big" segment can spare, since a real distribution can't have 2
of the 3 categories under 12% and still sum to 100).
`add` (Add a word) is no longer reachable from `home` — its entry point is
now `#addBtn`, a small `.icon-btn` ("+") in the `wordlist` screen's
back-row, next to the "Vocabulary" title. `backFromAdd` returns to
`wordlist` (re-running `renderWordList()` first, so a just-added word shows
up) instead of `home`. `wordlist`'s header (back-row, status/lang pills,
legend — everything above `#wordlistScroll`, wrapped in `.wl-sticky-header`)
stays fixed while the list scrolls: `#app` only sets `min-height`, so
normally a tall `.screen` grows past the viewport and the whole page
scrolls past the header too — `#wordlist.screen` alone gets a `max-height`
cap (`100vh`/`100svh`, same fallback pattern as `#app`), which makes
`.wordlist-scroll{flex:1; overflow-y:auto}` the actual scroll container
instead. Scoped to just this one screen by ID so it can't reintroduce the
`100dvh` address-bar bug documented below for `home`.

