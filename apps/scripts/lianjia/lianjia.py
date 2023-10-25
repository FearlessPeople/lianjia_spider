# -*- coding: utf-8 -*-

import datetime
import json
import multiprocessing
import os
import sqlite3
import sys
import textwrap
import time
from multiprocessing import Pool
from urllib.parse import urlparse

import pandas as pd
import psutil
import requests
from lxml import etree

print_sql = False


# pyinstaller --onefile --clean --noconfirm -n lianjia lianjia.py
def print2(*args, **kwargs):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}]", *args, **kwargs)


class SQLiteDB:
    def __init__(self, db_file='lianjia.db'):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def check_cursor(self):
        if self.cursor is None:
            self.cursor = self.conn.cursor()
        return self.cursor

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()

    def execute(self, sql, params=()):
        self.check_cursor()
        self.cursor.execute(sql, params)
        self.conn.commit()

    def query(self, sql):
        self.check_cursor()
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()

        columns = [column[0] for column in self.cursor.description]

        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        return result

    def commit(self):
        self.conn.commit()

    def insert(self, table, data, echo=False):
        fields = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        sql = f'INSERT INTO {table} ({fields}) VALUES ({placeholders})'
        data_values = tuple(data.values())
        if echo:
            formatted_sql = sql
            for value in data_values:
                formatted_sql = formatted_sql.replace('?', f"'{value}'", 1)
            print2(formatted_sql)
        self.execute(sql, data_values)

    def batch_insert(self, table, data):
        if len(data) == 0:
            raise Exception("Data is null")
        keys = data[0].keys()
        placeholders = ','.join(':' + key for key in keys)
        insert_statement = f'INSERT INTO {table} ({",".join(keys)}) VALUES ({placeholders})'
        self.check_cursor()
        for item in data:
            self.cursor.execute(insert_statement, item)
        self.conn.commit()

    def upsert(self, table, data):
        placeholders = ", ".join(["?"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute(sql, values)

    def update(self, table, data, condition):
        set_fields = ', '.join([f'{k}=?' for k in data.keys()])
        sql = f'UPDATE {table} SET {set_fields} WHERE {condition}'
        self.execute(sql, tuple(data.values()))

    def delete(self, table, condition):
        self.check_cursor()
        sql = f'DELETE FROM {table} WHERE {condition}'
        self.execute(sql)

    def count(self, table):
        self.check_cursor()
        self.cursor.execute(f"SELECT count(*) FROM {table};")
        return self.cursor.fetchall()[0][0]

    def select(self, table, condition=''):
        sql = f'SELECT * FROM {table}'
        if condition:
            sql += f' WHERE {condition} ;'
        return self.query(sql)


db = SQLiteDB()


class HttpUtils:

    @staticmethod
    def get(url, params=None, headers=None, timeout=None):
        try:
            response = requests.get(url=url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print2(f'Error in GET request: {e}')
        except Exception as e:
            print2(f'Error in GET request: {e}')

    @staticmethod
    def post(url, *args, **kwargs):
        try:
            response = requests.post(url, *args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print2(f'Error in POST request: {e}')
        except Exception as e:
            print2(f'Error in GET request: {e}')


def split_list(input_list, n):
    if len(input_list) % n == 0:
        cnt = len(input_list) // n
    else:
        cnt = len(input_list) // n + 1
    result = []
    for i in range(0, n):
        result.append(input_list[i * cnt:(i + 1) * cnt])
    return result


def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.hostname
    if domain.startswith('www.'):
        domain = domain[4:]
    subdomains = domain.split('.')
    if len(subdomains) == 3:
        return subdomains[0]
    elif len(subdomains) == 4:
        return ".".join(subdomains[0:2])
    else:
        return None


def extract_id_from_url(url):
    segments = url.split('/')
    last_segment = segments[-2]
    return last_segment


def get_base_province():
    final_result = []
    url = 'https://www.lianjia.com/city/'
    response = requests.get(url)
    if response.status_code == 200:
        tree = etree.HTML(response.text)
        province_elements = tree.xpath('//div[@class="city_province"]')
        for province in province_elements:
            province_name = province.xpath('./div/text()')
            if province_name:
                province_name = province_name[0]
                city_lists = province.xpath('./ul/li')
                for city in city_lists:
                    city_name = city.xpath('./a/text()')[0]
                    city_url = city.xpath('./a/@href')[0]
                    city_id = extract_domain(city_url)
                    insertdata = {
                        "province_name": province_name,
                        "city_id": city_id,
                        "city_name": city_name,
                        "city_url": city_url
                    }
                    final_result.append(insertdata)
    else:
        print2("Failed to retrieve data from the website.")
    return final_result


def get_sub_region(url):
    final_result = []
    response = HttpUtils.get(url)
    if response.status_code == 200:
        tree = etree.HTML(response.text)
        ershoufang_div = tree.xpath('//div[@class="position"]/dl[2]/dd/div')[0]
        a_elements = ershoufang_div.xpath('./div[2]/a')
        for a in a_elements:
            sub_region_name = a.xpath('./text()')[0]
            sub_region_url = a.xpath('./@href')[0]
            sub_region_id = sub_region_url
            final_result.append({
                "sub_region_id": sub_region_id,
                "sub_region_name": sub_region_name,
                "sub_region_url": sub_region_url
            })
    else:
        print2("Failed to retrieve data from the website.")
    return final_result


def get_base_areas(url):
    final_result = []
    response = HttpUtils.get(url)
    if response.status_code == 200:
        tree = etree.HTML(response.text)
        a_elements = tree.xpath('//div[@class="position"]/dl/dd/div/div/a')
        for a in a_elements:
            region_name = a.xpath('./text()')[0]
            region_url = a.xpath('./@href')[0]
            region_id = region_url
            region = {
                "region_id": region_id,
                "region_name": region_name,
                "region_url": region_url
            }
            sub_region_url = url + "/" + str(extract_id_from_url(region_url))
            sub_regions = get_sub_region(url=sub_region_url)
            if sub_regions:
                for sub_region in sub_regions:
                    final_result.append({**region, **sub_region})
            else:
                region['sub_region_id'] = region['region_id']
                region['sub_region_name'] = region['region_name']
                region['sub_region_url'] = region['region_url']
                final_result.append(region)
    else:
        print2("Failed to retrieve data from the website.")
    return final_result


def get_base_xiaoqu_pagenum(url):
    response = HttpUtils.get(url)
    if response.status_code == 200:
        tree = etree.HTML(response.text)
        page_div = tree.xpath('//div[@class="contentBottom clear"]/div[2]/div')
        if len(page_div) > 0:
            page_div_element = page_div[0]
            page_data = page_div_element.xpath('./@page-data')
            data_dict = json.loads(page_data[0])
            total_page = data_dict['totalPage']
            return total_page
        else:
            return 0
    else:
        print2("Failed to retrieve data from the website.")


def get_base_xiaoqu_by_page_url(url):
    final_result = []
    response = HttpUtils.get(url)
    if response.status_code == 200:
        tree = etree.HTML(response.text)
        li_elements = tree.xpath('//ul[@class="listContent"]/li')
        for li in li_elements:
            xiaoqu_name = li.xpath('./div[@class="info"]/div[@class="title"]/a/text()')[0]
            xiaoqu_url = li.xpath('./div[@class="info"]/div[@class="title"]/a/@href')[0]
            xiaoqu_id = extract_id_from_url(xiaoqu_url)
            xiaoqu = {
                "xiaoqu_id": xiaoqu_id,
                "xiaoqu_name": xiaoqu_name,
                "xiaoqu_url": xiaoqu_url
            }
            final_result.append(xiaoqu)
    else:
        print2("Failed to retrieve data from the website.")
    return final_result


def get_base_xiaoqu(url):
    final_result = []
    maxpage = get_base_xiaoqu_pagenum(url=url)
    if maxpage > 0:
        for i in range(1, maxpage + 1):
            newurl = url + f"pg{i}"
            xiaoqu_list = get_base_xiaoqu_by_page_url(url=newurl)
            final_result.extend(xiaoqu_list)
        return final_result
    else:
        return None


def get_community_detail(url):
    response = requests.get(url)
    if response.status_code == 200:
        final_result = []
        tree = etree.HTML(response.text)
        xiaoquInfoItems = tree.xpath('//div[@class="xiaoquInfoItem"]')
        for xiaoqu_info in xiaoquInfoItems:
            label = xiaoqu_info.xpath('.//span[@class="xiaoquInfoLabel"]/text()')[0]
            value = xiaoqu_info.xpath('.//span[@class="xiaoquInfoContent"]/text()')[0]
            final_result.append({
                "label": label,
                "value": value
            })
        return final_result


def create_table():
    init_sql = """
    CREATE TABLE IF NOT EXISTS `lj_base_province`
    (
        `id`            INTEGER PRIMARY KEY AUTOINCREMENT,
        `province_name` varchar(255),
        `city_id`       varchar(255),
        `city_name`     varchar(255),
        `city_url`      varchar(255),
        `create_time`   DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
        `update_time`   DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS `lj_base_areas`
    (
        `id`              INTEGER PRIMARY KEY AUTOINCREMENT,
        `city_id`         varchar(255),
        `region_id`       varchar(255),
        `region_name`     varchar(255),
        `region_url`      varchar(255),
        `sub_region_id`   varchar(255),
        `sub_region_name` varchar(255),
        `sub_region_url`  varchar(255),
        `create_time`     DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
        `update_time`     DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS `lj_base_xiaoqu`
    (
        `id`            INTEGER PRIMARY KEY AUTOINCREMENT,
        `city_id`       varchar(255),
        `region_id`     varchar(255),
        `sub_region_id` varchar(255),
        `xiaoqu_id`     varchar(255),
        `xiaoqu_name`   varchar(255),
        `xiaoqu_url`    varchar(255),
        `create_time`   DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
        `update_time`   DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS `lj_xiaoqu_detail`
    (
        `id`          INTEGER PRIMARY KEY AUTOINCREMENT,
        `xiaoqu_id`   varchar(255),
        `fwzs`        varchar(255), -- 房屋总数
        `ldzs`        varchar(255), -- 楼栋总数
        `create_time` DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
        `update_time` DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
    );
    """
    for sql in init_sql.split(";"):
        db.execute(sql=sql)


def db_init(province_name=None, city_name=None):
    if not province_name:
        raise Exception("未传递省份参数province_name")
    print2(f"开始初始化[{province_name}]省份基础数据...")
    province_list = get_base_province()
    db.delete(table='lj_base_province', condition=f" province_name='{province_name}' ")
    for province in province_list:
        if province['province_name'] == province_name:
            db.insert(table='lj_base_province', data=province, echo=print_sql)

    if city_name:
        condition = f" province_name='{province_name}' and city_name='{city_name}' "
    else:
        condition = f" province_name='{province_name}' "
    city_list = db.select(table='lj_base_province', condition=condition)
    for city in city_list:
        city_id = city['city_id']
        db.delete(table='lj_base_areas', condition=f" city_id='{city_id}'")
        url = city['city_url'] + "xiaoqu"
        areas_list = get_base_areas(url=url)
        for area in areas_list:
            area['city_id'] = city_id
            region_id = area['region_id']

            db.insert(table='lj_base_areas', data=area, echo=print_sql)

            # 子区域下各小区列表
            sub_region_id = area['sub_region_id']
            sub_region_url = area['sub_region_url']
            baseurl = f'https://{city_id}.lianjia.com{sub_region_url}'
            xiaoqu_list = get_base_xiaoqu(url=baseurl)
            if xiaoqu_list:
                for xiaoqu in xiaoqu_list:
                    xiaoqu_id = xiaoqu['xiaoqu_id']
                    xiaoqu['city_id'] = city_id
                    xiaoqu['region_id'] = region_id
                    xiaoqu['sub_region_id'] = sub_region_id
                    db.delete(table='lj_base_xiaoqu',
                              condition=f" city_id='{city_id}' and xiaoqu_id='{xiaoqu_id}'")
                    db.insert(table='lj_base_xiaoqu', data=xiaoqu, echo=print_sql)
            else:
                print2(f"{baseurl}下无小区信息")
    print2(f"[{province_name}]省份下所有城市、区域、子区域、小区信息初始化完成......")


def get_longdong(xiaoqu_detail):
    final_result = {}
    if xiaoqu_detail:
        for xiaoqu in xiaoqu_detail:
            if xiaoqu['label'] == '房屋总数':
                final_result['fwzs'] = xiaoqu['value']
            elif xiaoqu['label'] == '楼栋总数':
                final_result['ldzs'] = xiaoqu['value']
    return final_result


def to_excel(province_name, city, area):
    current_timestamp = time.time()
    current_timestamp = int(current_timestamp)
    file_path = f'{province_name}数据_{current_timestamp}.xlsx'
    lj_base_areas_sql = f"lj_base_areas"
    if city:
        lj_base_province_sql = f"(select * from lj_base_province where province_name='{province}' and city_name='{city}' )"
        file_path = f'{province_name}-{city}数据_{current_timestamp}.xlsx'
        if area:
            lj_base_areas_sql = f"(select * from lj_base_areas t where region_name='{area}')"
            file_path = f'{province_name}-{city}-{area}数据_{current_timestamp}.xlsx'
    else:
        lj_base_province_sql = f"(select * from lj_base_province where province_name='{province}' )"

    sql = f'''
    select 
       lbp.province_name   as `省份`
     , lbp.city_name       as `城市`
     , lba.city_id         as `城市ID`
     , lba.region_id       as `区域ID`
     , lba.region_name     as `区域名称`
     , lba.sub_region_id   as `子区域ID`
     , lba.sub_region_name as `子区域名称`
     , "`" || t.xiaoqu_id  as `小区ID`
     , t.xiaoqu_name       as `小区名称`
     , t.xiaoqu_url        as `小区URL`
     , lxd.fwzs            as `房屋总数`
     , lxd.ldzs            as `楼栋总数`
from lj_base_xiaoqu t
left join {lj_base_areas_sql} lba on t.city_id = lba.city_id and t.region_id = lba.region_id and t.sub_region_id = lba.sub_region_id
left join {lj_base_province_sql} lbp on lba.city_id = lbp.city_id
left join lj_xiaoqu_detail lxd on t.xiaoqu_id = lxd.xiaoqu_id
where lbp.province_name = '{province_name}'
group by 
       lbp.province_name 
     , lbp.city_name     
     , lba.city_id      
     , lba.region_id      
     , lba.region_name     
     , lba.sub_region_id   
     , lba.sub_region_name 
     , "`" || t.xiaoqu_id  
     , t.xiaoqu_name      
     , t.xiaoqu_url      
     , lxd.fwzs        
     , lxd.ldzs            
;'''
    query_list = db.query(sql)
    result_df = pd.DataFrame(query_list)
    result_df.to_excel(file_path, index=False)
    print2(f"导出成功:{file_path}")


def process_elements(all_xiaoqu):
    current_process = multiprocessing.current_process()
    current_process.name = "Lianjia_Process"
    xiaoqu_size = len(all_xiaoqu)
    for index, xiaoqu in enumerate(all_xiaoqu):
        xiaoqu_id = xiaoqu['xiaoqu_id']
        db.delete(table='lj_xiaoqu_detail', condition=f" xiaoqu_id = '{xiaoqu_id}'")
        xiaoqu_url = xiaoqu['xiaoqu_url']
        print2(f"{current_process.name}==>[{index}/{xiaoqu_size}]{xiaoqu_url}")
        xiaoqu_detail = get_community_detail(url=xiaoqu_url)
        if xiaoqu_detail:
            fwzs = get_longdong(xiaoqu_detail)['fwzs']
            ldzs = get_longdong(xiaoqu_detail)['ldzs']
            insert_detail = {
                'xiaoqu_id': xiaoqu_id,
                'fwzs': fwzs,
                'ldzs': ldzs
            }
            db.insert(table='lj_xiaoqu_detail', data=insert_detail)


def process_list(input_list):
    cpu_core_num = psutil.cpu_count(logical=False)
    split_result = split_list(input_list, cpu_core_num)
    p = Pool()
    print2('Parent process %s.' % os.getpid())
    for xiaoqu_list in split_result:
        p.apply_async(process_elements, args=(xiaoqu_list,))
    print2('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print2('All subprocesses done.')


def spider_by_condition(province, city=None, area=None):
    echo_msg = f"开始采集[{province}"
    lj_base_areas_sql = f"lj_base_areas"
    if city:
        echo_msg += f"-{city}"
        lj_base_province_sql = f"(select * from lj_base_province where province_name='{province}' and city_name='{city}' )"
        if area:
            echo_msg += f"-{area}"
            lj_base_areas_sql = f"(select * from lj_base_areas t where region_name='{area}')"
    else:
        lj_base_province_sql = f"(select * from lj_base_province where province_name='{province}' )"
    echo_msg += f"]区域下数据..."
    print2(echo_msg)

    sql = f"""
    select
    lbp.province_name
    ,lbp.city_name
    ,lba.city_id
    ,lba.sub_region_id
    ,lba.sub_region_name
    ,t.xiaoqu_id
    ,t.xiaoqu_name
    ,t.xiaoqu_url
    from lj_base_xiaoqu t
    inner join {lj_base_areas_sql} lba on t.city_id = lba.city_id and t.region_id=lba.region_id and t.sub_region_id=lba.sub_region_id
    inner join {lj_base_province_sql} lbp on lba.city_id = lbp.city_id
    left join lj_xiaoqu_detail lxd on t.xiaoqu_id = lxd.xiaoqu_id
    where 1=1
      and lxd.xiaoqu_id is null
    group by
    lbp.province_name
    ,lbp.city_name
    ,lba.city_id
    ,lba.sub_region_id
    ,lba.sub_region_name
    ,t.xiaoqu_id
    ,t.xiaoqu_name
    ,t.xiaoqu_url
    ;
    """
    print2(sql)
    all_xiaoqu = db.query(sql)
    process_list(all_xiaoqu)


def statistics_info():
    sql = f"""
    select lbp.province_name as `省份`
         , lbp.city_name as `城市`
         , count(distinct t.xiaoqu_id)   as `总小区数量`
         , count(distinct lxd.xiaoqu_id) as `已完成数量`
    from lj_base_xiaoqu t
    left join lj_base_province lbp on t.city_id = lbp.city_id
    left join lj_xiaoqu_detail lxd on t.xiaoqu_id = lxd.xiaoqu_id
    group by lbp.province_name
           , lbp.city_name;
    """
    all_xiaoqu = db.query(sql)
    statistics_df = pd.DataFrame(all_xiaoqu)
    print2("\n", statistics_df.to_string(index=False))


def main(province, city, area):
    db_init(province_name=province, city_name=city)
    spider_by_condition(province=province, city=city, area=area)


def print_disclaimer():
    message = """
    ######################################################################################################################
                                                   免责声明                                                               
    此工具仅限于学习研究，用户需自己承担因使用此工具而导致的所有法律和相关责任！作者不承担任何法律责任！                 
    ######################################################################################################################
    """
    print(textwrap.dedent(message))
    while True:
        user_input = input("如果您同意本协议, 请输入Y继续: (y/n) ")
        if user_input.lower() == "y":
            return True
        elif user_input.lower() == "n":
            sys.exit(0)


if __name__ == '__main__':
    create_table()
    disclaimer_accepted = print_disclaimer()
    if not disclaimer_accepted:
        exit()

    print("功能选项：\n1. 按区域导出\n2. 打印导出统计信息")
    function_choice = input("请输入功能序号: ")
    if function_choice == '2':
        statistics_info()
    elif function_choice == '1':
        province = input("请输入省份名称(必填): ")
        city = input("请输入省份下城市名称(可选): ")
        area = input("请输入省份下城市下区域名称(可选): ")
        if province:
            main(province, city, area)
            to_excel(province, city, area)
