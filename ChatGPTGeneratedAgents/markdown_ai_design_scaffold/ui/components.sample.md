---
tokens_ref: "../tokens/design-tokens.json"
components_must_include: ["Button", "TextField", "Stepper", "Alert"]
acceptance_criteria:
  - "Text contrast ratio ≥ 4.5:1"
  - "Touch targets ≥ 44x44dp"
---

## Components
### Button
Props: variant(primary|secondary), size(sm|md|lg), icon(optional)
States: default, hover, focus-visible, disabled, busy
