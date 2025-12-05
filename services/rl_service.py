import random
import json
import os
from datetime import datetime
from config import DATA_DIR
import logging

logger = logging.getLogger(__name__)

RL_STATE_FILE = os.path.join(DATA_DIR, "rl_agent_state.json")

# Define Actions (Search Queries/Vibes)
ACTIONS = [
    "Upbeat Pop Hits",
    "Lo-fi Study Beats",
    "Classic Rock Anthems",
    "Smooth Jazz",
    "Electronic Dance Focus",
    "Acoustic Coffee Shop"
]

class JukeboxAgent:
    def __init__(self):
        self.q_table = {} # Key: "Day-TimeBlock", Value: {Action: Score}
        self.load_state()
        
    def get_context(self):
        """Returns context string: DayOfWeek-TimeBlock"""
        now = datetime.now()
        day = now.strftime("%A") # Monday, Tuesday...
        hour = now.hour
        
        if hour < 12:
            time_block = "Morning"
        elif hour < 17:
            time_block = "Afternoon"
        else:
            time_block = "Evening"
            
        return f"{day}-{time_block}"
        
    def choose_action(self, epsilon: float = 0.2):
        """Epsilon-Greedy Action Selection"""
        context = self.get_context()
        
        # Initialize context if new
        if context not in self.q_table:
            self.q_table[context] = {action: 1.0 for action in ACTIONS} # Start neutral/positive
            
        # Explore
        if random.random() < epsilon:
            return random.choice(ACTIONS)
            
        # Exploit (Choose Max Q)
        action_scores = self.q_table[context]
        best_action = max(action_scores, key=action_scores.get)
        return best_action

    def update(self, action: str, reward: float):
        """Update Q-Value: Q(s,a) = Q(s,a) + alpha * (reward - Q(s,a))"""
        context = self.get_context()
        alpha = 0.1 # Learning rate
        
        if context not in self.q_table:
            self.q_table[context] = {a: 1.0 for a in ACTIONS}
            
        current_q = self.q_table[context].get(action, 1.0)
        new_q = current_q + alpha * (reward - current_q)
        self.q_table[context][action] = new_q
        
        self.save_state()
        logger.info(f"RL Update: {context} | {action} | Reward: {reward} | NewQ: {new_q:.2f}")

    def save_state(self):
        try:
            with open(RL_STATE_FILE, "w") as f:
                json.dump(self.q_table, f)
        except Exception as e:
            logger.error(f"Failed to save RL state: {e}")

    def load_state(self):
        if os.path.exists(RL_STATE_FILE):
            try:
                with open(RL_STATE_FILE, "r") as f:
                    self.q_table = json.load(f)
            except Exception:
                self.q_table = {}

# Singleton Agent
agent = JukeboxAgent()
