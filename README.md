# PKU Course Planner

## 项目简介

PKU Course Planner 旨在成为一个功能完善的、可视化的个人排课与课程管理助手。核心目标是帮助用户方便地规划自己的学期课表，并能智能识别和预警各类课程冲突（包括上课时间、考试时间），最终提供一个直观、易用的交互界面。

## 功能特性

- **课程信息管理**：从 JSON 文件加载课程数据，并将其结构化为 `Course` 对象。
- **智能冲突检测**：在添加课程时，自动检测与已有课程的时间冲突（包括星期、节次和单双周）。
- **可视化排课**：通过 Web 界面直观展示已选课程的课表。
- **课程管理**：支持添加、移除已选课程。
- **课表保存与加载**：支持将当前课表保存到本地文件，并在启动时自动加载。

## 安装与运行

1.  **克隆项目**：
    ```bash
    git clone <项目仓库地址>
    cd PKU-Course-Planner
    ```

2.  **安装依赖**：
    ```bash
    pip install -r requirements.txt
    ```

3.  **准备课程数据**：
    确保项目根目录下存在 `courses.json` 文件，其中包含课程信息。该文件应为 JSON 格式，包含课程列表。

4.  **运行应用**：
    ```bash
    python app.py
    ```
    应用将在 `http://127.0.0.1:5000/` 运行。

## API 文档

### 获取所有可用课程

-   **URL**: `/api/courses`
-   **方法**: `GET`
-   **参数**:
    -   `dept` (可选): 院系过滤
    -   `term` (可选): 学期过滤
    -   `year` (可选): 学年过滤
-   **响应**: `List[Course]` 对象列表（JSON 格式）

### 获取当前课表

-   **URL**: `/api/schedule`
-   **方法**: `GET`
-   **响应**: `List[Course]` 对象列表（JSON 格式），表示当前已选课程

### 添加课程到课表

-   **URL**: `/api/schedule/add`
-   **方法**: `POST`
-   **请求体**: 包含课程信息的 JSON 对象
-   **响应**:
    -   成功: `{"success": true, "message": "Course added successfully"}`
    -   冲突: `{"success": false, "message": "Conflict detected", "conflict_info": {...}}` (HTTP 409)

### 从课表移除课程

-   **URL**: `/api/schedule/remove`
-   **方法**: `POST`
-   **请求体**: `{"course_id": "课程号"}`
-   **响应**: `{"success": true, "message": "Course removed successfully"}`

### 保存课表

-   **URL**: `/api/schedule/save`
-   **方法**: `POST`
-   **响应**: `{"success": true, "message": "Schedule saved successfully"}`

## 前端界面

前端界面通过 `templates/index.html` 和 `static/js/main.js` 实现。

-   **左侧**: 课程筛选器和可用课程列表。用户可以根据学年、院系等条件筛选课程，并点击“添加”按钮将课程加入课表。
-   **右侧**: 可视化课表网格，以直观的方式展示已选课程的上课时间。当添加课程发生冲突时，会弹出警告并高亮冲突信息。

## 待办事项

请参考 `TODO.md` 文件获取更详细的开发计划和待办事项。
