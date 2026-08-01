# [Feature Name] Implementation Plan

> **For agents:** Do each task in sequence. Update a checkbox only after you verify its result.

**Status:** Active

**Goal:** [Describe the result in one sentence.]

**Architecture:** [Describe the implementation and its limits in two or three sentences.]

**Tech Stack:** [Give the languages, native tools, and current dependencies.]

## Global Constraints

- [Copy each project constraint from the Design Spec with its exact value.]

---

### Task N: [Task result]

**Files:**

- Create: `exact/path/to/new-file`
- Modify: `exact/path/to/existing-file`
- Test: `tests/exact/path/to/test-file`

**Interfaces:**

- Consumes: [Give current inputs and exact signatures.]
- Produces: [Give new or changed names, parameters, results, formats, or events.]

**Failure handling:**

- [Define the failure, recovery, cleanup, or propagation behavior.]

**Outcome:**

[Give the independent and observable task result.]

- [ ] **Step 1: Add the failing check**

[Give the exact test or validation content.]

[For metadata work, give the direct check and why a failing unit test is not useful.]

- [ ] **Step 2: Run the check and confirm the expected failure**

Run: `exact command`

Expected: FAIL because [missing behavior], not because of syntax or environment errors.

- [ ] **Step 3: Implement the minimum change**

[Give exact edits, signatures, algorithms, and commands.]

- [ ] **Step 4: Verify the task outcome**

Run: `exact command`

Expected: PASS with [specific output or count].

- [ ] **Step 5: Record the outcome**

[Complete the task only when the files, interfaces, failure behavior, and check agree with this Implementation Plan.]

## Complete Verification

Run: `exact full-suite command`

Expected: PASS with no unexpected warnings or skipped required coverage.
