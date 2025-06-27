import json
import pandas as pd
from course import Course

def load_courses_from_json(json_file_path):
    all_courses_data = []
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            all_courses_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path}. Check file format.")
        return []

    course_objects = []
    for course_item in all_courses_data:
        # Map JSON keys to our Course object keys
        schedule_time_raw = course_item.get("scheduleTime", "")
        print(f'[Crawler] Raw scheduleTime from JSON: {course_item.get("scheduleTime")}, Final schedule_time_raw: \'{schedule_time_raw}\'')
        
        course_data = {
            "semester": "", # Not available in this JSON format
            "department": "", # Not available in this JSON format
            "tableType": "", # Not available in this JSON format
            "internalSemester": "", # Not available in this JSON format
            "courseId": course_item.get("courseId", ""),
            "courseName": course_item.get("courseName", ""),
            "courseNameEn": "", # Not available in this JSON format
            "classNo": course_item.get("classNo", ""),
            "targetAudience": "", # Not available in this JSON format
            "courseType": course_item.get("courseType", ""),
            "credits": course_item.get("credits", ""),
            "weeklyHours": "", # Not available in this JSON format
            "totalHours": "", # Not available in this JSON format
            "teacher": course_item.get("teacher", ""),
            "scheduleWeek": course_item.get("scheduleWeek", ""),
            "scheduleTime": schedule_time_raw,
            "remark": course_item.get("remark", ""),
        }
        print(f"[Crawler] Course data for Course object: '上课时间': '{course_data.get('上课时间')}'")
        course_objects.append(Course(course_data))
    print(f"[Crawler] Created {len(course_objects)} Course objects.")
    return course_objects