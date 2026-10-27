# Vocabulary data sources

The deployed deck is generated once by `scripts/build_deck.py`. Runtime users do not contact external datasets or translation services.

## Curated cards

The original cards in `sources/curated-words.json` were assembled for Marathi Shabd Cards and include Hindi, English, readable romanisation, and example sentences.

## IndoWordNet imports

Additional English–Marathi and Marathi–Hindi mappings come from the [CFILT IndoWordNet Wordlists](https://github.com/cfiltnlp/IWN-WordLists). Imported cards carry `"source":"IndoWordNet"` and are generated from the repository's bilingual mappings.

The IndoWordNet wordlists are licensed under [Creative Commons Attribution-NonCommercial-ShareAlike 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). The generated imported vocabulary in `data/` is distributed under those terms. Attribution: CFILT, IIT Bombay; Pushpak Bhattacharyya, *IndoWordNet*, LREC 2010.

Imported English headwords are ranked with the [wordfreq English 25,000-word export](https://github.com/aparrish/wordfreq-en-25000), distributed under Creative Commons Attribution-ShareAlike 4.0. It is derived from Robyn Speer's `wordfreq` project and is used only to select learner-relevant entries during generation.

The application code and the independently curated cards are not relicensed by this notice.
