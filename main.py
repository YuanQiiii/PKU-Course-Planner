from pypinyin import pinyin, Style
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import re
import json
import pandas as pd

with open("setting.json", "r", encoding="utf-8") as f:
    loaded_data = json.load(f)  


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://iaaa.pku.edu.cn/iaaa/oauth.jsp?appID=portal2017&appName=%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E6%A0%A1%E5%86%85%E4%BF%A1%E6%81%AF%E9%97%A8%E6%88%B7%E6%96%B0%E7%89%88&redirectUrl=https%3A%2F%2Fportal.pku.edu.cn%2Fportal2017%2FssoLogin.do")
wait = WebDriverWait(driver, 10)

username_field = wait.until(EC.presence_of_element_located((By.ID, 'user_name'))) 
password_field = wait.until(EC.presence_of_element_located((By.ID, 'password')))  
username_field.send_keys(loaded_data["username"])  
password_field.send_keys(loaded_data["password"])  
password_field.send_keys(Keys.RETURN)

login_link = wait.until(EC.presence_of_element_located((By.ID, 'courseQuery')))
login_link.click()
time.sleep(2)  
driver.switch_to.window(driver.window_handles[-1])  

year_input = wait.until(EC.visibility_of_element_located(
    (By.CSS_SELECTOR, 'input[ng-model="year"]')
))

all_data = []

for term in loaded_data["year"]:
    year_input.clear()
    year_input.send_keys(term)
    time.sleep(1)
    
    dept_select = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select.cell-sel[ng-model='dept']"))
    )
    all_depts = dept_select.find_elements(By.TAG_NAME, "option")[1:]

    # 如果 loaded_data["dept"] 为空，则遍历所有院系, 否则只遍历指定院系
    for dept in all_depts:
        if loaded_data["dept"] and dept.text not in loaded_data["dept"]:
            continue
        dept_name = dept.text
        dept.click()
        time.sleep(1) 
        table_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select.cell-sel[ng-model='tableType']"))
        )
        all_tables = table_select.find_elements(By.TAG_NAME, "option")[1:]
        # 如果 loaded_data["stu"] 为空，则遍历所有表格, 否则只遍历指定表格
        for table in all_tables:
            if loaded_data["stu"] and table.text not in loaded_data["stu"]:
                continue
            table_name = table.text
            table.click()
            time.sleep(1)
            term_select = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.cell-sel[ng-model='term']"))
            )
            all_terms = term_select.find_elements(By.TAG_NAME, "option")[1:]
            # 如果 loaded_data["term"] 为空，则遍历所有内部学期, 否则只遍历指定内部学期
            for inner_term in all_terms:
                if loaded_data["term"] and inner_term.text not in loaded_data["term"]:
                    continue
                inner_term_name = inner_term.text
                inner_term.click()
                time.sleep(1)
                
                # 点击查询按钮
                search_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input.cell-btn[ng-click='retrCourseTable()']"))
                )
                search_button.click()
                time.sleep(1)
                
                # 等待表格加载完成
                try:
                    table_element = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table.row-border-table"))
                    )
                except TimeoutException:
                    continue  # 没有表格时跳过

                # 立即将元素转换为稳定的文本数据结构
                rows = table_element.find_elements(By.TAG_NAME, "tr")
                table_data = []
                for row in rows[1:]:  # 跳过表头
                    cols = row.find_elements(By.TAG_NAME, "td")
                    # 立即提取文本到列表（关键修改）
                    table_data.append([col.text for col in cols])  # 此时元素仍有效

                # 处理已缓存的数据
                for col_texts in table_data:
                    course_data = {
                        "学年学期": term,
                        "院系": dept_name,
                        "表格类型": table_name,
                        "内部学期": inner_term_name,
                        "课程名": col_texts[0] if len(col_texts) > 0 else "",
                        "课程类别": col_texts[1] if len(col_texts) > 1 else "",
                        "参考学分": col_texts[2] if len(col_texts) > 2 else "",
                        "班号": col_texts[3] if len(col_texts) > 3 else "",
                        "授课教师": col_texts[4] if len(col_texts) > 4 else "",
                        "起止周": col_texts[5] if len(col_texts) > 5 else "",
                        "上课时间": col_texts[6] if len(col_texts) > 6 else "",
                        "备注": col_texts[7] if len(col_texts) > 7 else ""
                    }
                    all_data.append(course_data)
                    
df = pd.DataFrame(all_data)

df.to_excel("课程数据汇总.xlsx", index=False)

print("数据收集完成，已保存到'课程数据汇总.xlsx'")