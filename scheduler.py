import json
from course import Course

class Scheduler:
    def __init__(self):
        self.selected_courses = []

    def add_course(self, course_to_add: Course):
        for existing_course in self.selected_courses:
            has_conflict, conflict_info = course_to_add.has_conflict(existing_course)
            if has_conflict:
                return False, conflict_info
        self.selected_courses.append(course_to_add)
        print(f"[Scheduler] After adding, {course_to_add.course_name} (ID: {course_to_add.course_id}) has Parsed Schedule: {course_to_add.schedule_parsed}")
        print(f"[Scheduler] Course {course_to_add.course_name} added. Total selected courses: {len(self.selected_courses)}")

    def remove_course(self, course_id: str):
        self.selected_courses = [c for c in self.selected_courses if c.course_id != course_id]

    def get_schedule(self):
        print(f"[Scheduler] get_schedule called. Returning {len(self.selected_courses)} courses.")
        return [c.to_dict() for c in self.selected_courses]

    def save_to_file(self, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([c.to_dict() for c in self.selected_courses], f, ensure_ascii=False, indent=4)

    def load_from_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.selected_courses = [Course(d) for d in data]
        except FileNotFoundError:
            self.selected_courses = []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filepath}. File might be corrupted.")
            self.selected_courses = []
