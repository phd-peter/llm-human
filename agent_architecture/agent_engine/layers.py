from pydantic import BaseModel, Field
from typing import List, Optional, Any
from dataclasses import dataclass

@dataclass(frozen=True)
class Constitution:
    goals: List[str]
    constraints: List[str]
    protocols: List[str]

    def render(self) -> str:
        return f"""
[CONSTITUTION]
GOALS:
{chr(10).join(f'- {g}' for g in self.goals)}
CONSTRAINTS:
{chr(10).join(f'- {c}' for c in self.constraints)}
PROTOCOLS:
{chr(10).join(f'- {p}' for p in self.protocols)}
"""

class State(BaseModel):
    current_approach: str = Field(..., description="Summary of the active algorithm or approach")
    hypothesis: str = Field(..., description="Why we think this will work")
    status: str = Field(..., description="Active | Stuck | Verifying | Finished")
    known_failures: List[str] = Field(default_factory=list, description="List of high-level failure modes encountered")
    next_objective: str = Field(..., description="The immediate goal for this turn")

    def render(self) -> str:
        return f"""
[STATE]
Current Approach: {self.current_approach}
Hypothesis: {self.hypothesis}
Status: {self.status}
Known Failures: {self.known_failures}
Next Objective: {self.next_objective}
"""

class Evidence(BaseModel):
    logs: List[str] = Field(default_factory=list)

    def select_relevant(self, state: State) -> str:
        # Smart selection logic as per UPDATE_LOGIC.md
        if not self.logs:
            return "No evidence yet."
        
        # Simple heuristic for now: Last 3 logs + any explicitly marked 'CRITICAL'
        # In a real implementation, this would use semantic search or robust filtering
        relevant_logs = self.logs[-3:]
        
        return f"""
[EVIDENCE]
{chr(10).join(relevant_logs)}
"""

    def add_log(self, content: str):
        self.logs.append(content)
