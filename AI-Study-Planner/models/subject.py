class Subject:

    def __init__(self, name, marks, exam_days, difficulty):

        self.name = name
        self.marks = marks
        self.exam_days = exam_days
        self.difficulty = difficulty

        self.priority = 0
        self.study_hours = 0

        # NEW
        self.remaining_hours = 0