# Prompt Runner (copy/paste to the AI after pasting `prompts/system.md`)

I will paste a series of Markdown files. For each, you will:
1) Parse front-matter and content.
2) Update `DesignDoc.md`.
3) Emit `Issues:` with any unmet acceptance criteria.
4) When all gates in `manifest.yaml` pass, output the final `DesignDoc.md` and a proposed `Decisions-ADR.md`.

Say: READY FOR FILES. Then I will paste them in this order:
- manifest.yaml
- briefs/brief.sample.md
- research/research.sample.md
- ux/flows.sample.md
- ui/components.sample.md
- tech/architecture.sample.md
- quality/requirements.sample.md
- tokens/design-tokens.json
