import json
import os
import time
from datetime import datetime, timedelta

class ScoreManager:
    def __init__(self):
        self.scores_dir = os.path.join("c:", "app", "random_blocks")
        self.scores_file = os.path.join(self.scores_dir, "scores.json")
        self.ensure_scores_file()

    def ensure_scores_file(self):
        """Initialize scores file if it doesn't exist"""
        if not os.path.exists(self.scores_dir):
            os.makedirs(self.scores_dir)
        
        if not os.path.exists(self.scores_file):
            default_data = {
                "scores": [],
                "statistics": {
                    "games_played": 0,
                    "total_time": 0
                }
            }
            with open(self.scores_file, 'w') as f:
                json.dump(default_data, f)

    def save_score(self, score, difficulty, time_played):
        """Save a new score with timestamp"""
        try:
            with open(self.scores_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"scores": [], "statistics": {"games_played": 0, "total_time": 0}}

        score_entry = {
            "score": score,
            "timestamp": time.time(),
            "difficulty": difficulty,
            "time_played": time_played
        }
        
        data["scores"].append(score_entry)
        data["statistics"]["games_played"] += 1
        data["statistics"]["total_time"] += time_played

        with open(self.scores_file, 'w') as f:
            json.dump(data, f)

    def get_best_scores(self):
        """Get best scores for different time periods"""
        try:
            with open(self.scores_file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "today": 0,
                "week": 0,
                "month": 0,
                "all_time": 0
            }

        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        today_scores = []
        week_scores = []
        month_scores = []
        all_scores = []

        for score in data["scores"]:
            score_time = datetime.fromtimestamp(score["timestamp"])
            all_scores.append(score["score"])
            
            if score_time >= today:
                today_scores.append(score["score"])
            if score_time >= week_ago:
                week_scores.append(score["score"])
            if score_time >= month_ago:
                month_scores.append(score["score"])

        return {
            "today": max(today_scores) if today_scores else 0,
            "week": max(week_scores) if week_scores else 0,
            "month": max(month_scores) if month_scores else 0,
            "all_time": max(all_scores) if all_scores else 0
        }

    def get_statistics(self):
        """Get gameplay statistics"""
        try:
            with open(self.scores_file, 'r') as f:
                data = json.load(f)
                return data["statistics"]
        except (FileNotFoundError, json.JSONDecodeError):
            return {"games_played": 0, "total_time": 0}
