from agent_engine.executive import AgentExecutive
from agent_engine.layers import Constitution
import os

def load_problem():
    if not os.path.exists("PROBLEM.md"):
        print("Error: PROBLEM.md not found. Please create one.")
        exit(1)
    with open("PROBLEM.md", "r") as f:
        return f.read()

def main():
    problem_text = load_problem()
    
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
