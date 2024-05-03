import pickle
import re
import time
from h5st import H5ST
from utils.digester_utils import Digester
import requests
import json5
import json
import copy
from fake_useragent import UserAgent

import os
import csv
import config
import logging  # 日志
import rich  # 富文本
from rich.progress import Progress, BarColumn, SpinnerColumn, TimeRemainingColumn, TimeElapsedColumn, TransferSpeedColumn  # rich进度条
from rich.panel import Panel  # rich面板
from rich.box import DOUBLE  # rich面板样式
import pyfiglet  # ASCII艺术
from pypinyin import lazy_pinyin, Style  # 拼音转换

style = Style.NORMAL

page_columns = [
    "[progress.description]{task.description}({task.completed}/{task.total})",  # 设置进度条头部
    SpinnerColumn(spinner_name='aesthetic', style="white"),  # 设置显示Spinner动画{spinner_name：头部动画名称；style：头部动画颜色}
    TransferSpeedColumn(),  # 设置传输速度
    BarColumn(complete_style="magenta", finished_style="green"),  # 设置进度条体{complete_style：进行中颜色；finished_style：完成颜色}
    "[progress.percentage][white]{task.percentage:>3.2f}%",  # 设置进度条尾部{[color]：百分比颜色；task.percentage：百分比格式化}
    "⏱ ",  # 设置进度条共计执行时间样式
    TimeElapsedColumn(),
    "⏳",  # 设置进度条预计剩余时间样式
    TimeRemainingColumn(),
]


class WriteProgress(Progress):
    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks), box=DOUBLE)


class Jd(object):
    def __init__(self):
        self.sku_id = ""
        self.page_config_dir_path = './page_config/'
        self.class_path = None
        self.name = None
        self.type = None
        self.headers = {
            "authority": "api.m.jd.com",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5,ko;q=0.4,fr;q=0.3",
            "origin": "https://item.jd.com",
            "referer": "https://item.jd.com/",
            "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": UserAgent().random,
            "x-referer-page": "https://item.jd.com/6274992.html",
            "x-rp-client": "h5_1.0.0"
        }
        self.cookies = {
            "__jdu": "1708653980687272576454",
            "shshshfpa": "e06713c9-50ca-abad-b1cd-3ad465c28803-1708691725",
            "shshshfpx": "e06713c9-50ca-abad-b1cd-3ad465c28803-1708691725",
            "TrackID": "1G-MmCrg2rDLoozbyXNVPMHSTQaN4nAWOrk4GtuEECd1_PXWL1D6OCP8a6bejS0FD3yZ-rJegmcbXmkcXpd4AMwWgoR5ZhwB9oyQnfKrkS_Mpm9BawUZytrOAA7QPQD8J",
            "thor": "82E7DAD074A2F55D0EF704FCF3C4DD87486776F9CCBB1560F7C638540DBADD9342225CC9BFD1053BC83604AEEF4A57B8F1405E13C8B64015794C58FD4B96C4D9DD3C86598DFF1902240F0921C05BD6F4B311AA5150951F998A590944280F869132C14B1A82DCAB53C2AABAE44D14E61C8FE5D7E8F9196EE279D6874A8944421966CA5216652FD45426681117E7AC0CCDF4BE13E26232C6AAC8EC7FF107436168",
        }
        self.session = requests.Session()
        # 设置重试次数 设置线程池
        self.timeout = 5
        self.page_num = 0

    def save_page_config_to_local(self, page_config):
        cookies_file = '{}{}.page_config'.format(self.page_config_dir_path, self.sku_id)
        directory = os.path.dirname(cookies_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(cookies_file, 'wb') as f:
            pickle.dump(page_config, f)

    def load_page_config(self):
        page_config_file = ''
        if not os.path.exists(self.page_config_dir_path):
            return None
        for name in os.listdir(self.page_config_dir_path):
            if name.endswith(f"{self.sku_id}.page_config"):
                page_config_file = '{}{}'.format(self.page_config_dir_path, name)
                break
        if page_config_file == '':
            return None
        with open(page_config_file, 'rb') as f:
            page_config = pickle.load(f)
        return page_config

    def get_page_config(self):
        page_config = self.load_page_config()
        if page_config is not None:
            return page_config
        url = f"https://item.jd.com/{self.sku_id}.html"
        response = self.session.get(url, headers=self.headers)
        # 确保请求成功
        if response.status_code == 200:
            # 查找'var pageConfig'变量
            match = re.search(r'var pageConfig = ({.*?});', response.text, re.DOTALL)
            if match:
                # 提取变量的值
                page_config_str = match.group(1)
                pageConfig = json5.loads(page_config_str)
                self.save_page_config_to_local(pageConfig)
                return pageConfig
            else:
                print("无法找到'var pageConfig'变量。")

    def getComments(self):
        pageConfig = self.get_page_config()
        body = {
            'productId': pageConfig['product']['skuid'],
            "score": 0,
            "sortType": 6,
            "page": f"{self.page_num}",
            "pageSize": 10,
            "isShadowSku": 0,
            "fold": 1,
            "bbtf": "",
            "shield": ""
        }
        params = {
            'appid': "item-v3",
            'functionId': "pc_club_productPageComments",
            'client': "pc",
            'clientVersion': "1.0.0",
            't': int(time.time() * 1000),
            'body': json.dumps(body, separators=(',', ':')),
            'x-api-eid-token': 'jdd03J27IVEQH32WSMEDRLBC23DAU3AF25GTMWOGGUPXM66CWQF5VMZKCVBD4U2GKSVGOCI7GDTOBVKGIEODPUKBHKMNDYIAAAAMPH2O66VYAAAAACNLTOIDE62AG5IX',
            'uuid': '181111935.1708653980687272576454.1708653980.1714693695.1714741755.10',
        }
        sha256_body = Digester.sha256(params['body'])
        d = copy.deepcopy(params)
        d['body'] = sha256_body
        h5st = H5ST(self.sku_id)
        h5st = h5st.gen_h5st(d)
        params['h5st'] = h5st
        params['loginType'] = '3'
        url = "https://api.m.jd.com/"
        response = self.session.get(url, headers=self.headers, cookies=self.cookies, params=params, proxies=config.PROXIES)
        return response.text

    def crawl_write(self):
        start_time = time.time()
        log = logging.getLogger("rich")  # 日志对象
        if not os.path.exists(config.DATA_PATH):
            os.makedirs(config.DATA_PATH)
        with WriteProgress(*page_columns) as progress:
            total_task = progress.add_task(f"[bold blue]爬取配置文件中所有商品评论", total=len(config.PRODUCTS))
            for key, value in config.PRODUCTS.items():
                result = pyfiglet.figlet_format(f"{' '.join(lazy_pinyin(key, style=style))}", font="small_slant")
                log.info(f"\n{result}")
                class_path = f'{config.DATA_PATH}/{key}'
                if not os.path.exists(class_path):
                    os.makedirs(class_path)
                midtask = progress.add_task(f"[bold green]爬取[{key}]", total=len(value))
                for v in value:
                    self.sku_id = v.get('productid')
                    self.type = v.get('type')
                    self.name = v.get('name').replace('/', '-')
                    type_path = f'{class_path}/{self.type}'
                    if not os.path.exists(type_path):
                        os.makedirs(type_path)
                    # 日志配置
                    logging.basicConfig(
                        level="INFO",
                        format="%(asctime)s - [%(levelname)s] - %(message)s",
                        datefmt="[%Y-%m-%d %H:%M:%S]",
                        handlers=[
                            logging.FileHandler(f"{class_path}/{self.type}/log.log", mode='a', encoding='utf-8')
                        ],
                    )

                    subtask = progress.add_task(f"[bold green]爬取[{self.name[:15]}...]", total=100)
                    for i in range(0, 100):
                        # 初始化 CSV 文件
                        self.class_path = class_path
                        filename = f'{self.class_path}/{self.type}/{self.name}.csv'
                        file_exists = os.path.isfile(filename)
                        csvfile = open(filename, 'a', newline='', encoding='utf-8')
                        fieldnames = ['userid', 'content', 'referenceTime', 'creationTime', 'buyCount', 'score', 'productColor', 'location']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        if not file_exists:
                            writer.writeheader()  # 写入表头，如果文件不存在的话
                        comments = json.loads(self.getComments()).get('comments')
                        try:
                            for comment in comments:
                                userid = comment['id']
                                content = comment['content']
                                referenceTime = comment['referenceTime']
                                creationTime = comment['creationTime']
                                buyCount = comment['extMap']['buyCount']
                                score = comment['score']
                                productColor = comment['productColor']
                                location = comment['location']
                                comment_dict = {
                                    'userid': userid,
                                    'content': content,
                                    'referenceTime': referenceTime,
                                    'creationTime': creationTime,
                                    'buyCount': buyCount,
                                    'score': score,
                                    'productColor': productColor,
                                    'location': location
                                }
                                writer.writerow(comment_dict)
                                self.page_num = i
                        except TypeError:
                            rich.print(Panel(f"[bold red]爬取被风控，请前往[京东任意商品页->商品评价]进行滑块验证[/bold red]", style="red", box=rich.box.DOUBLE, expand=False))
                            input(Panel("[bold green]验证完成后，按任意键继续...[/bold green]", style="green", box=rich.box.DOUBLE, expand=False))
                        progress.update(subtask, advance=1)  # 单页爬取完成，更新1格
                        time.sleep(5)
                    progress.update(midtask, advance=1)  # 单个商品爬取完成，更新1格
                    end_time = time.time()
                    log.info(f"[{self.type}/{self.name}]爬取完成丨耗时：{end_time - start_time:.2f}秒")
                progress.update(total_task, advance=1)  # 单个类别爬取完成，更新1格
            csvfile.close()


def main():
    jd = Jd()
    jd.crawl_write()


if __name__ == '__main__':
    main()
