import os
import re
import time
from PIL import Image
import requests
import json

from bs4 import BeautifulSoup


# 获取验证码图片并打开，返回cookie
def getVerificationCode(host):
    url = host + '/service/code?r=' + str(int(time.time() * 1000))
    # 发送HTTP请求获取图片数据
    response = requests.get(url)
    # 检查响应状态码是否为200，表示请求成功
    if response.status_code == 200:
        # 指定保存图片的文件路径
        file_path = 'D:\\验证码.png'

        # 保存图片到指定路径
        with open(file_path, 'wb') as file:
            file.write(response.content)

        # 将图片比例放大5倍
        img = Image.open(file_path)
        img = img.resize((img.width * 5, img.height * 5), Image.ANTIALIAS)
        img.save(file_path)

        # print(f'图片已保存到 {file_path}')

        # 在Windows上调用默认的图片查看应用程序打开图片
        os.system(f'start {file_path}')
    else:
        # print('无法获取图片')
        pass

    # 获取cookie
    cookie = response.headers['Set-Cookie']
    return cookie


# 将字符串的cookie转换为字典
def cookie2dict(cookie):
    # 先分割;符号
    cookie = cookie.split(';')
    cookie_dict = {}
    for item in cookie:
        # 再分割=符号
        cookie_dict[item.split('=')[0]] = item.split('=')[1]
    return cookie_dict


# 登陆英华课堂
def login(host, user, pwd, code, cookie):
    url = host + '/user/login'
    h_host = host.split('//')[1]
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': h_host,
        'Origin': host,
        'Referer': host + '/user/login',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/119.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
    }

    data = {
        'username': user,
        'password': pwd,
        'code': code,
        'redirect': '',  # 修正此处的键值对
    }

    try:
        # 发送登录请求
        response = requests.post(url, headers=headers, data=data, cookies=cookie)
        response.raise_for_status()  # 检查请求是否成功

        # 尝试解析JSON
        json_data = json.loads(response.text)
        # 转成bool类型
        return json_data
    except requests.exceptions.RequestException as e:
        print("ERROR:请求异常:", e)
        return False
    except json.JSONDecodeError as e:
        print("ERROR:JSON解析错误:", e)
        return False


# 获取课程列表
def getCourseList(host, cookie):
    url = host + '/user'
    h_host = host.split('//')[1]
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': h_host,
        'Referer': 'https://zswxy.yinghuaonline.com/user/login',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/119.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    # 发送请求
    response = requests.get(url, headers=headers, cookies=cookie)

    # 解析HTML
    html = response.text
    # 初始化返回的
    result = {}
    user_name = re.findall(r'<div class="name">(.+?)</div>', html)[0]
    result['user_name'] = user_name
    result['course_list'] = []
    # 假设html变量包含了您的HTML代码
    soup = BeautifulSoup(html, 'html.parser')

    # 从<div class="user-course">开始
    div = soup.find('div', class_='user-course')

    # 查找所有包含课程信息的div元素
    course_divs = div.find_all('div', class_='item')

    # 遍历每个课程div元素，提取courseId和课程名称
    # 设置一个计数器，用来给课程编号
    for index, course_div in enumerate(course_divs):
        a_tag = course_div.find('a', href=True)
        course_id = a_tag['href'].split('=')[-1]

        course_name_div = course_div.find('div', class_='name')
        course_name = course_name_div.get_text(strip=True)

        result['course_list'].append({
            'index': index,
            'course_id': course_id,
            'course_name': course_name
        })

    return result


# 获取所有课程的nodeid
def getNodeIds(host, courseId, cookie):
    # 将cookie拼接为字符串
    cookie = "; ".join([f"{item}={cookie[item]}" for item in cookie])
    url = f"{host}/user/course?courseId={courseId}"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh-HK;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Referer': f"{host}/user/index",
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    response = requests.get(url, headers=headers).text

    # <div class="ncoursecon-intro">
    #         <div class="name">沟通与写作</div>
    #         <div class="note">
    #             <div class="item">主讲教师：<span> 鲁老师</span></div>
    #         </div>
    # #     </div>
    # print("学生姓名：" + re.findall(r'<div class="name">(.+?)</div>', response)[0])
    # print("课程名称：" + re.findall(r'<div class="name">(.+?)</div>', response)[1])
    print("--------------------")

    # 获取第一节课nodeid

    nodeid = response.split("nodeId=")[1].split("\"")[0]

    # 根据第一节课nodeid，获取本大课的所有课程的nodeid

    url = host + "/user/node?nodeId=" + nodeid

    response = requests.get(url, headers=headers).text

    # 使用循环获取所有课程的nodeid

    node_ids = re.findall(r'nodeId=(\d+)', response)

    # 去重

    node_ids = list(set(node_ids))

    # 排序，从小到大

    node_ids.sort()

    return node_ids


# 获取nodeid小课程最新的评论
def getNewComment(host, courseId, nodeId, cookie):
    # 将cookie拼接为字符串
    cookie = "; ".join([f"{item}={cookie[item]}" for item in cookie])
    url = host + '/user/node_discuss/reply?courseId=' + courseId + '&nodeId=' + nodeId + '&_=' + str(
        int(time.time() * 1000))
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh-HK;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Referer': 'https://zswxy.yinghuaonline.com/user/node?nodeId=1446121',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    response = requests.get(url, headers=headers)

    # 解析json

    json_data = json.loads(response.text)

    # 获取 list 中的 第一个对象中的 content
    try:
        content = json_data['list'][0]['content']
    except IndexError:
        content = "谢谢老师"
        print("获取评论失败，使用默认评论：谢谢老师")

    # 去除html标签

    content = re.sub(r'<[^>]+>', '', content)

    return content


# 发送评论
def sendComment(host, courseId, node_id, content, cookie):
    # 将cookie拼接为字符串
    cookie = "; ".join([f"{item}={cookie[item]}" for item in cookie])
    url = f'{host}/user/node_discuss/add_reply'

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh-HK;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookie,
        'Origin': host,
        'Referer': f'{host}/user/node?courseId={courseId}&chapterId=&nodeId={node_id}',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    data = {
        'content': content,
        'images': '',
        'files': '',
        'courseId': courseId,
        'nodeId': node_id
    }

    # 下方

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        try:
            return response.json()
        except IOError:
            print("返回值不是json")
    else:
        return None

    return None

