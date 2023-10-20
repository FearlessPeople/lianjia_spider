# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import requests
from lxml import etree
from apps.utils.util_sqlite import SQLiteDB
from apps.utils.util_http import HttpUtils

db = SQLiteDB()


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


def get_base_province():
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
                    print(insertdata)
                    db.insert(table='lj_base_province', data=insertdata)
    else:
        print("Failed to retrieve data from the website.")


def get_sub_region(url):
    result = []
    response = HttpUtils.get(url)
    if response.status_code == 200:
        tree = etree.HTML(response.text)
        a_elements = tree.xpath('//div[@class="position"]/dl/dd/div/div[2]/a')
        for a in a_elements:
            sub_region_name = a.xpath('./text()')[0]
            sub_region_url = a.xpath('./@href')[0]
            sub_region_id = sub_region_url
            result.append({
                "sub_region_id": sub_region_id,
                "sub_region_name": sub_region_name,
                "sub_region_url": sub_region_url
            })
    else:
        print("Failed to retrieve data from the website.")
    return result


def get_base_areas(city_name):
    city = db.select(table='lj_base_province', condition=f" city_name='{city_name}'")
    city = city[0]
    city_id = city['city_id']
    url = city['city_url'] + "/xiaoqu/"
    response = HttpUtils.get(url)
    if response.status_code == 200:
        tree = etree.HTML(response.text)
        a_elements = tree.xpath('//div[@class="position"]/dl/dd/div/div/a')
        for a in a_elements:
            region_name = a.xpath('./text()')[0]
            region_url = a.xpath('./@href')[0]
            region_id = region_url
            region = {
                "city_id": city_id,
                "region_id": region_id,
                "region_name": region_name,
                "region_url": region_url
            }
            sub_regions = get_sub_region(url="https://bj.lianjia.com" + region_url)
            for sub_region in sub_regions:
                result = {**region, **sub_region}
                db.insert(table='lj_base_areas', data=result)
    else:
        print("Failed to retrieve data from the website.")


def main():
    # get_base_province()
    get_base_areas('北京')


if __name__ == '__main__':
    main()
