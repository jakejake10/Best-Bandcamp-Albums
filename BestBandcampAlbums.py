
from bs4 import BeautifulSoup
import requests
import sys
import subprocess
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from tkinter import Tk, Button, Entry
import urllib3
urllib3.disable_warnings()


def temp_ln(pInput):
    sys.stdout.write('\r')
    sys.stdout.write(pInput)
    sys.stdout.flush()


def end_ln():
    sys.stdout.write('\n')
    sys.stdout.flush()




#GET ALBUM URLs TO CHECK /////////////////////////////////////////////


class BcampSearch:
    def __init__(self, master):
        self.master = master
        master.title("BcampSearch")

        self.e_1 = Entry(master, width=100)
        self.e_1.insert(0, "https://bandcamp.com/?g=all&s=top&p=0&gn=0&f=all&w=0")
        self.e_1.pack()

        self.e_2 = Entry(master)
        self.e_2.insert(0, "0")
        self.e_2.pack()

        self.e_3 = Entry(master)
        self.e_3.insert(0, "2")
        self.e_3.pack()

        self.guess_button = Button(master, text="Get Albums", command=self.get_albums)
        self.guess_button.pack()
        

    def get_albums(self):
        start = int(self.e_2.get())
        end = int(self.e_3.get())
        url = str(self.e_1.get())
        root.destroy()

        srchUrls = []
        albUrls = []
        goodAlbUrls = []

        pgs = range(start, end + 1)
        if "/tag/" in url:
            if "?" in url:
                url = re.search('(.*?)\?', url)
                url = url[1]

            for i in pgs:
                if i == 1:
                    srchUrls.append(url)
                else:
                    srchUrls.append('{}?page={}'.format(url, i))

            # album url generation////////////////////////////////////////
            tag = re.search(r'(?<=tag/)(.*)', url)
            tag = tag[1]
            print('gathering album urls tagged {}...'.format(tag))

            for url in srchUrls:
                result = requests.get(url, verify=False)
                c = result.content
                soup = BeautifulSoup(c, "html.parser")
                for li in soup.find_all(class_="item"):
                    albUrls.append(li.a.get('href'))

        elif "/tag/" not in url and ".com" in url:
            category = re.search('(?<=\?g=)(.*?)(?=&)', url)
            print('gathering pages for {}...'.format(category.group(1)))

            for i in pgs:
                srchUrls.append(re.sub(r"(?<=&p=)(\d+)", str(i), url))

            for url in srchUrls:
                temp_ln('checking {}...'.format(url))
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument("--log-level=3")
                driver = webdriver.Chrome(executable_path='C:\\drivers\\chromedriver.exe', options=options)
                driver.get(url)
                #albums = driver.find_elements_by_css_selector('a.item-title')
                albums = WebDriverWait(driver, 30).until(expected_conditions.visibility_of_all_elements_located((By.XPATH, "//a[@class='item-title']")))
                
                for a in albums:
                    albUrls.append(a.get_attribute("href"))
                  
                    
                    

        else:

            for i in pgs:
                srchUrls.append('https://bandcamp.com/tag/{}?page={}&sort_field=pop'.format(url, i))

            # album url generation////////////////////////////////////////

            print('gathering album urls tagged {}...'.format(url))

            for url in srchUrls:
                result = requests.get(url, verify=False)
                c = result.content
                soup = BeautifulSoup(c, "html.parser")
                for li in soup.find_all(class_="item"):
                    albUrls.append(li.a.get('href'))

        temp_ln('found {} albums'.format(len(albUrls)))
        end_ln()
        print('checking albums...')

        checked = 0
        found = 0
        temp_ln('checked: {}, found:{}'.format(checked, found))
        for url in albUrls:
            temp_ln('checked: {}, found:{}'.format(checked, found))
            aPg = requests.get(url, verify=False)
            aPgC = aPg.content
            soup2 = BeautifulSoup(aPgC, "html.parser")
            if soup2.findAll(class_="more-writing"):
                goodAlbUrls.append(url)
                found += 1
            checked += 1

        if len(goodAlbUrls) != 0:
            launch = " ".join(map(str, goodAlbUrls))
            command = "cmd /c start chrome {} --new-window".format(launch)
            subprocess.Popen(command, shell=True)
    


root = Tk()
my_gui = BcampSearch(root)
root.mainloop()
