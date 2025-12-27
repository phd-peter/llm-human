# Python Executive: Update Logic & Pipeline

The "Python Executive" is the runtime system that wraps the LLM. It manages the lifecycle of the agent by updating the State and Evidence layers between single-turn calls.

## The Core Loop

1. **Construct Prompt**: Combine A (Constitution) + B (Current State) + C (Selected Evidence).
2. **Invoke LLM**: Send single-turn prompt. Get structured response (Plan + Code).
3. **Execute & Verify**: Run the code against tests, profilers, or validators.
4. **Update Asset Store**: Save full logs, code versions, and state history to DB/Files.
5. **Digest & Select**: Create *new* Layer B and Layer C summaries for the next turn.
6. **Repeat**: Until "Acceptance" criteria met.

---

## 1. Updating Layer B: State (The "Brain" Update)

The LLM is responsible for *proposing* the state update, but the Python Executive *enforces* structure.

**Input:**

- Old State.
- LLM's new decision (e.g., "Refine", "Pivot", "Finalize").
- Execution Result (Pass/Fail).

**Logic:**

- **If Execution == Fail:**
  - Update `status` to "Debugging".
  - Append failure specific summary to `known_failures`.
  - If `known_failures` contains > 3 similar failures (e.g., 3 TLEs in a row), **FORCE** `next_objective` to "Analyze Root Cause" or "Pivot Approach".
- **If Execution == Pass (Partial):**
  - Update `status` to "Optimizing".
  - Update `current_approach` details with new findings.
- **If LLM requests "Pivot":**
  - Archive current approach to `history_summary`.
  - Reset `current_approach` to new hypothesis.
  - Clear specific tasks, set `next_objective` to "Prototype New Approach".

## 2. Updating Layer C: Evidence (The "Reality" Update)

This is the most critical step for grounding. The Executive must act as a **Smart Selector**.

**Input:**

- Full execution logs (stdout, stderr).
- Test framework outputs (PyTest, custom Judge).
- Profiler stats.

**Selection Logic (The "Digest"):**

- **Do NOT** blindly append.
- **Prioritize New Info:** If we have 5 failures, show the *most recent* one and the *most distinct* one.
- **Context-Aware Selection:**
  - *If State == "Optimizing" (TLE prevention):* Select **Time Sweep** data (N=1k vs N=10k vs N=100k) and **Profiler** outlines.
  - *If State == "Debugging" (WA prevention):* Select **Smallest Failing Input** (Counter-example).
  - *If State == "Prototyping":* Select **Basic Syntax/Runtime Error** logs.

## 3. The "Structure Jump" Trigger (Anti-Greedy Mechanism)

To prevent local minima (polishing a bad algorithm), the Python Executive implements a **Frustration Counter**.

- **Variable:** `failure_streak_count`
- **Variable:** `structural_pivot_threshold` (e.g., 3)
- **Logic:**
  - If an approach fails structurally (TLE/WA) on the same test set `k` times:
    - **Inject System Directive:** "You have failed X times with the current approach. You MUST propose a fundamentally different algorithm / data structure. Do not refine."
    - This overrides the LLM's tendency to just "fix the bug".

## 4. Acceptance Gate (Termination)

The LLM cannot "decide" it is done. It must "prove" it.

- **Condition:** All internal tests pass AND (optional) heuristic complexity analysis satisfies constraints.
- **Action:** If LLM outputs `[FINALIZE]`, the Python Executive triggers the **Final Verification Suite** (Held-out tests, large N stress test).
- **Result:**
  - Pass -> Output solution.
  - Fail -> Reject `[FINALIZE]`, add failure to Evidence, continue loop.
