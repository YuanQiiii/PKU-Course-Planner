$(document).ready(function() {
    const courseColors = {};
    let colorIndex = 0;
    const colors = [
        '#a7d9ff', '#ffb3ba', '#bae1ff', '#baffc9', '#ffffba', '#ffdfba',
        '#c9afff', '#ffc9f2', '#c9ffba', '#ffbaea', '#bac9ff', '#ffbac9'
    ];

    function getCourseColor(courseId) {
        if (!courseColors[courseId]) {
            courseColors[courseId] = colors[colorIndex % colors.length];
            colorIndex++;
        }
        return courseColors[courseId];
    }

    // Function to render schedule
    function renderSchedule(schedule) {
        console.log("renderSchedule called with:", schedule);
        $('.course-block').remove(); // Clear existing courses

        schedule.forEach(course => {
            console.log("[Frontend] Rendering course:", course.course_name, "Parsed Schedule:", course.schedule_parsed); // Add this line
            const courseColor = getCourseColor(course.course_id);
            course.schedule_parsed.forEach(sch => {
                const day = sch.day;
                const start = sch.start;
                const end = sch.end;
                const weekType = sch.week_type;

                // Calculate position and size
                const grid = $('#schedule-grid');
                const headerHeight = grid.find('.grid-header').outerHeight();
                const cellWidth = grid.find('.grid-header').eq(1).outerWidth();
                const cellHeight = grid.find('.grid-cell').eq(0).outerHeight();

                console.log(`Course: ${course.course_name}, Day: ${day}, Start: ${start}, End: ${end}`);
                console.log(`headerHeight: ${headerHeight}, cellWidth: ${cellWidth}, cellHeight: ${cellHeight}`);

                const left = (day * cellWidth) + 'px';
                const top = (start * cellHeight) + headerHeight + 'px';
                const height = ((end - start + 1) * cellHeight) + 'px';
                const width = cellWidth + 'px';

                console.log(`Calculated: left=${left}, top=${top}, height=${height}, width=${width}`);

                const courseBlock = $(`<div class="course-block" 
                                        data-course-id="${course.course_id}"
                                        data-day="${day}"
                                        data-start="${start}"
                                        data-end="${end}"
                                        data-week-type="${weekType}"
                                        style="background-color: ${courseColor}; left: ${left}; top: ${top}; height: ${height}; width: ${width};">
                                        <h6>${course.course_name}</h6>
                                        <small>${course.teacher}</small><br>
                                        <small>${course.schedule_raw}</small>
                                        <button class="close-btn"><i class="fas fa-times"></i></button>
                                    </div>`);
                grid.append(courseBlock);
            });
        });
    }

    // Load initial schedule
    renderSchedule(initialSelectedSchedule);

    // Fetch courses button click handler
    $('#fetch-courses-btn').click(function() {
        const dept = $('#dept-select').val();
        const term = $('#term-select').val();
        const stuType = $('#stu-type-select').val();

        // You might want to send these as query parameters to /api/courses
        // For now, the backend uses setting.json, so this is just a trigger
        $.get('/api/courses', { dept: dept, term: term, stu: stuType }, function(data) {
            const courseList = $('#available-courses-list');
            courseList.empty();
            if (data.length === 0) {
                courseList.append('<p class="text-muted">没有找到课程。</p>');
                return;
            }
            data.forEach(course => {
                const courseItem = $(`<div class="course-list-item">
                                        <h6>${course.course_name} (${course.course_id})</h6>
                                        <small>教师: ${course.teacher} | 学分: ${course.credits}</small><br>
                                        <small>时间: ${course.schedule_raw} | 周次: ${course.weeks}</small>
                                        <button class="btn btn-sm btn-primary add-course-btn" data-course='${JSON.stringify(course)}'>添加</button>
                                    </div>`);
                courseList.append(courseItem);
            });
        }).fail(function(jqXHR, textStatus, errorThrown) {
            Swal.fire('错误', '获取课程失败: ' + jqXHR.responseJSON.error, 'error');
        });
    });

    // Add course button click handler (delegated event)
    $('#available-courses-list').on('click', '.add-course-btn', function() {
        const courseData = $(this).data('course');
        console.log("[Frontend] Course data from button click:", courseData); // Add this line
        $.ajax({
            url: '/api/schedule/add',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(courseData),
            success: function(response) {
                if (response.success) {
                    Swal.fire('成功', '课程已添加！', 'success');
                    $.get('/api/schedule', function(data) {
                        renderSchedule(data);
                    });
                } else {
                    // Handle conflict
                    const conflictInfo = response.conflict_info;
                    Swal.fire({
                        title: '冲突警告',
                        html: `与 <strong>${conflictInfo.with_course_name}</strong> 发生冲突！<br>${conflictInfo.details}`,
                        icon: 'warning',
                        confirmButtonText: '好的'
                    });
                    // Optionally highlight conflicting courses on the grid
                    $(`.course-block[data-course-id="${conflictInfo.with_course_name}"]`).addClass('conflict');
                    // Remove highlight after a few seconds
                    setTimeout(() => {
                        $('.course-block').removeClass('conflict');
                    }, 5000);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                Swal.fire('错误', '添加课程失败: ' + jqXHR.responseJSON.error, 'error');
            }
        });
    });

    // Remove course button click handler (delegated event)
    $('#schedule-grid').on('click', '.course-block .close-btn', function(e) {
        e.stopPropagation(); // Prevent click from bubbling to parent course-block
        const courseBlock = $(this).closest('.course-block');
        const courseId = courseBlock.data('course-id');

        Swal.fire({
            title: '确认删除？',
            text: "您确定要从课表中移除这门课程吗？",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: '是的，删除它！',
            cancelButtonText: '取消'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: '/api/schedule/remove',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ course_id: courseId }),
                    success: function(response) {
                        if (response.success) {
                            Swal.fire('已删除！', '课程已从课表中移除。', 'success');
                            $.get('/api/schedule', function(data) {
                                renderSchedule(data);
                            });
                        }
                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        Swal.fire('错误', '移除课程失败: ' + jqXHR.responseJSON.error, 'error');
                    }
                });
            }
        });
    });

    // Save schedule button click handler
    $('#save-schedule-btn').click(function() {
        $.ajax({
            url: '/api/schedule/save',
            type: 'POST',
            success: function(response) {
                if (response.success) {
                    Swal.fire('保存成功', '课表已保存到本地文件。', 'success');
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                Swal.fire('错误', '保存课表失败: ' + jqXHR.responseJSON.error, 'error');
            }
        });
    });
});