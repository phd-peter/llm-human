import re
import traceback
import sys
import io
import contextlib
from typing import Dict, Any, Tuple
from .layers import Constitution, State, Evidence
from .llm_client import LLMClient
from .store import Store

class AgentExecutive:
    def __init__(self, problem_text: str, constitution: Constitution):
        self.problem_text = problem_text
        self.constitution = constitution
        self.state = State(
            current_approach="None",
            hypothesis="Initial State",
            status="Active",
            known_failures=[],
            next_objective="Analyze problem and propose initial plan"
        )
        self.evidence = Evidence()
        self.client = LLMClient()
        self.store = Store()
        self.turn_count = 0
        self.max_turns = 10  # Safety limit

    def run(self):
        print("Starting Agent Executive...")
        while self.turn_count < self.max_turns:
            self.turn_count += 1
            print(f"\n--- Turn {self.turn_count} ---")
            
            # 1. Construct Prompt (Generation Phase)
            prompt = self._construct_prompt()
            
            # 2. Call LLM (Generation Phase)
            print("Invoking LLM (Generation)...")
            llm_response_text = self.client.call_chat(prompt)
            print("LLM Response received.")

            # 3. Parse Response
            parsed = self._parse_response(llm_response_text)
            
            # 4. Execute Code
            code = parsed.get("CODE", "")
            execution_log = ""
            execution_success = False
            
            if code.strip():
                print("Executing Code...")
                stdin_data = parsed.get("STDIN", "")
                execution_success, execution_log = self._execute_code(code, stdin_data)
            else:
                execution_log = "No code generated."
                execution_success = True # purely reasoning step?

            # 5. Evaluation Phase (Second LLM Call)
            print("Invoking LLM (Evaluation)...")
            eval_prompt = self._construct_evaluation_prompt(code, execution_log)
            eval_response_text = self.client.call_chat(eval_prompt)
            eval_parsed = self._parse_response(eval_response_text)
            print("Evaluation received.")
            
            # 6. Update Evidence
            thoughts = parsed.get("THOUGHTS", "")
            plan = parsed.get("PLAN", "")
            analysis = eval_parsed.get("ANALYSIS", "")
            
            self.evidence.add_log(f"Turn {self.turn_count} Logic:\n[THOUGHTS]\n{thoughts}\n[PLAN]\n{plan}\n\n[EXECUTION LOG]\n{execution_log}\n\n[EVALUATION]\n{analysis}")
            
            # 7. Update State (Based on Evaluation)
            state_update_text = eval_parsed.get("STATE_UPDATE", "")
            self._update_state(state_update_text, execution_success, execution_log)

            # 8. Save Asset
            self.store.save_turn(
                self.turn_count,
                self.state,
                self.evidence,
                prompt,
                llm_response_text + "\n\n[EVALUATION PHASE]\n" + eval_response_text
            )

            # 9. Check Termination
            # We trust the second LLM's status decision fully now
            if self.state.status == "Finished":
                print("Agent requested termination (Status: Finished).")
                break
        
        print("Agent Finished.")

    def _construct_prompt(self) -> str:
        # Load template (assuming it's in the parent directory or relative)
        try:
            with open("PROMPT_TEMPLATE.md", "r") as f:
                template = f.read()
        except FileNotFoundError:
            # Fallback path if running from agent_engine
            with open("../PROMPT_TEMPLATE.md", "r") as f:
                template = f.read()
            
        return template.replace("{{LAYER_A_CONTENT}}", self.constitution.render())\
                       .replace("{{PROBLEM_TEXT}}", self.problem_text)\
                       .replace("{{LAYER_B_CONTENT}}", self.state.render())\
                       .replace("{{LAYER_C_CONTENT}}", self.evidence.select_relevant(self.state))\
                       .replace("{{TURN_INFO}}", f"Current Turn: {self.turn_count} / {self.max_turns}")

    def _construct_evaluation_prompt(self, code: str, execution_log: str) -> str:
        try:
            with open("EVALUATION_PROMPT.md", "r") as f:
                template = f.read()
        except FileNotFoundError:
            with open("../EVALUATION_PROMPT.md", "r") as f:
                template = f.read()
                
        return template.replace("{{LAYER_A_CONTENT}}", self.constitution.render())\
                       .replace("{{PROBLEM_TEXT}}", self.problem_text)\
                       .replace("{{LAYER_B_CONTENT}}", self.state.render())\
                       .replace("{{CODE}}", code)\
                       .replace("{{EXECUTION_LOG}}", execution_log)

    def _parse_response(self, text: str) -> Dict[str, str]:
        # Simple regex parser for <TAG>content</TAG>
        tags = ["THOUGHTS", "PLAN", "CODE", "STATE_UPDATE", "STDIN", "ANALYSIS"]
        parsed = {}
        for tag in tags:
            pattern = f"<{tag}>(.*?)</{tag}>"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                parsed[tag] = match.group(1).strip()
            else:
                parsed[tag] = ""
        return parsed

    def _sanitize_code(self, code: str) -> str:
        code = code.strip()
        # Remove Markdown code fences if present
        if code.startswith("```"):
            lines = code.splitlines()
            # Remove first and last fence
            lines = [line for line in lines if not line.strip().startswith("```")]
            code = "\n".join(lines)
        return code.strip()

    def _execute_code(self, code: str, stdin_data: str = "") -> Tuple[bool, str]:
        # Capture stdout/stderr via subprocess to avoid blocking and allow stdin injection
        import subprocess
        import tempfile
        import os

        # Simple progress indicator for the user
        print("  > Executing Python Code with Subprocess...")

        success = False
        output_log = ""

        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file_name = temp_file.name
            # Write sanitized code to file
            temp_file.write(self._sanitize_code(code))
        
        try:
            # Run the subprocess
            print(f"    - Running input injection: {len(stdin_data)} chars...", file=sys.stdout)
            result = subprocess.run(
                [sys.executable, temp_file_name],
                input=stdin_data,
                text=True,
                capture_output=True,
                timeout=60  # 60 seconds timeout
            )
            
            # Combine stdout and stderr
            output_log = result.stdout
            if result.stderr:
                output_log += "\n[STDERR]\n" + result.stderr
            
            if result.returncode == 0:
                success = True
            else:
                success = False
                output_log += f"\nProcess exited with return code {result.returncode}"

        except subprocess.TimeoutExpired as e:
            success = False
            output_log = f"Execution timed out!\nSTDOUT so far:\n{e.stdout}\nSTDERR so far:\n{e.stderr}"
        except Exception as e:
            success = False
            output_log = f"Execution failed with error: {str(e)}"
            traceback.print_exc()
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
        
        return success, output_log

    def _update_state(self, state_update_text: str, exec_success: bool, exec_log: str):
        # In a robust system, we'd parse the state_update_text (YAML/JSON) and merge.
        # Here, we'll try to extract fields if formatted like "- Key: Value"
        # And we apply the "Update Logic" rules.
        
        # 1. Parse LLM proposal
        updates = {}
        for line in state_update_text.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                updates[k.strip("- ").lower().replace(" ", "_")] = v.strip()
        
        # 2. Apply Logic
        if not exec_success:
            self.state.status = "Debugging"
            self.state.known_failures.append(f"Turn {self.turn_count} Execution Error")
            # Frustration check
            if len(self.state.known_failures) > 3:
                self.state.next_objective = "PIVOT: Too many failures"
        else:
            if "status" in updates:
                raw_status = updates["status"].lower()
                if "finished" in raw_status or "finalized" in raw_status:
                    self.state.status = "Finished"
                elif "debug" in raw_status:
                    self.state.status = "Debugging"
                else:
                    self.state.status = "Active" # Default rollback if unclear, or keep raw? Let's use raw but normalized if simple.
                    # Actually, if it's not finished/debug, just trust the prompt or updates. 
                    # But for safety let's just use the raw value if it's short, otherwise 'Active'
                    if len(updates["status"]) < 20: 
                        self.state.status = updates["status"]
                    else:
                        # verbose status like the user saw
                        self.state.status = "Active"

            if "current_approach" in updates:
                self.state.current_approach = updates["current_approach"]
            if "next_objective" in updates:
                self.state.next_objective = updates["next_objective"]
