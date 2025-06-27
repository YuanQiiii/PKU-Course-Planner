import re

class Course:
    def __init__(self, course_dict):
        self.course_id = course_dict.get('courseId', '')
        self.course_name = course_dict.get('courseName', '')
        self.course_name_en = course_dict.get('courseNameEn', '') # Assuming frontend might send this, otherwise it will be empty
        self.teacher = course_dict.get('teacher', '')
        self.credits = course_dict.get('credits', '')
        self.class_id = course_dict.get('classNo', '')
        self.semester = course_dict.get('semester', '') # This might still be empty if frontend doesn't send it
        self.department = course_dict.get('department', '') # This might still be empty if frontend doesn't send it
        self.schedule_raw = course_dict.get('schedule_raw', '')
        self.weeks = course_dict.get('weeks', '')
        self.exam_time = course_dict.get('examTime', '') # Assuming frontend might send this, otherwise it will be empty
        self.note = course_dict.get('remark', '')
        print(f"[Course] __init__ received schedule_raw: '{self.schedule_raw}'")
        self.schedule_parsed = self.parse_schedule()

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'course_name_en': self.course_name_en,
            'teacher': self.teacher,
            'credits': self.credits,
            'class_id': self.class_id,
            'semester': self.semester,
            'department': self.department,
            'schedule_raw': self.schedule_raw,
            'weeks': self.weeks,
            'schedule_parsed': self.schedule_parsed,
            'exam_time': self.exam_time,
            'note': self.note
        }

    def parse_schedule(self):
        parsed_schedules = []
        # 预处理：全角转半角，并按分号切分
        segments = self.schedule_raw.replace('；', ';').replace('，', ';').split(';')
        
        day_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7}
        
        print(f"Parsing schedule_raw: '{self.schedule_raw}'")

        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
            
            # 正则表达式：周(一二三四五六日)(\d+)-?(\d+)?(?:\((单|双)\))?
            match = re.search(r"周([一二三四五六日])(\d+)-?(\d+)?(?:\((单|双)\))?", segment)
            
            if match:
                day_str, start_str, end_str, week_type_str = match.groups()
                
                day = day_map.get(day_str)
                start = int(start_str)
                end = int(end_str) if end_str else start
                
                week_type = 'all'
                if week_type_str == '单':
                    week_type = 'odd'
                elif week_type_str == '双':
                    week_type = 'even'
                
                parsed_schedules.append({
                    'day': day,
                    'start': start,
                    'end': end,
                    'week_type': week_type
                })
        print(f"[Course] Parsed schedules: {parsed_schedules}")
        return parsed_schedules

    def _parse_weeks(self, weeks_str):
        # 解析起止周字符串，例如 "1-16", "1-8(单), 9-16(双)"
        # 返回一个包含所有周的集合
        weeks_set = set()
        if not weeks_str:
            return weeks_set

        parts = weeks_str.replace('，', ',').split(',')
        for part in parts:
            part = part.strip()
            if not part:
                continue

            week_type = 'all'
            if '(单)' in part:
                week_type = 'odd'
                part = part.replace('(单)', '')
            elif '(双)' in part:
                week_type = 'even'
                part = part.replace('(双)', '')

            if '-' in part:
                start_week, end_week = map(int, part.split('-'))
                for week in range(start_week, end_week + 1):
                    if week_type == 'all':
                        weeks_set.add(week)
                    elif week_type == 'odd' and week % 2 != 0:
                        weeks_set.add(week)
                    elif week_type == 'even' and week % 2 == 0:
                        weeks_set.add(week)
            else:
                week = int(part)
                if week_type == 'all':
                    weeks_set.add(week)
                elif week_type == 'odd' and week % 2 != 0:
                    weeks_set.add(week)
                elif week_type == 'even' and week % 2 == 0:
                    weeks_set.add(week)
        return weeks_set

    def has_conflict(self, other_course):
        # 检查周次是否有交集
        self_weeks = self._parse_weeks(self.weeks)
        other_weeks = other_course._parse_weeks(other_course.weeks)
        
        if not (self_weeks & other_weeks): # 如果周次没有交集，则没有冲突
            return False, None

        # 检查上课时间是否有冲突
        for self_sch in self.schedule_parsed:
            for other_sch in other_course.schedule_parsed:
                # 星期相同
                if self_sch['day'] == other_sch['day']:
                    # 节次有重叠
                    if max(self_sch['start'], other_sch['start']) <= min(self_sch['end'], other_sch['end']):
                        # 周类型不互斥
                        # all vs all, all vs odd/even, odd vs odd, even vs even
                        if (self_sch['week_type'] == 'all' or other_sch['week_type'] == 'all' or
                            self_sch['week_type'] == other_sch['week_type']):
                            
                            # 进一步检查周次类型冲突
                            # 如果都是all，或者其中一个是all，或者两者周类型相同，则可能冲突
                            # 如果一个是单周，一个是双周，则不冲突
                            if not (self_sch['week_type'] == 'odd' and other_sch['week_type'] == 'even') and \
                               not (self_sch['week_type'] == 'even' and other_sch['week_type'] == 'odd'):
                                
                                # 构造冲突详情
                                day_map_reverse = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}
                                conflict_details = {
                                    'type': 'time_conflict',
                                    'with_course_name': other_course.course_name,
                                    'details': f"与 {other_course.course_name} 在周{day_map_reverse.get(self_sch['day'], '')}{self_sch['start']}-{self_sch['end']}节{'(' + self_sch['week_type'] + ')' if self_sch['week_type'] != 'all' else ''} 冲突"
                                }
                                return True, conflict_details
        return False, None