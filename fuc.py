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
    try:
        # 发送HTTP请求获取图片数据
        response = requests.get(url)
        # 检查响应状态码是否为200，表示请求成功
        response.raise_for_status()
        # 指定保存图片的文件路径
        file_path = 'D:\\验证码.png'
        # 保存图片到指定路径
        with open(file_path, 'wb') as file:
            file.write(response.content)
        # 将图片比例放大5倍
        img = Image.open(file_path)
        img = img.resize((img.width * 5, img.height * 5))
        img.save(file_path)
        # 在Windows上调用默认的图片查看应用程序打开图片
        os.system(f'start {file_path}')
    except requests.exceptions.RequestException as e:
        print("ERROR: 获取验证码失败:", e)
        return None
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
        'redirect': '',
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
        print("ERROR: 登录请求异常:", e)
        return False
    except json.JSONDecodeError as e:
        print("ERROR: JSON解析错误:", e)
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

    try:
        # 发送请求
        response = requests.get(url, headers=headers, cookies=cookie)
        response.raise_for_status()
        # 解析HTML
        html = response.text
        result = {}
        user_name = re.findall(r'<div class="name">(.+?)</div>', html)[0]
        result['user_name'] = user_name
        result['course_list'] = []
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', class_='user-course')
        course_divs = div.find_all('div', class_='item')

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
    except requests.exceptions.RequestException as e:
        print("ERROR: 获取课程列表失败:", e)
        return None
    except (IndexError, AttributeError) as e:
        print("ERROR: 解析课程列表失败:", e)
        return None


# 获取所有课程的nodeid
def getNodeIds(host, courseId, cookie):
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

    try:
        response = requests.get(url, headers=headers).text
        nodeid = response.split("nodeId=")[1].split("\"")[0]
        url = host + "/user/node?nodeId=" + nodeid
        response = requests.get(url, headers=headers).text
        node_ids = re.findall(r'nodeId=(\d+)', response)
        node_ids = list(set(node_ids))
        node_ids.sort()
        return node_ids
    except requests.exceptions.RequestException as e:
        print("ERROR: 获取节点ID失败:", e)
        return []
    except IndexError as e:
        print("ERROR: 解析节点ID失败:", e)
        return []


# 获取nodeid小课程最新的评论
def getNewComment(host, courseId, nodeId, cookie):
    cookie = "; ".join([f"{item}={cookie[item]}" for item in cookie])
    url = host + '/user/node_discuss/reply?courseId=' + courseId + '&nodeId=' + nodeId + '&_=' + str(
        int(time.time() * 1000))
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh-HK;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Referer': f"{host}/user/node?nodeId={nodeId}",
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_data = json.loads(response.text)
        content = json_data['list'][0]['content']
        content = re.sub(r'<[^>]+>', '', content)
        return content
    except requests.exceptions.RequestException as e:
        print("ERROR: 获取最新评论失败，使用默认值'谢谢老师':", e)
        return "谢谢老师"
    except (IndexError, KeyError) as e:
        print("ERROR: 解析最新评论失败，使用默认值'谢谢老师':", e)
        return "谢谢老师"


# 发送评论
def sendComment(host, courseId, node_id, content, cookie):
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/116.0.0.0 Safari/537.36',
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

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("ERROR: 发送评论失败:", e)
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print("ERROR: 解析发送评论结果失败:", e)
        return None
