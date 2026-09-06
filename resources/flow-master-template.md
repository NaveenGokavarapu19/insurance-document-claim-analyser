# Flow Master Template: Requirements to Code

## Purpose
Use this template to run a consistent, project-agnostic workflow from vague requirements to tested implementation.

## Project Context
- Project name: <PROJECT_NAME>
- Project type: <GREENFIELD_OR_EXISTING>
- Primary language: <LANGUAGE>
- Runtime/framework: <RUNTIME_OR_FRAMEWORK>
- Repository path: <REPO_PATH>
- Stakeholders: <STAKEHOLDERS>

## Inputs
- Raw requirement source: <DOC_OR_TRANSCRIPT_PATH>
- Constraints: <PERFORMANCE_SECURITY_COMPLIANCE>
- Non-functional requirements: <NFRS>
- Deadline or milestone: <DATE_OR_SPRINT>

## Required Artifacts
- requirements-decomposed.txt
- flow.md
- test-evidence.md
- handoff-summary.md

## Skill Routing Rules
1. If requirements are vague, run clarification first.
2. Run decomposition to produce module and function breakdown.
3. For existing codebases, run feature inventory to verify behavior parity.
4. Build implementation plan with dependency-aware order.
5. Run comments-first generation before coding each function.
6. Implement and validate one function at a time by default.

## Execution Modes
- Default mode: one-function-per-step.
- Fast mode: full-batch implementation only after explicit approval.

## Standard Step Sequence
1. Intake
- Capture goals, constraints, acceptance criteria, and exclusions.

2. Clarification
- Ask targeted questions for ambiguous areas.
- Freeze clarified requirement text.

3. Decomposition
- Break into modules.
- For each module, list candidate functions with role, inputs, outputs, constraints.

4. Planning
- Order functions by dependencies.
- Define test intent per function.
- Identify risk-heavy functions for early validation.

5. Comments-first pass
- For each function, generate requirement-aligned comment/spec text.
- Confirm comment matches acceptance criteria before coding.

6. Implementation loop
- Implement one function.
- Run tests for happy path and validation/error path.
- Confirm output contract and side effects.
- Record evidence.

7. Optional fast mode
- If approved, implement remaining functions in one batch.
- Run complete regression checks before merge.

8. Final validation
- Run diagnostics and runtime checks.
- Summarize what passed, what failed, and known limitations.

## Function-Level Quality Gate
A function is complete only when all are true:
1. Happy path passes.
2. Validation/error path passes.
3. Output structure matches contract.
4. Side effects are correct (state, storage, external calls).
5. No new diagnostics in edited files.

## Evidence Logging Template
For each function:
- Function: <FUNCTION_NAME>
- Requirement ID(s): <REQ_IDS>
- Inputs tested: <INPUTS>
- Expected result: <EXPECTED>
- Actual result: <ACTUAL>
- Status: <PASS_OR_FAIL>
- Notes: <NOTES>

## Failure Policy
1. Do not continue to next function on failure.
2. Fix function and rerun checks.
3. Document environment/tooling gaps when checks cannot run.
4. Only bypass with explicit approval and clear risk note.

## Completion Checklist
- Decomposition complete and traceable.
- Plan complete with dependencies.
- Comments-first completed for implemented functions.
- Function-level tests executed with evidence.
- Final diagnostics captured.
- Handoff summary produced.

## Handoff Summary Template
- Scope completed: <SCOPE>
- Files changed: <FILES>
- Tests run: <TESTS>
- Known risks: <RISKS>
- Next actions: <NEXT_STEPS>
