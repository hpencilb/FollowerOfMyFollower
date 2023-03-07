import json
import time

import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self):
        self.user_page_prefix = "https://weibo.com/p/100505"
        self.follower_suffix = "/follow?relate=fans"
        self.page_count = "&page="
        self.follower_attr = ("uid=", "fnick=")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/109.0",
            "Cookie": #FIXME
        }

    def get_user_followers(self, user_id, page=1, is_main=False):
        output = []
        if is_main:
            user_page_url = f"https://weibo.com/{user_id}/fans?type=&Pl_Official_RelationFans__83_page={page}"
        else:
            if page == 1:
                user_page_url = self.user_page_prefix + str(user_id) + self.follower_suffix
            else:
                user_page_url = self.user_page_prefix + str(user_id) + self.follower_suffix + self.page_count + \
                                str(page)
        r = requests.get(user_page_url, headers=self.headers)
        if r.url.startswith('https://passport.weibo.com'):
            print("Cookie expired!")
        bs = BeautifulSoup(r.text, "lxml")
        for s in bs.find_all("script"):
            if s.text.startswith("FM.view(") and "PCD_connectlist" in s.text:
                contents = s.text[8:-1]
                json_contents = json.loads(contents)
                if json_contents.get("html"):
                    f_bs = BeautifulSoup(json_contents.get("html"), "lxml")
                    follow_list = f_bs.find("ul", class_="follow_list")
                    if follow_list:
                        followers = follow_list.find_all("li", class_="follow_item S_line2")
                    else:
                        continue
                    for f in followers:
                        uid, fnick = '', ''
                        if action := f.get("action-data"):
                            attrs = action.split("&")
                            for attr in attrs:
                                if attr.startswith("uid="):
                                    uid = attr.replace("uid=", '')
                                if attr.startswith("fnick="):
                                    fnick = attr.replace("fnick=", '')
                        output.append((uid, fnick))
                    w_pages = f_bs.find("div", class_="W_pages")
                    if w_pages:
                        pages = w_pages.find_all('a', class_="S_txt1")
                        if page == 1:
                            max_page = 0
                            for page in pages:
                                if page.text.isnumeric():
                                    page_num = int(page.text)
                                    if page_num > max_page:
                                        max_page = page_num
                                    if max_page > 10:
                                        max_page = 10
                            print(f"page: 1/{max_page}")
                            for i in range(2, max_page + 1):
                                time.sleep(2)
                                print(f"page: {i}/{max_page}")
                                output.extend(self.get_user_followers(user_id, i, is_main))
        return list(set(output))


if __name__ == "__main__":
    crawler = Crawler()
