def generate_schedule(subjects, total_hours):
    for sub in subjects:
        weak_score = 100 - sub.marks
        urgency_score = 10 / sub.exam_days
        difficulty_score = sub.difficulty * 10

        sub.priority = weak_score + urgency_score * 100 + difficulty_score

    total_priority = sum(s.priority for s in subjects)

    for sub in subjects:
        allocated = (sub.priority / total_priority) * total_hours

        if sub.remaining_hours == 0:
            sub.remaining_hours = allocated
        else:
            sub.remaining_hours += allocated

        sub.study_hours = allocated

    return subjects


def reschedule(subjects, missed_subject_name):
    missed_sub = None

    for sub in subjects:
        if sub.name.lower() == missed_subject_name.lower():
            missed_sub = sub
            break

    if not missed_sub:
        return subjects

    missed_hours = missed_sub.study_hours
    missed_sub.remaining_hours += missed_hours

    for sub in subjects:
        sub.exam_days = max(1, sub.exam_days - 1)

    total_hours = sum(sub.remaining_hours for sub in subjects)
    return generate_schedule(subjects, total_hours)