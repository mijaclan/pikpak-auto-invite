# coding:utf-8
import constants
import hashlib
import json
import poplib
import random
import re
import string
import time
import uuid
from utils import imgSecret
from email.header import decode_header
from email.parser import Parser

import yaml
from bs4 import BeautifulSoup


def item_compare(img_list, mode_list):
    score = 0
    rank = 0
    for i in range(3):
        for j in range(3):
            if img_list[i][j] != mode_list[i][j]:
                score += 1
    # print(core)
    if score == 2:
        rank += 1
    return rank


def list_compare(frames):
    score_list = []
    flag = 0
    for frame in frames:
        img_list = frame["matrix"]
        scores = 0
        for mode_frame in frames:
            mode_list = mode_frame["matrix"]
            one_score = item_compare(img_list, mode_list)
            scores += one_score
        score_list.append(scores)
        flag += 1
    # print(score_list)
    for i in range(12):
        if score_list[i] == 11:
            print("Currently verify the correct serial number of the image：", i)
            return i


# 请求参数信息预处理
# 设置请求头基本信息
basicRequestHeaders_1 = constants.headersOne
basicRequestHeaders_2 = constants.headersTow

# UA表，随机信息采集
uaList = constants.uaList

# 获取UA
def get_User_Agent(client_id, device_id, ua_key, timestamp, phoneModel, phoneBuilder, version):
    UA = "ANDROID-com.pikcloud.pikpak/" + version +" protocolversion/200 accesstype/ clientid/" + client_id + " clientversion/" + version+" action_type/ networktype/WIFI sessionid/ deviceid/" + device_id + " providername/NONE devicesign/div101." + ua_key + " refresh_token/ sdkversion/1.1.0.110000 datetime/" + timestamp + " usrno/ appname/android-com.pikcloud.pikpak session_origin/ grant_type/ appid/ clientip/ devicename/" + phoneBuilder.capitalize() + "_" + phoneModel.capitalize() + " osversion/13 platformversion/10 accessmode/ devicemodel/" + phoneModel
    return UA


# 获取ua
def get_user_agent():
    tmp1 = random.randrange(90, 120)
    tmp2 = random.randrange(5200, 5500)
    tmp3 = random.randrange(90, 180)
    tmp_version = str(tmp1) + ".0." + str(tmp2) + "." + str(tmp3)
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' + tmp_version + ' Safari/537.36 '
    print(ua)
    return ua


# md5加密算法
def get_hash(str):
    obj = hashlib.md5()
    obj.update(str.encode("utf-8"))
    result = obj.hexdigest()
    return result


# 获取captcha_sign
def get_sign(orgin_str, version):
    salts = constants.salts
    salt_value = []

    for salt in salts:
        if salt["version"] == version:
            salt_value = salt["value"]
            break

    for salt in salt_value:
        if len(salt) > 0:
           temp = orgin_str + salt["salt"]
        orgin_str = get_hash(temp)


    print("Sign：", orgin_str)
    return orgin_str


def get_ua_key(device_id):
    rank_1 = hashlib.sha1((device_id + "com.pikcloud.pikpak1appkey").encode("utf-8")).hexdigest()
    rank_2 = get_hash(rank_1)
    return device_id + rank_2


# 邮箱接口函数，需自行配置
# 自定义邮箱接口，可配置自己的邮箱API接口实现自动化
def get_email():
    # 手动输入
    return input("请输入接收验证码的邮箱：")

def get_email_auto():
    # 自动生成
    # https://tempmail.plus/
    domain_list = ['mailto.plus', 'fexpost.com', 'fexbox.org', 'mailbox.in.ua', 'rover.info', 'chitthi.in', 'fextemp.com', 'any.pink', 'merepost.com']
    domain = random.choice(domain_list)
    # 随机新邮箱
    prefix = ''.join(random.choices(string.ascii_lowercase, k=6))
    email = f"{prefix}@{domain}"
    return email

# 解析邮件内容
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


def extract_h2_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    h2_tag = soup.find('h2')
    if h2_tag:
        return h2_tag.get_text()
    else:
        return None

# 接收验证码接口，可配置自己的邮箱API接口实现自动化
def get_verification_code():
    # 手动输入验证码
    return input("请输入接收到的验证码：")

def get_verification_code_auto(email):
    import requests
    retries = 1
    while retries < 20:
        print(f"邮件读取次数：{retries}")
        response = requests.get(f'https://tempmail.plus/api/mails?email={email}&first_id=0&epin=')
        data = response.json()
        if data.get("mail_list"):
            mail_id = data["mail_list"][0]["mail_id"]
            if mail_id != '':
                # 获取邮件id，再次请求
                mail_page = requests.get(f'https://tempmail.plus/api/mails/{mail_id}?email={email}&epin=')
                line_str = mail_page.json().get("text")
                return re.search(r'\n(\d+)\n', line_str).group(1)
            else:
                continue
        time.sleep(1)
        retries += 1
    input("Tempmail网站邮件读取失败，按任意键退出程序！")
    exit(0)

# 全部网络请求
# 初始化人机验证网页
# url,captcha_token,expires_in
def part2(client_id, captcha_token, device_id, captcha_sign, email, timestamp, User_Agent, version):
    import requests

    url = "https://user.mypikpak.com/v1/shield/captcha/init"

    querystring = {"client_id": client_id}

    payload = {
        "action": "POST:/v1/auth/verification",
        "captcha_token": captcha_token,
        "client_id": client_id,
        "device_id": device_id,
        "meta": {
            "captcha_sign": "1." + captcha_sign,
            "user_id": "",
            "package_name": "com.pikcloud.pikpak",
            # "client_version": "1.38.0",
            "client_version": version,
            "email": email,
            "timestamp": timestamp
        },
        "redirect_uri": "xlaccsdk01://xbase.cloud/callback?state=harbor"
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 获取图片列表
# pid,traceid,frames,result
def part3(device_id, user_agent, referer):
    import requests

    url = "https://user.mypikpak.com/pzzl/gen"

    querystring = {"deviceid": device_id, "traceid": ""}

    headers = {
        "Host": "user.mypikpak.com",
        "accept": "application/json, text/plain, */*",
        "user-agent": user_agent,
        "referer": referer,
    }
    headers.update(basicRequestHeaders_2)

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 验证图片序号
# result
def part4(pid, device_id, trace_id, f, n, p, a, c, referer, user_agent):
    import requests

    url = "https://user.mypikpak.com/pzzl/verify"

    querystring = {"pid": pid,
                   "deviceid": device_id, "traceid": trace_id, "f": f,
                   "n": n, "p": p, "a": a, "c": c}

    headers = {
        "Host": "user.mypikpak.com",
        "accept": "application/json, text/plain, */*",
        "user-agent": user_agent,
        "referer": referer,
    }
    headers.update(basicRequestHeaders_2)

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 发送验证码
# code,captcha_token,expires_in
def part5(device_id, captcha_token, pid, trace_id, user_agent, referer):
    import requests

    url = "https://user.mypikpak.com/credit/v1/report"

    querystring = {"deviceid": device_id,
                   "captcha_token": captcha_token,
                   "type": "pzzlSlider", "result": "0", "data": pid,
                   "traceid": trace_id}

    headers = {
        "Host": "user.mypikpak.com",
        "accept": "application/json, text/plain, */*",
        "user-agent": user_agent,
        "referer": referer,
    }
    headers.update(basicRequestHeaders_2)
    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 验证验证码1
# verification_id,expires_in,slected_channel
def part6(client_id, captcha_token, email, device_id, User_Agent):
    import requests

    url = "https://user.mypikpak.com/v1/auth/verification"

    querystring = {"client_id": client_id}

    payload = {
        "captcha_token": captcha_token,
        "email": email,
        "locale": "zh-CN",
        "target": "ANY",
        "client_id": client_id
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 验证验证码2
# verification_token,expires_in
def part8(client_id, verification_id, verification_code, device_id, User_Agent):
    import requests

    url = "https://user.mypikpak.com/v1/auth/verification/verify"

    querystring = {"client_id": client_id}

    payload = {
        "client_id": client_id,
        "verification_id": verification_id,
        "verification_code": verification_code
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 安全验证
# captcha_token,expires_in
def part8_1(client_id, captcha_token, device_id, captcha_sign, email, timestamp, User_Agent, version):
    import requests

    url = "https://user.mypikpak.com/v1/shield/captcha/init"

    querystring = {"client_id": client_id}

    payload = {
        "action": "POST:/v1/auth/signup",
        "captcha_token": captcha_token,
        "client_id": client_id,
        "device_id": device_id,
        "meta": {
            "captcha_sign": "1." + captcha_sign,
            "user_id": "",
            "package_name": "com.pikcloud.pikpak",
            # "client_version": "1.38.0",
            "client_version": version,
            "email": email,
            "timestamp": timestamp
        },
        "redirect_uri": "xlaccsdk01://xbase.cloud/callback?state=harbor"
    }
    headers = {
        "Host": "user.mypikpak.com",
        "x-device-id": device_id,
        "user-agent": User_Agent,
        "accept-language": "zh",
        "content-type": "application/json",
        "accept-encoding": "gzip"
    }

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 注册账号
# access_token,expires_in,sub
def part9(client_id, captcha_token, client_secret, email, name, password, verification_token, device_id, User_Agent):
    import requests

    url = "https://user.mypikpak.com/v1/auth/signup"

    querystring = {"client_id": client_id}

    payload = {
        "captcha_token": captcha_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "email": email,
        "name": name,
        "password": password,
        "verification_token": verification_token
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


# 安全验证
# captcha_token,expires_in
def part10(client_id, captcha_token, device_id, captcha_sign, user_id, timestamp, User_Agent, version):
    import requests

    url = "https://user.mypikpak.com/v1/shield/captcha/init"

    querystring = {"client_id": client_id}

    payload = {
        "action": "POST:/vip/v1/activity/invite",
        "captcha_token": captcha_token,
        "client_id": client_id,
        "device_id": device_id,
        "meta": {
            "captcha_sign": "1." + captcha_sign,
            "user_id": user_id,
            "package_name": "com.pikcloud.pikpak",
            # "client_version": "1.38.0",
            "client_version": version,
            "timestamp": timestamp
        },
        "redirect_uri": "xlaccsdk01://xbase.cloud/callback?state=harbor"
    }
    headers = {
        "X-Device-Id": device_id,
        "User-Agent": User_Agent,
    }
    headers.update(basicRequestHeaders_1)

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    print(response.text)
    return json.loads(response.text)


def one_invite(user_id, phoneModel, phoneBuilder, invite_code, captcha_token, device_id, access_token, User_Agent, version):
    import requests

    url = "https://api-drive.mypikpak.com/vip/v1/activity/invite"

    payload = {
        "data": {
            "sdk_int": "33",
            "uuid": device_id,
            "userType": "1",
            "userid": user_id,
            "userSub": "",
            "product_flavor_name": "cha",
            "language_system": "zh-CN",
            "language_app": "zh-CN",
            "build_version_release": "13",
            "phoneModel": phoneModel,
            "build_manufacturer": phoneBuilder,
            "build_sdk_int": "33",
            "channel": "official",
            "versionCode": "10150",
            # "versionName": "1.38.0",
            "versionName": version,
            "installFrom": "other",
            "country": "PL"
        },
        "apk_extra": {"channel": "official"}
    }
    headers = {
        "Host": "api-drive.mypikpak.com",
        "authorization": "Bearer " + access_token,
        "product_flavor_name": "cha",
        "x-captcha-token": captcha_token,
        "x-client-version-code": "10150",
        "x-device-id": device_id,
        "user-agent": User_Agent,
        "country": "PL",
        "accept-language": "zh-CN",
        "x-peer-id": device_id,
        "x-user-region": "2",
        "x-system-language": "zh-CN",
        "x-alt-capability": "3",
        "accept-encoding": "gzip",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


# 邀请码填写
def part_invite(user_id, phoneModel, phoneBuilder, invite_code, captcha_token, device_id, access_token, User_Agent):
    import requests

    url = "https://api-drive.mypikpak.com/vip/v1/order/activation-code"

    payload = {"activation_code": invite_code}
    headers = {
        "Host": "api-drive.mypikpak.com",
        "authorization": "Bearer " + access_token,
        "product_flavor_name": "cha",
        "x-captcha-token": captcha_token,
        "x-client-version-code": "10150",
        "x-device-id": device_id,
        "user-agent": User_Agent,
        "country": "DK",
        "accept-language": "zh-CN",
        "x-peer-id": device_id,
        "x-user-region": "2",
        "x-system-language": "zh-CN",
        "x-alt-capability": "3",
        "content-length": "30",
        "accept-encoding": "gzip",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


def part11(user_id, phoneModel, phoneBuilder, invite_code, captcha_token, device_id, access_token, User_Agent, version):
    import requests

    url = "https://api-drive.mypikpak.com/vip/v1/activity/invite"

    payload = {
        "data": {
            "sdk_int": "33",
            "uuid": device_id,
            "userType": "1",
            "userid": user_id,
            "userSub": "",
            "product_flavor_name": "cha",
            "language_system": "zh-CN",
            "language_app": "zh-CN",
            "build_version_release": "13",
            "phoneModel": phoneModel,
            "build_manufacturer": phoneBuilder,
            "build_sdk_int": "33",
            "channel": "spread",
            "versionCode": "10142",
            # "versionName": "1.38.0",
            "versionName": version,
            "installFrom": "other",
            "country": "NO"
        },
        "apk_extra": {
            "channel": "spread",
            "invite_code": invite_code
        }
    }
    headers = {
        "Host": "api-drive.mypikpak.com",
        "authorization": "Bearer " + access_token,
        "product_flavor_name": "cha",
        "x-captcha-token": captcha_token,
        "x-client-version-code": "10142",
        "x-device-id": device_id,
        "user-agent": User_Agent,
        "country": "NO",
        "accept-language": "zh-CN",
        "x-peer-id": device_id,
        "x-user-region": "2",
        "x-system-language": "zh-CN",
        "x-alt-capability": "3",
        "accept-encoding": "gzip",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


# 程序运行主函数
def start():
    # 配置项初始化
    # 参数值
    invite_code = "验证码信息为空！"
    email = '邮箱信息为空！'
    verification_code = '邮箱验证码为空！'

    # 运行模式
    invite_code_mode = 1
    email_mode = 1
    verification_code_mode = 1

    # 版本
    version_list = ['1.38.0', '1.38.1', '1.39.0', '1.40.0', '1.40.1', '1.40.2', '1.40.3', '1.41.0', '1.42.6', '1.43.4']
    version = random.choice(version_list)
    print(f"本次运行所使用的版本为：{version}")

    # 读取配置文件
    try:
        with open('config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            invite_code_mode = config['invitationCode']['mode']
            invite_code = config['invitationCode']['value']
            email_mode = config['email']['mode']
            verification_code_mode = config['verificationCode']['mode']
    except Exception:
        input("配置文件读取异常，按任意键退出程序！")
        exit(0)

    # 邀请码
    if invite_code_mode == 2:
        print(f"本次邀请码为：{invite_code}")
    else:
        invite_code = input("请输入你的账号邀请码：")

    # 客户端id
    client_id = "YNxT9w7GMdWvEOKa"
    # 设备id
    device_id = str(uuid.uuid4()).replace("-", "")
    # 当前时间戳
    timestamp = str(int(time.time()) * 1000)

    # 新用户邮箱
    if email_mode == 2:
        email = get_email_auto()
        print(f"新邮箱信息：{email}")
    else:
        email = get_email()
        print(f"新邮箱信息：{email}")

    # 获取签证信息
    # org_str = client_id + "1.38.0" + "com.pikcloud.pikpak" + device_id + timestamp
    org_str = client_id + version + "com.pikcloud.pikpak" + device_id + timestamp
    captcha_sign = get_sign(org_str, version)
    print(f"captcha_sign：{captcha_sign}")

    # 设备信息
    randomPhone = random.choice(uaList)
    print(f"device_info：{randomPhone}")

    phoneModel = randomPhone['model']
    phoneBuilder = "XIAOMI"
    ua_key = get_ua_key(device_id)
    User_Agent = get_User_Agent(client_id, device_id, ua_key, timestamp, phoneModel, phoneBuilder, version)
    user_agent = get_user_agent()
    time.sleep(1)
    action2 = part2(client_id, "", device_id, captcha_sign, email, timestamp, user_agent, version)

    # pid,traceid,frames,result
    action3 = part3(device_id, user_agent, action2['url'])

    select_id = list_compare(action3['frames'])
    img_data = imgSecret(action3['frames'], select_id, action3['pid'])
    print(img_data)

    # result
    action4 = part4(action3['pid'], device_id, action3['traceid'], img_data['f'], img_data['ca'][0], img_data['ca'][1],
                    img_data['ca'][2], img_data['ca'][3], action2['url'], user_agent)
    time.sleep(1)
    # code,captcha_token,expires_in
    action5 = part5(device_id, action2["captcha_token"], action3['pid'], action3['traceid'], user_agent, action2['url'])

    # verification_id,expires_in,slected_channel
    action6 = part6(client_id, action5["captcha_token"], email, device_id, user_agent)

    # 获取验证码
    if verification_code_mode == 2:
        verification_code = get_verification_code_auto(email)
        print(f"注册验证码：{verification_code}")
    else:
        verification_code = get_verification_code()
        print(f"注册验证码：{verification_code}")

    # verification_token,expires_in
    action8 = part8(client_id, action6['verification_id'], verification_code, device_id, User_Agent)

    timestamp = str(int(time.time()) * 1000)
    org_str = client_id + version + "com.pikcloud.pikpak" + device_id + timestamp
    captcha_sign = get_sign(org_str,version)
    User_Agent = get_User_Agent(client_id, device_id, ua_key, timestamp, phoneModel, phoneBuilder, version)

    action8_1 = part8_1(client_id, action2["captcha_token"], device_id, captcha_sign, email, timestamp, User_Agent, version)
    client_secret = "dbw2OtmVEeuUvIptb1Coyg"
    time.sleep(1)
    # access_token,expires_in,sub
    # 账号的昵称设置
    name = email.split("@")[0]
    # 账号的密码设置
    password = "......00"
    action9 = part9(client_id, action8_1['captcha_token'], client_secret, email, name, password,
                    action8['verification_token'], device_id, User_Agent)
    time.sleep(1)
    # captcha_token,expires_in
    action10 = part10(client_id, action8_1['captcha_token'], device_id, captcha_sign, action9['sub'], timestamp,
                      User_Agent, version)

    # 邀请填写
    one_invite(action9['sub'], phoneModel, phoneBuilder, invite_code, action10['captcha_token'], device_id,
               action9['access_token'], User_Agent, version)
    part_invite(action9['sub'], phoneModel, phoneBuilder, invite_code, action10['captcha_token'], device_id,
                action9['access_token'], User_Agent)

    print("邀请成功")
    print("邮箱：", email)
    print("密码：", password)
    print("用户名：", name)
    print("结束运行")
    exit(0)


if __name__ == '__main__':
    start()
