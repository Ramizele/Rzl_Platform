# AGENTS - Rzl_Platform

## Source of Highest Hierarchy

- Upstream template authority: `https://github.com/Gentleman-Programming/gentle-ai`
- Local control plane: `platform/gentle_ai/`

## Operating Rules

1. Use `gentle-ai` contracts for agents/components/presets as default source of truth.
2. Keep this repository in template mode (no imported operational data from external repos).
3. Apply local adaptations only through:
   - `platform/gentle_ai/MANIFEST_gentle_ai_template_v0.1.yaml`
   - `platform/gentle_ai/runbooks/*`
4. Keep bucket architecture aligned with:
   - `platform/architecture/template_architecture_map.md`
