# Cubic Course Outline

Updated: 2026-06-06

## Format Decision

Use Markdown as the source format first.

Reason:

- It is easy to revise.
- It works well with Git.
- It can later be converted into PDF, slides, scripts, and web pages.
- Proofs, notation, diagrams, and source notes can evolve without re-exporting a designed PDF every time.

When the course stabilizes, generate:

- A student-facing PDF.
- A short-video script pack.
- A slide deck for each module.
- A numbered-cube instruction sheet.

## Core Promise

This course uses the Rubik's cube as a physical model for group theory.

The course has two layers:

- Public layer: intuitive, visual, and story-driven.
- Rigorous layer: definitions, propositions, proofs, and clearly stated conventions.

## Notation Conventions To Fix Early

Before writing final lessons, define:

- Whether a "state" fixes the cube in space or identifies states up to whole-cube rotation.
- Whether centers are treated as fixed reference pieces on the 3x3.
- Whether moves are quarter-turn face moves only, or also allow half-turns as one move.
- How corners and edges are numbered.
- How orientations are encoded.
- Whether the solved cube has a fixed color scheme.

These conventions affect counts and statements. The course must state them explicitly.

## Main Theorems

### Theorem 1: Number Of 2x2 States

Standard count with fixed cube orientation:

```text
8! * 3^7 = 88,179,840
```

If whole-cube rotations are considered the same position:

```text
8! * 3^7 / 24 = 3,674,160
```

Public explanation:

- There are 8 corner cubies.
- They can be arranged in `8!` orders.
- Each corner can be twisted in 3 ways.
- But the last corner twist is forced by the first 7, so the orientation factor is `3^7`, not `3^8`.
- If we do not care which way the whole cube is held, divide by the 24 rotational symmetries of the cube.

Rigorous proof plan:

1. Model a 2x2 state as `(sigma, tau)` where `sigma in S_8` is the corner permutation and `tau in (Z/3Z)^8` records corner orientations.
2. Prove the invariant `sum_i tau_i = 0 mod 3`.
3. Prove all pairs `(sigma, tau)` satisfying this invariant are reachable.
4. Therefore the fixed-orientation group has size `8! * 3^7`.
5. If quotienting by whole-cube rotations, prove the rotation group acts freely on physically labelled fixed-color states, giving division by 24.

Important nuance:

- The division by 24 is not a vague "duplicate" correction. It is a quotient by the cube rotation group. We must define the group action and justify why each orbit has size 24 under the chosen convention.

### Theorem 2: Number Of 3x3 States

Standard count:

```text
8! * 3^7 * 12! * 2^11 / 2
= 43,252,003,274,489,856,000
```

Public explanation:

- There are 8 corners and 12 edges.
- Corners can be permuted in `8!` ways and twisted in `3^7` legal ways.
- Edges can be permuted in `12!` ways and flipped in `2^11` legal ways.
- But edge and corner permutation parity must match, so only half of the naive combinations are legal.

Rigorous proof plan:

1. Model a 3x3 state by:
   - corner permutation `sigma_c in S_8`
   - corner orientation vector `tau_c in (Z/3Z)^8`
   - edge permutation `sigma_e in S_12`
   - edge orientation vector `tau_e in (Z/2Z)^12`
2. Prove the corner orientation invariant:
   `sum tau_c = 0 mod 3`.
3. Prove the edge orientation invariant:
   `sum tau_e = 0 mod 2`.
4. Prove the parity invariant:
   `sgn(sigma_c) = sgn(sigma_e)`.
5. Prove reachability: every assignment satisfying these three invariants is reachable by legal cube moves.
6. Count:
   - `8!` corner permutations
   - `3^7` corner orientations
   - `12!` edge permutations
   - `2^11` edge orientations
   - divide by 2 for the parity constraint

Important nuance:

- The famous number is not obtained by sticker-level counting. It is a cubie-level count with orientation constraints and parity constraints.
- Draft lesson files:
  - Audience notes: [lesson_01_3x3_state_count_notes.md](lesson_01_3x3_state_count_notes.md)
  - Polished paid-course note: [lesson_01_course_note.html](lesson_01_course_note.html)
  - Voiceover script: [../scripts/lesson_01_3x3_state_count_voiceover.md](../scripts/lesson_01_3x3_state_count_voiceover.md)

### Theorem 3: You Cannot Swap Only Two Pieces On A 3x3

Precise statement:

On a legal 3x3 cube, no legal move sequence can swap exactly two corner cubies while fixing all other cubies and orientations. Likewise, no legal move sequence can swap exactly two edge cubies while fixing all other cubies and orientations.

Public explanation:

- Swapping two pieces is an odd permutation.
- Legal 3x3 moves always preserve the rule that corner permutation parity and edge permutation parity match.
- If only two corners are swapped, corner parity changes but edge parity does not.
- That violates the invariant.

Rigorous proof plan:

1. Define the sign homomorphism `sgn: S_n -> {+1, -1}`.
2. Show a transposition has sign `-1`.
3. For each basic face turn on a 3x3, compute its induced corner permutation and edge permutation.
4. Show the two signs are equal for every generator.
5. Therefore `sgn(sigma_c) * sgn(sigma_e)` is invariant, or equivalently `sgn(sigma_c) = sgn(sigma_e)` is preserved from the solved state.
6. A state with only two corners swapped has `sgn(sigma_c) = -1` and `sgn(sigma_e) = +1`, impossible.
7. A state with only two edges swapped is similarly impossible.

2x2 comparison:

- On a 2x2, there are no edge cubies imposing a matching edge parity constraint.
- The 2x2 cube group contains all corner permutations subject only to the corner orientation constraint.
- Therefore a pure transposition of two corner cubies is possible on the 2x2 in the fixed-orientation model, provided orientations are legal.

This contrast is good content: the 3x3 has a hidden parity lock that the 2x2 does not have.

### Theorem 4: God's Number

Correct current statements:

- In the half-turn / face-turn metric, God's number for the standard 3x3 is 20.
- In the quarter-turn metric, God's number is 26.
- Do not state the general 3x3 value as 19.

Public explanation:

- Imagine every cube state as a city.
- A legal move is a road from one city to another.
- God's number is the maximum shortest-path distance from any city back to solved.
- It is not a human beginner method; it is an optimality statement about the whole graph.

Rigorous path:

1. Define the Cayley graph of the cube group with a chosen generating set.
2. Define distance from the identity.
3. Define the diameter of the Cayley graph.
4. Explain why God's number is the diameter under the chosen move metric.
5. Explain at a high level why the known proof is computational and uses symmetry reduction.
6. Cite the accepted computational results rather than pretending to give a short hand proof.

## Additional Attractive Theorems And Episodes

### Episode A: Why The Last Corner Twist Is Forced

Claim:

On a legal cube, you cannot twist exactly one corner in place.

Why it works:

- It is visual, surprising, and easy to demonstrate with a disassembled cube.
- It introduces modular arithmetic and orientation invariants.

Proof target:

- Prove `sum corner twists = 0 mod 3`.

### Episode B: Why The Last Edge Flip Is Forced

Claim:

On a legal 3x3, you cannot flip exactly one edge in place.

Why it works:

- It pairs naturally with the corner twist theorem.
- It is an excellent bridge from parity to invariants.

Proof target:

- Prove `sum edge flips = 0 mod 2`.

### Episode C: Why Commutators Are The Soul Of Solving

Claim:

Many solving algorithms are built from commutators: `ABA^{-1}B^{-1}`.

Why it works:

- It connects practical cube algorithms to group theory.
- It gives viewers a reason to care about noncommutativity.

Proof target:

- Show how a commutator can affect a small subset of pieces while restoring most of the cube.

### Episode D: Why Cube Moves Do Not Commute

Claim:

Doing `R` then `U` is different from doing `U` then `R`.

Why it works:

- It is the simplest possible entry to nonabelian groups.

Proof target:

- Exhibit one cubie whose final position differs under `RU` and `UR`.

### Episode E: The Cube Group Is Generated By Six Face Turns

Claim:

All legal cube positions are generated by a small set of moves.

Why it works:

- It introduces generators and relations.
- It makes "group" feel operational rather than abstract.

Proof target:

- State the cube group as a subgroup generated by `U, D, L, R, F, B` and their inverses.
- Defer full presentation by generators and relations unless needed.

### Episode F: Why Some Patterns Look Symmetric But Are Algebraically Different

Claim:

Visual symmetry and group-theoretic distance are different concepts.

Why it works:

- It creates strong visual content.
- It prevents viewers from assuming "pretty pattern = easy/near solved."

Proof target:

- Compare selected patterns by move distance and invariant data.

### Episode G: The 15 Puzzle And The Rubik's Cube Have The Same Kind Of Secret

Claim:

Both puzzles hide parity constraints.

Why it works:

- The 15 puzzle has a famous impossibility result.
- It gives a broader mathematical story: invariants explain impossible puzzles.

Proof target:

- Present both as permutation puzzles with parity-like invariants.

### Episode H: What Changes If You Take The Cube Apart And Reassemble It?

Claim:

Most physically reassembled-looking configurations are not legally reachable by turns.

Why it works:

- This is very concrete and product-friendly.
- It makes the state-count theorem feel real.

Proof target:

- Compare all mechanically assembleable cubie arrangements with legally reachable states.
- Use orientation and parity constraints to explain the ratio.

## Proposed Course Structure

### Part 1: The Cube As A Mathematical Object

1. What is a cube state?
2. Pieces versus stickers.
3. Moves as reversible operations.
4. Why "same state" depends on convention.

### Part 2: The 2x2 Cube

5. Corners as permutations.
6. Corner orientation and mod 3.
7. Counting 2x2 states.
8. Why the whole-cube rotation quotient divides by 24.
9. Why the 2x2 can do things the 3x3 cannot.

### Part 3: The 3x3 Cube

10. Corners, edges, centers.
11. Edge flips and mod 2.
12. Corner twists and mod 3.
13. Permutation parity.
14. Counting all legal 3x3 states.
15. Why swapping only two pieces is impossible.

### Part 4: Algorithms As Group Theory

16. Noncommutativity: why order matters.
17. Commutators.
18. Conjugation.
19. How algorithms isolate effects.
20. From beginner methods to group operations.

### Part 5: Distance And God's Number

21. The cube graph.
22. Move metrics.
23. God's algorithm versus human algorithms.
24. God's number: 20 or 26 depending on metric.
25. What a computational proof proves.

### Part 6: Broader Mathematical View

26. Symmetric groups and alternating groups.
27. Group actions.
28. Orbits and stabilizers.
29. Invariants across puzzles.
30. Why abstract algebra is a language for structure.

## Product Tie-In

The numbered cube should be introduced only after notation has value.

Recommended use:

- Number the 8 corners on the 2x2/3x3 corner model.
- Number the 12 edges on the 3x3 model.
- Use the numbers to write cycle notation in the course notes.
- Include a one-page "how to read your numbered cube" sheet.

The product should make the proof easier to follow, not merely decorate the cube.
