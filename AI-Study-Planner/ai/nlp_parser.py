import re

KNOWN_SUBJECTS = [
    "math", "os", "ai", "dbms", "cn", "physics",
    "chemistry", "biology", "english", "java", "python"
]

def extract_data(text):

    text_lower = text.lower()

    subjects = []
    marks = []
    exam_days = []
    hours = None

    # -----------------------------
    # Extract hours
    # -----------------------------
    hours_match = re.search(r'(\d+)\s*(hour|hr)', text_lower)
    if hours_match:
        hours = int(hours_match.group(1))

    # -----------------------------
    # Extract subject blocks
    # -----------------------------
    for sub in KNOWN_SUBJECTS:
        if sub in text_lower:
            subjects.append(sub.capitalize())

            # Find numbers near subject
            pattern = rf"{sub}.*?(\d+).*?(\d+)"
            match = re.search(pattern, text_lower)

            if match:
                marks.append(int(match.group(1)))
                exam_days.append(int(match.group(2)))

    # -----------------------------
    # If nothing found
    # -----------------------------
    if not subjects:
        return {"error": "subjects_not_found"}

    return {
        "subjects": subjects,
        "marks": marks,
        "exam_days": exam_days,
        "hours": hours
    }