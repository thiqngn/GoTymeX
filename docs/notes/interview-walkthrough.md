# Interview walkthrough: Lending Analytics Design (planning material, not for submission)

Purpose: a 12-minute walk-through of the submitted design for the second-round panel, plus
the points to stress, the questions to expect, and the lines not to cross. Written 2026-10-15
from the submitted `Lending_Analytics_Design.docx` (image numbers below refer to its figures).

Rules carried over from HANDOFF.md still apply in the room: patterns only, no company, system
or table names from past work; no dollar amounts or record counts; do not claim platform,
Spark-at-scale or streaming experience. Say "I designed", "I chose", "I rejected".

---

## 0. The one-sentence frame (say it first, say it last)

"Four services, four databases, nothing enforces the join. I built one append-only capture path,
turned it into as-of history, and put every business question on top of that history, so the
platform can always say what it knew, when it knew it, and what it did not capture."

Three words the panel should remember: **append-only, as-of, honest.**

---

## 1. The 12-minute track (seven beats)

Time per beat is a target; cut beats 4 and 5 to one line each if the panel steers early.

### Beat 1. The problem in one picture (1 min) — Image 1
- Four MySQL databases, three teams, REST and Kafka between them. The application number is
  the only value all four carry, under two column names, and nothing enforces it.
- Every cross-service join used to live in application code. The design moves it into the
  platform, once, with the evidence of where every value came from.
- Four questions: funnel, decision reproducibility, morning watchlist, PII proof. Everything
  else in the document exists to answer one of those four.

### Beat 2. Pipeline: one capture path, two speeds (2.5 min) — Images 2, 3, 4
- DMS reads each writer's binlog into S3 Parquet, one-minute files. Bronze is an append-only
  change log, continuous, full refresh blocked. Silver and Gold are a dbt project rebuilt
  daily at 05:00, tunable to 30 minutes.
- **Stress:** the daily build and the alert stream read the *same* landing files. They cannot
  disagree about what happened, and nothing is "real-time" unless a question needs it. Only one
  does: a failed disbursement, and money moving after a DECLINED decision.
- **Stress:** the alert table is also the outbox. Record first, send second, deterministic alert
  id from disbursement id + change sequence + rule. A crash never loses an alert; a replay never
  duplicates one. The daily build re-tests every disbursement as the backstop.
- **Stress (Image 4):** a `loan_offer` row re-issued and soft-deleted is one row in the source
  and three versions in Silver. "Even if the sources have since changed" is only answerable
  because nothing in Bronze is ever updated.
- Failure modes by design: a capture gap opens a row in `ref.capture_gap`, an as-of read inside
  it returns NOT_CAPTURED, a cohort over it freezes as HELD. A contracted column that disappears
  is the *only* hard failure in the pipeline; an unknown enum becomes UNMAPPED, still sums, and
  is published as a contract violation.

### Beat 3. Data model: the boundary and the star (2 min) — Images 5, 7, 8
- Nineteen history tables built by one macro, one row per captured version with valid_from /
  valid_to. Every as-of read in the document uses the same predicate on these tables.
- **Stress (identifier boundary):** direct identifiers stop at that one macro. national_id
  becomes a keyed hash (HMAC-SHA-256 with key_version); names, mobile, email, DOB go clear to a
  restricted schema. Only the transform principal can run the hash function, so nobody can
  compute the key for a chosen id. Rotation is just a daily rebuild from Bronze.
- Gold is a plain star: three facts (application, disbursement, whitelist entry), five
  dimensions, no stored aggregates; metrics are code-owned views, so Product owns a definition
  by owning a file. Dimension keys are the business codes themselves.
- Beside the star, written once and never edited: the frozen cohort, the decision input record,
  the morning watchlist snapshot, the quality-gate verdict. "What someone was shown" is a record.

### Beat 4. Q1 funnel: freeze, restate, gate (2 min) — Images 9, 10
- Cohort keyed on the *first* submission ever captured, so a rewrite of submitted_at cannot move
  an application between months.
- **Stress:** drop-off reason = first exit after the last re-entry on one cross-service timeline,
  read at day 14. Funded + five buckets + in-progress always sums to the cohort. The roll-up to
  the brief's five reasons is a versioned seed mapping, not logic, so Product can change it with
  a diff.
- **Stress:** a mature cohort is frozen; today's recompute is diffed against it; the two-threshold
  gate (flag / hold) decides publication, and ownership is split: the Lending squad sets flag,
  Product sets hold. A held cohort publishes a HELD row, never silence.

### Beat 5. Q2 reproducibility: the honesty boundary (1.5 min) — Images 11, 12
- The platform proves what the sources held and what the engine copied. It cannot prove what the
  engine read unless the engine says so. Say that out loud; it is the strongest thing in Q2.
- Every input carries an evidence grade and its own read time. Two bureau fetches in the read
  window → `ambiguous_input`. An input arriving after the record → a new record version flagged
  late-arriving; the old version stays. Records are re-derived weekly and a hash mismatch is
  published as a defect, never corrected. Legacy v1 decisions are served as-is, graded
  NOT_CAPTURED.
- This is where the confirm item comes from: ask the decision service for an inputs snapshot
  event keyed on application number + decision version. Small change, lifts every answer to the
  top grade.

### Beat 6. Q3 and Q4 together: operational list, regulatory proof (1.5 min) — Images 14, 15, 16
- Q3: offer read by version (the row is overwritten in place), acceptance as an anti-join at
  data_as_of, expiry-pending offers *lead* the list because a customer can still accept until the
  expiry job runs. Each morning's list is snapshotted, so "what ops was told" is a record too.
- Q4: proof is evidence, not configuration. Six evidence tables, none of them business data.
  **Stress:** audit logs and S3 data events go to a write-once bucket in a security-owned account
  the platform cannot alter; a probe principal in the analyst group reads masked columns every day
  and tries the forbidden layers; the absence proof scans every analyst-readable column for
  national-id and mobile patterns. Break-glass reads are joined to their ticket.

### Beat 7. The decision log in 60 seconds, then the ask (1.5 min) — Image 17 (captioned 19)
- Identity: normalised application number is the only cross-service key; person_key is a keyed
  hash of national_id; service UUIDs are kept and *measured*, never joined on.
- Joins: as of commit time, against history, to one common cut-off, orphans kept and published,
  grain tested on every entity.
- Rejected: holding back rows until sources agree. It ties every metric to the worst integration
  and changes the denominator, so the funnel stops reconciling to application counts. Instead:
  one owner per fact, every disagreement published with an owner, gate in aggregate.
- Close: "Everything I would confirm before shipping is in section 7, none of it blocking. The
  design works day one on DMS, and swaps to the services' Kafka topics without touching anything
  downstream of Bronze once six criteria are met."

---

## 2. The clever bits, ranked (if they only hear five things)

1. **One capture path feeds both speeds.** Batch and stream cannot disagree; NRT is justified
   from the schema (one use case), not from the brief's wording.
2. **The identifier boundary is one macro, one function, one principal.** No analyst-readable
   table has ever held a direct identifier, so Q4 is an absence proof plus access evidence, not a
   masking audit.
3. **Freeze, diff, gate, with split ownership.** Mature cohorts are written once; corrections are
   versioned restatements with a reason; the squad flags, Product holds; HELD is a row.
4. **The honesty boundary in Q2.** Evidence grades, ambiguous and late-arriving flags, weekly
   re-derivation with a hash, legacy served as-is. The platform never claims more than it saw.
5. **Outbox alert with deterministic ids.** Record, then send; replay-safe; target swappable.
6. **Capture gaps are data.** NOT_CAPTURED and HELD instead of a guess; the funnel starts at the
   first month with no gap.
7. **Disagreement is a dataset, not a blocker.** `dq_disagreement` with an owner per row; amounts
   expected to differ across hops get a tolerance per hop.
8. **The drop-off timeline rule.** First exit after last re-entry; buckets always sum; the roll-up
   is a versioned mapping Product owns.
9. **Kafka reuse with six criteria.** Shows you are not religious about DMS: the fallback is
   designed, with the exact conditions written down.
10. **Business codes as dimension keys; frozen rows carry names as text.** A frozen cohort never
    depends on a dimension that changes later.

---

## 3. Questions to expect, and the short answers

**Why DMS instead of the Kafka CDC topics the services already have?**
Reuse is the strongest alternative and I say so. I could not confirm six things about those
topics (all 19 tables, full after-image and deletes, commit time and in-commit order, keyed
partitioning, no compaction with retention above the recovery window, a snapshot path). Any one
missing means no history for Silver. DMS until an owner confirms; then Bronze reads the topics
and nothing downstream changes.

**Why dbt when it is not in the brief's stack?**
It runs on the same SQL warehouse and catalog, so it adds no engine or data store to govern. It
gives me model-level masks and tags reviewed with the code, seeds for versioned mappings, and
tests for grain and edge cases. The volume (thousands of applications a day) makes a full daily
rebuild cheap, which is what makes "a fix reaches all of history tomorrow" true.

**Why not stream Silver and Gold?**
No question reads Gold more than once a day. A 14-day cohort gains nothing from minutes. Always-on
compute and small files for no reader. The route is tunable to 30 minutes if that changes.

**What if an application returns to APPLYING after submission?** (known open point)
`last_submitted_at` is documented as "after edit", which implies it can. The cohort is keyed on
the first submission, so the application stays in its month; a later APPLYING_EXPIRED would need
its own fine code inside the cohort rather than exclusion. It is a confirm item I would add.

**Is REVERSED un-funding?**
The funded loan fact carries a negative row per reversal; the funnel keeps FUNDED as the
application service said it and flags `is_reversed`. The brief never says, so I did not decide
it silently.

**How do you handle a national_id that holds several ID schemes?**
I assume one scheme and publish two counts: values that collapse into one key after
normalisation, and applicants with the same name and mobile under different keys. Open question
to the application team; name matching widens personal-data use, so I show the size first.

**Key rotation breaks historical joins, doesn't it?**
Every row carries key_version and Silver is rebuilt daily from Bronze, so rotation is a re-key,
not a migration. The restricted schema and bridge are rebuilt the same morning.

**How is erasure reconciled with regulatory retention?**
Retention wins for raw data and decision records. Analytical layers honour erasure: the bridge
and identity rows go, personal attributes are nulled, seven days of table history then vacuumed.
Frozen cohorts carry no person at all.

**What breaks if decided_at is write time rather than commit time?**
The decision input record reads each input as of its own time with a 15-minute lag margin and
records capture lag; the ambiguity is measured from data, not assumed. Listed under "measured
rather than asked".

**What would you do first on day one?**
Get the six Kafka answers and the national_id answer, and get the source contract (19 tables,
enums, product map) signed by the three teams. The platform referees numbers that teams already
disagree on, so definition ownership is part of the deliverable.

---

## 4. Nits in the submitted document, so they never surprise you

Say "illustrative" and move on; do not volunteer these, but know them.
- Image 10: the headline funded share does not exactly equal the channel-weighted average of the
  per-channel rates (about half a point off). Values are illustrative.
- Image 12: header says "four inputs" and tile says "1 of 4", but the table has five rows and
  three carry flags.
- Figure captions in sections 5.1, 6.1 and 6.3 are numbered 19, 17, 18 in that order.
- Section 7 never states the bank-local zone (Asia/Manila) or the regulator assumption in words;
  Manila appears only in Image 14. If asked: "cohort month is bank-local, timestamps stored in
  UTC with the source zone recorded; the regulator assumption is a one-line change."
- The fifth question (whitelist-to-application) has a fact table but no answer section. If asked:
  it is `fct_whitelist_entry`, applied-within-30-days and funded-within-window per entry.
- Three vendor claims carry dates after my reference (Declarative Automation Bundles rename,
  ABAC masks GA April 2026, Lakeflow Connect MySQL CDC Beta July 2026). Verify against the docs
  tonight so you can say them with a straight face, or say "bundles" and "the beta connector".

---

## 5. Lines not to cross
- No past employer, product or table names. "A quoting system", "a CRM", "an alerting job".
- No numbers from past work. "Hundreds of records moved", "a seven-figure aggregate".
- Do not claim you have run Lakeflow, DMS or Structured Streaming in production. Say "I chose it
  because" and "the documentation says"; if pressed, "I have not operated this at scale; here is
  how I would find out on week one."
- Do not defend the vendor dates you have not verified.
