import { Alg } from "cubing/alg";
import { cube3x3x3 } from "cubing/puzzles";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const outDir = path.resolve("assets/generated");
await mkdir(outDir, { recursive: true });

const states = [
  { id: "solved", label: "Solved", alg: "" },
  { id: "r_turn", label: "R", alg: "R" },
  { id: "r_u", label: "R U", alg: "R U" },
  { id: "commutator", label: "A B A^-1 B^-1", alg: "R U R' U'" },
];

const stickerColors = {
  U: "#F8F6EF",
  R: "#D64235",
  F: "#31B56A",
  D: "#F3D34A",
  L: "#F08A33",
  B: "#2C74C9",
};

function shiftedFaces(index) {
  const faces = ["U", "R", "F", "D", "L", "B"];
  const offset = index % faces.length;
  return faces.slice(offset).concat(faces.slice(0, offset));
}

function drawNet(label, faces) {
  const size = 22;
  const gap = 3;
  const facePositions = {
    U: [3, 0],
    L: [0, 3],
    F: [3, 3],
    R: [6, 3],
    B: [9, 3],
    D: [3, 6],
  };
  const cells = [];
  let faceIndex = 0;
  for (const [face, [fx, fy]] of Object.entries(facePositions)) {
    for (let row = 0; row < 3; row++) {
      for (let col = 0; col < 3; col++) {
        const x = 24 + (fx + col) * (size + gap);
        const y = 42 + (fy + row) * (size + gap);
        const colorKey = faces[(faceIndex + row + col) % faces.length];
        cells.push(
          `<rect x="${x}" y="${y}" width="${size}" height="${size}" rx="3" fill="${stickerColors[colorKey]}" stroke="#232323" stroke-width="1"/>`,
        );
      }
    }
    faceIndex += 1;
  }
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="360" height="290" viewBox="0 0 360 290">
  <rect width="360" height="290" fill="#F6F1E8"/>
  <text x="24" y="28" font-family="Menlo, monospace" font-size="18" fill="#232323">${label}</text>
  ${cells.join("\n  ")}
</svg>
`;
}

const kpuzzle = await cube3x3x3.kpuzzle();
const solvedSvg = await cube3x3x3.svg();
await writeFile(path.join(outDir, "cube3x3_solved_cubing.svg"), solvedSvg);

const metadata = [];
for (const [index, state] of states.entries()) {
  const alg = new Alg(state.alg);
  const pattern = kpuzzle.defaultPattern().applyAlg(alg);
  const filename = `cube_state_${state.id}.svg`;
  await writeFile(path.join(outDir, filename), drawNet(state.label, shiftedFaces(index)));
  metadata.push({
    ...state,
    image: `assets/generated/${filename}`,
    pattern: pattern.toJSON(),
  });
}

await writeFile(
  path.join(outDir, "cube_states.json"),
  JSON.stringify(
    {
      generatedBy: "scripts/generate_cube_assets.mjs",
      library: "cubing",
      puzzle: "3x3x3",
      states: metadata,
    },
    null,
    2,
  ) + "\n",
);

console.log(`Generated ${states.length + 2} cubing assets in ${outDir}`);
