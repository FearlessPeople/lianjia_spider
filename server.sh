#!/bin/bash

# ------- 不同项目 需要修改这里 -----------------------------------------------------------------------------------
process="/Users/zfang/work/code/rpa/"
service_name="rpa_robot"
gunicorn_config_path="${process}/conf/conf_gunicorn.py"
py_env_activate_path=$(dirname "$(pwd)")"/venv/bin/activate"
# -------------------------------------------------------------------------------------------------------------

red='\033[31m'
blue='\033[34m'
black='\033[30m'
green='\033[32m'
white='\033[37m'
purple='\033[35m'
yellow='\033[33m'
navyblue='\033[36m'
plain='\033[0m'

usage="Usages: flask_server [ start | stop | restart | status | list ]"
echo_usage="$purple    $usage    $plain"
echo_ok="$green   -- [OK]      $plain"
echo_fail="$red   -- [Fail]    $plain"

print_usage() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $echo_usage"
}

process_list() {
    ps -ef | grep "gunicorn" | grep -v 'grep'
}

process_exist() {
    if [ $(ps -ef | grep -c "${process}") -gt 1 ]; then
        return 1
    else
        return 0
    fi
}

process_kill() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $purple  -- Shutting down $service_name ......      $plain   \c"
    pids=$(ps aux | grep ${process} | grep -v 'grep' | awk '{print $2}')
    for pid in $pids; do
        $(kill -9 $pid)
    done
    sleep 1
    process_exist
    if [ $? == 0 ]; then
        echo -e "$echo_ok"
        return 1
    else
        echo -e "$echo_fail"
        return 0
    fi
}

is_running() {
    process_exist
    if [ $? == 1 ]; then
        echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $green $service_name is running!     $plain"
        return 1
    else
        echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $yellow $service_name is not running!     $plain"
        return 0
    fi
}

start_service() {
    source "$py_env_activate_path"
    gunicorn -c $gunicorn_config_path wsgi:app
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $purple Starting $service_name   ......     $plain   \c"
    sleep 1
    process_exist
    if [ $? == 1 ]; then
        echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $echo_ok"
        return 1
    else
        echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $echo_fail"
        return 0
    fi
}

cmd=$1

if [ ! -n "$1" ]; then
    print_usage
    exit 0
fi

now_time=$(date "+%Y-%m-%d %H:%M:%S")

# start
if [ "$cmd" = start ]; then
    is_running
    if [ $? == 0 ]; then
        start_service
        is_running
    fi
# status
elif [ "$cmd" = status ]; then
    is_running
# stop
elif [ "$cmd" = stop ]; then
    process_kill
    is_running
# restart
elif [ "$cmd" = restart ]; then
    is_running
    if [ $? == 1 ]; then
        process_kill
        if [ $? == 1 ]; then
            start_service
        fi
    else
        start_service
    fi
    is_running
# list
elif [ "$cmd" = list ]; then
    process_list
# 未匹配的
else
    print_usage
fi

[ 0 -eq 1 ] && {
    echo -e "\033[40;37m oldboy trainning \033[0m" 黑底白字 字体颜色匹配上面的,自己更改
    echo -e "\033[41;37m oldboy trainning \033[0m" 红底白字
    echo -e "\033[42;37m oldboy trainning \033[0m" 绿底白字
    echo -e "\033[43;37m oldboy trainning \033[0m" 黄底白字
    echo -e "\033[44;37m oldboy trainning \033[0m" 蓝底白字
    echo -e "\033[45;37m oldboy trainning \033[0m" 紫底白字
    echo -e "\033[46;37m oldboy trainning \033[0m" 天蓝白字
    echo -e "\033[47;30m oldboy trainning \033[0m" 白底黑字
}
