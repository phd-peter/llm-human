# Layer Definitions

This document defines the three layers of context injected into the LLM at every step. These layers ensure the agent maintains identity and direction without relying on conversation history.

## Layer A: Constitution (Identity)

**Nature:** Immutable, Static.
**Purpose:** Defines *who* the agent is and *how* it must behave.
**Content:**

- **Role:** Single, persistent problem-solving agent.
- **Goal:** Produce a 100% correct solution passing all constraints.
- **Priorities:** Correctness > Time Complexity > Code Stability.
- **Negative Constraints:** Do not assume unstated constraints. Do not finalize without evidence.
- **Protocol:** Rules for when to switch approaches vs. refine current approach.

### Example Schema

```markdown
[CONSTITUTION]
You are a single, persistent problem-solving agent.
Goal: Produce a solution that is 100% correct and passes all constraints.
Rules:
1. Do not assume constraints not stated in the problem.
2. Do not finalize without evidence from tests.
3. If TLE occurs > 3 times, MUST propose a structural change.
```

## Layer B: State (Working Memory)

**Nature:** Mutable, Iterative.
**Purpose:** Defines *where* the agent is in the problem-solving process.
**Content:**

- **Current Approach:** Summary of the active algorithm (e.g., "DP with Prefix Sum").
- **Hypothesis:** Why we think this will work.
- **Status:** Active | Stuck | Verifying | Finished.
- **Known Failures:** List of high-level failure modes encountered (e.g., "TLE at N=20000").
- **Next Objective:** The immediate goal for this turn (e.g., "Optimize inner loop").

### Example Schema (JSON/YAML-like)

```json
{
  "current_approach": {
    "name": "Greedy with Priority Queue",
    "complexity": "O(N log N)",
    "status": "Refining"
  },
  "history_summary": [
    "Attempt 1: Brute force O(N^2) -> TLE",
    "Attempt 2: Greedy -> WA on edge cases"
  ],
  "current_objective": "Fix WA by adding edge case handling for N=1"
}
```

## Layer C: Evidence (Reality)

**Nature:** Append-only (log), Selectively retrieved.
**Purpose:** Defines *what is true* in reality. Grounding.
**Content:**

- **Test Results:** Pass/Fail, Execution Time, Memory Usage.
- **Profiler Output:** Hotspots in the code.
- **Error Logs:** Stack traces, specific failure inputs.
- **Verification:** Metamorphic test results (e.g., "Invariant violated").

**Constraint:** Do NOT dump all history. Only inject the *relevant* evidence for the current state.

- If fixing TLE -> Show Profiler logs and Time Sweep data.
- If fixing WA -> Show the specific Counter-example input/output.

### Example Schema

```text
[EVIDENCE]
- Test Run #5: STARTED
- Input: N=100,000
- Result: TLE (Terminated after 3.0s)
- Profiler: 90% time spent in `calculate_cost` function (Line 42).
- Comparison: Previous O(N^2) approach failed at N=5000. Current approach fails at N=100,000.
```
