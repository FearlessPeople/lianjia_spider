# -*- coding: utf-8 -*-


import requests
from lxml import etree

url = 'https://www.lianjia.com/city/'
response = requests.get(url)

if response.status_code == 200:
    # 创建一个 XPath 解析对象
    tree = etree.HTML(response.text)
    # # 所有省份
    # shenfen = tree.xpath('//div[@class="city_province"]/div/text()')
    # print(shenfen)
    # # 所有城市
    # city = tree.xpath('//div[@class="city_province"]/ul/li/a/text()')
    # print(city)
    # # 每个城市的链接地址
    # city_href = tree.xpath('//div[@class="city_province"]/ul/li/a/@href')
    # print(city_href)
    province_elements = tree.xpath('//div[@class="city_province"]')
    for province in province_elements:
        province_name = province.xpath('./div/text()')
        if province_name:
            province_name = province_name[0]
            city_lists = province.xpath('./ul/li')
            for city in city_lists:
                city_name = city.xpath('./a/text()')[0]
                city_url = city.xpath('./a/@href')[0]
                print(f"{province_name}-{city_name}-{city_url}")




else:
    print("Failed to retrieve data from the website.")
