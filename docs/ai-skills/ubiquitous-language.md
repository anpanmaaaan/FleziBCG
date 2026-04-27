# Skill: ubiquitous-language

## Purpose
Extract a domain-driven-design style glossary from discussions, specs, and code.

## Use when
- A project needs consistent terminology.
- Different docs use different names for the same concept.
- You need a shared business/domain language.

## Process
1. Extract candidate terms.
2. Group synonyms and aliases.
3. Pick canonical terms.
4. Define each term in business language.
5. Identify forbidden/deprecated terms.
6. Add examples and counterexamples.

## Output format
```md
# Ubiquitous Language

| Canonical Term | Definition | Allowed Aliases | Deprecated Terms | Notes |
|---|---|---|---|---|

## Naming Rules
## Open Terminology Questions
```

## Rules
- Prefer business meaning over technical implementation.
- Mark aliases clearly.
- Do not invent canonical terms if the domain has not decided.
- Flag conflicts.
