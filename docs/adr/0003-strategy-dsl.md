# ADR 0003 — Strategy DSL

* Status: accepted
* Date: 2026-04-08

## Context

Researchers need to author strategies quickly. We considered:

1. Plain Python files dropped into a sandbox.
2. Lua / TCL embedded interpreter.
3. A YAML/JSON DSL with a hand-written parser.
4. Pure visual graph (no text representation).

## Decision

We chose option **3** — YAML on disk plus a hand-written
tokenizer/parser/evaluator pipeline. We then layered the visual
builder on top: it serialises back to the same YAML, so the two
authoring modes are fully round-trip compatible.

## Consequences

* No `eval`, no sandbox escapes. The evaluator only knows about the
  registered indicators, operators, and rule actions.
* Strategies are reviewable in pull requests just like code.
* The visual builder can be changed independently of the engine.
* Cost: we have to extend the parser by hand whenever a new operator
  is added, but this is rare.
