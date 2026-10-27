#!/usr/bin/env python3
"""Build the static, sharded learning deck.

The script runs only when the vocabulary is intentionally rebuilt. The browser
never downloads WordNet or runs a translation/transliteration model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "sources" / "curated-words.json"
OUTPUT = ROOT / "data"
IWN_RAW = "https://raw.githubusercontent.com/cfiltnlp/IWN-WordLists/master"
FREQUENCY_RAW = "https://raw.githubusercontent.com/aparrish/wordfreq-en-25000/main/wordfreq-en-25000-log.json"
POS_FILES = {"noun": "dictionary-nouns", "verb": "dictionary-verbs", "adj": "dictionary-adjectives", "adv": "dictionary-adverbs"}
PACK_SIZE = 250
STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "into", "onto", "than", "then", "there", "their",
    "they", "them", "these", "those", "what", "when", "where", "which", "while", "who", "whom", "whose",
    "why", "how", "are", "was", "were", "been", "being", "have", "has", "had", "does", "did", "can",
    "could", "will", "would", "shall", "should", "may", "might", "must", "not", "but", "or", "nor",
    "yet", "so", "very", "more", "most", "some", "any", "each", "every", "either", "neither", "both",
    "all", "few", "many", "other", "another", "such", "own", "same", "just", "only", "even", "also",
    "about", "above", "after", "again", "against", "before", "below", "between", "during", "over", "under",
    "here", "there", "your", "ours", "theirs", "its", "our", "his", "her", "you", "she", "him", "hers",
    "bitch", "bastard", "cunt", "fuck", "fucking", "nigger", "penis", "porn", "rape", "rapist", "slut",
    "vagina", "whore",
}

LABELS = {
    "adjectives": "Adjectives", "adverbs": "Adverbs", "animals": "Animals",
    "birds": "Birds", "body": "Body", "clothing": "Clothing", "colors": "Colours",
    "family": "Family", "food": "Food", "fruits": "Fruits", "general-nouns": "General nouns",
    "house": "Home", "household": "Household", "kitchen": "Kitchen", "nature": "Nature",
    "numbers": "Numbers", "objects": "Objects", "phrases": "Phrases", "places": "Places",
    "time": "Time", "vegetables": "Vegetables", "verbs": "Verbs",
    "dictionary-adjectives": "More adjectives", "dictionary-adverbs": "More adverbs",
    "dictionary-nouns": "More nouns", "dictionary-verbs": "More verbs",
}

VOWELS = {"अ":"a","आ":"aa","इ":"i","ई":"ee","उ":"u","ऊ":"oo","ऋ":"ri","ए":"e","ऐ":"ai","ओ":"o","औ":"au"}
SIGNS = {"ा":"aa","ि":"i","ी":"ee","ु":"u","ू":"oo","ृ":"ri","े":"e","ै":"ai","ो":"o","ौ":"au","ॅ":"ae","ॉ":"o"}
CONSONANTS = {
    "क":"k","ख":"kh","ग":"g","घ":"gh","ङ":"ng","च":"ch","छ":"chh","ज":"j","झ":"jh","ञ":"ny",
    "ट":"t","ठ":"th","ड":"d","ढ":"dh","ण":"n","त":"t","थ":"th","द":"d","ध":"dh","न":"n",
    "प":"p","फ":"ph","ब":"b","भ":"bh","म":"m","य":"y","र":"r","ल":"l","व":"v","श":"sh",
    "ष":"sh","स":"s","ह":"h","ळ":"l","क़":"q","ख़":"kh","ग़":"g","ज़":"z","ड़":"d","ढ़":"dh","फ़":"f",
}


def romanize(text: str) -> str:
    chars = list(text)
    out: list[str] = []
    i = 0
    while i < len(chars):
        char = chars[i]
        if char in CONSONANTS:
            out.append(CONSONANTS[char])
            next_char = chars[i + 1] if i + 1 < len(chars) else ""
            if next_char in SIGNS:
                out.append(SIGNS[next_char])
                i += 1
            elif next_char == "्":
                i += 1
            else:
                out.append("a")
        elif char in VOWELS:
            out.append(VOWELS[char])
        elif char in {"ं", "ँ"}:
            out.append("n")
        elif char == "ः":
            out.append("h")
        elif char == "ऽ":
            out.append("'")
        elif char not in {"़", "्"}:
            out.append(char)
        i += 1
    result = "".join(out)
    return " ".join(re.sub(r"a$", "", word) for word in result.split())


def read_mapping(path: Path) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            key, separator, value = raw_line.strip().partition(": ")
            if not separator or not value or value == "null":
                continue
            mapping[key] = value.split()
    return mapping


def source_file(iwn_dir: Path | None, relative: str, temporary: Path) -> Path:
    if iwn_dir:
        return iwn_dir / relative
    destination = temporary / relative.replace("/", "-")
    urllib.request.urlretrieve(f"{IWN_RAW}/{relative}", destination)
    return destination


def clean_english(value: str) -> str | None:
    value = value.replace("_", " ").strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z '-]{2,38}", value):
        return None
    if len(value.split()) > 3 or value.lower() in STOPWORDS:
        return None
    return value.lower()


def first_native(values: list[str]) -> str | None:
    for raw_value in values:
        value = raw_value.replace("_", " ")
        if re.search(r"[ऀ-ॿ]", value):
            return value
    return None


def frequency_ranks(frequency_file: Path | None, temporary: Path) -> dict[str, int]:
    path = frequency_file or temporary / "wordfreq-en-25000-log.json"
    if not frequency_file:
        urllib.request.urlretrieve(FREQUENCY_RAW, path)
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {word.lower(): rank for rank, (word, _) in enumerate(rows)}


def imported_candidates(iwn_dir: Path | None, frequency_file: Path | None, existing: set[str]) -> list[dict]:
    candidates: list[dict] = []
    seen = set(existing)
    with tempfile.TemporaryDirectory() as tmp:
        temporary = Path(tmp)
        ranks = frequency_ranks(frequency_file, temporary)
        datasets = []
        english_parts: dict[str, set[str]] = defaultdict(set)
        for pos, category in POS_FILES.items():
            en_mr = read_mapping(source_file(iwn_dir, f"bilingual/English-Marathi/{pos}.txt", temporary))
            en_hi = read_mapping(source_file(iwn_dir, f"bilingual/English-Hindi/{pos}.txt", temporary))
            datasets.append((pos, category, en_mr, en_hi))
            for english_raw in en_mr:
                english = clean_english(english_raw)
                if english:
                    english_parts[english].add(pos)
        for pos, category, en_mr, en_hi in datasets:
            for english_raw, marathi_values in en_mr.items():
                english = clean_english(english_raw)
                if not english or english in seen or len(english_parts[english]) > 1:
                    continue
                marathi = first_native(marathi_values)
                hindi = first_native(en_hi.get(english_raw, []))
                if not marathi or not hindi:
                    continue
                rank = ranks.get(english)
                if rank is None:
                    continue
                display_english = f"To {english}" if pos == "verb" else english.capitalize()
                stable = hashlib.sha1(f"{pos}|{english}|{marathi}".encode()).hexdigest()[:12]
                candidates.append({
                    "id": f"iwn-{stable}", "category": category, "en": display_english,
                    "hi": hindi, "mr": marathi, "mr_roman": romanize(marathi),
                    "part_of_speech": pos, "source": "IndoWordNet", "review_status": "imported", "_rank": rank,
                })
                seen.add(english)
    return sorted(candidates, key=lambda card: (card["_rank"], card["en"]))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def build(total: int, iwn_dir: Path | None, frequency_file: Path | None) -> None:
    curated = json.loads(CURATED.read_text(encoding="utf-8"))
    existing = {card["en"].lower().removeprefix("to ") for card in curated}
    needed = max(0, total - len(curated))
    imported = imported_candidates(iwn_dir, frequency_file, existing)[:needed]
    if len(imported) < needed:
        raise RuntimeError(f"Only {len(imported)} suitable imported cards found; {needed} required")
    for card in imported:
        card.pop("_rank", None)

    cards_by_category: dict[str, list[dict]] = defaultdict(list)
    for card in [*curated, *imported]:
        cards_by_category[card["category"]].append(card)

    OUTPUT.mkdir(exist_ok=True)
    for old_file in OUTPUT.glob("*.json"):
        old_file.unlink()

    categories = []
    card_locations: dict[str, str] = {}
    for category in sorted(cards_by_category):
        cards = cards_by_category[category]
        shards = []
        for offset in range(0, len(cards), PACK_SIZE):
            shard_cards = cards[offset:offset + PACK_SIZE]
            shard_number = offset // PACK_SIZE + 1
            filename = f"{category}-{shard_number:02d}.json"
            write_json(OUTPUT / filename, shard_cards)
            shards.append({"file": f"data/{filename}", "count": len(shard_cards)})
            for card in shard_cards:
                card_locations[str(card["id"])] = f"data/{filename}"
        categories.append({
            "id": category, "label": LABELS.get(category, category.replace("-", " ").title()),
            "count": len(cards), "shards": shards,
        })

    search_index = []
    for category in categories:
        for shard in category["shards"]:
            for card in json.loads((ROOT / shard["file"]).read_text(encoding="utf-8")):
                search_index.append([card["id"], card["en"], card["hi"], card["mr"], card["mr_roman"], shard["file"]])
    write_json(OUTPUT / "search-index.json", search_index)
    write_json(OUTPUT / "manifest.json", {
        "version": 1, "total": len(curated) + len(imported), "curated": len(curated),
        "imported": len(imported), "categories": categories,
        "legacyLocations": {str(card["id"]): card_locations[str(card["id"])] for card in curated},
        "sources": [{"name": "Curated Marathi Shabd Cards"}, {"name": "CFILT IndoWordNet", "license": "CC BY-NC-SA 4.0"}],
    })
    print(f"Built {len(curated) + len(imported)} cards in {len(categories)} categories and {sum(len(c['shards']) for c in categories)} shards")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--total", type=int, default=5000)
    parser.add_argument("--iwn-dir", type=Path, help="Optional local clone of cfiltnlp/IWN-WordLists")
    parser.add_argument("--frequency-file", type=Path, help="Optional local wordfreq-en-25000-log.json")
    args = parser.parse_args()
    build(args.total, args.iwn_dir, args.frequency_file)
