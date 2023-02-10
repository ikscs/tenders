from playwright.sync_api import sync_playwright

BROWSER = 'Firefox'
if BROWSER not in ('Chromium', 'Webkit', 'Firefox'): error

class Playwright():
    def __init__(self):
        self.mgr = sync_playwright()
        self.exit = type(self.mgr).__exit__
        self.pw = type(self.mgr).__enter__(self.mgr)
        headless = False
        if BROWSER == 'Chromium':
            self.browser = self.pw.chromium.launch(headless = headless)
        elif BROWSER == 'webkit':
            self.browser = self.pw.webkit.launch(headless = headless)
        elif BROWSER == 'Firefox':
            self.browser = self.pw.firefox.launch(headless = headless)
            self.context = self.browser.new_context(ignore_https_errors = True)
        self.page = None

    def close(self):
        self.browser.close()
        self.exit(self.mgr, None, None, None)

    def get(self, *arg):
        if not self.page:
#            self.page = self.browser.new_page()
            self.page = self.context.new_page()
        self.page.goto(*arg)

    @property
    def page_source(self):
        if not self.page:
            return ''
        return self.page.content()

if __name__ == '__main__':
    play = Playwright()

    play.get('https://example.com')
    print(play.page_source)

    play.close()
