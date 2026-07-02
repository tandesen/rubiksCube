# Codex Workflow For Cubic

Updated: 2026-06-06

## Short Answer

Do not start by building many agents.

For the current stage of Cubic, one Codex thread plus durable project files is enough. The bottleneck is not role coverage; the bottleneck is turning ideas into a coherent course, proofs, scripts, product tests, and published content.

## Why One Codex Thread Is Enough For Now

Codex can already switch roles inside one workflow:

- Product manager: define roadmap, scope, milestones, product tests.
- Mathematical editor: formalize definitions, prove claims, find gaps.
- Scriptwriter: write hooks, voiceover drafts, outlines, and short-video scripts.
- Research assistant: check sources and flag claims that need citations.
- Business critic: test pricing, margins, positioning, and risks.
- Project manager: maintain files, backlog, and weekly execution plans.

The practical advantage of one thread:

- Context stays together.
- Course notation remains consistent.
- Decisions are written into the same repository.
- Less time is spent managing assistants instead of building the project.

## When Multiple Agents Become Useful

Multiple agents are useful only when there are independent workstreams that can be checked against each other.

Good later use cases:

- One agent drafts a proof, another reviews it for mathematical gaps.
- One agent writes a popular video script, another rewrites it for retention and platform style.
- One agent researches competitors, another extracts product implications.
- One agent checks supplier economics, another pressure-tests the pricing model.

Bad early use cases:

- Creating an "AI company" before the course has a stable outline.
- Splitting roles so much that every decision requires coordination.
- Giving each role a separate memory before the project has shared terminology.

## Recommended Operating Model

Use one main Codex thread as the project lead.

Inside a request, name the mode explicitly:

- "以数学审稿人的身份..."
- "以产品经理的身份..."
- "以短视频编导的身份..."
- "以商业质疑者的身份..."

Ask Codex to write durable outputs into files:

- `docs/` for strategy, syllabus, outlines, and lesson plans.
- `research/` for sources and mathematical verification.
- `scripts/` for video scripts.
- `slides/` for slide decks.
- `memory/` for project decisions and durable context.

## Prompt Pattern

Use this shape:

```text
主题：三阶魔方状态数
角色：数学审稿人 + 大众科普编导
产出：
1. 大众版解释
2. 严谨证明
3. 视频脚本
4. 需要画的图
5. 需要查证的来源
写入：docs/lesson_state_count.md
```

## Working Rule

Build files first, agent architecture later.

The project needs a course spine, proof library, script library, and product validation loop before it needs a multi-agent organization.

