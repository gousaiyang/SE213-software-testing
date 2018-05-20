# -*- coding: utf-8 -*-

import json
import time
import unittest

from selenium import webdriver
from selenium.webdriver.support.ui import Select


# Load all config variables into the global namespace.
with open('config.json', 'r') as f:
    globals().update(json.load(f))


class TestBookStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        '''Initialize the web driver only once.
        Doing this repeatedly in `setUp()` could be time-consuming.'''
        cls.driver = webdriver.Chrome(webdriver_path)
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(webdriver_wait_time)

    def test_xxx(self):
        '''Test xxx feature of the book store.'''
        self.driver.get(target_url)
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        '''Stop the web driver only once.
        Doing this repeatedly in `tearDown()` could be time-consuming.'''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
