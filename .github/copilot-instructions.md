# Copilot instructions

- Keep ordinary URL scoring offline: never fetch, visit, or resolve a submitted URL during analysis. Domain enrichment is a separate opt-in path and must keep its public-address checks.
- Use synthetic links for tests and demos. Keep synthetic benchmark results separate from public-data measurements and state sample limitations accurately.
- Preserve the explanation for each verdict: URL signals, email signals, model feature contributions, and any high-signal score floor should remain distinguishable.
- Do not present the classifier as reliable protection. Its training data is synthetic, and the documented recall limits must remain visible in user-facing claims.
- Keep batch scoring behavior aligned with single-link scoring and preserve existing input limits and escaping in the UI.
- Use the existing Flask package and Python requirements. Run relevant pytest checks for code changes; CI also runs evaluation and coverage reporting.
