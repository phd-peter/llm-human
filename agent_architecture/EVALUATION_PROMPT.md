# Evaluation Prompt Template

[CONSTITUTION]
{{LAYER_A_CONTENT}}

[CONTEXT]
You are the **Evaluation Module** of an algorithmic agent.
We have just executed a turn. Your job is to analyze the **Execution Result** and decide if the problem is solved or if further debugging/refinement is needed.

--------------------------------------------------------------------------------

[PROBLEM]
{{PROBLEM_TEXT}}

--------------------------------------------------------------------------------

[PREVIOUS STATE]
{{LAYER_B_CONTENT}}

--------------------------------------------------------------------------------

[GENERATED CODE & EXECUTION RESULT]
Below is the code that was just executed and its output.

```python
{{CODE}}
```

**Output Log:**

```text
{{EXECUTION_LOG}}
```

--------------------------------------------------------------------------------

[TASK]

1. ANALYZE the execution log. Did the code run successfully? Did it produce the expected answer?
2. COMPARE the result against the Problem Requirements.
3. DECIDE the new State.
   - If the log shows strict correctness and efficiency, set Status to "Finished".
   - If there was an error or the answer is wrong, set Status to "Debugging".
   - If more work is needed, set Status to "Active".

[OUTPUT FORMAT]
<ANALYSIS>
(Brief reasoning about the execution result)
</ANALYSIS>

<STATE_UPDATE>

- Current Approach: (Update if changed)
- Status: (Must be "Active", "Debugging", or "Finished")
- Next Objective: (What to do next turn)
</STATE_UPDATE>
