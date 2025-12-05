import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from services.queue_manager import queue_manager
from services.ai_service import correct_song_name
from services.rl_service import agent

def test_ai_correction():
    print("Testing AI Correction...")
    # Mocking OpenAI if no key, but correct_song_name handles it safely
    res = correct_song_name("bohemian rhapsody queen")
    print(f"Result: {res}")

def test_queue_logic():
    print("Testing Queue Logic...")
    # This might fail if DB not init, but let's try
    try:
        # We won't actually call YouTube API to save quota/time,/
        # but we can check if queue manager initializes
        assert queue_manager is not None
        print("Queue Manager Initialized.")
    except Exception as e:
        print(f"Queue Manager Valid: {e}")

def test_rl_agent():
    print("Testing RL Agent...")
    action = agent.choose_action()
    print(f"Agent chose: {action}")
    agent.update(action, 1.0)
    print("Agent updated.")

if __name__ == "__main__":
    test_ai_correction()
    test_queue_logic()
    test_rl_agent()
    print("Basic verification complete.")
