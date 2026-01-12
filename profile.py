# profile.py
import json
import os

PROFILE_FILE = "profile.json"

def load_profile():
    default = {
        "name": "Новичок",
        "avatar": 1,
        "exercises": {
            "math": {"level": 1, "score": 0, "correct_in_row": 0},
            "memory": {"level": 1, "score": 0, "correct_in_row": 0},
            "attention": {"level": 1, "score": 0, "correct_in_row": 0},
            "logic": {"level": 1, "score": 0, "correct_in_row": 0}
        }
    }

    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                def deep_merge(base, update):
                    for k, v in base.items():
                        if k not in update:
                            update[k] = v
                        elif isinstance(v, dict) and isinstance(update[k], dict):
                            deep_merge(v, update[k])
                    return update
                return deep_merge(default, loaded)
        except:
            pass
    return default

def save_profile(profile):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

def get_avg_level(profile):
    levels = [ex["level"] for ex in profile["exercises"].values()]
    return round(sum(levels) / len(levels))