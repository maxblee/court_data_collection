from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class SeleniumBase:
    def __init__(self, start_url, headless=True, exec_path=None):
        opts = Options()
        opts.headless = headless
        if exec_path is not None:
            self.driver = webdriver.Firefox(options=opts, executable_path=exec_path)
        else:
            self.driver = webdriver.Firefox(options=opts)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.driver.quit()