# Lesson 01 Visual Design Brief

Updated: 2026-06-29

## Why The Current Markdown Feels Weak

The current notes are mathematically usable, but not audience-ready:

- too much plain text;
- theorem/proof/intuition are visually undifferentiated;
- formulas do not have a visual path;
- no diagrams for cubies, cycles, or invariants;
- no reading hierarchy for casual readers versus proof readers.

## References Checked

Design references:

- Interactive Linear Algebra, Dan Margalit and Joseph Rabinoff: structured online textbook with clear chapter hierarchy and navigable mathematical sections.
- Immersive Linear Algebra, J. Strom, K. Astrom, and T. Akenine-Moller: emphasizes interactive figures and visual intuition.
- Hefferon's Linear Algebra: first undergraduate textbook style; proves results but develops mathematical maturity through motivation, examples, and exercises.
- Mathigon: visual, interactive mathematical learning environment with strong color and manipulatives.

Local mathematical rigor reference:

- Janet Chen, `research/Group Theory and the Rubik's Cube.pdf`.

## Proposed Versions

### Version A: 彩色本科教材版

Use when:

- final PDF needs to feel like a serious undergraduate math handout;
- proof rigor matters;
- readers may print it or annotate it.

Features:

- theorem, definition, proof, and intuition boxes;
- restrained but clear color;
- formulas in large display cards;
- diagrams placed beside arguments;
- proof steps numbered.

### Version B: 可视化探索版

Use when:

- lesson is consumed on phone or web;
- viewer needs visual intuition before formal proof;
- diagrams should lead the explanation.

Features:

- bigger graphics;
- card-based sections;
- visual counting pipeline;
- invariant dashboard;
- proof compressed into "why this cannot change" panels.

### Version C: 可售卖课程讲义版

Use when:

- bundled with cubes/PDF;
- needs a polished brand feeling;
- should look more premium than free notes.

Features:

- strong cover section;
- lesson map;
- chapter quote / key result;
- numbered-cube product tie-in;
- clean proof appendix style.

## Recommendation

Use Version A as the mathematical source of truth, Version B as the web/video companion, and Version C as the paid PDF style.

Do not make the rigorous proof visually playful. Use color to organize logic, not to decorate logic.

## Decision After Review

德森 prefers the Version A style: clean, colorful, and structured.

The final course note should not maintain three separate versions. The three-version file is only for style comparison.

The paid-course source file is now:

- `docs/lesson_01_course_note.html`

Design decisions:

- Use one polished course note as the product artifact.
- Keep Definition / Theorem / Proof as the main colored modules.
- Do not use a separate "intuition box" type. Intuitive explanation can appear as ordinary prose or short notes.
- Use the local generated cover image from `pics/` as the cover until a better custom image is made.
- Mention numbered cubes where they genuinely help explain permutations and cycle notation.
