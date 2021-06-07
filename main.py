from time import sleep
from selenium import webdriver

driver_path = './chromedriver'


class CommentScrapper:
    def __init__(self, video_url):
        self.video_url = video_url
        self.driver = webdriver.Chrome(driver_path)
        self.driver.get(video_url)
        sleep(1)
        self.driver.find_element_by_xpath("/html/body/div/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/span").click()
        self.driver.find_element_by_xpath('//*[@id="movie_player"]').click()
        sleep(10)


CommentScrapper('https://www.youtube.com/watch?v=uz9ki7DiTwk')