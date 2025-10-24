# Markdown‑Driven AI Design Workflow

This scaffold lets you drive an AI to create a complete design document using plain Markdown files with YAML front‑matter. 
You write or edit the files; the AI reads them (in this order) and produces artifacts, comments, and updates.

## Structure
- `manifest.yaml` — controls read order and gating rules
- `briefs/` — problem definition(s)
- `research/` — competitive analysis and insights
- `ux/` — IA, flows, wireframes (described textually)
- `ui/` — tokens and component specs
- `tech/` — architecture and API contracts
- `quality/` — accessibility and brand requirements
- `decisions/` — ADR-style log of design decisions
- `tokens/` — design tokens (JSON)
- `prompts/` — system/role prompts to keep the AI “in character”
- `workflows/` — how to run (with a single long prompt or a script)

## How to use
1. Edit `briefs/brief.sample.md` and `manifest.yaml` for your project.
2. Feed the AI the contents of `prompts/system.md`, then `workflows/prompt_runner.md` as the user message.
3. Paste in your Markdown files in the order the runner asks (or point your tool at the folder).
4. The AI returns a `DesignDoc.md` and suggested edits to individual files.

> Tip: Keep each file small and focused. Use front‑matter to define measurable acceptance criteria the AI can test.
