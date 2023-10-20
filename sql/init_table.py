# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version    : v1.0
@author     : fangzheng
@contact    : fangzheng@rp-pet.cn
@software   : PyCharm
@filename   : init_table.py
@create time: 2023/10/10 5:51 PM
@modify time: 2023/10/10 5:51 PM
@describe   : 
-------------------------------------------------
"""

init_sql = """
CREATE TABLE IF NOT EXISTS `lj_base_province`
(
    `id`            INTEGER PRIMARY KEY AUTOINCREMENT,
    `province_name` varchar(255),
    `city_id`       varchar(255),
    `city_name`     varchar(255),
    `city_url`      varchar(255),
    `start_time`    DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    `end_time`      DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    `create_time`   DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    `update_time`   DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
);

-- 城市区域表
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
    `start_time`      DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    `end_time`        DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    `create_time`     DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime')),
    `update_time`     DATETIME DEFAULT (datetime(CURRENT_TIMESTAMP, 'localtime'))
);

-- 所有小区表
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

-- 每个小区采集详细数据表
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
