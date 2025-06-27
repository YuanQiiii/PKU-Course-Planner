# TODO

## 整体规划

将当前项目从一个课程信息爬取工具，升级为一个功能完善的、可视化的个人排课与课程管理助手。核心目标是帮助用户方便地规划自己的学期课表，并能智能识别和预警各类课程冲突（包括上课时间、考试时间），最终提供一个直观、易用的交互界面。

## 具体计划

### 第一阶段：后端重构与核心功能实现

#### 1. **模块化课程信息 (`course.py` 的设计与实现)**

**目标:** 将目前爬取到的零散课程信息，封装成结构化的 `Course` 对象，为后续的排课和冲突检测提供坚实的数据基础。

**实现细节:**

* **创建 `course.py` 模块，并定义 `Course` 类。**
  * **类的属性:**
    * `course_id` (str): 课程号 (e.g., '00431010')
    * `course_name` (str): 课程名
    * `course_name_en` (str): 课程英文名
    * `teacher` (str): 授课教师
    * `credits` (str): 参考学分
    * `class_id` (str): 班号
    * `semester` (str): 开课学期 (e.g., '24-25 第一学期')
    * `department` (str): 开课院系
    * `schedule_raw` (str): 原始上课时间字符串 (e.g., "周一3-4; 周三5-6(双)")
    * `weeks` (str): 起止周 (e.g., "1-16")
    * `schedule_parsed` (list): 解析后的上课时间列表，格式见下方。
    * `exam_time` (str): 考试时间 (待扩展)
    * `note` (str): 备注信息

  * **类的方法:**
    * `__init__(self, course_dict)`: 构造函数，接收爬取到的课程字典作为参数，并在内部调用 `self.parse_schedule()`。
    * `to_dict(self)`: 将 `Course` 对象序列化为字典，方便前端交互。
    * `has_conflict(self, other_course)`: **核心冲突检测方法**。接收另一个 `Course` 对象，返回布尔值。
      * **冲突条件**: 两门课程的 `weeks` 有交集，**并且** `schedule_parsed` 中存在任意两个时间段满足：
                1. 星期 (`day`) 相同。
                2. 节次有重叠。
                3. 周类型 (`week_type`) 不互斥 (即 `all` vs `all`, `all` vs `odd/even`, `odd` vs `odd`, `even` vs `even`)。
    * `parse_schedule(self)`: **私有的核心解析方法**。
            1. **预处理**: 将 `schedule_raw` 中的全角符号转为半角，并用分号 `;` 切分出独立的时间段。
            2. **正则解析**: 对每个时间段，使用正则表达式 `re.search(r"周([一二三四五六日])(\d+)-?(\d+)?(?:\((单|双)\))?", segment)` 捕获星期、开始节次、结束节次（可选）和单双周（可选）。
            3. **结构化存储**: 将解析出的信息转换为字典 `{'day': int, 'start': int, 'end': int, 'week_type': str}` 并存入 `self.schedule_parsed` 列表。
                *`day`: "一" 至 "日" 映射为 `1` 至 `7`。
                * `end`: 如果正则没有匹配到结束节次（如“周三3”），则 `end` 等于 `start`。
                * `week_type`: 值为 `'odd'` (单), `'even'` (双), 或 `'all'` (无标注)。

* **重构 `main.py`:**
  * 将爬虫逻辑完整地移入一个新的 `crawler.py` 模块。
  * `crawler.py` 的爬取函数执行后，应返回一个 `List[Course]` 对象列表。

#### 2. **排课与冲突检测模块 (`scheduler.py` 的设计与实现)**

**目标:** 创建一个核心调度器，用于管理用户已选课程，并在添加新课程时进行实时冲突检测。

**实现细节:**

* **创建 `scheduler.py` 模块，并定义 `Scheduler` 类。**
  * **类的属性:**
    * `selected_courses` (List[Course]): 存储用户已选的 `Course` 对象。
  * **类的方法:**
    * `add_course(self, course_to_add)`:
            1. 遍历 `self.selected_courses`，调用 `course_to_add.has_conflict(existing_course)`。
            2. 如果检测到冲突，返回 `(False, conflict_info)`，其中 `conflict_info` 是描述冲突详情的字典，如 `{'type': 'time_conflict', 'with_course_name': '大学物理', 'details': '周三5-6节(双)'}`。
            3. 若无冲突，则将课程添加进 `self.selected_courses` 并返回 `(True, None)`。
    * `remove_course(self, course_id)`: 根据课程号移除已选课程。
    * `get_schedule(self)`: 返回所有已选课程的列表（每个课程都是字典格式）。
    * `save_to_file(self, filepath)` 和 `load_from_file(self, filepath)`: 实现课表的本地保存和加载。

### 第二阶段：Web 应用开发与可视化

#### 3. **Flask Web 应用搭建与可视化前端**

**目标:** 将后端功能通过 Web 框架暴露为 API，并构建一个直观、可交互的前端页面。

**实现细节:**

* **创建 `app.py` (Flask 主应用):**
  * **API Endpoints:**
    * `GET /api/courses`: 接收 `year`, `dept` 等参数，调用 `crawler` 模块获取课程数据，返回 `List[Dict]`。
    * `GET /api/schedule`: 调用 `Scheduler` 实例的 `get_schedule()` 方法，返回当前用户的课表。
    * `POST /api/schedule/add`: 接收课程信息的 JSON，调用 `Scheduler.add_course()`，返回操作结果。
    * `POST /api/schedule/remove`: 接收 `course_id`，调用 `Scheduler.remove_course()`。
    * `POST /api/schedule/save`: 触发课表的本地保存。
  * **页面路由 `/`**: 渲染主页面 `index.html`。

* **前端实现 (`templates/index.html` 和 `static/js/main.js`):**
  * **界面布局**:
    * **左侧**: 课程筛选器（学年、院系）和一个“获取课程”按钮。下方是获取到的课程列表，每项都包含详细信息和“添加”按钮。
    * **右侧**: 一个 7x14 的 HTML `<table>` 作为可视化课表网格。
  * **核心交互逻辑**:
        1. **加载**: 页面加载时，请求 `/api/schedule` 接口，将已保存的课程渲染到右侧课表上。
        2. **渲染课程格**:
            *每个课程在课表上用一个 `div` 表示，绝对定位于正确的星期和节次。
            * 为每个课程块分配一个独特的背景色，使其易于区分。
            *`div` 内显示课程名、教师和地点。
        3. **添加课程**: 点击“添加”按钮后，向 `/api/schedule/add` 发送请求。
            * **若成功**: 在右侧课表动态生成新的课程格。
            * **若失败**: 弹出一个明确的警告框（例如使用 `SweetAlert` 库），高亮显示冲突的课程，并提示“与【课程A】在【周三5-6节】发生冲突”。
        4. **移除课程**: 在已选课程上有“移除”按钮，点击后调用移除 API，并从课表视图中删除对应的 `div`。
