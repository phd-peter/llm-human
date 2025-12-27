import os
import json
from datetime import datetime
from pathlib import Path
from .layers import State, Evidence

class Store:
    def __init__(self, run_id: str = None):
        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_path = Path("runs") / run_id
        self.base_path.mkdir(parents=True, exist_ok=True)
        print(f"Store initialized at {self.base_path}")

    def save_turn(self, turn_id: int, state: State, evidence: Evidence, raw_input: str, raw_output: str):
        turn_dir = self.base_path / str(turn_id)
        turn_dir.mkdir(exist_ok=True)

        # Save State
        with open(turn_dir / "state.json", "w") as f:
            f.write(state.model_dump_json(indent=2))

        # Save Evidence Summary (conceptual, dumping all logs for now as it's append only)
        with open(turn_dir / "evidence_log.json", "w") as f:
            f.write(evidence.model_dump_json(indent=2))

        # Save Raw IO
        with open(turn_dir / "prompt_in.txt", "w") as f:
            f.write(raw_input)
        
        with open(turn_dir / "llm_out.txt", "w") as f:
            f.write(raw_output)
