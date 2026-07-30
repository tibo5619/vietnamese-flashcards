# Nhặt Chữ — Vietnamese Flashcards

Static, single-page PWA for Vietnamese↔English flashcard practice. No backend,
no build step, no framework — plain HTML/CSS/JS, deployed as a free static
site. This file is read automatically by Claude Code at the start of any
session opened in this folder — keep it up to date after each chantier.

## Live site & repo

- Public site: https://tibo5619.github.io/vietnamese-flashcards/
- GitHub repo: https://github.com/tibo5619/vietnamese-flashcards (public —
  required for free GitHub Pages hosting on a personal account)
- Hosting: GitHub Pages, deployed from the `main` branch root, auto-rebuilds
  ~30-60s after every push.

## File structure

- `index.html` — the entire app: markup, CSS, and JS in one file.
- `data/<bookId>.json` — vocabulary for one book (e.g. `data/connect1.json`),
  an array of `{id, vn, en, lesson}`. Loaded at runtime via `fetch()`.
- `manifest.json`, `icons/` — PWA manifest + app icons (Add to Home Screen).
- `sw.js` — service worker, network-first caching (see "Known constraints").
- `.gitignore` — excludes `.claude/` (local Claude Code config) and `.DS_Store`.

## Data model

- **Vocabulary catalog**: `BOOKS` array in `index.html` (near the top of the
  `<script>`), e.g. `{ id, title, file, lessonsCount }`. `loadBooksData()`
  fetches every book's JSON file and tags each entry with `book: bookDef.id`,
  filling the global `baseVocab` array.
- **Recipe to add a new book** (e.g. Connect 2): drop `data/connect2.json`
  (same shape as `data/connect1.json`) → add one line to `BOOKS` → add the
  file path to `ASSETS` in `sw.js` and bump `CACHE_NAME` → done. Lessons
  default to **inactive** until the user turns them on (see active-scope).
- **Active scope** (`active-scope` localStorage key): `{ [bookId]: { [lesson]:
  true|false } }`. Drives `activeVocab()`, which feeds session draws, the
  Vocabulary screen, and home stats. `allVocab()` (unfiltered) is used ONLY by
  the duplicate check in "Add a word" — a word must be catchable as a
  duplicate even if its lesson isn't active yet. Connect 1 lessons default to
  active (pre-existing content); anything added later defaults to inactive.
- **Custom vocab** (`custom-vocab` localStorage key): user-added words,
  `{id, vn, en, lesson:null}`, always included in `activeVocab()` regardless
  of active-scope — no toggle for these.
- **Progress** (`progress` localStorage key): per-direction learning memory,
  `{ [wordId]: { vn2en: {correct, wrong, last}, en2vn: {...} } }`. `last`
  (`'correct'`|`'wrong'`) drives known/review categorization — a word flips
  category each time it's answered again. Weighted session draw: 60% new /
  30% review / 10% known (see the long comment above `buildDeck()` for the
  fallback cascade when a pool is short or empty).
- **Other localStorage keys**: `quick-notes` (free-text scratchpad),
  `issue-reports` (user-flagged translation/spelling/app-behavior issues).
- **All storage is `localStorage`** — per-device, per-browser, never synced,
  never sent anywhere. Export/Import (Settings → Data) is the only way to
  move data across devices/browsers.

## UI structure

Screens (each a `<section class="screen">`, shown via `showScreen(id)`):
`home` → `session` / `add` / `wordlist` / `issues` / `settings`.
`settings` is a 3-entry menu (`.menu-btn` rows): **Vocabulary sources**
(→ `settingsSources`, vertical per-lesson checklist, includes a disabled/
blurred preview section for not-yet-added books) / **Data**
(→ `settingsData`, Export/Import) / **Reset Progression** (opens the existing
confirm popup directly, no sub-screen).

## Known constraints (read before touching related code)

- **No native `confirm()`/`alert()`** — use the in-app `.wl-popup-backdrop`
  pattern instead. (Originally a Claude.ai sandbox quirk; kept as the
  established pattern for consistency even outside that sandbox.)
- **Card flip is 2D** (`transform: scaleX()`), not 3D `rotateY` +
  `backface-visibility` — the 3D version had a flicker bug.
- **Swipe uses Pointer Events on the card element** — interactive buttons
  must NOT be placed inside the card (it captures pointer events for swipe
  handling; a button inside the back face won't register clicks). Session
  action buttons live in `.session-actions`, outside the card.
- **Service worker is network-first**, not cache-first (`sw.js`, cache name
  bumped to `nhat-chu-v3`). A cache-first version was shipped first and
  caused already-installed phones to keep serving a stale `index.html`
  forever after a code update — don't revert this without re-solving that.
- **`#app` uses `min-height:100svh`**, not `100dvh` — `dvh` caused the home
  screen to visibly grow (pushing the footer off-screen) when a mobile
  browser's address bar collapses on scroll.
- **Haiku "Check with AI" is disabled**, replaced by a local-only
  "Check for duplicates" (no network call). The removal comment right above
  `checkDuplicates()` in `index.html` documents exactly how to re-add it via
  a serverless function (planned in a future chantier — see below).
- **No PDF of the source textbooks has ever been read in this Claude Code
  project.** The existing `data/connect1.json` (359 words) was extracted in
  a separate, earlier Claude.ai chat, before this project existed. To expand
  it or add Connect 2, the user needs to attach the relevant PDF pages in a
  new chat — Claude Code can read PDFs directly when attached.

## Working agreement with this user (complete beginner, non-technical)

- Explain concepts in plain language before acting; no unexplained jargon.
- **Never run `git push` — the user always runs it themselves in Terminal**,
  by design (credential safety: Claude must never handle GitHub tokens).
  Claude prepares commits locally and asks for confirmation first.
  Local-only git commands (init, add, commit, revert) don't need this.
- Ask for explicit confirmation before anything that touches GitHub or
  changes repo/account settings.
- Conversation in French, code/comments/UI text in English.
- One Claude Code chat per distinct chantier (mirrors this project's own
  history of "Sandbox chat" / "Production chat" / one chat per feature in
  its earlier Claude.ai days). Minor tweaks don't need their own chat — do
  them in whatever chat is already open.

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

## Planned next (not started)

- **Vocabulary content**: add Connect 2 (needs its PDF), broaden Connect 1
  beyond the end-of-book glossary (needs the lesson PDFs), rework existing
  Connect 1 entries (translations, sort-order handling for VN words starting
  with "(", recontextualizing). Note: the "(" sorting issue is likely a sort
  logic fix (ignore leading parentheses when comparing) rather than a data
  fix — don't rewrite entries just to work around it.
- **Add-word verification redesign**: replace the disabled Haiku check with
  something that doesn't depend on Claude.ai's sandbox — most likely a small
  serverless function (Cloudflare Worker / Netlify or Vercel function) that
  holds an API key server-side. Needs its own design discussion (which
  platform, how secrets are stored, deployment flow).
- **Later**: extract grammar rules from Connect 1/2 (needs their PDFs) for a
  possible grammar section; extract example sentences per word for a richer
  card back.
