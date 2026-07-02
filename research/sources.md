# Source Notes

Updated: 2026-06-06

## God's Number

Working publication standard:

- For the standard 3x3 Rubik's cube, God's number is 20 in the half-turn / face-turn metric.
- In the quarter-turn metric, God's number is 26.
- Do not publish "every position can be solved in no more than 19 moves" as a general 3x3 statement.

Initial sources to cite/check:

- `https://www.cube20.org/`: states that every Rubik's Cube position can be solved in 20 moves or less in the half-turn metric, and that Rokicki, Kociemba, Davidson, and Dethridge proved the exact value 20 in July 2010.
- `https://www.cube20.org/qtm/`: states that God's number is 26 in the quarter-turn metric, proved by Tomas Rokicki and Morley Davidson in August 2014.
- Rokicki et al. and related papers should be used for rigorous references when writing the proof/research notes.

Need later:

- Build a proper bibliography with URLs, dates accessed, and publication references.
- Separate computational proof explanation from mathematical group-theory preliminaries.

## Cube State Counts

Working publication standard:

- 2x2 fixed-orientation state count: `8! * 3^7 = 88,179,840`.
- 2x2 count up to whole-cube rotations: `8! * 3^7 / 24 = 3,674,160`.
- 3x3 state count: `8! * 3^7 * 12! * 2^11 / 2 = 43,252,003,274,489,856,000`.

Initial sources to cite/check:

- Local source: `research/Group Theory and the Rubik's Cube.pdf`, Janet Chen. This is the main rigor model for Cubic's 3x3 state-count proof and legal-configuration theorem.
- `https://www.homepages.ucl.ac.uk/~ucahjmt/groups/other/rubik/index.html`: UCL Rubik's Cube Group Theory notes; states the Rubik's cube group order as `43,252,003,274,489,856,000`.
- `https://proofwiki.org/wiki/Total_Number_of_Reachable_Positions_on_Rubik%27s_Cube`: ProofWiki page for the 3x3 reachable-position count. Use only after checking the proof and notation.

Need later:

- Find or produce a rigorous self-contained 2x2 proof.
- Decide whether the student-facing course uses fixed cube orientation or quotient by whole-cube rotations as the default convention.
