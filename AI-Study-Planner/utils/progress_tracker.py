import json
import os
from datetime import datetime, date, timedelta
from pathlib import Path
import streamlit as st

# Ensure data directory exists
DATA_DIR = Path(__file__).parent.parent / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_progress():
    ensure_data_dir()
    if not PROGRESS_FILE.exists():
        default_data = {
            "streak": 0,
            "last_study_date": None,
            "total_hours_studied": 0.0,
            "subject_progress": {},
            "daily_logs": []
        }
        save_progress(default_data)
        return default_data

    try:
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
            # Ensure all required keys exist
            if "streak" not in data:
                data["streak"] = 0
            if "last_study_date" not in data:
                data["last_study_date"] = None
            if "total_hours_studied" not in data:
                data["total_hours_studied"] = 0.0
            if "subject_progress" not in data:
                data["subject_progress"] = {}
            if "daily_logs" not in data:
                data["daily_logs"] = []
            return data
    except Exception as e:
        print(f"Error loading progress: {e}")
        # Return default if corrupted
        return {
            "streak": 0,
            "last_study_date": None,
            "total_hours_studied": 0.0,
            "subject_progress": {},
            "daily_logs": []
        }


def save_progress(data):
    ensure_data_dir()
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        print(f"Error saving progress: {e}")
        return False


def get_today_date():
    return date.today().isoformat()


def update_streak(progress):
    today = get_today_date()
    last_date = progress.get("last_study_date")

    # Already studied today - keep current streak
    if last_date == today:
        return progress.get("streak", 0)

    # Studied yesterday - continue streak
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    if last_date == yesterday:
        progress["streak"] = progress.get("streak", 0) + 1
    else:
        # New streak (or streak was broken)
        progress["streak"] = 1

    progress["last_study_date"] = today
    return progress["streak"]


def log_study_session(subject_name, hours_completed, notes=""):
    try:
        progress = load_progress()

        # Ensure hours is float
        hours_completed = float(hours_completed)

        # Update streak
        streak = update_streak(progress)

        # Create session log
        session = {
            "date": datetime.now().isoformat(),
            "subject": str(subject_name),
            "hours_completed": hours_completed,
            "notes": str(notes) if notes else ""
        }

        # Add to logs
        if "daily_logs" not in progress:
            progress["daily_logs"] = []
        progress["daily_logs"].append(session)

        # Update total hours
        if "total_hours_studied" not in progress:
            progress["total_hours_studied"] = 0.0
        progress["total_hours_studied"] += hours_completed

        # Update subject progress
        if "subject_progress" not in progress:
            progress["subject_progress"] = {}

        if subject_name not in progress["subject_progress"]:
            progress["subject_progress"][subject_name] = {
                "total_hours": 0.0,
                "sessions_count": 0,
                "last_studied": None
            }

        progress["subject_progress"][subject_name]["total_hours"] += hours_completed
        progress["subject_progress"][subject_name]["sessions_count"] += 1
        progress["subject_progress"][subject_name]["last_studied"] = datetime.now().isoformat()

        # Save to file
        if save_progress(progress):
            return streak
        else:
            return -1  # Error indicator
    except Exception as e:
        print(f"Error in log_study_session: {e}")
        return -1


def get_missed_subjects(schedule):
    """Check which subjects from schedule were not studied today"""
    try:
        progress = load_progress()
        today = get_today_date()

        # Get subjects studied today
        studied_today = set()
        for log in progress.get("daily_logs", []):
            log_date = ""
            if isinstance(log.get("date"), str):
                log_date = log["date"][:10]
            else:
                log_date = str(log.get("date"))[:10]

            if log_date == today:
                studied_today.add(log.get("subject", ""))

        # Find missed subjects
        missed = []
        for sub in schedule:
            if sub.name not in studied_today:
                missed.append(sub)

        return missed
    except Exception as e:
        print(f"Error in get_missed_subjects: {e}")
        return []


def get_study_stats(days=7):
    """Get study stats for last N days"""
    try:
        progress = load_progress()
        cutoff = date.today() - timedelta(days=days)

        recent_logs = []
        for log in progress.get("daily_logs", []):
            try:
                log_date_str = ""
                if isinstance(log.get("date"), str):
                    log_date_str = log["date"][:10]
                else:
                    log_date_str = str(log.get("date"))[:10]

                log_date = date.fromisoformat(log_date_str)
                if log_date >= cutoff:
                    recent_logs.append(log)
            except:
                continue

        # Calculate daily hours
        daily_hours = {}
        for log in recent_logs:
            day = ""
            if isinstance(log.get("date"), str):
                day = log["date"][:10]
            else:
                day = str(log.get("date"))[:10]

            hours = float(log.get("hours_completed", 0))
            daily_hours[day] = daily_hours.get(day, 0.0) + hours

        return {
            "streak": progress.get("streak", 0),
            "total_hours": float(progress.get("total_hours_studied", 0)),
            "recent_daily_hours": daily_hours,
            "subject_breakdown": progress.get("subject_progress", {})
        }
    except Exception as e:
        print(f"Error in get_study_stats: {e}")
        return {
            "streak": 0,
            "total_hours": 0.0,
            "recent_daily_hours": {},
            "subject_breakdown": {}
        }


def get_today_logs():
    """Get all logs for today"""
    try:
        progress = load_progress()
        today = get_today_date()

        today_logs = []
        for log in progress.get("daily_logs", []):
            log_date = ""
            if isinstance(log.get("date"), str):
                log_date = log["date"][:10]
            else:
                log_date = str(log.get("date"))[:10]

            if log_date == today:
                today_logs.append(log)

        return today_logs
    except Exception as e:
        print(f"Error in get_today_logs: {e}")
        return []


def has_logged_today(subject_name=None):
    """Check if already logged today"""
    try:
        today_logs = get_today_logs()
        if subject_name is None:
            return len(today_logs) > 0

        for log in today_logs:
            if log.get("subject") == subject_name:
                return True
        return False
    except Exception as e:
        print(f"Error in has_logged_today: {e}")
        return False


def reset_progress():
    """Reset all progress data"""
    try:
        default_data = {
            "streak": 0,
            "last_study_date": None,
            "total_hours_studied": 0.0,
            "subject_progress": {},
            "daily_logs": []
        }
        return save_progress(default_data)
    except Exception as e:
        print(f"Error in reset_progress: {e}")
        return False