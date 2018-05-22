# -*- coding: utf-8 -*-

import functools
import io
import json
import os
import sys
import time
import unittest

import colorlabels as cl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

assert sys.version_info[0] >= 3

# Load all config variables into the global namespace.
with open('config.json', 'r') as f:
    globals().update(json.load(f))


def pretty_msg_test_func(func):
    '''Function decorator to make a test function emit pretty messages.'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        p = cl.progress("Running test case '%s'..." % func.__name__, cl.PROGRESS_SPIN, erase=True)

        try:
            func(*args, **kwargs)
        except Exception:
            p.stop()
            cl.error("Test case '%s' failed." % func.__name__)
            raise
        else:
            p.stop()
            cl.success("Test case '%s' passed." % func.__name__)

    return wrapper


def pretty_msg_test_class(cls):
    '''Class decorator to make all test functions in a test class emit pretty messages.'''
    for func in filter(callable, (getattr(cls, n) for n in dir(cls) if n.startswith('test_'))):
        setattr(cls, func.__name__, pretty_msg_test_func(func))

    return cls


@pretty_msg_test_class
class TestBookStore(unittest.TestCase):
    usr_uname = 'testuser'
    usr_pwd = '000000'
    admin_uname = 'admin'
    admin_pwd = 'NF3z075ZCqmAiQCP'

    @classmethod
    def setUpClass(cls):
        '''Initialize the web driver only once.
        Doing this repeatedly in `setUp()` could be time-consuming.'''
        cls.driver = webdriver.Chrome(webdriver_path, service_log_path=os.devnull)
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(webdriver_wait_time)
        cls.wait = WebDriverWait(cls.driver, webdriver_wait_time)

    def setUp(self):
        # load web page
        self.driver.get(target_url)
        time.sleep(2)

    def login(self, admin=False):
        # trigger login
        self.driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul/li[2]/a').click()
        # fill-in form, submit
        if admin:
            self.driver.find_element_by_xpath('//*[@id="loginUsername"]').send_keys(self.admin_uname)
            self.driver.find_element_by_xpath('//*[@id="loginPassword"]').send_keys(self.admin_pwd)
        else:
            self.driver.find_element_by_xpath('//*[@id="loginUsername"]').send_keys(self.usr_uname)
            self.driver.find_element_by_xpath('//*[@id="loginPassword"]').send_keys(self.usr_pwd)

        self.driver.find_element_by_xpath('//*[@id="btnLogin"]').click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="myNavbarNickname"]')))  # till username is displayed

    def logout(self, from_home=True, admin=False):
        if admin:
            self.driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul[2]/li/a').click()
            self.driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul[2]/li/ul/li[5]/a').click()
        else:
            self.driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul/li[2]/a').click()

            if from_home:
                self.driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul/li[2]/ul/li[6]/a').click()
            else:
                self.driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul/li[2]/ul/li[8]/a').click()

    def test_user_login(self):
        '''Test xxx feature of the book store.'''
        # login
        self.login()
        # check username display
        self.assertEqual(self.driver.find_element_by_xpath('//*[@id="myNavbarNickname"]').text, "测试用户")
        # logout
        self.logout()

    def test_search_book(self):
        # choose a catagory
        select = Select(self.driver.find_element_by_xpath('//*[@id="selectCategory"]'))
        select.select_by_visible_text('计算机')
        kwd = self.driver.find_element_by_xpath('//*[@id="searchBookInput"]')
        kwd.clear()
        kwd.send_keys('Java')
        # check result
        result = self.driver.find_element_by_xpath('//*[@id="book-4"]/div/div/h4')
        self.assertEqual(result.text, 'Java编程思想')

    def test_purchase(self):
        self.login()
        # check cart before adding
        title = self.driver.find_element_by_xpath('//*[@id="book-1"]/div/div/h4').text
        self.driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul/li[1]/a').click()
        time.sleep(2)  # wait for ajax
        for i, _ in enumerate(self.driver.find_elements_by_xpath('/html/body/div[1]/div/table/tbody/tr')):
            # if present, delete it
            if self.driver.find_element_by_xpath('/html/body/div[1]/div/table/tbody/tr[{}]/td[1]'.format(i + 1)).text == title:
                self.driver.find_element_by_xpath('/html/body/div[1]/div/table/tbody/tr[{}]/td[5]/button[2]'.format(i + 1)).click()
                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="btnDeleteItem"]'))).click()
                self.wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="btnDeleteItem"]')))
        self.driver.back()
        # trigger book detail modal, and add to cart
        self.driver.find_element_by_xpath('//*[@id="book-1"]/div/div/button').click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="btnAddToCart"]'))).click()
        # check cart
        self.driver.get(target_url)
        self.driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul/li[1]/a').click()
        time.sleep(2)  # wait for ajax
        added = False
        for i, _ in enumerate(self.driver.find_elements_by_xpath('/html/body/div[1]/div/table/tbody/tr')):
            if self.driver.find_element_by_xpath('/html/body/div[1]/div/table/tbody/tr[{}]/td[1]'.format(i + 1)).text == title:
                added = True
        self.assertTrue(added)
        # checkout
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/button'))).click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="btnPay"]'))).click()
        self.assertEqual(self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="payStatus"]/div'))).text, '支付成功！')
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="payDialog"]/div/div')))
        # logout
        time.sleep(2)
        self.logout(from_home=False)

    def test_modify_self_info(self):
        driver = self.driver

        self.login()

        driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul/li[2]/a').click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/nav[1]/div/div[2]/ul/li[2]/ul')))
        driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul/li[2]/ul/li[3]/a').click()

        # wait until the form is loaded
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="myProfileDialog"]/div')))

        update_avatar_btn = driver.find_element_by_xpath('/html/body/div[5]/input')
        update_avatar_btn.send_keys(os.getcwd() + "/avatar.png")

        time.sleep(5)
        tips = driver.find_element_by_xpath('//*[@id="myProfileUploadTips"]')
        self.assertIn("上传成功", tips.text)

        cancel_btn = driver.find_element_by_xpath('//*[@id="myProfileDialog"]/div/div/div[3]/button[2]')
        cancel_btn.click()

        self.logout()

    def test_admin_login(self):
        driver = self.driver

        self.login(admin=True)

        title = driver.find_element_by_xpath('/html/body/nav[1]/div/div[1]/a')
        self.assertEqual(title.text, "网上书店管理系统")

        self.logout(admin=True)

    def test_admin_stats(self):
        driver = self.driver

        self.login(admin=True)

        driver.find_element_by_xpath('/html/body/nav[1]/div/div[2]/ul[1]/li[5]/a').click()
        time.sleep(4)

        title = driver.find_element_by_xpath('/html/body/div[1]/h1')
        self.assertEqual(title.text, "销售统计")

        select = Select(driver.find_element_by_xpath('//*[@id="filterCategory"]'))
        select.select_by_index(1)
        driver.find_element_by_xpath('//*[@id="btnFilterCategory"]').click()
        self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="filterCategoryResult"]')))

        person = driver.find_element_by_xpath('//*[@id="filterCategoryPerson"]')
        quantity = driver.find_element_by_xpath('//*[@id="filterCategoryQuantity"]')
        price = driver.find_element_by_xpath('//*[@id="filterCategoryPrice"]')
        self.assertIn("购买人数", person.text)
        self.assertIn("总销量", quantity.text)
        self.assertIn("总金额", price.text)

        self.logout(admin=True)

    @classmethod
    def tearDownClass(cls):
        '''Stop the web driver only once.
        Doing this repeatedly in `tearDown()` could be time-consuming.'''
        cls.driver.quit()


if __name__ == '__main__':
    testsuite = unittest.TestLoader().loadTestsFromTestCase(TestBookStore)
    with io.StringIO() as f:
        unittest.TextTestRunner(stream=f).run(testsuite)
        cl.info('Message from unittest:')
        print(f.getvalue())
