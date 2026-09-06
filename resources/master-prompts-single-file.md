# Master Prompt Library: Requirements to Code Workflow

Use this single file as your reusable prompt reference for future projects.

## 1) Clarification Prompt
Prompt:
You are helping me implement a project from requirements.
Review the requirement text below and ask only the minimum high-value clarification questions needed to remove ambiguity.
Prioritize missing acceptance criteria, input/output contracts, validation rules, error behavior, and non-functional constraints.
Return:
1. Clarification questions
2. Assumptions if unanswered
3. A cleaned requirement draft

Requirement text:
<PASTE_REQUIREMENTS>

## 2) Decomposition Prompt
Prompt:
Decompose the cleaned requirements into modules and atomic functions.
For each function, provide:
- Suggested Function Name
- Role
- Input contract
- Output contract
- Validation rules
- Error cases
- Dependency notes
- Requirement ID mapping
Return the result in a format suitable for requirements-decomposed.txt.

Requirements:
<PASTE_CLEANED_REQUIREMENTS>

## 3) Implementation Plan Prompt
Prompt:
Create a dependency-aware implementation plan from this decomposition.
Return:
1. Ordered function sequence
2. Why each step is in that order
3. Test intent for each function
4. Risk hotspots and early validation points
5. Default one-function-per-step mode
6. Optional full-batch mode (only with explicit approval)

Decomposition:
<PASTE_DECOMPOSITION>

## 4) Comments-First Prompt (Per Function)
Prompt:
Use comments-first discipline.
Write the function comment/spec text first, then wait for approval before implementation.
The comment must include intent, input/output contract, validation rules, and failure behavior.

Function name:
<FUNCTION_NAME>

Requirement:
<FUNCTION_REQUIREMENT>

## 5) Code Implementation Prompt (Per Function)
Prompt:
Implement exactly one function based on the approved comment/spec.
Do not modify unrelated functions.
After coding, run function-level checks and report results.

Function name:
<FUNCTION_NAME>

Approved comment/spec:
<PASTE_APPROVED_COMMENT>

## 6) Function Test Prompt
Prompt:
Create and run function-level tests for the target function.
Must include:
1. Happy path
2. Validation/error path
3. Output contract check
4. Side-effect check (if state changes)
Return suggested inputs, expected outputs, actual outputs, and pass/fail.

Function name:
<FUNCTION_NAME>

## 7) Batch Mode Approval Prompt
Prompt:
I approve full-batch implementation mode for the remaining functions.
Implement all remaining items from the plan, then run regression checks and provide a concise change report with risks.

Remaining scope:
<PASTE_SCOPE>

## 8) Final Validation Prompt
Prompt:
Run final validation on the implemented scope.
Return:
1. Diagnostics summary
2. Test summary
3. Regressions found/not found
4. Known limitations
5. Next actions

Changed files:
<PASTE_FILE_LIST>

## 9) Handoff Prompt
Prompt:
Prepare a handoff summary for another developer.
Include:
- Scope completed
- Files changed
- Tests executed
- Open risks
- Recommended next steps

Project context:
<PASTE_CONTEXT>

## 10) Master Flow Runner Prompt
Prompt:
Execute this workflow end-to-end using strict one-function-per-step mode unless I explicitly approve full-batch mode:
1. Clarify requirements
2. Decompose to modules/functions
3. Build dependency-aware plan
4. Comments-first for each function
5. Implement one function
6. Test one function
7. Report and continue
8. Final validation and handoff
At each step, provide artifacts and concise evidence.

Requirement source:
<PASTE_REQUIREMENTS>

## Quick Use Guide
1. Start with Clarification Prompt.
2. Run Decomposition Prompt.
3. Run Implementation Plan Prompt.
4. For each function, run Comments-First -> Code Implementation -> Function Test prompts.
5. Optionally switch to Batch Mode Approval Prompt.
6. Finish with Final Validation and Handoff prompts.
