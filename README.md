# Marathi Shabd Cards

A static flashcard site for learning everyday Marathi words from Hindi and English.

- `index.html` – loads the small deck manifest, then requests category shards only as cards are needed. After the first set, each set contains one word from the previous set, one from an older recent set, and three unseen words from different categories.
- `manifest.webmanifest`, `sw.js`, `icons/` – make the page installable as a home-screen app on iPhone and Android, with offline support.
- `data/manifest.json` – category names, shard locations, counts, and source metadata for the generated 5,000-card deck.
- `data/*.json` – generated category shards of at most 250 cards. These files are cached only after the app needs them.
- `data/search-index.json` – a compact index loaded only when a user searches.
- `sources/curated-words.json` – the original 711 reviewed cards with example sentences.
- `scripts/build_deck.py` – the one-time generator that combines curated cards with frequency-ranked IndoWordNet mappings.

Press **Next 5 words** for a set with two revision words and three new words. Recent sets and seen words are saved in the browser so revision continues across visits. Use the search at the top to find matching English, Hindi, Marathi, or romanised Marathi cards without changing learning progress.

The manifest and previously requested category shards are cached for repeat visits. Exact searches are prioritised; broad partial searches show at most 20 cards to keep the page responsive. See `DATA_SOURCES.md` for attribution and data licensing.

## Rebuilding the deck

The generated deck is committed to the repository, so GitHub Pages performs no data build and users never download source datasets. Rebuild only when intentionally updating vocabulary:

```bash
python3 scripts/build_deck.py --total 5000
```

The generator downloads eight bilingual mapping files from the official CFILT IndoWordNet repository plus a compact CC BY-SA English frequency list. Pass `--iwn-dir` and `--frequency-file` to use local copies.

## Hosting on GitHub Pages

1. Push `main` to GitHub.
2. On github.com open the repo, then **Settings → Pages**.
3. Under **Build and deployment** set Source to **Deploy from a branch**, Branch to **main**, folder **/ (root)**, and Save.
4. Wait a minute, then open `https://kuldeepkr16.github.io/learnings/`.

No deployment build step is required because generated category files are committed.

## Add to iPhone home screen

1. Open the Pages URL in **Safari** (not Chrome; only Safari can install web apps on iOS).
2. Tap the **Share** button, then **Add to Home Screen**, then **Add**.
3. Launch it from the home screen. It opens full screen without the Safari bar, and the deck works offline after the first load.

To pick up a rebuilt deck, open the app once while online; the new service worker refreshes the generated files as they are requested.

## Adding words

Append an object to `sources/curated-words.json`, then run the generator:

```json
{
  "id": 662,
  "category": "kitchen",
  "en": "Sieve",
  "hi": "छलनी",
  "mr": "चाळणी",
  "mr_roman": "chalni",
  "example": { "mr": "पीठ चाळणीने चाळ.", "roman": "Pith chalnine chaal.", "en": "Sift the flour with the sieve." }
}
```

Spellings follow common standard Marathi; regional forms vary.
