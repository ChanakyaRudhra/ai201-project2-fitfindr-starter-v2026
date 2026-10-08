# Acceptance criteria - FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card - in at least 4 of 5 tries.

**Why this target:**

My search is a plain keyword-overlap match, not semantic search - some phrasings in a query won't share any keywords with a listing's title, description, or style_tags even when a human would consider it a match. I'm leaving room for 1 miss from query phrasing the keyword scorer can't bridge.

> **Revised in unit 4:** Given a query that matches at least one listing, the agent completes all three tool calls and returns a fit card, in 5 of 5 tries on a known-good query. The retrieval-robustness-to-phrasing claim is dropped from this criterion.
>
> **Why revised:** `run_eval.py` maps each criterion to one scenario, repeated 5 times with the SAME query - not 5 different phrasings. `search_listings` is fully deterministic, so for a fixed query, retrieval either matches on every try or none; there is no way this test structure could produce a genuine 4-of-5 on the retrieval-robustness claim the original target was reasoning about. My 5/5 result confirms the pipeline didn't crash on a known-good query, not that search tolerates varied phrasing - that would need 5 distinct queries mapped to one row, which the current scenario-to-row structure doesn't support. The number wasn't wrong for what I originally meant; what I could actually measure with this harness is a narrower claim, so the criterion now says what was really tested.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change - 5 of 5 tries.

**Why this target:**

This path doesn't depend on word-level judgment calls the way criterion 1 does - it's a binary check (empty list or not) against a condition my code controls directly. If search_listings returns [], the branch either fires or it doesn't; there's no partial-credit phrasing issue like keyword overlap introduces in criterion 1.

---

## 3. Session state carries the selected item correctly

For 5 different queries that return results, the item named in
session["selected_item"] (by title or id) is the same item referenced in the
final fit card's text, in 5 of 5 tries.

**Why this target:**

State either flows through the session correctly or it doesn't - there's no model randomness involved in whether the right item's id or title shows up in the downstream output. A bug here would be deterministic and should reproduce every time, so I expect 5 of 5 rather than leaving room for a miss.

---

## 4. The fit card varies but stays grounded

Across 3 runs on the same item, no two fit cards share an identical opening
sentence, and all 3 mention the item's price at least once.

**Why this target:**

The fit card calls the model, so identical wording every run would actually mean something is wrong (caching or temperature=0), not that it's working well. But variation in wording shouldn't come at the cost of dropping required content - the price is a concrete, checkable detail that should survive every rewording, even as the opening sentence changes.

---

## 5. The empty wardrobe gets real advice, not a placeholder

Given an empty wardrobe, suggest_outfit returns a non-empty string of general
styling advice (not an error, not an empty string) in 5 of 5 tries.

**Why this target:**

This is a binary code path, not a model-quality judgment - the function either checks for an empty items list and branches into general advice, or it doesn't. Since the branch condition is deterministic and fully in my control, I expect this to hold every time rather than occasionally.

---

<!-- ────────────────────────────────────────────────────────────────────────
     UNIT 4 - read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.

         >
         > **Why revised:** "different" wasn't checkable - two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         X "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ─────────────────────────────────────────────────────────────────────────── -->
