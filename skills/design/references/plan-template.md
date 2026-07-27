# [Feature Name] Implementation Plan

> **For agentic workers:** Implement this plan task by task and update each checkbox only after its outcome is verified.

**Goal:** [One sentence describing what this builds.]

**Architecture:** [Two or three sentences describing the implementation shape and boundaries.]

**Tech Stack:** [Languages, native tools, and existing dependencies.]

## Global Constraints

- [Copy each project-wide constraint from the spec with its exact value.]

---

### Task N: [Outcome-oriented task name]

**Files:**

- Create: `exact/path/to/new-file`
- Modify: `exact/path/to/existing-file`
- Test: `tests/exact/path/to/test-file`

**Interfaces:**

- Consumes: [Existing inputs and exact signatures.]
- Produces: [New or changed names, parameters, return values, formats, or events.]

**Failure handling:**

- [Define the expected failure, recovery, cleanup, or propagation behavior.]

**Outcome:**

[State the independently observable result of completing this task.]

- [ ] **Step 1: Add the failing check**

[Show the exact test or validation content. For metadata-only work, state the direct validator and why a failing unit test is not useful.]

- [ ] **Step 2: Run the check and confirm the expected failure**

Run: `exact command`

Expected: FAIL because [missing behavior], not because of syntax or environment errors.

- [ ] **Step 3: Implement the minimum change**

[Show exact edits, signatures, algorithms, and command details needed by an engineer without hidden context.]

- [ ] **Step 4: Verify the task outcome**

Run: `exact command`

Expected: PASS with [specific output or count].

- [ ] **Step 5: Record the outcome**

[Mark the task complete only after the files, interfaces, failure behavior, and check match this plan.]

## Complete Verification

Run: `exact full-suite command`

Expected: PASS with no unexpected warnings or skipped required coverage.
