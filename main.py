#  Copyright (c) 2024. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
import csv
import os
import time
import random
import httpx
import re
from fake_useragent import UserAgent
from tqdm import tqdm

import jd_cookies

global name


def get_dispose_comments(alldata):
    # 通过接受到的json数据
    comments = alldata['comments']  # 评论全部数据
    results = []
    for data in comments:
        if "location" in data:
            content = data['content']  # 评论
            creationtime = data['creationTime']  # 时间
            location = data['location']  # ip
            productcolor = data['productColor']  # 商品款式
            result_dic = {
                'content': content,
                'creationtime': creationtime,
                'location': location,
                'productcolor': productcolor,
            }
            results.append(result_dic)  # 这里可以方便大家保存数据
        else:
            content = data['content']  # 评论
            creationtime = data['creationTime']  # 时间
            productcolor = data['productColor']  # 商品款式
            location = '无'
            result_dic = {
                'content': content,
                'creationtime': creationtime,
                'location': location,
                'productcolor': productcolor,
            }
            results.append(result_dic)  # 这里可以方便大家保存数据
        # 检查csv文件是否存在,不存在则创建
        file_exists = os.path.isfile(f'data/{name}.csv')
        csvfile = open(f'data/{name}.csv', 'a', newline='', encoding='utf-8')
        fieldnames = ['content', 'creationtime', 'location', 'productcolor']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()  # 写入表头，如果文件不存在的话
        writer.writerows(results)


def get_forms_comments(productid, client):
    url = 'https://api.m.jd.com/?appid=item-v3'
    # 获取时间戳(毫秒)
    timestamp = int(time.time() * 1000)
    # 构造新的表单
    data = {
        'functionId': 'pc_club_productPageComments',
        'client': 'pc',
        'clientVersion': '1.0.0',
        't': timestamp,  # 时间戳
        'loginType': '3',
        'uuid': '181111935.1706791191786871307752.1706791191.1712766948.1712794165.2',
        'productId': productid,  # 商品编码
        'score': '0',
        'sortType': '5',
        'page': '0',
        'pageSize': '10',
        'isShadowSku': '0',
        'fold': '1',
        'bbtf': '',
        'shield': ''
    }
    resp = client.get(url, params=data)
    # 判断状态吗是否为200是则返回json数据和页面最大数,否则重新请求
    if resp.status_code == 200:
        alldata = resp.json()
        maxpage = alldata['maxPage']
        return alldata, maxpage
    else:
        get_forms_comments(productid, client)


def get_dispose_comments2(alldata):
    comments = alldata['comments']  # 评论全部数据
    results = []
    for data in comments:
        if "location" in data:
            content = data['content']  # 评论
            creationtime = data['creationTime']  # 时间
            location = data['location']  # ip
            productcolor = data['productColor']  # 商品款式
            result_dic = {
                'content': content,
                'creationtime': creationtime,
                'location': location,
                'productcolor': productcolor,
            }
            results.append(result_dic)  # 这里可以方便大家保存数据
        else:
            content = data['content']  # 评论
            creationtime = data['creationTime']  # 时间
            productcolor = data['productColor']  # 商品款式
            location = '无'
            result_dic = {
                'content': content,
                'creationtime': creationtime,
                'location': location,
                'productcolor': productcolor,
            }
            results.append(result_dic)  # 这里可以方便大家保存数据
        # 检查csv文件是否存在,不存在则创建
        file_exists = os.path.isfile(f'data/{name}.csv')
        csvfile = open(f'data/{name}.csv', 'a', newline='', encoding='utf-8')
        fieldnames = ['content', 'creationtime', 'location', 'productcolor']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()  # 写入表头，如果文件不存在的话
        writer.writerows(results)


def get_forms_comments2(productid, client, i):
    # 这里这段代码是为了完成翻页操作
    url = 'https://api.m.jd.com/?appid=item-v3'
    timestamp = int(time.time() * 1000)  # 获取时间戳
    data = {
        'functionId': 'pc_club_productPageComments',
        'client': 'pc',
        'clientVersion': '1.0.0',
        't': timestamp,  # 时间戳
        'loginType': '3',
        'uuid': '181111935.1706791191786871307752.1706791191.1712766948.1712794165.2',
        'productId': productid,  # 商品编码
        'score': '0',
        'sortType': '5',
        'page': i,  # 翻页
        'pageSize': '10',
        'isShadowSku': '0',
        'rid': '0',
        'fold': '1',
        'bbtf': '',
        'shield': ''
    }
    resp = client.get(url, params=data)
    if resp.status_code == 200:
        alldata = resp.json()
        get_dispose_comments2(alldata)
    else:
        get_forms_comments2(productid, client, i)


def get_crawling_homepage(client, name):
    url = f'https://search.jd.com/Search?'
    # 构造表单
    data = {
        'keyword': name,
        'enc': 'utf - 8',
        'spm': 'a.0.0',
        'pvid': '1de57a0845254674b2e422004fccbf59'
    }
    resp = client.get(url, params=data)
    html_data = resp.text
    if resp.status_code == 200:
        obj = re.compile(r'<div class="p-name p-name-type-2">.*?href="(?P<url>.*?)".*?<em>.*?<font class="skcolor_ljg">(?P<name>.*?)</font>.*?</em>', re.S)
        page = obj.finditer(html_data)
        results = []
        for item in page:
            url_homepage = 'https' + item.group('url')
            commodity = item.group('name')
            productid_1 = url_homepage.split('/')[3]
            productid_2 = productid_1.split('.')[0]
            results.append((url_homepage, commodity, productid_2))

        return results  # 返回所有匹配结果的列表
    else:
        print("请求失败正在为您重新请求,请求状态码:", resp)
        time.sleep(1)
        get_crawling_homepage(client, name)


def get_cerebrum():
    global name
    ua = UserAgent()  # 初始化UA库
    name = input('请输入你要查询商品评论的商品名称:')
    headers = {
        'User-Agent': ua.random,  # 随机UA
        'Cookie': random.choice(jd_cookies.COOKIES_LIST),  # cookie池
        'Referer': 'https://www.jd.com/'
    }
    client = httpx.Client(http2=True, headers=headers, timeout=15)
    # 发送请求获取返回的京东主页html,然后进行re处理匹配需要的数据
    results = get_crawling_homepage(client=client, name=name)
    # 循环results获取商品名称页面地址和productId
    for result in results:
        url_homepage = result[0].replace("https", "https://")
        commodity = result[1]
        productid = result[2]
        print('-------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print('商品名称:' + commodity, '页面地址:' + url_homepage)
        # 发送请求获取返回的json数据和页面最大数
        alldata, maxpage = get_forms_comments(productid=productid, client=client)
        # 判断页面最大数
        if maxpage == 1:
            # 发送json数据
            get_dispose_comments(alldata)

        elif maxpage >= 1:
            # 发送json数据
            get_dispose_comments(alldata)
            maxpage += 1
            # 使用for循环完成翻页操作
            for maxpage2 in tqdm(range(1, maxpage), colour='white', desc='正在获取以上链接商品规格的评论'):
                get_forms_comments2(i=maxpage2, client=client, productid=productid)
                time.sleep(3)

        elif maxpage == 0:
            print('没有评论哦~')


if __name__ == '__main__':
    get_cerebrum()
