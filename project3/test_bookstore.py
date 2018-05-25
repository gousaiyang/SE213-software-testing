# -*- coding: utf-8 -*-

import functools
import io
import json
import os
import random
import re
import secrets
import time
import unittest

import colorlabels as cl
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

# Load all config variables into the global namespace.
with open('config.json', 'r') as f:
    globals().update(json.load(f))

# Some utility functions.


def file_content_b(filename):
    '''Return bytes content of a file with the given name.'''
    with open(filename, 'rb') as fin:
        content = fin.read()
    return content


def url_content_b(url, **kwargs):
    '''Return bytes content of the HTTP response when requesting the given URL.'''
    return requests.get(url, **kwargs).content


def parse_float(s):
    '''Parse float value in a string.'''
    return float(re.findall(r'([\d.]+)', s)[0])


def pretty_msg_test_func(func):
    '''Function decorator to make a test function emit pretty messages.'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        p = cl.progress(f"Running test case '{func.__name__}'...", cl.PROGRESS_SPIN, erase=True)

        try:
            func(*args, **kwargs)
        except:
            p.stop()
            cl.error(f"Test case '{func.__name__}' failed.")
            raise
        else:
            p.stop()
            cl.success(f"Test case '{func.__name__}' passed.")

    return wrapper


def pretty_msg_test_class(cls):
    '''Class decorator to make all test functions in a test class emit pretty messages.'''
    for func in filter(callable, (getattr(cls, n) for n in dir(cls) if n.startswith('test'))):
        setattr(cls, func.__name__, pretty_msg_test_func(func))

    return cls


@pretty_msg_test_class
class TestBookStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''Initialize the web driver only once.
        Doing this repeatedly in `setUp()` could be time-consuming.'''

        # Disable verbose output.
        options = webdriver.ChromeOptions()
        options.add_argument('--log-level=3')
        options.add_argument('--disable-logging')
        options.add_argument('--silent')

        # Launch Chrome Driver.
        cls.driver = webdriver.Chrome(webdriver_path, service_log_path=os.devnull, chrome_options=options)
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(webdriver_wait_time)
        cls.wait = WebDriverWait(cls.driver, webdriver_wait_time)

        # Load the home page first.
        cls.driver.get(target_url)
        time.sleep(5)

    def wait_for_jQuery(self):
        '''Wait for jQuery actions to finish.'''
        self.wait.until(lambda driver: driver.execute_script('return window.jQuery && jQuery.active == 0'))

    def setUp(self):
        '''Wait for Ajax to finish before each test case.'''
        self.wait_for_jQuery()

    def tearDown(self):
        '''Ensure logout and navigate to home page, whether the test case passed or failed.'''
        self.driver.get(target_url + '/logout')

    def login(self, *, admin=False):
        '''Login as a customer or an admin.'''
        # Click "login", wait for the dialog to show up.
        self.driver.find_element_by_link_text('登录').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'loginDialog')))

        # Fill in the form.
        username_box = self.driver.find_element_by_id('loginUsername')
        username_box.clear()
        username_box.send_keys(admin_uname if admin else customer_uname)
        password_box = self.driver.find_element_by_id('loginPassword')
        password_box.clear()
        password_box.send_keys(admin_pwd if admin else customer_pwd)

        # Click "login", wait until the page is reloaded and the nickname is displayed.
        self.driver.find_element_by_id('btnLogin').click()
        self.wait_for_jQuery()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'myNavbarNickname')))
        self.wait_for_jQuery()

    def modal_cancel(self, modal_id):
        '''Cancel a modal dialog using mouse actions.'''
        action = ActionChains(self.driver)
        action.move_to_element_with_offset(self.driver.find_element_by_css_selector(f'#{modal_id} > div > div'), -2, -2)
        action.click()
        action.perform()
        self.wait.until(EC.invisibility_of_element_located((By.ID, modal_id)))

    def get_balance(self):
        '''Retrieve balance of the current user.'''
        # Toggle the dropdown and open my profile dialog.
        self.driver.find_element_by_css_selector('a[class="dropdown-toggle"]').click()
        self.wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, '管理个人信息')))
        self.driver.find_element_by_partial_link_text('管理个人信息').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'myProfileDialog')))
        self.wait_for_jQuery()

        # Parse balance and close the dialog.
        balance = parse_float(self.driver.find_element_by_id('myBalance').text)
        self.modal_cancel('myProfileDialog')
        return balance

    def test_1_customer_login(self):
        '''Test login as customer.'''
        self.login()

        # Check whether the username is correct.
        self.assertEqual(self.driver.find_element_by_id('myNavbarNickname').text, '测试用户')

    def test_2_customer_search_book(self):
        '''Test book searching for customers.'''
        # Search for a random long name, expect no search result.
        kwd_box = self.driver.find_element_by_id('searchBookInput')
        kwd_box.clear()
        kwd_box.send_keys(secrets.token_urlsafe(20))
        self.wait_for_jQuery()
        self.assertEqual(self.driver.find_element_by_id('bookContainer').text, '无搜索结果')

        # Search by category '计算机' and keyword 'a', expect a book called 'Java编程思想'.
        Select(self.driver.find_element_by_id('selectCategory')).select_by_visible_text('计算机')
        kwd_box.clear()
        kwd_box.send_keys('a')
        self.assertEqual(self.driver.find_element_by_css_selector('#book-4 > div > div > h4').text, 'Java编程思想')

        # Search by Chinese keyword '编程', expect a non-empty result.
        kwd_box.clear()
        kwd_box.send_keys('编程')
        self.wait_for_jQuery()
        self.assertNotEqual(self.driver.find_element_by_id('bookContainer').text, '无搜索结果')

    def test_3_customer_purchase(self):
        '''Test book purchasing for customers.'''
        self.login()

        # First of all, navigate to the cart page. clear the cart if the cart already contains some books.
        self.driver.find_element_by_partial_link_text('购物车').click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[data-target="#payDialog"]')))
        self.wait_for_jQuery()
        if re.findall(r'<tr id="item-(\d+)">', self.driver.page_source):
            for delete_button in self.driver.find_elements_by_css_selector('button[data-target="#deleteDialog"]'):
                delete_button.click()
                self.wait.until(EC.visibility_of_element_located((By.ID, 'deleteDialog')))
                self.driver.find_element_by_id('btnDeleteItem').click()
                self.wait.until(EC.invisibility_of_element_located((By.ID, 'deleteDialog')))
        self.driver.back()
        self.wait_for_jQuery()

        # Then, add the book with ID 1 to the cart. Quantity is random.
        self.driver.find_element_by_css_selector('#book-1 > div > div > button').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'detailDialog')))
        self.wait_for_jQuery()
        name = self.driver.find_element_by_id('bookDetailName').text
        price = parse_float(self.driver.find_element_by_id('bookDetailPrice').text)
        quantity = random.randint(1, 5)
        totprice = price * quantity
        quantity_box = self.driver.find_element_by_id('addQuantity')
        quantity_box.clear()
        quantity_box.send_keys(str(quantity))
        self.driver.find_element_by_id('btnAddToCart').click()
        self.wait.until(EC.invisibility_of_element_located((By.ID, 'detailDialog')))

        # Then, check current balance.
        old_balance = self.get_balance()

        # After that, navigate to the cart page and check the cart.
        self.driver.find_element_by_partial_link_text('购物车').click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[data-target="#payDialog"]')))
        self.wait_for_jQuery()
        self.assertEqual(self.driver.find_element_by_xpath('//tbody/tr[1]/td[1]').text, name)
        self.assertAlmostEqual(parse_float(self.driver.find_element_by_xpath('//tbody/tr[1]/td[2]').text), price)
        self.assertEqual(self.driver.find_element_by_xpath('//tbody/tr[1]/td[3]').text, str(quantity))
        subtotal = parse_float(self.driver.find_element_by_xpath('//tbody/tr[1]/td[4]').text)
        total = parse_float(self.driver.find_element_by_id('totalPriceText').text)
        self.assertAlmostEqual(subtotal, total)
        self.assertAlmostEqual(subtotal, totprice)

        # Now we are ready to perform the payment. Check the order summary before clicking "Pay".
        self.driver.find_element_by_css_selector('button[data-target="#payDialog"]').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'payDialog')))
        self.wait_for_jQuery()
        self.assertEqual(self.driver.find_element_by_id('payTotalItems').text, '1')
        self.assertEqual(self.driver.find_element_by_id('payTotalQuantity').text, str(quantity))
        self.assertAlmostEqual(parse_float(self.driver.find_element_by_id('payTotalPrice').text), total)
        self.driver.find_element_by_id('btnPay').click()

        # Wait for the page to redirect. Check information in the order history page.
        self.wait.until(lambda driver: '<h1>我的历史订单</h1>' in driver.page_source)
        self.wait_for_jQuery()
        max_id = max(map(int, re.findall(r'<tr id="order-(\d+)">', self.driver.page_source)))  # Get ID of the last order.
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')  # Scroll to page bottom.
        self.driver.find_element_by_css_selector(f'#order-{max_id} > td.col-md-1 > button[data-target="#detailDialog"]').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'detailDialog')))
        self.wait_for_jQuery()
        self.assertEqual(self.driver.find_element_by_xpath('//*[@id="detailTable"]/tr/td[1]').text, name)
        self.assertAlmostEqual(parse_float(self.driver.find_element_by_xpath('//*[@id="detailTable"]/tr/td[2]').text), price)
        self.assertEqual(self.driver.find_element_by_xpath('//*[@id="detailTable"]/tr/td[3]').text, str(quantity))
        self.assertAlmostEqual(parse_float(self.driver.find_element_by_xpath('//*[@id="detailTable"]/tr/td[4]').text), totprice)
        self.modal_cancel('detailDialog')

        # Finally, check our balance.
        new_balance = self.get_balance()
        self.assertAlmostEqual(old_balance - new_balance, totprice)

    def test_4_customer_edit_profile(self):
        '''Test profile editing (uploading avatar) for customers.'''
        test_avatar_filename = 'avatar.png'
        self.login()

        # This test case is divided into two stages.
        # Stage 1: Delete the current avatar. Check whether the avatar in the navbar becomes the default avatar.
        # Stage 2: Upload a new avatar. Check whether the avatar in the navbar becomes the new avatar.
        for stage in (0, 1):
            self.driver.find_element_by_css_selector('a[class="dropdown-toggle"]').click()
            self.wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, '管理个人信息')))
            self.driver.find_element_by_partial_link_text('管理个人信息').click()
            self.wait.until(EC.visibility_of_element_located((By.ID, 'myProfileDialog')))
            self.wait_for_jQuery()

            if stage == 0:
                self.driver.find_element_by_id('btnDeleteMyAvatar').click()
                self.wait_for_jQuery()
            else:
                self.driver.find_element_by_css_selector('input[type="file"]').send_keys(os.path.realpath(test_avatar_filename))
                self.wait.until(lambda driver: '上传成功' in driver.find_element_by_id('myProfileUploadTips').text)

            self.driver.find_element_by_id('btnUpdateMyProfile').click()
            self.wait.until(EC.invisibility_of_element_located((By.ID, 'myProfileDialog')))
            self.wait_for_jQuery()
            current_avatar_url = self.driver.find_element_by_id('myNavbarAvatar').get_attribute('src')

            if stage == 0:
                self.assertEqual(current_avatar_url, target_url + '/img/default/user.png')
            else:
                self.assertEqual(file_content_b(test_avatar_filename), url_content_b(current_avatar_url))

    def test_5_admin_login(self):
        '''Test login as admin.'''
        self.login(admin=True)

        # Check whether the navbar brand becomes the brand for admin.
        self.assertEqual(self.driver.find_element_by_css_selector('a[class="navbar-brand"]').text, '网上书店管理系统')

    def test_6_admin_manage_categories(self):
        '''Test category management for admin.'''
        self.login(admin=True)

        # First of all, navigate to the category management page.
        self.driver.find_element_by_partial_link_text('分类管理').click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[data-target="#addCategoryDialog"]')))
        self.wait_for_jQuery()

        # Then, add the book with ID 1 to the category with ID 6.
        self.driver.find_element_by_css_selector('button[data-target="#addBookToCategoryDialog"][data-id="6"]').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'addBookToCategoryDialog')))
        id_to_add = 1
        book_to_add_box = self.driver.find_element_by_id('addBookToCategoryBookId')
        book_to_add_box.clear()
        book_to_add_box.send_keys(str(id_to_add))
        self.driver.find_element_by_id('btnAddBookToCategory').click()
        self.wait_for_jQuery()
        if '该书籍已经属于该分类' in self.driver.find_element_by_id('addBookToCategoryStatus').text:
            self.modal_cancel('addBookToCategoryDialog')
        else:
            self.wait.until(EC.invisibility_of_element_located((By.ID, 'addBookToCategoryDialog')))

        # After that, check whether the book has successfully been added to the category.
        self.driver.find_element_by_css_selector('button[data-target="#categoryDetailDialog"][data-id="6"]').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'categoryDetailDialog')))
        self.wait_for_jQuery()
        max_id = max(map(int, re.findall(r'<tr id="bc-(\d+)">', self.driver.page_source)))  # The last relation ID.
        self.assertEqual(self.driver.find_element_by_css_selector(f'#bc-{max_id} > th').text, str(id_to_add))

        # Now, remove the book from the category. Check and accept the confirmation.
        self.driver.find_element_by_css_selector(f'#bc-{max_id} > td.col-md-2 > button').click()
        alert = self.driver.switch_to.alert
        self.assertEqual(alert.text, '确实要从当前分类中删除书籍 MySQL：从删库到跑路 吗？')
        alert.accept()
        self.modal_cancel('categoryDetailDialog')

        # Finally, check whether the book has successfully been removed from the category.
        self.driver.find_element_by_css_selector('button[data-target="#categoryDetailDialog"][data-id="6"]').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'categoryDetailDialog')))
        self.wait_for_jQuery()
        for el in self.driver.find_elements_by_css_selector('#detailTable > tr > th'):
            self.assertNotEqual(el.text, str(id_to_add))
        self.modal_cancel('categoryDetailDialog')

    def test_7_admin_manage_users(self):
        '''Test user management for admin.'''
        self.login(admin=True)

        # Navigate to the user management page.
        self.driver.find_element_by_partial_link_text('用户管理').click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[data-target="#addDialog"]')))
        self.wait_for_jQuery()

        # This test case is divided into two stages.
        # Stage 1: Set the user with ID 2 to be an admin. Check whether the user has successfully become an admin.
        # Stage 2: Set the user with ID 2 to be a customer. Check whether the user has successfully become a customer.
        for stage in (0, 1):
            self.driver.find_element_by_css_selector('button[data-target="#updateDialog"][data-id="2"]').click()
            self.wait.until(EC.visibility_of_element_located((By.ID, 'updateDialog')))
            self.wait_for_jQuery()
            new_role_id = 1 - stage
            self.driver.find_element_by_id(f'updateUserRole{new_role_id}').click()
            self.driver.find_element_by_id('btnUpdateUser').click()
            self.wait.until(EC.invisibility_of_element_located((By.ID, 'updateDialog')))
            new_role_name = ('普通用户', '管理员')[new_role_id]
            self.assertEqual(self.driver.find_element_by_css_selector('#user-2 > td:nth-child(5)').text, new_role_name)

    def test_8_admin_stats(self):
        '''Test sales statistics querying for admin.'''
        self.login(admin=True)

        # Navigate to the sales statistics page.
        self.driver.find_element_by_partial_link_text('销售统计').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'btnFilterCategory')))

        # Test filtering by category. Check whether result is in a correct format.
        Select(self.driver.find_element_by_id('filterCategory')).select_by_index(1)
        self.driver.find_element_by_id('btnFilterCategory').click()
        self.wait.until(EC.visibility_of_element_located((By.ID, 'filterCategoryResult')))
        self.assertIn('购买人数', self.driver.find_element_by_id('filterCategoryPerson').text)
        self.assertIn('总销量', self.driver.find_element_by_id('filterCategoryQuantity').text)
        self.assertIn('总金额', self.driver.find_element_by_id('filterCategoryPrice').text)

    @classmethod
    def tearDownClass(cls):
        '''Stop the web driver only once.
        Doing this repeatedly in `tearDown()` could be time-consuming.'''
        cls.driver.quit()


if __name__ == '__main__':
    # Intercept the output from unittest and display it in the end.
    testsuite = unittest.TestLoader().loadTestsFromTestCase(TestBookStore)
    with io.StringIO() as f:
        unittest.TextTestRunner(stream=f).run(testsuite)
        cl.info('Message from unittest:')
        print(f.getvalue(), end='')
