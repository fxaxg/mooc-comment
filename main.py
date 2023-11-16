# 本文件用于登陆英华课堂，获取课程列表，选择课程，复制最新评论，发送评论
import json
import time
import fuc

# 读取当前目录下的config.json 中的"host"的值
host = ''
# Open the config.json file
with open('config.json', 'r') as file:
    # Load the contents of the file
    config = json.load(file)

def main():
    global course_id
    msg = """

  /$$$$$$  /$$                           /$$$$$$$$           /$$                 /$$
 /$$__  $$| $$                          |__  $$__/          | $$                |__/
| $$  \__/| $$$$$$$   /$$$$$$  /$$$$$$$    | $$    /$$   /$$| $$$$$$$   /$$$$$$  /$$
| $$      | $$__  $$ /$$__  $$| $$__  $$   | $$   | $$  | $$| $$__  $$ |____  $$| $$
| $$      | $$  \ $$| $$$$$$$$| $$  \ $$   | $$   | $$  | $$| $$  \ $$  /$$$$$$$| $$
| $$    $$| $$  | $$| $$_____/| $$  | $$   | $$   | $$  | $$| $$  | $$ /$$__  $$| $$
|  $$$$$$/| $$  | $$|  $$$$$$$| $$  | $$   | $$   |  $$$$$$/| $$$$$$$/|  $$$$$$$| $$
 \______/ |__/  |__/ \_______/|__/  |__/   |__/    \______/ |_______/  \_______/|__/
                                                                                    
                                                                                    
                                                                                                                                     
    欢迎使用英华课堂自动评论脚本 v1.0
    By：Chentubai
    Email：chentubai@qq.com
-----------------------------------
"""

    print(msg)
    user = input("> 请输入学号：")
    pwd = input("> 请输入密码：")
    print("> [信息]：正在获取验证码...")
    time.sleep(2)
    # 获取验证码图片并打开，返回cookie
    cookie = fuc.getVerificationCode(host)
    cookie = fuc.cookie2dict(cookie)  # 将字符串的cookie转换为字典
    code = input("请输入验证码：")
    print("> [信息]：正在登陆英华课堂...")

    # 暂停2秒
    time.sleep(2)

    # 登陆英华课堂
    login_result = fuc.login(host, user, pwd, code, cookie)

    if login_result.get('status'):
        print("> [信息]：登陆成功！")
    else:
        print("> [错误]：登陆失败：" + login_result.get('msg'))
        print("按回车键退出...")
        input()  # 等待用户输入任意字符
        exit()

    # 获取课程列表
    course_info = fuc.getCourseList(host, cookie)
    print("-----------------------------------")
    print("> [信息]：欢迎你，" + course_info['user_name'] + "！")
    time.sleep(2)
    print("> [信息]：正在获取课程列表...")
    time.sleep(1)
    print("> [信息]：课程列表获取成功！")
    print("-----------------------------------")
    print("> 你的课程列表：")

    for course_item in course_info['course_list']:
        time.sleep(0.2)
        print(f" [{course_item['index']}]、{course_item['course_name']}")

    # 获取用户输入
    try:
        course_index = int(input("> 请输入课程编号："))

        # 检查输入的编号是否在有效范围内
        if 0 <= course_index <= len(course_info["course_list"]):
            selected_course = course_info["course_list"][course_index]
            course_id = selected_course['course_id']
        else:
            print("输入的编号不在课程列表范围内，请重新输入。")
    except ValueError:
        print("请输入有效的数字。")

    print("> [信息]：开始刷评论...")
    # 获取课程所有的nodeid（课程的小节）
    node_ids = fuc.getNodeIds(host, course_id, cookie)
    i = 1
    for node_id in node_ids:
        # 获取最新的评论
        content = fuc.getNewComment(host, course_id, node_id, cookie)

        msg = '> [信息]：第' + str(i) + '条评论：' + content
        print(msg)

        # 发送评论

        result = fuc.sendComment(host, course_id, node_id, content, cookie)

        try:
            if result['status']:
                print('> [信息]：评论成功！')
            else:
                print('> [错误]：评论失败：' + result['msg'])
        except:  # 如果没有status字段，说明评论成功
            print('> ' + result)

        # 延迟5秒时间

        time.sleep(3)

        i += 1

    print("按回车键退出...")
    input()  # 等待用户输入任意字符


if __name__ == '__main__':
    main()
