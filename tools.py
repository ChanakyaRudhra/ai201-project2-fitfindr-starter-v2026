"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively - "M" should match "S/M".

                     \u26a0\ufe0f  Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec - decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches - an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic - thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts -
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings(\'graphic tee\', max_price=30))"
    """
    import re

    def size_tokens(s: str) -> set[str]:
        return set(re.split(r"[^A-Za-z0-9]+", s.upper())) - {""}

    listings = load_listings()
    target_size_tokens = size_tokens(size) if size else None

    candidates = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if target_size_tokens is not None:
            listing_size_tokens = size_tokens(listing["size"])
            if not (target_size_tokens & listing_size_tokens):
                continue
        candidates.append(listing)

    query_words = set(re.findall(r"[a-z0-9]+", description.lower()))

    # Weighted scoring: a word match in the title or style_tags is a much
    # stronger signal of relevance than a word match buried in the listing's
    # free-text description. Scoring all three fields equally let incidental
    # description overlap (e.g. "layering under a graphic tee" in a mesh
    # top's description) outrank genuinely tagged matches.
    TITLE_WEIGHT = 3
    STYLE_WEIGHT = 2
    DESC_WEIGHT = 1

    scored = []
    for listing in candidates:
        title_words = set(re.findall(r"[a-z0-9]+", listing["title"].lower()))
        style_words = set(re.findall(r"[a-z0-9]+", " ".join(listing["style_tags"]).lower()))
        desc_words_listing = set(re.findall(r"[a-z0-9]+", listing["description"].lower()))

        score = (
            TITLE_WEIGHT * len(query_words & title_words)
            + STYLE_WEIGHT * len(query_words & style_words)
            + DESC_WEIGHT * len(query_words & desc_words_listing)
        )
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    return [listing for _, listing in scored[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.
    """
    title = new_item['title']
    category = new_item['category']
    colors = ', '.join(new_item['colors'])
    style = ', '.join(new_item['style_tags'])
    item_desc = f"{title} ({category}, colors: {colors}, style: {style})"

    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        prompt = (
            f"Someone is considering buying this thrifted item:\n{item_desc}\n\n"
            f"They haven't told you what else is in their closet. Suggest one or "
            f"two general outfit ideas for this piece - what kind of items would "
            f"pair well with it, described generally rather than referencing a "
            f"specific owned item."
        )
    else:
        lines = []
        for w in wardrobe_items:
            w_name = w['name']
            w_category = w['category']
            w_colors = ', '.join(w['colors'])
            w_style = ', '.join(w['style_tags'])
            lines.append(f"- {w_name} ({w_category}, colors: {w_colors}, style: {w_style})")
        wardrobe_lines = "\n".join(lines)
        prompt = (
            f"Someone is considering buying this thrifted item:\n{item_desc}\n\n"
            f"Here is their existing wardrobe:\n{wardrobe_lines}\n\n"
            f"Suggest one or two specific outfits that pair this new item with "
            f"pieces they already own. Name the actual wardrobe pieces by name."
        )

    return generate(
        prompt,
        system="You are a thrift-fashion stylist giving concise, practical outfit advice.",
        cache=config.CACHE_ENABLED,
        temperature=config.TEMPERATURE,
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.
    """
    if not outfit or not outfit.strip():
        return (
            f"No outfit suggestion was available to build a caption from for "
            f"{new_item.get('title', 'this item')}."
        )

    title = new_item['title']
    price = new_item['price']
    platform = new_item['platform']
    colors = ', '.join(new_item['colors'])
    style = ', '.join(new_item['style_tags'])

    prompt = (
        f"Write a short social media caption (2 to 4 sentences) for a thrift "
        f"find someone is posting about.\n\n"
        f"Item: {title}\n"
        f"Price: ${price}\n"
        f"Platform: {platform}\n"
        f"Colors: {colors}\n"
        f"Style: {style}\n\n"
        f"Outfit idea to reference: {outfit}\n\n"
        f"Write it like a real post, not a product description. Mention the "
        f"item, its price, and the platform once each, and be specific about "
        f"the vibe."
    )

    return generate(
        prompt,
        system="You write short, authentic-sounding social captions for thrift fashion finds.",
        cache=config.CACHE_ENABLED,
        temperature=config.TEMPERATURE,
    )
