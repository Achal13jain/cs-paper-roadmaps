# Contributing

Thanks for your interest. Curation is the product here — every entry should
sharpen the line of thought, not pad the count. That standard applies to your
contributions and to mine.

## What to contribute

**Yes, please:**

- **Add a missing paper** that genuinely belongs in a roadmap
- **Fix a wrong fact** — a misattributed author, a wrong date, a broken arXiv link
- **Improve a TL;DR or takeaway** that buries the lede or misrepresents the paper
- **Replace a paywalled link** with a free primary source (arXiv preferred)
- **Propose a new roadmap** in [Discussions](https://github.com/Achal13jain/cs-paper-roadmaps/discussions) before opening a PR — adding a 12th field is a big decision, and the criteria below need to be met

**Probably no, sorry:**

- Bulk additions of 20+ papers from a personal reading list
- Style/aesthetic rewrites that don't fix anything substantive
- Paper inclusions because "they're famous" — fame ≠ pedagogical value
- Replacing the MVRP path of a roadmap based on personal preference

## Quality bar for a new paper

Before opening a PR, ask whether the paper meets all four:

1. **Foundational or frontier.** It either *founded* a line of thought (the first SGD paper, Attention Is All You Need) or represents a *current frontier* worth understanding (FlashAttention, AlphaFold 3). Solid mid-tier work usually doesn't make the cut — there are too many good papers and not enough attention.
2. **Free, primary source available.** arXiv, the author's personal page, the conference's open archive, OpenReview. Not a paywalled journal version, not a Wikipedia summary, not a blog explainer.
3. **Fits a real gap in the sequence.** If the field already covers transformer pretraining at Level 2, a sixth pretraining paper at Level 2 isn't adding much. Better candidates are gaps: things mentioned as prerequisites for later papers but not currently included.
4. **You've actually read it.** Sounds basic, but: don't add papers based on their abstract or other people's summaries.

## The data format

Each paper is a single call to the `p()` helper inside `index.html`'s data block:

```js
p(NUM, LEVEL, MVRP, TITLE, AUTHORS, INSTITUTION, DATE, URL,
  TLDR,
  WHY_READ_THIS,
  PREREQUISITES,
  KEY_TAKEAWAY)
```

Where:

- `NUM` — sequential number within the roadmap (continues from the highest existing)
- `LEVEL` — integer 0 through 9
- `MVRP` — boolean; `true` if this paper is on the Minimum Viable Reading Path
- `TITLE` — exact title as published. Use Unicode characters (`α`, `→`, `λ`) when the original does
- `AUTHORS` — `"FirstAuthor et al."` for >2 authors; `"A, B"` for 2; full name for 1
- `INSTITUTION` — primary affiliation at time of publication ("Google Brain", not "Google" or "Google DeepMind" if it was Google Brain then)
- `DATE` — `"Mon YYYY"` or `"YYYY"` if month is unclear
- `URL` — preferred order: arXiv abstract page > author's personal page > conference open archive
- `TLDR` — 1–2 sentences, present tense. *What* the paper says, not what makes it important
- `WHY_READ_THIS` — 1–2 sentences. *Where* this paper sits in the field's intellectual lineage
- `PREREQUISITES` — semicolon-separated. Should genuinely be needed to follow the paper
- `KEY_TAKEAWAY` — one sentence. The thing to remember if you forget the rest

### Example

```js
p(4, 1, true,
  'Attention Is All You Need',
  'Vaswani et al.',
  'Google Brain',
  'Jun 2017',
  'https://arxiv.org/abs/1706.03762',
  'Introduces the Transformer: an attention-only architecture with no recurrence or convolution.',
  'The architectural blueprint underlying every modern LLM. Read it for the original framing.',
  'Seq2seq with attention; matrix multiplication.',
  'Self-attention is fully parallelisable, captures long-range dependencies, and scales beautifully.'),
```

## Style rules for prose

- **TL;DRs:** present tense, active voice. Describe what the paper does, not what it influenced. ("Introduces X" not "Was the first to introduce X.")
- **Why-read:** focus on the paper's *function* in the field's lineage. ("The genesis of the current LLM era" beats "Very influential.")
- **Takeaways:** memorable, declarative, often slightly opinionated. Should be quotable in isolation.
- **No hype words.** "Revolutionary," "groundbreaking," "game-changing" — cut them. The paper's importance is conveyed by its placement in the sequence.
- **No marketing capitalization.** "transformer" not "Transformer", "attention" not "Attention" (titles excepted).

## Workflow

1. **Open an issue first** for: new papers, factual corrections, broken links, new roadmap proposals. Pick the matching template at [/issues/new/choose](https://github.com/Achal13jain/cs-paper-roadmaps/issues/new/choose).
2. **Wait for triage.** A maintainer will tag the issue `accepted`, `needs-discussion`, or `won't-merge`. Don't open a PR for new papers without `accepted` — it spares us both wasted time.
3. **Open a PR** referencing the issue (`Fixes #N`). Make the smallest possible diff that solves the problem.
4. **Update affected fields if needed.** If you're shifting `NUM` values, the MVRP click-jump references those numbers — re-check that nothing breaks.
5. **Verify locally.** Run `python3 -m http.server 8000` (or any static server), open the site, and confirm:
   - Your paper appears in the right roadmap and level
   - Its expansion shows TL;DR, why, prereqs, takeaway, and "View paper" link
   - The link opens to a free, working source
   - If MVRP, the paper appears in the MVRP visualization at the top
   - The `Total papers` count in the footer increased correctly

## What happens after a PR

- One maintainer review. We may ask for edits to TL;DR phrasing, prereq accuracy, or level placement.
- Squash-merge with a Conventional-Commits-style message: `add(llms): Mamba: Linear-Time Sequence Modeling`
- The site auto-deploys to GitHub Pages on merge.

## Code of conduct

Participation in this project is governed by the [Code of Conduct](./CODE_OF_CONDUCT.md). Be kind, assume good faith, disagree on substance.

## License of contributions

By contributing, you agree that:

- Your prose contributions (summaries, takeaways) are licensed under [CC BY 4.0](./LICENSE-CONTENT)
- Your code contributions are licensed under [MIT](./LICENSE-CODE)
- You have the right to license what you contribute (i.e., it's your original work, not lifted from a copyrighted source)

Paper titles, abstracts, and figures referenced here belong to their original authors and are not redistributed by this project.
