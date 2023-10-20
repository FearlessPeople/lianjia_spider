# -*- coding: utf-8 -*-
import re
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class TimeFmt:
    YYYYmmddHHMMSS = '%Y%m%d%H%M%S'
    mmddHH = '%m%d%H'
    hh_mm_ss = '%H:%M:%S'
    YYYY_mm_dd_HH_MM_SS = '%Y-%m-%d %H:%M:%S'
    YYYY_mm_dd_HH_MM_SS_f = '%Y-%m-%d %H:%M:%S.%f'
    YYYY_mm_dd_HH_MM = '%Y-%m-%d %H:%M'
    YYYY_mm_dd = '%Y-%m-%d'
    YYYY_mm = '%Y-%m'


class DateUtil:
    @staticmethod
    def time_stamp():
        """
        获取当前时间戳
        :return:
        """
        return int(time.mktime(datetime.now().timetuple()))

    @staticmethod
    def now_ymd():
        """
        获取当前日期YYYY_mm_dd格式
        :return: 字符串形式YYYY_mm_dd日期
        """
        return datetime.now().strftime(TimeFmt.YYYY_mm_dd)

    @staticmethod
    def now_time(*args, echo=False):
        """
        打印当前时间
        :param args:
        :param echo:
        :return:
        """
        now = datetime.now()
        if echo:
            print('-- now_time:', now)
        for item in args:
            print(item)
        return now

    @staticmethod
    def now_time_str():
        """
        获取当前日期YYYY_mm_dd_HH_MM_SS_f格式
        :return: 字符串形式YYYY_mm_dd_HH_MM_SS_f日期
        """
        return datetime.now().strftime(TimeFmt.YYYY_mm_dd_HH_MM_SS_f)

    @staticmethod
    def yestday():
        """
        获取昨日日期
        :return: datetime格式昨日日期
        """
        current_date = datetime.now()
        return current_date - timedelta(days=1)

    @staticmethod
    def yesrtday_str(days=1, fmt=TimeFmt.YYYY_mm_dd):
        """
        获取昨日YYYY_mm_dd格式日期
        :param days:
        :return:
        """
        yesrtday_dt = datetime.now() - timedelta(days)
        return yesrtday_dt.strftime(fmt)

    @staticmethod
    def yestday_timestamp(hour=0, minute=0, second=0):
        """
        获取昨日日期时间戳格式
        :return:
        """
        current_date = datetime.now()
        yesterday_date = current_date - timedelta(days=1)
        yesterday_date = yesterday_date.replace(hour=hour, minute=minute, second=second, microsecond=0)
        return yesterday_date.timestamp()

    @staticmethod
    def fmt(any_time, fmt):
        """
        根据指定格式格式化指定日期
        :param any_time: 指定日期
        :param fmt: 指定格式
        :return:
        """
        return any_time.strftime(fmt)

    @staticmethod
    def fmt_hh_mm_ss(any_time=datetime.now()):
        """
        根据传入时间格式化为hh_mm_ss
        :param any_time:
        :return:
        """
        return any_time.strftime(TimeFmt.hh_mm_ss)

    @staticmethod
    def fmt_yyyy_mm_dd(any_time=datetime.now()):
        """
        根据传入时间格式化为YYYY_mm_dd
        :param any_time:
        :return:
        """
        return any_time.strftime(TimeFmt.YYYY_mm_dd)

    @staticmethod
    def fmt_yyyy_mm_dd_hh_mm(any_time=datetime.now()):
        """
        根据传入时间格式化为YYYY_mm_dd_HH_MM
        :param any_time:
        :return:
        """
        return any_time.strftime(TimeFmt.YYYY_mm_dd_HH_MM)

    @staticmethod
    def fmt_yyyy_mm_dd_hh_mm_ss(any_time=datetime.now()):
        """
        根据传入时间格式化为YYYY_mm_dd_HH_MM_SS
        :param any_time:
        :return:
        """
        return any_time.strftime(TimeFmt.YYYY_mm_dd_HH_MM_SS)

    @staticmethod
    def this_month_total_days(any_time=datetime.now()):
        """
        当月总天数
        :param any_time:
        :return:
        """
        ndt = any_time.replace(day=28) + timedelta(days=4)
        ndt = ndt.replace(day=1) - timedelta(days=1)
        return ndt.day

    @staticmethod
    def this_month_day_1(any_time=datetime.now()):
        """
        本月1号
        :param any_time:
        :return:
        """
        return any_time.replace(day=1)

    @staticmethod
    def this_month_last_day(any_time=datetime.now()):
        """
        本月最后一天
        :param any_time:
        :return:
        """
        next_month = any_time.replace(day=28) + timedelta(days=4)
        return next_month - timedelta(days=next_month.day)

    @staticmethod
    def last_month_the_same_day(any_time=datetime.now()):
        """
        上个月同一天
        :param any_time:
        :return:
        """
        cur_day = any_time.day
        last_month = any_time.replace(day=1) - timedelta(days=1)
        try:
            return last_month.replace(day=cur_day)
        except Exception as e:  # 如果上个月没有对应日期，例如 2月只有28天情况，则返回上月最后一天
            if str(e) == 'day is out of range for month':
                return any_time.replace(day=1) - timedelta(days=1)

    @staticmethod
    def last_month_day_1(any_time=datetime.now()):
        """
        上个月1号
        :param any_time:
        :return:
        """
        last_month = any_time.replace(day=1) - timedelta(days=1)
        return last_month.replace(day=1)

    @staticmethod
    def up_month_day_1():
        """
        上月第一天
        :return:
        """
        current_date = datetime.now()
        current_month = current_date.month
        # 计算上个月的月份
        last_month = current_month - 1 if current_month != 1 else 12
        # 计算上个月的年份
        last_year = current_date.year - 1 if current_month == 1 else current_date.year
        # 构造上个月的第一天日期
        first_day_of_last_month = datetime(last_year, last_month, 1)
        return first_day_of_last_month

    @staticmethod
    def up_month_yesrtday():
        """
        获取上月的昨天同期日期：
        1、例如今日是2023-07-18，则返回2023-06-17
        2、如果是月初1号2023-07-01，则返回上月月初1号2023-06-01
        :return:
        """
        current_date = datetime.now()
        current_month = current_date.month
        # 计算上个月的月份和年份
        last_month = current_month - 1 if current_month != 1 else 12
        last_year = current_date.year - 1 if current_month == 1 else current_date.year
        last_day = current_date.day - 1 if current_date.day != 1 else current_date.day
        return datetime(last_year, last_month, last_day)

    @staticmethod
    def last_month_last_day(any_time=datetime.now()):
        """
        上个月最后一天
        :param any_time:
        :return:
        """
        return any_time.replace(day=1) - timedelta(days=1)

    @staticmethod
    def get_the_same_time(months, day):
        """
        # 获取 前后月份 第几天 的当前时间
        :param months: 0 当前月份 正整数n 下n个月份 负整数 上n个月份
        :param day: 0 月份的第几天 注意 特殊月份的天数
        :return:
        """
        dt = datetime.now() + relativedelta(months=months, day=day)
        return dt

    @staticmethod
    def get_relative_time(any_time, year=None, month=None, day=None, hour=None, minute=None):
        """
        计算 相对时间，应用举例如下：
        now_time = datetime.now()
        dt = DateUtil.get_relative_time(now_time, year=-2, month=9, day=-3, hour=-2, minute=-77)
        """
        params = {'year': year, 'month': month, 'day': day, 'hour': hour, 'minute': minute}
        for key, value in params.items():
            if value and isinstance(value, int):
                if key == 'year':
                    any_time = any_time.replace(year=any_time.year + value)
                elif key == 'month':
                    date = any_time
                    year = date.year
                    month = date.month
                    day = date.day
                    if month == 1:
                        month = 12
                        year -= 1
                    else:
                        month -= 1
                    if day == 31 and month in (4, 6, 9, 11):
                        day = 30
                    if day > 28 and month == 2:
                        day = 29 if year % 4 == 0 else 28

                    any_time = datetime.strptime(
                        '%s-%s-%s %s:%s:%s' % (year, month, day, date.hour, date.minute, date.second),
                        '%Y-%m-%d %H:%M:%S')
                    # any_time = any_time.replace(month=any_time.month + value)
                elif key == 'day':
                    any_time += timedelta(days=value)
                elif key == 'hour':
                    any_time = any_time + timedelta(hours=value)
                elif key == 'minute':
                    any_time = any_time + timedelta(minutes=value)
        return any_time

    @staticmethod
    def datetime_to_unix_int(date_time=datetime.now()):
        """
        # 将时间格式转换为int类型UNIX 时间
        :param date_time:
        :return:
        """
        dtime = date_time.timetuple()
        ans_time = time.mktime(dtime)
        unix_time_int = int(ans_time)
        return unix_time_int

    @staticmethod
    def datetime_to_str(date_time, format_str):
        """
        格式化日期
        :param date_time: 需格式化日期
        :param format_str: 格式
        :return:
        """
        if date_time is not None and format_str is not None:
            return date_time.strftime(format_str)
        else:
            return ""

    @staticmethod
    def replace_t(date_str):
        if date_str is not None and date_str != '':
            if date_str.find('.') > 0:
                date_str = date_str[0: date_str.find('.')]
            date_str = date_str.replace('T', ' ')
            return date_str
        else:
            return ""

    @staticmethod
    def now_str(format_str=TimeFmt.YYYY_mm_dd):
        return datetime.now().strftime(format_str)

    @staticmethod
    def datetime_to_zh_ymd(date_time):
        return date_time.strftime('%Y{0}%m{1}%d{2}').format(*'年月日')

    @staticmethod
    def datetime_to_zh_ymdhms(date_time):
        return date_time.strftime('%Y{0}%m{1}%d{2} %H{3}%M{4}').format(*'年月日时分')

    @staticmethod
    def get_week_day(date=datetime.now()):
        """
        获取当前日期的星期
        :param date:
        :return: 返回dict(0: '星期一')
        """
        week_day_dict = {
            0: '星期一',
            1: '星期二',
            2: '星期三',
            3: '星期四',
            4: '星期五',
            5: '星期六',
            6: '星期天',
        }
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
        index = date.weekday()
        return index, week_day_dict[index]

    @staticmethod
    def get_week_scope(date_x, n_week=0, week_start=1, return_str_type=True, return_items=False):
        if isinstance(date_x, str):
            date_x = datetime.strptime(date_x, '%Y-%m-%d')
        week_x, week_off = date_x.weekday(), 0
        if week_x + 1 < week_start:
            week_off = 1
        week_start = date_x + timedelta(days=(-week_x + (week_start - 1) + 7 * (n_week - week_off)))
        week_end = week_start + timedelta(days=6)

        if return_items:
            week_scope = [week_start]
            days = 1
            while len(week_scope) < 7:
                week_scope.append(week_start + timedelta(days=days))
                days += 1
        else:
            week_scope = week_start, week_end

        if return_str_type:
            week_scope = [item.strftime('%Y-%m-%d') for item in week_scope]
        return week_scope
        # print(get_week_start_and_end('2021-03-10', n_week=0, week_start=3))

    @staticmethod
    def create_date_list(date_start=None, date_end=None, num=None):
        temp_ymd = '%Y-%m-%d'
        if date_start is None:
            date_start = datetime.now().strftime(temp_ymd)
        date_start = datetime.strptime(date_start, temp_ymd)
        if date_end:
            date_end = datetime.strptime(date_end, temp_ymd)
        date_list = list()
        date_list.append(date_start.strftime(temp_ymd))
        if date_end:
            while date_start < date_end:
                date_start += timedelta(days=+1)
                date_list.append(date_start.strftime(temp_ymd))
        elif num:
            while num > 1:
                date_start += timedelta(days=1)
                date_list.append(date_start.strftime(temp_ymd))
                num -= 1
        return date_list

    @staticmethod
    def format_date_by_str(date_string, target_pattern='%Y-%m-%d'):
        # 日期格式转换(yyyy-MM-dd HH:mm:ss,yyyy/MM/dd,yyyyMMdd
        patterns = {'%Y-%m-%d %H:%M:%S': r'\d{4}-[01]\d-[0123]\d\s{1,2}[012]\d:[0-5]\d:[0-5]\d',
                    '%Y/%m/%d': r'\d{4}/[01]\d/[0123]\d', '%Y%m%d': r'\d{4}[01]\d[0123]\d'}
        for key, value in patterns.items():
            if re.match(value, date_string, re.M | re.I):
                # 字符转换为tuple
                time_tuple = time.strptime(date_string, key)
                # tuple转化为字符串
                return time.strftime(target_pattern, time_tuple)
            else:
                pass
        return ''

    @staticmethod
    def last_last_month_start():
        """
        上上月初，例如：今天是2023-07-20，则返回2023-05-01
        """
        current_date = datetime.now()
        last_month = current_date.replace(day=1) - timedelta(days=1)
        # 取上上月
        last_last_month = last_month - relativedelta(months=1)
        last_last_month_start = last_last_month.replace(day=1)
        return last_last_month_start

    @staticmethod
    def last_last_month_day(times=None):
        """
        上上月同期，例如：今天是2023-07-20，则返回2023-05-20，如果5月天数小于今日，则返回5月月末
        :param times:
        :return:
        """
        current_time = datetime.now()
        if times:
            current_time = times

        curr_day_num = current_time.day
        # 设置为本月1号，再减1天，就到上月末
        last_month = current_time.replace(day=1) - timedelta(days=1)
        # 设置为本月1号，再减1天，就到上上月末
        last_last_date = last_month.replace(day=1) - timedelta(days=1)

        last_day_num = last_last_date.day
        if curr_day_num < last_day_num:
            last_last_date = last_last_date.replace(day=curr_day_num)

        return last_last_date

    @staticmethod
    def is_weekend(dt=datetime.now()):
        """
        判断传入的datetime类型参数是否周末
        :param dt:
        :return: 周末返回True，否则返回False
        """
        weekday = dt.weekday()
        # 判断是否是周六（5表示周六）或周日（6表示周日）
        if weekday == 5 or weekday == 6:
            return True
        else:
            return False

    @staticmethod
    def getweek(dt=datetime.now()):
        """
        返回传入的datetime类型参数对应的周末
        :param dt:
        :return: 0:周一  ***  6:周日
        """
        return dt.weekday()

    @staticmethod
    def get_day_index(day):
        """
        获取传入day数字在当月是第几个索引值，例如：传入8返回1，传入18返回2，传入28返回3
        :param day:
        :return:
        """
        today = datetime.now()
        year = today.year
        month = today.month

        # 创建当月第一天的日期对象
        first_day_of_month = datetime(year, month, 1)

        # 计算指定日期的索引值
        day_index = (day - first_day_of_month.day) // 10

        return day_index
