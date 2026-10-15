# Presentation context (resume point for the interview walkthrough)

Status as of 2026-10-15. Read this first when continuing the presentation work from another
machine or another Claude session. HANDOFF.md still holds the git rules (noreply identity,
`unset GH_TOKEN` before pushing) and the submission rules; both still apply.

## Where things stand

- The take-home (`Lending_Analytics_Design.docx`, repo root) was submitted and passed. It is
  the source of truth and must not be edited.
- Second-round in-person interview is on 2026-10-16. The deliverable now is a 12-minute
  walkthrough for the hiring panel, not a new document.
- Done: a 13-slide deck (online artifact and a .pptx), a talk-track note, and one independent
  review whose fixes are applied. Everything is committed on `main` of
  https://github.com/thiqngn/GoTymeX.
- Not done: the mock Q&A rehearsal; verifying three vendor dates in the document (see Known
  nits below).

## Files and what each one is for

| Path | What it is |
|---|---|
| `docs/Lending_Analytics_Walkthrough.pptx` | The PowerPoint to present from. 13 slides, 16:9, speaker notes on every slide. Cambria headings, Calibri text. |
| `docs/deck/build_pptx.py` | Builds that .pptx from the figures. The slide text lives in this script; edit here and rebuild, never in PowerPoint, or the two copies drift. |
| `docs/deck/project/deck.json`, `docs/deck/project/slides/*.html` | Source of the online deck (Claude Slides artifact). One HTML section per slide, the `<aside>` is the speaker notes. Same wording as the .pptx. |
| `docs/figures/image*.png` | The 12 figures used by both decks, extracted from the .docx. Numbered as the .docx media files, not as the captions. |
| `docs/deck/docx2md.py` | Extracts the .docx to markdown plus media, for re-reading the document without pandoc. |
| `docs/notes/interview-walkthrough.md` | The talk track in seven beats, the clever bits ranked, ten expected questions with answers, the nits to pre-empt, lines not to cross. |
| `docs/notes/HANDOFF.md`, `CONTEXT.md`, `tricky-parts.md`, `patterns.md` | Planning notes from before the submission. Still useful for answering questions; some lines go beyond what the document says (see Rules). |

The online deck: https://claude.ai/artifact/FYd6ageeSeaVHX2c7q9Sec. It is private to the
claude.ai account that created it. From a different account, work from the repo files; a new
artifact can be published from `docs/deck/project/` (publish `deck.json` plus the slide files
with the Slides artifact type, and re-upload the figures, then fix the `/_blob/...` image
references to the new upload ids).

## The 13 slides

| # | id | Idea | Figure (document caption number) |
|---|---|---|---|
| 1 | cover | Title, the one-sentence frame | none |
| 2 | frame | Four databases, one shared value, nothing enforces it | 1 |
| 3 | questions | The four questions and what each really tests | none (table) |
| 4 | pipeline | One capture path feeds both speeds | 2 |
| 5 | stream | Record the alert first, then send it (outbox) | 3 |
| 6 | history | History captured, never reconstructed; capture gaps | 4 |
| 7 | boundary | Direct identifiers stop at one macro, one function, one principal | 17 (section 6.1; file image18.png) |
| 8 | star | Gold as a plain star plus written-once records | 8 |
| 9 | q1 | Pinned cohort, summing reason, freeze-diff-gate | 10 |
| 10 | q2 | Proves what the sources held, says what it cannot prove | 12 |
| 11 | q3q4 | Watchlist as a record; proof as evidence | 14 and 16 |
| 12 | decisions | The decision log in five principles (dark slide) | none (table) |
| 13 | close | Nothing open is blocking: ask, measure, owners | none |

Sections: intro (1–3), pipeline (4–6), model (7–8), answers (9–11), log (12–13).
Timing: 11 to 13 minutes uninterrupted; plan 20 to 25 with questions. If cut to ten
minutes: drop slide 8, merge slides 2 and 3.

## Design choices (keep them if editing)

- Canvas 1920×1080 in the HTML sources; the .pptx script maps design pixels to inches.
- Palette: navy `#15223A` (cover and slide 12 background, headings), off-white `#F6F3EC`
  (content background), orange `#E38B3A` (accents; matches the document's orange for clear
  identifiers), teal `#1F6F8B`, body text `#3C4656`, muted `#6B7484`, rule `#DED8CC`.
- Online deck fonts: Source Serif 4 headings, IBM Plex Sans text. The .pptx uses Cambria and
  Calibri so it renders the same on any Office install.
- Every content slide: heading at the top margin, figure on a white panel, footer with the
  figure's caption number in the document and the slide number.

## Review already applied

An independent reviewer read only the document and the deck. Verdict: faithful, sensible
order, no contradictions. Applied fixes: three slides resized to avoid overflow; seven note
sentences that came from the planning notes rather than the document were removed or rewritten
(cohort-level diff per mapping version, "signed by the three teams", the KYC refresh line,
unnamed owners for the 14-day window and the source contract, "ships on day one"). The .pptx
was rendered through PowerPoint and checked slide by slide after four layout fixes.

Still my framing rather than the document's words, and fine to keep: the three words
"append-only, as-of, honest"; the "what it tests" column on slide 3; the third bullet under
"Measure from the data" on slide 13.

## Known nits that travel into the deck (do not redraw before the interview)

- Figure 10 (slide 9): the headline funded share is about half a point off the channel-weighted
  average. Say "illustrative"; do not read the numbers aloud.
- Figure 12 (slide 10): the header says four inputs and the tile says 1 of 4, but the table has
  five rows and three carry flags. If asked: five inputs, the record carries a flag per input.
- Figure 17 (slide 7): the arrow from the applicant box leads to the box naming the JSON blobs,
  which live in other tables. A drawing shortcut; the document's text places them correctly.
- Figure captions in the document run 16, 19, 17, 18 in reading order. Footers cite the number
  as printed.
- Three vendor dates in the document are unverified: "Declarative Automation Bundles (formerly
  Databricks Asset Bundles)", "ABAC mask policies GA since April 2026", "Lakeflow Connect MySQL
  CDC Beta as of July 2026". Check current docs, or say "bundles" and "the beta connector".
- Section 7 of the document never states the bank-local time zone (Asia/Manila) or the
  regulator assumption in words. One-line answer if asked: cohort month is bank-local,
  timestamps stored in UTC with the source zone recorded; the regulator assumption is a
  one-line change.

## Rules for any edit

- No candidate name and no employer name anywhere in the deck or notes (the cover byline is
  "Walkthrough of the submitted design"). HANDOFF.md's candidate line is the only occurrence
  in the repo and is planning material.
- Patterns only: no company, system or table names from past work; no figures from past work;
  do not claim production experience with Lakeflow, DMS or Structured Streaming.
- Slide text and speaker notes say only what the document says. The planning notes
  (CONTEXT.md, patterns.md, tricky-parts.md) hold ideas the document does not, so a line taken
  from them must be checked against the .docx first.
- Keep the .pptx and the HTML sources in step: change the wording in both, or in
  `build_pptx.py` and the matching `slides/<id>.html`.

## How to rebuild the .pptx

Needs Python with `python-pptx` and `Pillow`. From the repo root:

```bash
python docs/deck/build_pptx.py docs/Lending_Analytics_Walkthrough.pptx docs/figures
```

To re-extract the document text and figures (writes `draft.md` and `media/` into the output
folder; keep that folder out of the repo):

```bash
python -I docs/deck/docx2md.py Lending_Analytics_Design.docx <output-folder>
```

To check the render on Windows with PowerPoint installed, export the slides to PNG through
PowerShell (`$app = New-Object -ComObject PowerPoint.Application`, open the file, then
`$p.Export("<folder>", "PNG", 1600, 900)`) and look at each image.

## Next steps

1. Mock Q&A: Claude plays the panel, one question at a time from section 3 of
   `interview-walkthrough.md`, pushing back on weak answers. First question: why DMS instead of
   the Kafka CDC topics the services already have.
2. Verify the three vendor dates before the interview.
3. Ask the panel at the start how long they want; cut per the timing note above.
