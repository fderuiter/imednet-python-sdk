# Project Agent Skills

Installed from [mattpocock/skills](https://github.com/mattpocock/skills) for use with AI coding agents (Google Antigravity, Claude Code, Codex, etc.).

All skills are registered in `.agents/skills.json` and discovered under `.agents/skills/<skill-name>/`.

---

## Skill Router

When unsure which skill to reach for, use:
- **`/ask-matt`**: Explains the full workflow topology and directs you to the right skill or on-ramp.

---

## Engineering Skills

### User-Invoked
- **`/ask-matt`**: Ask which skill or flow fits your situation. A router over the skills in this repository.
- **`/grill-with-docs`**: Grilling session that builds your domain model in `CONTEXT.md` and ADRs.
- **`/implement`**: Build work described by spec/tickets test-first and review before committing.
- **`/improve-codebase-architecture`**: Scan codebase for deepening opportunities.
- **`/setup-matt-pocock-skills`**: Configure this repo for engineering skills (issue tracker, triage labels, domain docs).
- **`/to-spec`**: Turn conversation into a spec and publish to the issue tracker.
- **`/to-tickets`**: Break specs/plans into tracer-bullet tickets with blocking edges.
- **`/triage`**: Move issues through a state machine of triage roles.
- **`/wayfinder`**: Chart and resolve large, foggy efforts as decision tickets.

### Model-Invoked / Automated
- **`code-review`**: Two-axis review (Standards + Spec) of diffs before committing.
- **`codebase-design`**: Deep module and clean seam design discipline.
- **`diagnosing-bugs`**: Disciplined root-cause isolation and regression testing.
- **`domain-modeling`**: Build and maintain project domain model and ADRs.
- **`prototype`**: Build throwaway prototypes to answer design questions.
- **`research`**: Investigate questions against primary sources via background agent.
- **`resolving-merge-conflicts`**: Intent-traced git conflict resolution.
- **`tdd`**: Test-driven development with red-green-refactor loop.
- **`wizard`**: Interactive wizard script for human-only operational steps.

---

## Productivity Skills

### User-Invoked
- **`/grill-me`**: Relentless interview to resolve design decisions (stateless).
- **`/handoff`**: Compact conversation into a handoff document for another session/agent.
- **`/teach`**: Stateful multi-session learning workspace.
- **`/to-questionnaire`**: Turn decisions into questionnaires for external stakeholders.
- **`/wait-what`**: Clarify and re-pitch misunderstood agent responses.

### Model-Invoked / Foundational
- **`grilling`**: Reusable interview primitive across decision trees.
- **`writing-for-agents`**: Discipline for authoring agent-readable documents and skills.

---

## In-Progress Skills

- **`claude-handoff`**: Context compaction for Claude Code.
- **`implement-spec`**: Multi-agent spec execution across ticket task graphs.
- **`loop-me`**: Feedback loop driver.
- **`retro`**: Analyze session transcripts to extract systemic improvements.
- **`setup-ts-deep-modules`**: Deep module boundary enforcement for TypeScript.
- **`writing-beats`**: Assemble raw material into a narrative journey of beats.
- **`writing-fragments`**: Mine raw writing fragments into a single quarry file.
- **`writing-shape`**: Shape raw material into an article paragraph by paragraph.

---

## Misc Skills

- **`git-guardrails-claude-code`**: Safety guardrails blocking destructive git commands.
- **`migrate-to-shoehorn`**: Migration tool to shoehorn architecture.
- **`scaffold-exercises`**: Scaffolding coding exercises.
- **`setup-pre-commit`**: Configure pre-commit hooks.

