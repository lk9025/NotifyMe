# -*- coding: utf-8 -*-

from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from apscheduler.scheduler import Scheduler
from config import *

import smtplib
import requests
import redis
import time


def get_time():
    return time.strftime("%Y-%m-%d %A %X %Z", time.localtime(time.time()))


class Notifier:
    def __init__(self):
        self._redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
        self._targets = TARGETS

    def _create_session(self, target):
        session = requests.session()
        session.headers.update(target["headers"])
        ### 获得formhash值
        login_url = target["login"]["url"]
        login_page = session.get(login_url).text
        login_soup = BeautifulSoup(login_page)
        formhash = login_soup.find("input", attrs={"name": "formhash"})
        ### 登录
        post_data = target["login"]["data"]
        post_data["formhash"] = formhash
        session.post(login_url, post_data)

        return session

    def _has_any_keyword(self, title, keywords):
        return any([keyword in title for keyword in keywords])

    def _get_new_posts_from_page(self, page):
        posts = []
        page_soup = BeautifulSoup(page)
        ### 遍历页面上每个帖子
        for tag in page_soup.find_all("a"):
            if "class" in tag.attrs and tag["class"] == ["s", "xst"]:
                title = tag.string.encode("utf-8")
                url = tag["href"].encode("utf-8")
                post = {"title": title, "url": url}
                ### 新帖判断：
                ### 1.标题中至少包含KEYWORDS中的一个关键字
                ### 2.标题中不包含EXCLUDE_KEYWORDS中的任何关键字
                ### 3.该帖在redis中不存在，也即还没被爬取过
                if self._has_any_keyword(title, KEYWORDS) and\
                        not self._has_any_keyword(title, EXCLUDE_KEYWORDS) and\
                        not self._redis.sismember("outdated_posts", post):
                    posts.append(post)

        return posts

    def _notify(self, posts):
        if not posts:
            print "New posts not found. %s" % get_time()
            return

        content = ""
        for post in posts:
            content += '<br><a href="%s">%s</a></br>' %\
                       (post["url"],  post["title"])

        mail = MIMEText(content, "html", "utf-8")
        mail["Accept-Language"] = "zh-CN"
        mail["Accept-Charset"] = "ISO-8859-1, utf-8"
        mail["Subject"] = MAIL_SUBJECT
        mail["From"] = MAIL_FROM
        mail["To"] = MAIL_TO

        try:
            smtp = smtplib.SMTP()
            smtp.connect(MAIL_HOST)
            smtp.starttls()
            smtp.login(MAIL_USER, MAIL_PASSWORD)
            smtp.sendmail(MAIL_FROM, MAIL_TO, mail.as_string())
            print "Send email successfully. %s" % get_time()
        except Exception, e:
            print "Fail to send email: %s. %s" % (str(e), get_time())
        finally:
            smtp.close()

    def _update_redis(self, posts):
        for post in posts:
            self._redis.sadd("outdated_posts", post)

    def run(self):
        posts = []

        for target in self._targets:
            session = self._create_session(target)
            page = session.get(target["url"]).text
            posts.extend(self._get_new_posts_from_page(page))

        self._notify(posts)
        self._update_redis(posts)


if __name__ == "__main__":
    notifier = Notifier()
    notifier.run()

    scheduler = Scheduler(daemonic=False)
    scheduler.add_interval_job(notifier.run, minutes=INTERVAL)
    scheduler.start()
