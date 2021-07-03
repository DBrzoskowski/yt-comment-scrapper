import csv
import json
from time import sleep
from selenium import webdriver

JSON_FILE = 'settings.json'

MOVED_DOWN = 1000

DRIVER_PATH = './chromedriver'
COOKIE_ACCEPT = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/span"
SOUND_OFF = '//*[@id="movie_player"]/div[28]/div[2]/div[1]/span/button'
MOVIE_PLAYER = '//*[@id="movie_player"]'


op = webdriver.ChromeOptions()
op.add_argument('headless')   # disables the browser


def get_data_from_json(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)


class CommentScrapper:
    def __init__(self, json_data):
        self.json_data = json_data
        self.clean_data = []
        if self.json_data.get('open_browser'):
            self.driver = webdriver.Chrome(DRIVER_PATH)
        else:
            self.driver = webdriver.Chrome(DRIVER_PATH, options=op)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(1920, 1200)  # setup default browser size
        self.driver.get(self.json_data.get("video_url"))
        sleep(1)
        self.driver.find_element_by_xpath(COOKIE_ACCEPT).click()
        self.driver.find_element_by_xpath(SOUND_OFF).click()  # mute
        self.driver.find_element_by_xpath(MOVIE_PLAYER).click()  # stop video
        sleep(2)

    def check_all_comments_load(self):
        loaded = self.driver.find_element_by_id("continuations").find_elements_by_tag_name("dom-if")
        return True if loaded else False

    def loading_comments(self):
        x = 0
        y = self.driver.execute_script("return document.documentElement.scrollHeight")

        while self.check_all_comments_load():
            sleep(1)
            self.driver.execute_script(f"window.scrollTo({x}, {y});")
            sleep(1)
            x = y
            y += MOVED_DOWN

    def clean_data_append(self, comment_data):
        result = []

        if len(comment_data) >= 7:
            # Skip the information about the comment is pinned
            skip_pinned = comment_data[1:]
            result = skip_pinned[:-2]

        # without likes or with likes
        if len(comment_data) == 6:
            result = comment_data[:-2]
        elif len(comment_data) == 4 or len(comment_data) == 5:
            result = comment_data[:-1]
        else:
            print(comment_data)

        if len(result) == 4:
            self.clean_data.append(result)
        elif len(result) == 3:
            # when no likes change to 0
            result.append('0')
            self.clean_data.append(result)
        else:
            pass

    def open_replies(self, comment):
        x1, y2 = comment.location.values()
        self.driver.execute_script(f"window.scrollTo({x1}, {y2 - 150});")
        sleep(2)
        comment.click()
        sleep(1)

    def save_clean_data(self, comments, comment_type):
        for index, comment in enumerate(comments, start=1):
            if comment_type == "REPLIES":
                self.open_replies(comment)
            else:
                comment_data = comment.text.split('\n')
                self.clean_data_append(comment_data)
            print(f"[GET] {comment_type} Comment - {int(index * 100 / len(comments))}%")

        # Get all replies id's from first comment when open's
        sleep(1)
        cd = comments[0].find_elements_by_xpath('//*[@id="contents"]/ytd-comment-renderer')
        [self.clean_data_append(i.text.split('\n')) for i in cd if i != '']

    def get_replies(self, comments):
        replies = comments[0].find_elements_by_xpath('//*[@id="more-replies"]')
        self.save_clean_data(replies, "REPLIES")

    def get_data_from_comments(self):
        self.loading_comments()

        comments = self.driver.find_element_by_id("contents").find_elements_by_tag_name("ytd-comment-thread-renderer")
        self.save_clean_data(comments, "NORMAL")
        self.get_replies(comments)
        self.save_data_to_csv()

    def save_data_to_csv(self):
        csv_file = None
        csv_end = self.json_data.get('csv_file_name')
        if csv_end.endswith('.csv'):
            csv_file = csv_end
        else:
            csv_file += ".csv"

        with open(csv_file, 'w', encoding='UTF8', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'When', 'Comment', 'Likes'])
            [writer.writerow(i) for i in self.clean_data]


json_data = get_data_from_json(JSON_FILE)
scrapper = CommentScrapper(json_data)
scrapper.get_data_from_comments()
