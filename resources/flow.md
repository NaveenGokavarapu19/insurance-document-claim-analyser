# Flow: Reusable Requirements-to-Code Workflow

## Objective
Build a repeatable process for new projects that starts from vague requirements, produces structured decomposition, writes comments first, implements one function at a time by default, and validates each function for confidence.

## Supported Project Types
1. Greenfield projects.
2. Existing codebases.
3. Python-first projects, extensible to other stacks.

## Default Delivery Artifacts
1. requirements-decomposed.txt
2. flow.md
3. notebooklm-video-script.md

## Skill Routing Strategy
1. Use clarifying-scenarios only when requirements are vague or missing constraints.
2. Use decompose-requirements as the primary skill to produce architecture modules and function-level requirements.
3. Use feature-inventory for existing codebases to validate coverage and identify missing functionality.
4. Use creating-implementation-plan to produce implementation order, dependencies, and task breakdown.
5. Use comment-to-code to generate comments or spec text function by function before coding.
6. Use implementing-code for implementation tasks.
7. Use python-fact-grounded-coding mindset for diagnostics and runtime verification after each function.

## Execution Modes
1. Default mode: strict one-function-per-step.
2. Optional fast mode: full implementation batch only after explicit user approval.

## Standard Execution Steps
1. Intake requirement.
2. If requirement is vague, run clarification questions first.
3. Build decomposition with modules, function names, role, input, output, and constraints.
4. Build plan with ordered function tasks and dependency notes.
5. Run comments-first pass for each function requirement.
6. Implement only one function.
7. Run validation tests for that function.
8. Share pass or fail result.
9. Move to next function only after pass.
10. If user approves full implementation, switch to batch mode for remaining tasks.
11. Finalize with diagnostics, behavior checks, and summary of known gaps.

## One-Function Confidence Gate
Each function must pass all checks before moving on:
1. Happy path test passes.
2. Validation or error path test passes.
3. Response structure is correct.
4. Side effects are correct for state-changing functions.

## Testing Rule
Each function must include either:
1. User-input-driven test path, or
2. Validation-focused test path with expected result.

## Greenfield vs Existing Branch
1. Greenfield: decompose-requirements -> creating-implementation-plan -> comment-to-code -> implementing-code.
2. Existing: clarifying-scenarios if needed -> feature-inventory -> decompose-requirements normalization -> creating-implementation-plan -> comment-to-code -> implementing-code.

## Quality Gates
1. No unresolved diagnostics in edited files.
2. No regression in previously passing paths.
3. Function-level tests executed and reported.
4. Final result includes known limitations and next actions.

## Failure Policy
1. If a function fails tests, fix that function before moving ahead.
2. Do not skip failed validation unless user explicitly requests a temporary bypass.
3. If environment lacks lint tools, document the limitation and provide alternative checks.

## Completion Checklist
1. Requirements decomposition exists and is structured.
2. Function comments align with requirements.
3. Each function is implemented and tested with evidence.
4. Default one-function mode is respected unless full-mode approval is provided.
5. Final summary includes what passed, what remains, and tooling gaps.
