__author__ = 'm1'

import re

from bs4 import BeautifulSoup


class KvSimpleSearchResponse:
    total_found = 0
    page_nr = 0
    pages_total = 0
    error_code = 200
    found_id = {}


    def __init__(self, response_code, html_response):
        self.error_code = response_code
        if self.error_code == 200:
            soup = BeautifulSoup(html_response)
            self.total_found = int(re.sub("\D", "", soup.find("h1", {"class": "inner title"}).getText()))
            self.page_nr = int(soup.find(id="choose_page").get("value"))
            self.pages_total = int(soup.find("a", {"class": "count"}).getText())
            url_pattern_ = re.compile('^.*-([0-9]*)\.html.*')
            self.found_id = [url_pattern_.match(tag.get('href')).group(1) for tag in
                             soup.findAll("a", {"class": "object-title-a text-truncate"})]


    def __str__(self):
        return "KvSimpleSearchResponse[error_code={}, total_found={}, page_nr={}, pages_total={}, found_id={}]".format(
            self.error_code, self.total_found, self.page_nr, self.pages_total, self.found_id)

