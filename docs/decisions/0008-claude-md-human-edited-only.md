# ADR-0008: CLAUDE.md is human-edited only

**Status:** Accepted
**Date:** 2026-05-14

## Context

`CLAUDE.md` is the working agreement between the human and Claude Code. It controls how Claude Code behaves, what it will and won't do, how it teaches, and what's in scope. If Claude Code can edit this file itself, it can silently change its own instructions — which undermines the human's control over the collaboration.

## Decision

**Claude Code may not edit `CLAUDE.md` directly.** If a change to `CLAUDE.md` is warranted (e.g., updating the teaching protocol, adding a guardrail, recording a new decision), Claude Code must propose the diff in chat and wait for the human to apply it manually.

## Alternatives considered

- **Claude Code edits CLAUDE.md freely** — efficient but removes human oversight. Claude could accidentally or deliberately change its own constraints.
- **CLAUDE.md is read-only in the filesystem** — enforces the rule technically but breaks the workflow when legitimate updates are needed.

## Consequences

- Human always knows what instructions Claude Code is operating under
- Proposed CLAUDE.md changes are visible in chat before they take effect — creates a natural review step
- Slight friction when updating instructions — acceptable trade-off for maintaining control
- Claude Code is expected to flag when it believes CLAUDE.md should be updated, rather than silently proceeding under outdated instructions
