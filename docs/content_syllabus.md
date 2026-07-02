# Content Syllabus

Updated: 2026-06-06

This file is the compact syllabus. The fuller proof-oriented outline lives in [course_outline.md](course_outline.md).

## Module A: Concrete Cube Intuition

Purpose: give non-mathematical viewers enough cube language to follow the story.

Topics:

- What are faces, stickers, pieces, corners, edges, and centers?
- Why centers matter on a 3x3 but not on a 2x2 in the same way.
- What a move does physically.
- What counts as the same or different cube state.
- Why solving algorithms are sequences of reversible operations.

## Module B: 2x2 as the First Group Theory Model

Purpose: use the 2x2 cube as a clean entry point.

Topics:

- Corners as objects being permuted.
- Orientation of corners.
- Legal moves as permutations plus orientation changes.
- Why not every arbitrary arrangement is physically reachable.
- The role of invariants.

Proof targets:

- Count the 2x2 state space under a clearly chosen convention.
- Explain corner orientation constraints.
- Explain how whole-cube rotations affect counting if included or quotiented out.

## Module C: 3x3 State Counting

Purpose: derive the famous number carefully.

Topics:

- Centers, edges, corners.
- Corner permutations and orientations.
- Edge permutations and orientations.
- Parity constraint linking edge and corner permutations.
- Final state-count formula.

Proof targets:

- Derive the standard 3x3 reachable-state count:
  `43,252,003,274,489,856,000`
- Explain why this is smaller than the naive sticker arrangement count.
- State all conventions explicitly.

## Module D: Why You Cannot Swap Only Two Pieces

Purpose: connect a viral claim to a rigorous invariant.

Topics:

- Permutation parity.
- Legal moves and parity constraints.
- Why a single transposition is odd.
- Why cube moves cannot produce "only two pieces swapped" while everything else remains fixed, under the standard legal 3x3 mechanism.

Proof targets:

- Formalize the statement.
- Distinguish swapping two stickers, two pieces, two corners, and two edges.
- Show how parity rules out the illegal case.

## Module E: God's Number

Purpose: explain what the result means without overstating it.

Topics:

- What "distance" means in a Cayley graph.
- Quarter-turn metric versus half-turn metric.
- God's algorithm versus human solving methods.
- Why exhaustive computation and symmetry reduction matter.

Proof/research standard:

- Use the current accepted values: 20 in half-turn / face-turn metric, and 26 in quarter-turn metric.
- Never state "19 moves" as the general 3x3 God's number.
- Always specify the metric before stating a move bound.


## Module F: From Cube to Abstract Algebra

Purpose: use the cube as a bridge to real algebra.

Topics:

- Groups, generators, relations.
- Symmetric and alternating groups.
- Group actions.
- Stabilizers and orbits.
- Cayley graphs.
- Invariants and impossibility proofs.
