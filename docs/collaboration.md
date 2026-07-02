# Collaboration

Updated: 2026-06-06

## How 德森 Should Use Codex For Cubic

Use Codex as a project partner across five workflows.

Default setup:

- Use one main Codex thread for now.
- Ask Codex to switch roles inside the request instead of maintaining many separate agents.
- Add multiple agents later only for independent review, market research, or parallel drafting.
- Keep durable project knowledge in this repository.

## 1. Mathematical Rigor

Ask for:

- Proof checking.
- Full derivations.
- Notation cleanup.
- Claim verification before publishing.
- Separating intuitive explanation from formal proof.

Useful prompt shape:

> 帮我把这个魔方结论写成严谨证明。先指出定义和约定，再证明，再给大众版解释。

## 2. Course And Script Writing

Ask for:

- Video outlines.
- Short-video hooks.
- Long-form lecture scripts.
- Slide structure.
- PDF notes.
- Diagrams and animation specs.

Useful prompt shape:

> 基于 `docs/content_syllabus.md`，写一期 5 分钟视频脚本，主题是三阶魔方状态数。要求大众能懂，但附带严谨推导。

## 3. Product And Business

Ask for:

- Unit economics.
- Pricing tests.
- Product bundle design.
- Supplier comparison.
- Preorder plan.
- Risk review.

Useful prompt shape:

> 按 38 元售价，帮我算 2x2+3x3 套装的单件利润模型，列出还必须确认的成本。

## 4. Production Management

Ask for:

- Weekly content plan.
- Publishing calendar.
- Script backlog.
- Experiment tracking.
- Comment and feedback synthesis.

Useful prompt shape:

> 根据最近 10 条视频表现，帮我判断下一周拍什么，并更新路线图。

## 5. Repository Maintenance

Codex should keep project knowledge in files, not only in chat.

Preferred structure:

- `memory/` for durable project context.
- `docs/` for planning, course structure, scripts, and business documents.
- `research/` for source notes and claim verification.
- `scripts/` for actual video scripts.
- `slides/` for lesson decks.
- `assets/` for diagrams, images, and cube mockups.

## Working Rule

For this project, Codex should be direct and critical:

- Push toward publishing and selling small tests.
- Challenge weak business assumptions.
- Preserve mathematical rigor.
- Avoid turning every idea into an overbuilt system.
- Keep writing durable files whenever a decision matters.
