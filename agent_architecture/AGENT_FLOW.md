# Agent Architecture Flow & Termination Logic

This document outlines the high-level control flow of the Agent Architecture, specifically focusing on the decision loop and termination conditions.

## High-Level Logic Flow

The Agent Executive operates in a continuous loop until a termination condition is met.

```mermaid
graph TD
    Start([Start Agent]) --> Init[Initialize State, Constitution, Evidence]
    Init --> TurnStart{Turn count < Max Turns?}
    
    TurnStart -- No --> StopLimit([Terminating: Max Turns Reached])
    TurnStart -- Yes --> ConstructPrompt[Construct Prompt]
    
    ConstructPrompt --> CallLLM[Call LLM (Gemini)]
    CallLLM --> ParseResp[Parse Response]
    
    ParseResp --> ExecuteCode{Has Code?}
    ExecuteCode -- Yes --> RunCode[Execute Python Code]
    ExecuteCode -- No --> LogicOnly[Skip Execution]
    
    RunCode --> ExecResult{Success?}
    ExecResult -- Yes --> UpdateState[Update State\nbased on STATE_UPDATE]
    ExecResult -- No --> SetDebug[Set Status = Debugging]
    
    LogicOnly --> UpdateState
    
    UpdateState --> SaveTurn[Save Turn to Store]
    
    SaveTurn --> CheckTerm{Termination Condition?}
    
    CheckTerm -- "Status == Finished" --> StopSuccess([Terminating: Goal Achieved])
    CheckTerm -- "[FINALIZE] in PLAN" --> StopSuccess
    CheckTerm -- Else --> TurnStart
```

## Termination Conditions

The agent terminates in one of three ways:

1. **Explicit Completion (Status)**
    * **Trigger**: The LLM outputs `Status: Finished` or `Status: Finalized` within the `<STATE_UPDATE>` tag.
    * **Logic**: `self.state.status` is updated to `"Finished"`, causing the loop to break.

2. **Explicit Completion (Plan)**
    * **Trigger**: The LLM includes the token `[FINALIZE]` within the `<PLAN>` tag.
    * **Logic**: The `[FINALIZE]` token is detected during the post-processing check.

3. **Safety Limit (Max Turns)**
    * **Trigger**: The loop counter reaches `self.max_turns` (default: 10).
    * **Logic**: The `while self.turn_count < self.max_turns` condition fails.

## Key Logic Components

### The "Updates" Mechanism

After every turn, the agent updates its internal state based on two factors:

1. **Execution Result**: If code execution fails (exception or timeout), the status is forced to `"Debugging"`.
2. **LLM Proposal**: If execution succeeds (or there was no code), the agent reads the `<STATE_UPDATE>` block (e.g., `Current Approach: ...`, `Status: ...`) to update its belief state.

### Code Execution

* Code is executed in a **restricted** environment (using `exec()`).
* It has a **60-second timeout** to prevent infinite loops.
* Standard Output (stdout) and Standard Error (stderr) are captured and fed back into the **Evidence** for the next turn.
