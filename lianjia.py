# -*- coding: utf-8 -*-

import json
import sys
import textwrap
import time
from urllib.parse import urlparse

import pandas as pd
import requests
from lxml import etree
from pypinyin import lazy_pinyin, Style

from utils.util_http import HttpUtils
from utils.util_print import print2
from utils.util_sqlite import db

print_sql = False

sys_platform = sys.platform


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
        `detail_json` varchar(500), -- 详细信息json格式
        `create_time` DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
        `update_time` DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
    );
    """
    for sql in init_sql.split(";"):
        db.execute(sql=sql)


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


def get_price(t):
    if len(t) > 0:
        result = t.xpath('/html/body/div[6]/div[2]/div[1]/div/span[1]/text()')
        if result:
            return str(result[0])
    else:
        return 0


def get_value(tree, xpath_str):
    try:
        return str(tree.xpath(xpath_str)[0])
    except Exception as e:
        print(e)
        return ""


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
                "value": str(value)
            })
        final_result.append({
            'label': '挂牌均价',
            'value': get_price(tree)
        })
        final_result.append({  # 物业费
            'label': get_value(tree, '/html/body/div[6]/div[2]/div[2]/div[2]/div[1]/span[1]/text()'),
            'value': get_value(tree, '/html/body/div[6]/div[2]/div[2]/div[2]/div[1]/span[2]/text()')
        })
        final_result.append({  # 经纬度
            'label': '经纬度',
            'value': get_value(tree, '/html/body/div[6]/div[2]/div[2]/div[2]/div[2]/span[2]/span/@mendian')
        })

        return final_result


def get_first_letter(text):
    pinyin_list = lazy_pinyin(text, style=Style.FIRST_LETTER)
    return ''.join(pinyin_list)


def get_merged_dict(xiaoqu_detail):
    final_result = {}
    if xiaoqu_detail:
        for xiaoqu in xiaoqu_detail:
            final_result[xiaoqu['label']] = xiaoqu['value']
    return final_result


class LianjiaSpider:
    def __init__(self, province_name, city_name=None, area_name=None):
        self.province_name = province_name
        self.city_name = city_name
        self.area_name = area_name
        self.signals = None
        self.max_num = 0  # 本次采集的总小区数量，用于设置页面上进度条最大值
        self.run_flag = True

    def db_init(self):
        if not self.province_name:
            raise Exception("未传递省份参数province_name")
        print2(f"正在初始化[{self.province_name}]省份基础数据...")
        province_list = get_base_province()
        db.delete(table='lj_base_province', condition=f" province_name='{self.province_name}' ")
        for province in province_list:
            if not self.run_flag:
                return
            if province['province_name'] == self.province_name:
                db.insert(table='lj_base_province', data=province, echo=print_sql)

        if self.city_name:
            condition = f" province_name='{self.province_name}' and city_name='{self.city_name}' "
        else:
            condition = f" province_name='{self.province_name}' "
        city_list = db.select(table='lj_base_province', condition=condition)
        for city in city_list:
            if not self.run_flag:
                return
            city_id = city['city_id']
            db.delete(table='lj_base_areas', condition=f" city_id='{city_id}'")
            url = city['city_url'] + "xiaoqu"
            areas_list = get_base_areas(url=url)
            for area in areas_list:
                if not self.run_flag:
                    return
                area['city_id'] = city_id
                region_id = area['region_id']

                db.insert(table='lj_base_areas', data=area, echo=print_sql)

                # 子区域下各小区列表
                sub_region_id = area['sub_region_id']
                sub_region_url = area['sub_region_url']
                baseurl = f'https://{city_id}.lianjia.com{sub_region_url}'
                xiaoqu_list = get_base_xiaoqu(url=baseurl)
                xiaoqu_list_len = len(xiaoqu_list) if xiaoqu_list else 0
                if xiaoqu_list:
                    for index, xiaoqu in enumerate(xiaoqu_list):
                        if not self.run_flag:
                            return
                        xiaoqu_id = xiaoqu['xiaoqu_id']
                        xiaoqu['city_id'] = city_id
                        xiaoqu['region_id'] = region_id
                        xiaoqu['sub_region_id'] = sub_region_id
                        db.delete(table='lj_base_xiaoqu',
                                  condition=f" city_id='{city_id}' and xiaoqu_id='{xiaoqu_id}'")
                        db.insert(table='lj_base_xiaoqu', data=xiaoqu, echo=print_sql)
                        print2(f"{city_id}-小区id：{xiaoqu_id}")
                        self.signals.export_statu_print.emit(str(f'{index}/{xiaoqu_list_len}'))
                else:
                    print2(f"{baseurl}下无小区信息")
        print2(f"[{self.province_name}]省份下所有城市、区域、子区域、小区信息初始化完成......")

    def stop(self):
        errmsg = "程序被退出"
        print2(errmsg)
        raise Exception(errmsg)

    def to_excel(self):
        current_timestamp = time.time()
        current_timestamp = int(current_timestamp)
        file_path = f'{self.province_name}数据_{current_timestamp}.xlsx'
        lj_base_areas_sql = f"lj_base_areas"
        if self.city_name:
            lj_base_province_sql = f"(select * from lj_base_province where province_name='{self.province_name}' and city_name='{self.city_name}' )"
            file_path = f'{self.province_name}-{self.city_name}数据_{current_timestamp}.xlsx'
            if self.area_name:
                lj_base_areas_sql = f"(select * from lj_base_areas t where region_name='{self.area_name}')"
                file_path = f'{self.province_name}-{self.city_name}-{self.area_name}数据_{current_timestamp}.xlsx'
        else:
            lj_base_province_sql = f"(select * from lj_base_province where province_name='{self.province_name}' )"

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
        ,json_extract(lxd.detail_json,'$.建筑类型') as `建筑类型`
        ,json_extract(lxd.detail_json,'$.房屋总数') as `房屋总数`
        ,json_extract(lxd.detail_json,'$.楼栋总数') as `楼栋总数`
        ,json_extract(lxd.detail_json,'$.绿化率')   as `绿化率`
        ,json_extract(lxd.detail_json,'$.容积率')   as `容积率`
        ,json_extract(lxd.detail_json,'$.交易权属') as `交易权属`
        ,json_extract(lxd.detail_json,'$.建成年代') as `建成年代`
        ,json_extract(lxd.detail_json,'$.用水类型') as `用水类型`
        ,json_extract(lxd.detail_json,'$.用水类型') as `用水类型`
        ,json_extract(lxd.detail_json,'$.用电类型') as `用电类型`
        ,json_extract(lxd.detail_json,'$.挂牌均价') as `挂牌均价`
        ,json_extract(lxd.detail_json,'$.物业费')   as `物业费`
        ,json_extract(lxd.detail_json,'$.经纬度')   as `经纬度`
    from lj_base_xiaoqu t
    left join {lj_base_areas_sql} lba on t.city_id = lba.city_id and t.region_id = lba.region_id and t.sub_region_id = lba.sub_region_id
    left join {lj_base_province_sql} lbp on lba.city_id = lbp.city_id
    left join lj_xiaoqu_detail lxd on t.xiaoqu_id = lxd.xiaoqu_id
    where lbp.province_name = '{self.province_name}'
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
    ;'''
        query_list = db.query(sql)
        result_df = pd.DataFrame(query_list)
        result_df.to_excel(file_path, index=False)
        self.signals.export_statu_print.emit(str(f"{file_path}"))
        print2(f"导出成功:{file_path}")

    def process_elements(self, all_xiaoqu):
        try:
            # current_process = multiprocessing.current_process()
            # current_process.name = "Lianjia_Process"
            xiaoqu_size = len(all_xiaoqu)
            for index, xiaoqu in enumerate(all_xiaoqu):
                if self.run_flag:
                    xiaoqu_id = xiaoqu['xiaoqu_id']
                    db.delete(table='lj_xiaoqu_detail', condition=f" xiaoqu_id = '{xiaoqu_id}'")
                    xiaoqu_url = xiaoqu['xiaoqu_url']
                    # print2(f"{current_process.name}==>[{index}/{xiaoqu_size}]{xiaoqu_url}")
                    print2(f"[{index}/{xiaoqu_size}]{xiaoqu_url}")
                    self.signals.export_statu_print.emit(str(f'{index}/{xiaoqu_size}'))
                    xiaoqu_detail = get_community_detail(url=xiaoqu_url)
                    merged_dict = get_merged_dict(xiaoqu_detail)

                    # [{'label': '建筑类型', 'value': '塔楼/板楼/塔板结合/平房'},
                    # {'label': '房屋总数', 'value': '250户'},
                    # {'label': '楼栋总数', 'value': '7栋'},
                    # {'label': '绿化率', 'value': '15%'},
                    # {'label': '容积率', 'value': '2.2'},
                    # {'label': '交易权属', 'value': '商品房/房改房'},
                    # {'label': '建成年代', 'value': '暂无信息'},
                    # {'label': '供暖类型', 'value': '集中供暖/自采暖'},
                    # {'label': '用水类型', 'value': '民水'},
                    # {'label': '用电类型', 'value': '民电'},
                    # {'label': '挂牌均价', 'value': 11376},
                    # {'label': '物业费', 'value': '0.1至0.45元/平米/月'},
                    # {'label': '经纬度', 'value': '113.676176,34.782529'}]
                    if xiaoqu_detail:
                        insert_detail = {
                            'xiaoqu_id': xiaoqu_id,
                            'detail_json': json.dumps(merged_dict, ensure_ascii=False)
                        }
                        db.insert(table='lj_xiaoqu_detail', data=insert_detail)
                else:
                    print2("程序停止运行......")
                    return
        except Exception as e:
            print2(e)
            return f"Exception in child process: {str(e)}"

    def process_list(self, input_list):
        self.process_elements(input_list)

        # cpu_core_num = psutil.cpu_count(logical=False)
        # split_result = split_list(input_list, cpu_core_num)
        #
        # if sys_platform == 'win32':  # windows系统不采用多进程形式跑任务
        #     process_elements(input_list)
        # else:
        #     p = Pool()
        #     subprocess_results = []
        #     for xiaoqu_list in split_result:
        #         result = p.apply_async(process_elements, args=(xiaoqu_list,))
        #         subprocess_results.append(result)
        #     print2('Waiting for all subprocesses done...')
        #     p.close()
        #     p.join()
        #
        #     for result in subprocess_results:
        #         try:
        #             res = result.get()
        #             if res:
        #                 print2(res)  # 打印子进程的异常信息
        #         except Exception as e:
        #             print2(f"Error in child process: {str(e)}")
        #
        #     print2('All subprocesses done.')

    def get_spider_list(self):
        echo_msg = f"开始采集[{self.province_name}"
        lj_base_areas_sql = f"lj_base_areas"
        if self.city_name:
            echo_msg += f"-{self.city_name}"
            lj_base_province_sql = f"(select * from lj_base_province where province_name='{self.province_name}' and city_name='{self.city_name}' )"
            if self.area_name:
                echo_msg += f"-{self.area_name}"
                lj_base_areas_sql = f"(select * from lj_base_areas t where region_name='{self.area_name}')"
        else:
            lj_base_province_sql = f"(select * from lj_base_province where province_name='{self.province_name}' )"
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
        if len(all_xiaoqu) > 0:
            self.max_num = len(all_xiaoqu)
            return all_xiaoqu
        else:
            print2(f"{self.province_name}-{self.city_name}下没有小区信息可采集.")
            return None

    def spider_by_condition(self):
        self.db_init()
        all_xiaoqu = self.get_spider_list()
        if all_xiaoqu:
            self.process_list(all_xiaoqu)
        else:
            return


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
    print("======================统计信息======================")
    print(statistics_df.to_string(index=False))
    print("===================================================")


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


def run():
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
            ljSpider = LianjiaSpider(province_name=province, city_name=city, area_name=area)
            ljSpider.db_init()
            ljSpider.spider_by_condition()
            ljSpider.to_excel()


def main():
    run()


if __name__ == '__main__':
    main()

    # province = "河南"
    # city = "郑州"
    # area = None
    #
    # ljSpider = LianjiaSpider(province_name=province, city_name=city, area_name=area)
    # ljSpider.db_init()
    # ljSpider.spider_by_condition()
    # ljSpider.to_excel()
