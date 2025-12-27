from agent_engine.executive import AgentExecutive
from agent_engine.layers import Constitution
import os

def load_problem(file_name):
    if not os.path.exists(file_name):
        print(f"Error: {file_name} not found. Please create one.")
        exit(1)
    with open(file_name, "r") as f:
        return f.read()

def main():
    promblem_file_name = "PROBLEM_4675.md"
    problem_text = load_problem(promblem_file_name)
    
    # Default Constitution (this could also be loaded from a file)
    constitution = Constitution(
        goals=["Solve the problem with 100% correctness", "Maximize efficiency"],
        constraints=["Do not assume unstated constraints", "Pass all provided verification tests"],
        protocols=["Refine approach if fails 3 times", "Pivot if structural failure detected"]
    )
    
    agent = AgentExecutive(problem_text, constitution)
    agent.run()

if __name__ == "__main__":
    main()
