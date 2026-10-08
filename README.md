# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr is an agent for thrifting: you describe what you want (e.g. "a vintage graphic tee under $30, size M") and it searches real listings, works out what the item would pair with from your existing wardrobe, and writes a short caption you'd actually post about the find. Unlike a fixed pipeline, it decides what to do next based on what each step returns — if nothing in the listings matches, it stops and tells you what to change instead of continuing with nothing to work from.

---

## Tool Inventory

### search_listings(description, size=None, max_price=None)
- **What it does:** Searches the listings data for items matching a description, with optional size and price filters, returning the best keyword matches first.
- **Inputs:** `description` (str) — keywords describing the desired item. `size` (str | None) — a size string to filter by; matched by splitting both the target and the listing's size field on non-alphanumeric characters into uppercase tokens and requiring an exact token match (so "M" matches "S/M" but not "US 9" — this avoids false substring hits like `"s" in "us 9"`). `max_price` (float | None) — inclusive price ceiling.
- **Returns:** `list[dict]` of matching listing dicts (fields: id, title, description, category, style_tags, size, condition, price, colors, brand, platform), sorted by keyword-overlap score with `description`, highest first, capped at `config.SEARCH_RESULT_LIMIT`.
- **Empty case:** Returns an empty list — never `None`, never raises.

### suggest_outfit(new_item, wardrobe)
- **What it does:** Given a thrifted item and the user's wardrobe, asks the model for one or two outfit combinations using pieces the user already owns.
- **Inputs:** `new_item` (dict) — a listing dict. `wardrobe` (dict) — a dict with an `items` key holding a list of wardrobe item dicts; the list may be empty.
- **Returns:** `str` — a non-empty string with outfit suggestions naming specific wardrobe pieces.
- **Empty case:** When `wardrobe["items"]` is empty, returns general styling advice for the item as a string — never raises, never returns `""`.

### create_fit_card(outfit, new_item)
- **What it does:** Writes a short, two-to-four sentence caption someone would actually post about the find, mentioning the item, its price, and its platform once each, and specific about the vibe.
- **Inputs:** `outfit` (str) — the suggestion string returned by `suggest_outfit`. `new_item` (dict) — the listing dict for the item.
- **Returns:** `str` — a two-to-four sentence caption. Output varies run to run (model-generated, temperature > 0, caching disabled during real testing).
- **Empty case:** If `outfit` is empty or whitespace-only, returns a descriptive fallback message rather than raising.

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, `agent.py::run_agent` puts a message in `session["error"]` naming what the user could change (e.g. "No matches — try raising your price ceiling or using a broader description"), and returns the session immediately without calling `suggest_outfit` or `create_fit_card`. Otherwise, the first search result is stored as `session["selected_item"]`, and the loop proceeds to `suggest_outfit` then `create_fit_card`, storing each result back into the session before the next call reads it out.


**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::parse_query`. Extracts a `$amount` as `max_price` (first dollar figure found), an explicit "size X" phrase or a common standalone size token (XXS/XS/S/M/L/XL/XXL/S-M/M-L) as `size`, and treats the remaining text — with the price phrase, size phrase, and the word "under" stripped — as the search `description`.

**What moves through the session:** `query` → `parsed` (description/size/max_price) → `search_results` → `selected_item` (first result) → `outfit_suggestion` → `fit_card`. The branch checks `search_results`: if empty, `session["error"]` is set to a message naming what to change, and the function returns immediately without calling `suggest_outfit` or `create_fit_card`.

---

## Sample Run

**One full query** — to be added once the loop is wired (Milestone 5).

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', ...}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', ...}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', ...}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', ...}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', ...}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', ...}]
```

```
$ python -c "from tools import search_listings; print(search_listings('designer ballgown', size='XXS', max_price=5))"
[]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
**Buy them.** Vintage Levi's 501s are a closet staple... [2 outfits naming real wardrobe pieces: White ribbed tank top, Oversized grey crewneck sweatshirt, Black cropped zip hoodie, Black combat boots, Brown leather belt]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
You can't go wrong with these two effortless routes: 1. The Classic Casual Look... 2. The Streetwear Vibe... [general advice, no wardrobe items referenced — confirms empty-wardrobe path works]
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Nothing beats the effortless 90s streetwear vibe of a truly broken-in pair of vintage Levi's 501 jeans. I just scored these medium wash blues on Depop for $38 and they fit like an absolute dream. Throw them on with some fresh white sneakers and you've got the ultimate laid-back uniform.
```

**Variability check (cache disabled, criterion 4):** 3 runs on the same item, same outfit input, `AI201_CACHE=0`:
1. "Found the holy grail of denim today—these vintage Levi's 501 jeans... Just dropped them on my depop for $38..."
2. "Nothing beats the fit of broken-in vintage Levi's 501s. Snagged this medium wash pair for just $38 on depop..."
3. "Nothing beats the wash on these vintage Levi's 501 jeans... Got them for $38... Up now on my depop!"

No two share an identical opening sentence; all 3 mention the $38 price and the Depop platform.


---

## How I Used AI

**Moment 1**

- *What I asked for:* An implementation of `suggest_outfit` that builds a prompt from the new item and the wardrobe.
- *What came back:* A version that used backslash-escaped quotes inside f-string `{}` expressions (e.g. `f"{new_item[\\'title\\']}"`), which raised `SyntaxError: unexpected character after line continuation character` the moment I ran it.
- *What I changed:* Diagnosed that Python disallows backslashes inside f-string expression braces (pre-3.12), so I rewrote it to pull each dict value into a plain variable first (`title = new_item['title']`) and only referenced those plain variables inside the f-strings.

**Moment 2**

- *What I asked for:* Help deciding how `search_listings` should match on size, given the docstring's warning that a naive substring check is wrong (`"s" in "us 9"` is `True`).
- *What came back:* The suggestion to split both the target size and the listing's size field into uppercase alphanumeric tokens and require an exact token-set intersection, rather than a substring test.
- *What I changed:* Implemented it as written — `"M"` now correctly matches `"S/M"` (shared token `M`) but does not match `"US 9"` (no shared token), which was the exact failure case the docstring called out.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->



**Happy path**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee - Butterfly Print, Graphic Tee - 2003 Tour Bootleg Style, Vintage Band Tee - Faded Grey ... +7 more
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: **Outfit 1: Y2K Streetwear** *   **Top:** Y2K Butterfly Baby Tee *   **Bottoms:** Baggy straight-leg jeans (da...
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Found the ultimate early 2000s butterfly baby tee for just $18 over on Depop! I'm totally obsessed with the pi...
```

**Empty search**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[3] branch
      ->    empty search results, stopping
```

**On the MCP move:** `search_listings` was moved onto MCP because it doesn't call the model, making it the simplest seam to move first. `agent.py::run_agent` no longer imports `search_listings` directly; it now calls `call_tool("search_listings", {...})` from `mcp_client.py`, which starts `mcp_server.py` as a subprocess over stdio, sends the request, and returns the unwrapped result. The tool itself (`tools.py::search_listings`) is unchanged — `mcp_server.py` registers a thin wrapper around it with a description and typed inputs written for a reader who can't see the code. Running `python app.py ask 'vintage graphic tee under $30'` before and after the move returned the identical item, outfit, and fit card — the call now goes through a subprocess and the MCP protocol instead of a direct Python call, but the return value's shape and content were unaffected.


---


## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to irun this project: [RUNNING.md](RUNNING.md)**
