# Unspecified decisions

The brief did not tell you everything. Every time you or your agent chose
something the brief did not specify, add a line here.

Examples of the kind of thing that counts: what fields the record has, what
happens to an issue with no clear type, how confident is confident enough,
what the output looks like when the model returns nothing usable.

You will need this list in W2, when we reconstruct the requirements this
build implicitly assumed. The comparison across the cohort is the lesson, so
write down what you actually decided, not what you think is the right answer.

---

- The CLI reads one issue JSON object from a file or stdin; it does not fetch issues from GitHub.
- Repository context comes from an explicit `--repo`, the input's `repo`, or its GitHub issue URL, in that order.
- The record contains summary, issue type, optional repository-specific component, severity, reproduction-step presence, confidence, and rationale; it does not choose a destination queue.
- Issue types are bug, enhancement, documentation, question, meta, or unknown; severity uses low, medium, high, critical, or unknown, and absent evidence maps to unknown.
- Confidence is an overall model estimate on a numeric 0-to-1 scale and is not treated as a routing threshold.
- The model must return strict JSON; invalid or incomplete results fail visibly instead of being repaired or silently defaulted.
- Issue text is untrusted evidence only, and the model call has no tools or authority to follow instructions embedded in that text.
