# Vocabulary change log (Connect 1 + Connect 2)

Not loaded automatically — read this file only when asked to look up why a
specific word was merged, reworded, or kept separate. One entry per word
per commit; exact before/after JSON is in that commit (`git show <hash> --
data/`).

## 2026-08-01 — commit `909a4b9`

Also added the "(N)" sense-count feature this commit: same-spelling VN
homonyms kept as separate cards get a grey "(N)" in the wordlist, and merge
into one card (all senses listed) on VN-front session cards. Code:
`mergeVnCard()` / `candidateCategory()` in `index.html`.

- **cảm / cảm lạnh** — merged into one card ("(to have) a cold"): same
  word, general vs medically-precise form.
- **mang / mang theo** — merged ("to carry with, to bring with"): "theo"
  just adds "along".
- **mát / mát mẻ** — merged ("cool, nice (weather)"): base word vs
  expressive/reduplicated form.
- **khô / khô ráo** — merged ("dry"): base word vs emphatic "thoroughly
  dry".
- **ngập / ngập nước** — merged ("flooded"): general (can be figurative)
  vs literal water flooding.
- **ồn / ồn ào** — merged ("noisy"): "ồn ào" is the form actually used.
- **tiện / tiện lợi** — merged ("convenient"): spoken/casual vs
  written/descriptive.
- **mùa hè / mùa hạ** — merged ("summer"), tagged (casu.)/(litt.):
  everyday vs literary/poetic register.
- **tiệc / bữa tiệc** — merged ("party"): word vs "the occasion" framing.
- **bếp / nhà bếp** — merged into "nhà bếp" only ("kitchen"): "bếp" alone
  is ambiguous (room vs stove).
- **ngừng / ngưng** — merged ("to stop, to pause, to cease"): regional
  variant (Bắc vs Nam).
- **bộ phận** — kept as 2 cards (true homonym): "part (machine, body)" /
  "department, division". Added "(machine, body)" for clarity.
- **chỉ** — kept as 2 cards (true homonym): "just, only, merely" / "to
  guide, to show, to instruct, to teach".
- **mới** — kept as 2 cards (true homonym): "just, very recently" / "just
  (later than expected)".
- **nên** — kept as 2 cards (true homonym): "therefore" / "should".
- **trả** — kept as 2 cards (true homonym): "to pay" / "to return, to
  give back".
- **hoạt động** — kept only the Connect 2 L2 sense ("operation, activity;
  to operate, to run"); Connect 1's shorter "activity" was redundant.
- **trên** — kept only Connect 2's fuller sense ("on, above, over, more
  than").
- **trong** — merged into one card ("in, inside, within, during"), kept
  in the earlier lesson (Connect 2 L1).
- **nhận** — kept only "to get, to receive"; dropped the "to hire, to
  recruit" sense instead of renaming it to "tuyển dụng" (that word already
  existed as its own card — would've been an exact duplicate).

## 2026-08-07 — commit `6c32325`

- **hang / động** — merged ("cave").
- **thoải mái / dễ chịu** — merged ("comfortable").
- **lười / làm biếng** — merged ("lazy").
- **tập / luyện tập** — merged ("to practice").
- **còn / vẫn** — merged ("still").
- **sản phẩm / mặt hàng** — merged ("product").
- **hàng hóa** — reworded to "goods, merchandise" (dropped "product" —
  that sense now lives on the merged sản phẩm/mặt hàng card).
- **hết** → "to be over; to run out (of)" / **kết thúc** → "to end; to
  finish; to conclude" — kept separate, reworded for clarity.
- **cuộc sống** → "everyday life" / **đời** → "one's life; lifetime" —
  kept separate, reworded.
- **tình yêu** → "love (noun)" / **yêu thương** → "to love; to care for
  (people, pets)" / **yêu thích** → "to like; to enjoy (things,
  activities)" — kept separate, reworded.
- **giá** → "the price" / **giá cả** → "prices (in general)" — kept
  separate, reworded.
- **rửa** → "to wash (body, dishes, food, ...)" / **giặt** → "to wash
  (clothes); to do the laundry" — kept separate, reworded.
- **hàng xóm** (casual) / **láng giềng** (formal) — kept separate, tagged.
- **tính** (casual) / **dự tính** (formal) — kept separate, tagged.
- **bà con** (casual) / **họ hàng** (formal) — kept separate, tagged.
- **nên** (casual) / **do đó** (formal) — kept separate, tagged.
- **kinh nghiệm** → "experience; expertise; skills" / **trải nghiệm** →
  "experience; to experience (life)" — kept separate, reworded.
- **nghỉ ngơi** → "to rest" / **thư giãn** → "to relax" — kept separate,
  reworded.

## 2026-08-08 — commit `1215a2d`

- **nghỉ** → "to stop; to take a break; to have a day off" / **nghỉ ngơi**
  → "to rest" — kept separate, reworded for clarity.
- **giọng** → "voice; accent; tone; dialect" / **giọng nói** → "speaking
  voice" — kept separate, reworded.
- **phụ / phụ giúp** — merged ("to help; to assist").
- **tiện ích** → "amenities; facilities (around a place/service)" /
  **tiện nghi** → "amenities; facilities (inside a place)" — kept
  separate, reworded.
- **mơ** → "to dream (general)" / **mơ ước** → "to dream; to wish for" —
  kept separate, reworded.
- **họp mặt / sum họp** — merged ("to get together; to gather; to
  reunite").
- **nghỉ lễ** → "to go on a holiday during public holiday" — reworded for
  precision (was just "to go on a holiday").
- **buổi học** → "class; lesson session" / **bài** → "lesson;
  practice/exercise" — kept separate, reworded for clarity.

## 2026-08-08 — commit `ed481b0`

- **rửa** → "to wash (with water)" — reworded.
- **vệ sinh** → "to clean; to maintain hygiene" — reworded.
- **xài** → "to use" / **sử dụng** → "to use" — kept as 2 separate VN
  cards (different spelling) but given the identical English gloss, by
  request — no casual/formal tag this time.
- **xài tiền** → "to spend (money)" — unchanged; now the sole "to spend"
  card since "xài" dropped that sense.

## 2026-08-16 — chantier 21 vocab-review session

- **mời** → "to invite (polite, formal)" — distinguished from "rủ"
  (friendly/informal invite); both confirmed accurate as a pair.
- **gấp ... lần**, **vừa ... vừa ...**, **tuy ... nhưng ...**, **hơi** —
  removed from vocabulary entirely (not reworded). Each already has its own
  full Grammar-tab card (structure/explanation/examples); keeping them as
  vocab flashcards too was pure duplication with no added value.
- **nhẹ** → "light (weight); mild, not serious" — the old gloss ("not
  serious, not severe") only showed the derived/figurative sense, missing
  the primary literal meaning.
- **nặng** → "heavy (weight); serious, severe" — same fix, mirror word of
  "nhẹ".
- **mong muốn** → "to wish for, to hope for (more formal/emphatic than
  muốn)" — old gloss risked an English connotation ("desire") the Vietnamese
  word doesn't carry (mong muốn is specifically non-sexual desire).
  **muốn** added as a new word ("to want (casual, everyday)") — more
  fundamental/frequent than "mong muốn" but wasn't in the list at all.
- **bao tay / găng tay** — merged into one card ("glove"), kept `bao
  tay`'s id (`b6`), deleted the separate `găng tay` custom-vocab entry.
  Genuine regional variant (bao tay = South, găng tay = North) — see the
  new "Regional-variant convention" in CLAUDE.md "Data model".
- **hướng dẫn** → "to teach, to instruct, to guide (formal, comprehensive)"
  / **chỉ** → "to guide, to show, to instruct, to teach (direct, simple)"
  — both already existed with near-identical, overlapping glosses; added
  short register qualifiers to distinguish them instead of rewording.
- **nhờ** → "to ask for a favor" — old gloss ("to ask for help; please")
  conflated the request itself with "giúp" (the actual act of helping).
- **lát nữa** → "a bit later (time only)" / **chút nữa** → "a bit later /
  a bit more (time or amount)" — both already existed, reworded together
  for consistent phrasing ("in a little while" → "a bit later") and to
  state the one real difference (chút nữa also covers quantity/degree).
- **túi tiền** → "budget, what one can afford (casual)" — old gloss
  ("budget, financial capacity") was accurate but overly abstract; register
  note added instead of the literal "money pocket" root (judged less
  useful here than for nhẹ/nặng, since the figurative jump is small).
- **bạn bè** → "friends (as a group)" — same core meaning, made the
  collective/plural sense visually clearer than a bare "s".
- **diện tích** → "size, area (e.g. m²)" / **khu vực** → "zone, area,
  region" / **dung tích** → "volume, capacity (e.g. liters)" — all three
  already existed; diện tích and khu vực both listed the bare word "area",
  the actual source of the confusion being reviewed. Standardized together
  rather than fixing one in isolation.
- **điện máy** → "appliances, electronics (general term)" / **điện tử** →
  "electronics (circuits, e.g. phones)" — both already existed sharing the
  word "electronics"; điện máy is the broad retail/everyday term (any
  electrical appliance), điện tử is the narrower technical one (devices
  with circuits).
- **chăm chỉ / siêng** — merged into one card ("hardworking, diligent"),
  kept `chăm chỉ`'s id (`c32`), deleted `siêng` (`b275`). **Type 2 by the
  classification found this same session** (different spelling, true
  synonyms, not similar/overlapping spelling) — per the merge-direction bug
  noted in CLAUDE.md "Planned next", this should end up split again in
  VN→EN once that mechanism exists; flagging here now so the future audit
  doesn't have to rediscover it.
