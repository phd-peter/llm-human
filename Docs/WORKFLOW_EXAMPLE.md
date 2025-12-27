# Example Workflow Trace

This document traces how the **Layers (B & C)** evolve during a hypothetical problem-solving session.

**Problem:** Find the maximum pair sum in an array `A` of size `N=100,000` such that `A[i] + A[j] < K`.

---

## Turn 1: Initialization

**Input**: Zero state.
**Prompt [STATE]**: `{"status": "New", "current_approach": "None"}`
**Prompt [EVIDENCE]**: `None`

**LLM Output**:

- Plan: "I will use a brute force O(N^2) approach to ensure correctness first."
- Code: `for i in range(N): for j in range(i+1, N): ...`

**Python Executive Action**:

- Run code with N=100,000.
- Result: **TIMEOUT** (Stopped after 3s).
- Update State: Status -> "Debugging", Known Failures -> ["TLE at N=100k"].
- Update Evidence: Save performance log.

---

## Turn 2: The TLE Realization

**Prompt Injection**:

- **[STATE]**:

  ```json
  {
    "status": "Debugging",
    "current_approach": "Brute Force O(N^2)",
    "known_failures": ["TLE on large inputs (N=100k)"]
  }
  ```

- **[EVIDENCE]**:

  ```text
  - Run #1: FAILED (Time Limit Exceeded)
  - Input size: N=100,000
  - Execution Time: > 3.0s
  - Estimated Complexity: O(N^2) is too slow for N=10^5.
  ```

**LLM Output**:

- Thought: "O(N^2) is indeed too slow. I need O(N log N) or O(N). I should sort the array and use Two Pointers."
- Plan: "Implement sorting + two pointer technique."
- Code: `A.sort(); left=0, right=N-1; ...`

**Python Executive Action**:

- Run code with N=100,000.
- Result: **Passes** time limit, but fails a specific edge case check (e.g., handling duplicates).
- Update State: Approach -> "Two Pointers", Status -> "Refining", Failure -> "WA on duplicates".
- Update Evidence: Add specific failing input.

---

## Turn 3: The Refinement

**Prompt Injection**:

- **[STATE]**:

  ```json
  {
    "status": "Refining",
    "current_approach": "Sorted + Two Pointers",
    "known_failures": ["WA on duplicates input"]
  }
  ```

- **[EVIDENCE]**:

  ```text
  - Run #2: PERFORMANCE OK (0.1s) but ACCURACY FAIL.
  - Failing Input: [1, 3, 3, 5], K=6
  - Expected: 6 (3+3)
  - Got: 4 (1+3)
  ```

**LLM Output**:

- Thought: "Ah, the condition `i < j` was mishandled when elements are the same..."
- Code: *Fixes logic*

**Python Executive Action**:

- Run code. **All Tests Pass.**
- Final Validation Run: Success.
- Action: Terminate and output solution.
