from flask import Flask, render_template, request, jsonify
import json
from crawler import load_courses_from_json
from scheduler import Scheduler
from course import Course
import os

app = Flask(__name__)
scheduler = Scheduler()

# Load initial courses from JSON file
JSON_COURSE_FILE = "/home/xianyu/projects/PKU-Course-Planner/courses.json"
all_available_courses = load_courses_from_json(JSON_COURSE_FILE)


@app.route("/")
def index():
    # Get all available courses (initially unfiltered)
    available_courses_for_template = [c.to_dict() for c in all_available_courses]
    # Get currently selected courses
    selected_schedule_for_template = scheduler.get_schedule()
    return render_template(
        "index.html",
        available_courses=available_courses_for_template,
        selected_schedule=selected_schedule_for_template,
    )


@app.route("/api/courses", methods=["GET"])
def get_courses():
    year_filter = request.args.get("year")
    dept_filter = request.args.get("dept")
    term_filter = request.args.get("term")
    stu_filter = request.args.get("stu")

    filtered_courses = []
    for course in all_available_courses:
        match = True
        if year_filter and course.semester and year_filter not in course.semester:
            match = False
        if dept_filter and course.department and dept_filter not in course.department:
            match = False
        if term_filter and course.semester and term_filter not in course.semester:
            match = False
        # Assuming 'stu' filter might be part of courseType or other field if available
        # For now, let's skip 'stu' filter as it's not directly mapped in the provided JSON
        # if stu_filter and course.course_type and stu_filter not in course.course_type:
        #     match = False

        if match:
            filtered_courses.append(course.to_dict())

    return jsonify(filtered_courses)


@app.route("/api/schedule", methods=["GET"])
def get_schedule():
    return jsonify(scheduler.get_schedule())


@app.route("/api/schedule/add", methods=["POST"])
def add_course_to_schedule():
    course_data = request.json
    print(f"[App] Received course data for add: {course_data}")
    if not course_data:
        return jsonify({"error": "Invalid course data"}), 400

    course_to_add = Course(course_data)
    success, conflict_info = scheduler.add_course(course_to_add)

    if success:
        return jsonify({"success": True, "message": "Course added successfully"})
    else:
        if success:
            print(f"[App] Course {course_to_add.course_name} added successfully.")
            return jsonify({"success": True, "message": "Course added successfully"})
        else:
            print(
                f"[App] Conflict detected for {course_to_add.course_name}: {conflict_info}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Conflict detected",
                        "conflict_info": conflict_info,
                    }
                ),
                409,
            )  # 409 Conflict


@app.route("/api/schedule/remove", methods=["POST"])
def remove_course_from_schedule():
    course_id = request.json.get("course_id")
    if not course_id:
        return jsonify({"error": "Course ID not provided"}), 400

    scheduler.remove_course(course_id)
    return jsonify({"success": True, "message": "Course removed successfully"})


@app.route("/api/schedule/save", methods=["POST"])
def save_schedule():
    try:
        scheduler.save_to_file("my_schedule.json")
        return jsonify({"success": True, "message": "Schedule saved successfully"})
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Failed to save schedule: {e}"}),
            500,
        )


if __name__ == "__main__":
    # Load schedule on startup
    scheduler.load_from_file(
        os.path.join(os.path.dirname(__file__), "my_schedule.json")
    )
    app.run(debug=True)
