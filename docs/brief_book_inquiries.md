# Brief: thesis and inquiry per block

**Status: draft.** The input format of the retriever is still to be agreed with the editorial AI through CRITIQUE.
This document describes what is proposed and marks what is still open.

## What the retriever receives per block

Each block has three parts, and only one of them goes to search:

- **Identifier** of the block, within its thesis.
- **Thesis**: one bounded, declarative sentence that gives the block's subject to whoever writes and checks the prose. The thesis is not sent to search.
- **Inquiry**: the only part sent to search. It is the same for both books by default (see open items).

## What to write

**Thesis.** One declarative sentence stating what the two books could be shown to claim about the subject, in agreement or in conflict.

- It needs a real point of contact, not just a shared subject. "Both books talk about society" is too thin. "Both books can be read as describing a form of self-presentation that substitutes for direct experience" is a point on which two authors can plausibly agree or disagree.
- Before settling a thesis, check whether its inquiries weave into one line. If the theme pulls toward two threads that would not meet even in principle, they are two theses, not one overly broad thesis.

**Inquiry.** A specific question that can be answered from passages, not a summary of a book's scope.

- Single, not compound. A question joining two asks with "and" is two questions; split them into separate blocks.
- Tied to the thesis, but covering one slice of it.
- Prefer inquiries where both authors can plausibly assert something comparable, not something merely adjacent.

## Open (to discuss in CRITIQUE, not decided)

- **Vocabulary per book.** Whether the inquiry is written once for both books, or each book gets its own wording. The answer depends on the adaptive retrieval, which has not been designed yet.
- **Compound inquiries.** A thesis with two distant parts may not fit a single question. If the rule above stays, that case needs explicit handling and must not be resolved silently.
- **Period terms.** A modern term with no equivalent in the book may return nothing, even when the book treats the same pattern in another form. Whether the brief should ask for a translation of the term into the structural role it plays, or whether that is the retriever's job, has not been decided.
- **Alternative wordings.** This document provides no alternative wordings written by the person or by the brief. If the retriever generates variants, that is the retriever's decision, not this document's.

## Output format

Plain text, no bold, headers, lists or code fences. One line per theme, thesis and block.

```
Theme 1: <title, as given>

Thesis 1.1: <bounded declarative sentence>
  Block 1.1a: <single, non-compound inquiry>
  Block 1.1b: <single, non-compound inquiry>

Thesis 1.2: <bounded declarative sentence>
  Block 1.2a: <single, non-compound inquiry>

Theme 2: <title, as given>

Thesis 2.1: <...>
  Block 2.1a: <...>
```

Label rules:
- `Theme N:` follows the order in which the themes appear. The number of themes is not fixed.
- `Thesis N.M:` where N is the theme's number and M counts the theses within it, starting at 1. Each thesis has a unique label in the document.
- `Block N.Ma:` where N.M is the thesis label and the letter counts the blocks within it. Each block label is unique in the document.
- A theme needs only one thesis unless it fails the weaving test above; in that case, split it into theses with their own labels.
- Each block has exactly one inquiry. There are no alternatives or variants.

Every block must trace back to its thesis, and every thesis to its theme.
