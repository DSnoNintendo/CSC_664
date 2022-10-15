import mimetypes
import os
import sys
from threading import Thread

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from time import sleep
import urllib
import urllib.request
import requests
from requests.exceptions import InvalidSchema
from time import time
from PIL import Image
import argparse

import shutil

NUM_THREADS = 4


class Excva8r:
    def __init__(self):
        try:
            # try to open ChromeDriver
            browser_options = ChromeOptions()
            browser_options.headless = True
            browser_options.add_argument('--disable-dev-shm-usage')
            browser_options.add_argument('--no-sandbox')
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=browser_options)
            print("Browser is ready")
            self.browserOpen = True
        except ValueError:  # if chrome not available, try firefox
            # try to open FirefoxDriver
            browser_options = FirefoxOptions()
            browser_options.headless = True
            browser_options.add_argument('--disable-dev-shm-usage')
            browser_options.add_argument('--no-sandbox')
            self.driver = webdriver.Firefox(GeckoDriverManager().install(), options=browser_options)
            self.browserOpen = True
        except:
            self.browserOpen = False

        self.timeout = None
        self.max = None
        self.counter = 0
        self.start = None

    def getAll(self, search_term, destination='excav8r/', timeout=300, max=500, as_list=False):
        if as_list:
            img_links = []
            img_links.extend(self.__getDdgElements(search_term))
            img_links.extend(self.__getGoogleElements(search_term))
            return self.__linksToImgs(img_links, max=max)

        self.start = time()
        if not os.path.isdir(destination):
            os.mkdir(destination)

        self.destination = destination
        self.max = max
        self.timeout = timeout
        self.counter = 0
        img_links = []

        if self.counter == max: return

        print("Scraping DuckDuckGo...")
        img_links.extend(self.__getDdgElements(search_term))
        print("Scraping Google...")
        img_links.extend(self.__getGoogleElements(search_term))


        print("Saving Images")
        for link in img_links:
            print(time() - self.start)
            if (time() - self.start > self.timeout):
                print("timeout reached")
                print("%s images found with keyword: %s" % (self.counter, search_term))
                self.driver.quit()
                return
            self.__save(link)

        print("%s images found with keyword: %s" % (self.counter, search_term))

        return

    def getDuckDuckGo(self, search_term, destination='excav8r/', timeout=300, max=1000, as_list=False):
        if as_list:
            img_links = []
            img_links.extend(self.__getDdgElements(search_term))
            return self.__linksToImgs(img_links, max=max)

        self.start = time()

        if not os.path.isdir(destination):
            os.mkdir(destination)

        self.destination = destination
        self.max = max
        self.search_term = search_term
        self.timeout = timeout
        self.counter = 0
        img_links = []

        if self.counter == max: return

        img_links.extend(self.__getDdgElements(search_term))

        for l in self.__divide_list(img_links, NUM_THREADS):
            threads = []
            t = Thread(target=self.__save_list, args=(l, self.start))
            threads.append(t)

        self.__run_threads(threads)

        for link in img_links:
            if max == 0: break
            print(time() - self.start)
            if (time() - self.start > self.timeout):
                print("timeout reached")
                print("%s images found with keyword: %s" % (self.counter, search_term))
                return
            self.__save(link)
            max -= 1

        print("%s images found with keyword: %s" % (self.counter, search_term))

        return self.counter

    def getGoogle(self, search_term, destination='excav8r/', timeout=300, max=1000, as_list = False):
        if as_list:
            img_links = []
            img_links.extend(self.__getGoogleElements(search_term))
            return self.__linksToImgs(img_links, max=max)

        self.start = time()

        if not os.path.isdir(destination):
            os.mkdir(destination)

        self.destination = destination
        self.max = max
        self.search_term = search_term
        self.timeout = timeout
        self.counter = 0

        if self.counter == max: return

        img_links = []

        img_links.extend(self.__getGoogleElements(search_term))

        for link in img_links:
            if max == 0: break
            print(time() - self.start)
            if (time() - self.start > self.timeout):
                print("timeout reached")
                print("%s images found with keyword: %s" % (self.counter, search_term))
                return
            self.__save(link)
            max -= 1

        print("%s images found with keyword: %s" % (self.counter, search_term))

        return self.counter

    def closeBrowser(self):
        if self.browserOpen:
            self.driver.quit()
        else:
            print("Can't close the browser if the browser isn't open")

    def newBrowser(self):
        if not self.browserOpen:
            try:
                # try to open ChromeDriver
                browser_options = ChromeOptions()
                browser_options.headless = True
                browser_options.add_argument('--disable-dev-shm-usage')
                browser_options.add_argument('--no-sandbox')
                self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=browser_options)
                self.browserOpen = True
            except ValueError:  # if chrome not available, try firefox
                # try to open FirefoxDriver
                browser_options = FirefoxOptions()
                browser_options.headless = True
                browser_options.add_argument('--disable-dev-shm-usage')
                browser_options.add_argument('--no-sandbox')
                self.driver = webdriver.Firefox(GeckoDriverManager().install(), options=browser_options)
        else:
            print("Browser already open")

    def __save_list(self, l, t):
        for link in l:
            if self.max == 0: break
            print(time() - self.start)
            if time() - self.start > self.timeout:
                print("timeout reached")
                print("%s images found with keyword: %s" % (self.counter, self.search_term))
                return
            self.__save(link)
            self.max -= 1


    def __run_threads(self, threads):
        for x in threads:
            x.start()
        for x in threads:
            x.join()

    def __getDdgElements(self, search_term):
        print("Scraping DuckDuckGo")
        self.driver.get('https://duckduckgo.com/?q=%s&t=hx&va=g&iar=images' % search_term.replace(' ', '+'))
        footer = self.driver.find_element_by_class_name("footer")

        while not footer.is_displayed():
            self.__scroll()
            self.__moreDdg()

        elements = self.driver.find_elements_by_xpath("//img[contains(@class,'img')]")

        img_links = []

        for image in elements:
            img_links.append(image.get_attribute('src'))

        print(str(len(img_links)) + " image links scraped from DuckDuckGo Images")

        return img_links

    def __linksToImgs(self, img_links, max=1000):
        print("creating %s Image objects" % str(max))
        images = []

        for link in img_links:
            if max == 0: break
            try:
                images.append(Image.open(requests.get(link, stream=True).raw))
                max -= 1
            except InvalidSchema as e:
                pass
        return images




    def __getGoogleElements(self, search_term):
        self.driver.get('http://www.google.com/images?q=' + search_term.replace(' ', '+'))

        while not self.__endReachedGoogle():
            self.__scroll()
            self.__moreGoogle()
            self.__retryGoogle()
            self.__endReachedGoogle()

        elements = self.driver.find_elements_by_tag_name('img')

        img_links = []

        for image in elements:
            if image.get_attribute('src') != None and int(image.get_attribute('height')) > 50:
                img_links.append(image.get_attribute('src'))

        print(str(len(img_links)) + " image links scraped from Google Images")

        return img_links



    def __save(self, img_url):
        print(img_url)
        try:
            if 'jpeg' in img_url:
                urllib.request.urlretrieve(img_url, '%s%s%s.jpg' % (self.destination, self.search_term, self.counter))
                self.counter += 1
            else:
                response = requests.get(img_url)
                content_type = response.headers['content-type']
                ext = mimetypes.guess_extension(content_type)
                file = open('%s%s%s%s' % (self.destination, self.search_term.replace(' ', '_'), self.counter, ext), "wb")
                file.write(response.content)
                file.close()
                self.counter += 1
        except InvalidSchema as e:
            pass


    def __scroll(self):
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        sleep(0.1)

    def __moreGoogle(self):
        xpath = "//input[@value='Show more results']"
        try:
            self.driver.find_element_by_xpath(xpath).click()
            sleep(0.1)
            self.__scroll()
        except Exception as e:
            pass

    def __moreDdg(self):
        xpath = "//span[contains(text(), 'Show More')]"
        try:
            self.driver.find_element_by_xpath(xpath).click()
            sleep(0.1)
            self.__scroll()
        except Exception as e:
            pass

    def __retryGoogle(self):
        xpath = '/html/body/div[2]/c-wiz/div[3]/div[1]/div/div/div/div/div[3]/div[1]/div[2]/div[3]/div/span'
        try:
            self.driver.find_element_by_xpath(xpath).click()
            sleep(0.1)
            self.__scroll()

        except Exception as e:
            pass

    def __endReachedGoogle(self):
        xpath = '//div[@role="heading"]'
        try:
            ele = self.driver.find_element_by_xpath(xpath)
            if ele.text == 'Looks like you\'ve reached the end':
                return True
            return False
        except Exception as e:
            return False

    def __divide_list(self, l, n):

        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]