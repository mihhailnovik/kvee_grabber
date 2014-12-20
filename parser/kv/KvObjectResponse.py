__author__ = 'm1'

from bs4 import BeautifulSoup
import re
import sys
from datetime import datetime
import constants
import logging

class KvObjectResponse:

    def __init__(self, id, response_code, html_response):
        log = logging.getLogger(__name__)
        self.error_code = response_code
        self.kvid = id
        self.parsed_date = datetime.now()
        if self.error_code == 200:
            try :
                self.rooms = None
                self.area = None
                self.floor_nr = None
                self.build_year = None
                self.condition = None
                self.type = None
                self.maakond = None
                self.city = None
                self.block = None
                self.create_date = None
                self.street = None
                self.price = None
                soup = BeautifulSoup(html_response)
                title = soup.find("h1", {"class": "title"}).getText().split(',')
                self.type = title[0][0].strip()
                self.maakond = title[1].strip().split()[3]
                self.city = title[2].strip()
                self.block = title[3].strip()
                try:
                    self.create_date = datetime.strptime(title[-1].split()[-1].strip()[1:-1], '%d.%m.%y')
                except:
                    log.error("error during parsing create_date - {}".format(sys.exc_info()[0]))
                    pass
                self.street = ' '.join(title[-1].split()[0:-1]).strip()
                price_unparsed = re.findall("\d+", soup.find("p", {"class":"object-price"}).find("strong").getText().strip())
                self.price = int(price_unparsed[0]+price_unparsed[1])
                data_table_soup = BeautifulSoup(str(soup.find("table", {"class": "table-lined object-data-meta"})))
                tds = data_table_soup.find_all("td")
                ths = data_table_soup.find_all("th")

                for i in range(0, len(ths)):
                    if constants.PARSE_ROOM_NR in ths[i].get_text():
                        try:
                            self.rooms = int(tds[i-1].get_text().strip())
                        except:
                            log.error("error during parsing rooms - {}".format(sys.exc_info()[0]))
                            pass
                    elif constants.PARSE_AREA in ths[i].get_text():
                        try:
                            self.area = float(tds[i-1].get_text().strip().split()[0])
                        except:
                            log.error("error during parsing area - {}".format(sys.exc_info()[0]))
                            pass
                    elif constants.PARSE_FLOOR in ths[i].get_text():
                        self.floor_nr = tds[i-1].get_text().strip()
                    elif constants.PARSE_YEAR in ths[i].get_text():
                        try:
                            self.build_year = int(tds[i-1].get_text().strip())
                        except:
                            log.error("error during parsing build_year - {}".format(sys.exc_info()[0]))
                            pass
                    elif constants.PARSE_CONDITION in ths[i].get_text():
                        self.condition = tds[i-1].get_text().strip()
                self.parsed_status = 'success'
                self.parsed_error_info = ''
                # TODO energy level etc...
            except:
                self.parsed_status = "error"
                self.parsed_error_info = sys.exc_info()[0]
        else:
            self.parsed_status = "error"
            self.parsed_error_info = "http response {}".format(self.error_code)

    def __dict__(self):
        return {'kvid': self.kvid, 'price' : self.price,'rooms' : self.rooms, 'area' : self.area,
                'floor_nr' : self.floor_nr, 'build_year' : self.build_year, 'condition' : self.condition,
                'type' : self.type, 'maakond' : self.maakond, 'city' : self.city, 'block' : self.block,
                'create_date' : self.create_date, 'street' : self.street, 'parsed_date': self.parsed_date,
                'parsed_status' : self.parsed_status, 'parsed_error_info' : self.parsed_error_info }

    def __str__(self):
        return "KvObjectResponse[error_code[{}]" \
               "kvid[{}] " \
               "price[{}], " \
               "rooms[{}], " \
               "area[{}], " \
               "floor_nr[{}], " \
               "build_year[{}], " \
               "condition[{}], " \
               "type[{}], " \
               "maakond[{}], " \
               "city[{}], " \
               "block[{}], " \
               "create_date[{}], " \
               "street[{}] ".format(self.error_code, self.kvid, self.price,
                                    self.rooms, self.area, self.floor_nr, self.build_year,
                                    self.condition, self.type, self.maakond, self.city, self.block,
                                    self.create_date, self.street)