# -*- coding: utf-8 -*-

# Redis配置
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379

# 爬取目标
TARGETS = (
    {
        ### 需要爬取的页面
        "url": "http://bbs.stuhome.net/forum.php"
               "?mod=forumdisplay&fid=61&filter=typeid&typeid=290",
        ### 登录信息
        "login":
        {
            "url": "http://bbs.stuhome.net/member.php"
                   "?mod=logging&action=login",
            "data":
            {
                "username": "yourname",
                "password": "yourpassword",
                "loginfield": "username",
                "loginsubmit": "true"
            }
        },
        "headers":
        {
            "user-agent": "Mozilla/5.0 (Windows NT 5.1) "
                          "AppleWebKit/536.11 (KHTML, like Gecko) "
                          "Chrome/20.0.1132.57 Safari/536.11",
        },
    },
    )

# 关键字
KEYWORDS = ["自行车", "小轮车", "山地车", "公路车"]
EXCLUDE_KEYWORDS = ["求", "买"]

# 邮件发送
MAIL_HOST = "mail host"
MAIL_SUBJECT = "subject"
MAIL_FROM = "from"
MAIL_TO = "to"
MAIL_USER = "username"
MAIL_PASSWORD = "password"

# 任务时间间隔(分钟)
INTERVAL = 1
