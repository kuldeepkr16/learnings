# Marathi Shabd Cards

A single-page flashcard site for learning everyday Marathi words from Hindi and English.

- `index.html` – the page. Loads `words.json`, picks 5 random words, shows them as flip cards. Front: English + Hindi. Back: Marathi in Devanagari, a readable romanised form, and one example sentence.
- `manifest.webmanifest`, `sw.js`, `icons/` – make the page installable as a home-screen app on iPhone and Android, with offline support.
- `words.json` – the deck (661 words across house, kitchen, food, vegetables, fruits, family, body, clothing, numbers, colours, time, nature, animals, places, verbs, adjectives, phrases).

Refresh the page or press **Next 5 words** for a new random set. Repeats are intentional, for revision.

## Hosting on GitHub Pages

1. Push `main` to GitHub.
2. On github.com open the repo, then **Settings → Pages**.
3. Under **Build and deployment** set Source to **Deploy from a branch**, Branch to **main**, folder **/ (root)**, and Save.
4. Wait a minute, then open `https://kuldeepkr16.github.io/learnings/`.

No build step: the page fetches `words.json` relative to itself.

## Add to iPhone home screen

1. Open the Pages URL in **Safari** (not Chrome; only Safari can install web apps on iOS).
2. Tap the **Share** button, then **Add to Home Screen**, then **Add**.
3. Launch it from the home screen. It opens full screen without the Safari bar, and the deck works offline after the first load.

To pick up a new deck after editing `words.json`, open the app once while online; it refreshes the cached copy automatically.

## Adding words

Append an object to `words.json`:

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
