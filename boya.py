from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    element_to_be_clickable,
    invisibility_of_element_located,
    presence_of_element_located,
    presence_of_all_elements_located,
    url_to_be,
)
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
import time
import json

login_url = "https://sso.buaa.edu.cn/login?service=https%3A%2F%2Fbykc.buaa.edu.cn%2Fsystem%2Fhome"
home_url = "https://bykc.buaa.edu.cn/system/home"
course_url = "https://bykc.buaa.edu.cn/system/course-select"
xpath = {
    "学工号输入": "/html/body/div[2]/div/div[3]/div[2]/div[1]/div[1]/div/input",
    "密码输入": "/html/body/div[2]/div/div[3]/div[2]/div[1]/div[3]/div/input",
    "登录按钮": "/html/body/div[2]/div/div[3]/div[2]/div[1]/div[7]/input",
    "我的课程": "/html/body/main/div[1]/aside/div/ul/li[3]/div/div",
    "选择课程": "/html/body/main/div[1]/aside/div/ul/li[3]/div/ul/li[1]",
    "刷新列表": "/html/body/main/div[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[2]/a",
    "稍等片刻": "/html/body/main/div[3]",
    "课程列表": "/html/body/main/div[1]/div/div/div[2]/div[1]/div/div/div/div/div[2]/table/tbody/tr",
    "确定": "/html/body/div[1]/div/div/div[3]/button[2]",
}


def launch_browser(type, path):
    if type.lower() == "chrome":
        return webdriver.Chrome(service=webdriver.ChromeService(path))
    elif type.lower() == "firefox":
        return webdriver.Firefox(service=webdriver.FirefoxService(path))
    elif type.lower() == "edge":
        return webdriver.Edge(service=webdriver.EdgeService(path))
    else:
        raise ValueError("Unsupported browser type")


def login(driver, wait, user_info):
    print(f"[{time.ctime()}] 正在登录...")
    driver.get(login_url)
    driver.switch_to.frame("loginIframe")
    input_box = wait.until(
        presence_of_element_located((By.XPATH, xpath["学工号输入"]))
    )
    input_box.send_keys(user_info["id"])
    input_box = wait.until(
        presence_of_element_located((By.XPATH, xpath["密码输入"]))
    )
    input_box.send_keys(user_info["password"])
    button = wait.until(element_to_be_clickable((By.XPATH, xpath["登录按钮"])))
    button.click()


def navigate_to_course_selection(wait):
    print(f"[{time.ctime()}] 登录成功，进入选课页面")
    try:
        wait.until(url_to_be(home_url))
        driver.refresh()
    except TimeoutException:
        driver.get(home_url)
    menu = wait.until(element_to_be_clickable((By.XPATH, xpath["我的课程"])))
    menu.click()
    menu = wait.until(element_to_be_clickable((By.XPATH, xpath["选择课程"])))
    menu.click()


def resolve_course_xml(course_xml):
    elements = course_xml.find_elements(By.XPATH, ("./td"))
    return {
        "状态": elements[0].find_element(By.XPATH, "./div/span").text,
        "课程名称": elements[1].text,
        "已选人数": int(elements[8].find_element(By.XPATH, "./span[1]").text),
        "课程人数": int(elements[8].find_element(By.XPATH, "./span[3]").text),
        "操作": elements[9].find_elements(By.XPATH, "./a"),
    }


def get_courses_info(wait):
    course_list = wait.until(
        presence_of_all_elements_located((By.XPATH, xpath["课程列表"]))
    )
    return [resolve_course_xml(course_xml) for course_xml in course_list]


def select_course(wait, course_info):
    if course_info["状态"] == "预告":
        print(f"[{time.ctime()}] 课程未开始：{course_info['课程名称']}")
        return False
    elif course_info["状态"] in ["选课结束", "已开课"]:
        print(f"[{time.ctime()}] 选课已截止：{course_info['课程名称']}")
        return True

    print(
        f"[{time.ctime()}] 尝试报名课程：{course_info['课程名称']} ({course_info['状态']}), "
        f"当前人数：{course_info['已选人数']}/{course_info['课程人数']}"
    )

    for button in course_info["操作"]:
        if button.text == "报名课程":
            button.click()
            confirm = wait.until(
                element_to_be_clickable((By.XPATH, xpath["确定"]))
            )
            confirm.click()
            return False
        elif button.text == "退选课程":
            print(f"[{time.ctime()}] 选课成功：{course_info['课程名称']}")
            return True
    return False


def flush_page(wait, wait_time, names):
    while True:
        button = wait.until(
            element_to_be_clickable((By.XPATH, xpath["刷新列表"]))
        )
        button.click()
        wait.until(
            invisibility_of_element_located((By.XPATH, xpath["稍等片刻"]))
        )
        courses = get_courses_info(wait)
        for course in courses:
            if course["课程名称"] in names and select_course(wait, course):
                names.remove(course["课程名称"])

        if not names:
            return
        time.sleep(wait_time)


if __name__ == "__main__":
    config = json.load(open("config.json", "r", encoding="utf-8"))
    driver_type = config["driver"]["type"]
    driver_path = config["driver"]["path"]
    wait_time = config["wait-time"]
    courses = config["courses"]
    user_info = config["account"]

    print(f"[{time.ctime()}] 浏览器启动")
    driver = launch_browser(driver_type, driver_path)
    wait = WebDriverWait(driver, timeout=5)

    login(driver, wait, user_info)

    while True:
        try:
            navigate_to_course_selection(wait)
            flush_page(wait, wait_time, courses)
        except NoSuchWindowException:
            print(f"[{time.ctime()}] 浏览器已关闭")
            exit()
        except Exception:
            print(f"[{time.ctime()}] 发生错误，正在重试...")
            continue
        break

    print(f"[{time.ctime()}] 浏览器关闭")
    driver.quit()
