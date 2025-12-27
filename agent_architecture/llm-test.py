import sys
import os

# Add the current directory to sys.path to ensure we can import agent_engine
sys.path.append(os.getcwd())

try:
    from agent_engine.llm_client import LLMClient
except ImportError as e:
    print(f"ImportError: {e}")
    # Fallback/Debug: try to look into subfolder if running from parent? 
    # But CWD is agent_architecture, agent_engine is a subdir.
    # Without __init__.py it is a namespace package, usually works in Py3.
    sys.exit(1)

def main():
    print("Initializing LLMClient...")
    try:
        client = LLMClient()
        print(f"Client initialized with model: {client.model_name}")
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        return

    prompt = "Hello, are you working? Reply with 'Yes, I am working.'"
    print(f"\nSending prompt: '{prompt}'")
    
    try:
        response = client.call_chat(prompt)
        print("\n--- Response from LLM ---")
        print(response)
        print("-------------------------")
    except Exception as e:
        print(f"Error calling chat: {e}")

if __name__ == "__main__":
    main()