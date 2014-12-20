__author__ = 'm1'

from io import BytesIO
import pycurl
from datetime import datetime
import os
import logging.config
import sys

import dataset
import yaml

from KvObjectResponse import KvObjectResponse
from KvSimpleSearchResponse import KvSimpleSearchResponse
from SearchSimpleParameters import SearchSimpleParameters
import constants


BASE_URL = "http://www.kv.ee/"
BASE_OBJECT_SHOW_URL = BASE_URL + "index.php?act=object.show&"
BASE_SEARCH_SIMPLE_URL = BASE_URL + "?act=search.simple&"


def prepare_curl():
    c = pycurl.Curl()
    c.setopt(pycurl.HTTPHEADER, ["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                                 "Accept-Language: en-US,en;q=0.8",
                                 "Connection: keep-alive",
                                 "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/38.0.2125.101 Safari/537.36"
    ])
    return c


def setup_logging():
    path = 'logging.yaml'
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)


def search_simple(search_simple_parameters):
    storage = BytesIO()
    c = prepare_curl()
    c.setopt(c.URL, BASE_SEARCH_SIMPLE_URL + search_simple_parameters.to_url())
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    response_code = c.getinfo(c.RESPONSE_CODE)
    response_html = storage.getvalue()
    response = KvSimpleSearchResponse(response_code, response_html)
    # getinfo must be called before close.
    c.close()
    return response


def search_new_ids(initial_search_parameters, kv_table):
    log = logging.getLogger(__name__)
    initial_search_result = search_simple(initial_search_parameters)
    log.info("Search all id's initial search result is {}".format(initial_search_result.error_code))
    total_found = initial_search_result.total_found
    pages = int(total_found / initial_search_parameters.page_size)
    log.info("total found {}, pages = {}".format(total_found, pages))
    id_set = set()
    for j in range(1, int(pages)):
        initial_search_parameters.page = j
        current_result = search_simple(initial_search_parameters)
        log.info("process {} page, result {}".format(j, current_result.error_code))
        id_set_to_process = set()
        found_element = False
        for found_id in current_result.found_id:
            if kv_table.find_one(kvid=found_id) is None:
                id_set_to_process.add(found_id)
            else:
                log.info("Already have {}, it means we are done with new stuff".format(found_id))
                found_element = True
        id_set.update(id_set_to_process)
        if found_element:
            return id_set
    log.info("New id's {}".format(id_set))
    return id_set


def get_info(id):
    log = logging.getLogger(__name__)
    log.info("Getting full info of {}".format(id))
    storage = BytesIO()
    c = prepare_curl()
    c.setopt(c.URL, BASE_OBJECT_SHOW_URL + "object_id={}".format(id))
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    response_code = c.getinfo(c.RESPONSE_CODE)
    response_html = storage.getvalue()
    response = KvObjectResponse(id, response_code, response_html)
    log.info("Query for {} response error code {}".format(id, response_code))
    if response_code != 200:
        log.error("Http server request failed with code[{}], html = {}".format(response_code, response_html))
    c.close()
    return response


def insert_or_update(name, value, table):
    if table.find_one(name=name) is None:
        table.insert({"name": name, "value": value})
    else:
        table.update({"name": name, "value": value}, ['name'])

if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Synchronization started {}".format(datetime.now()))
    obj_db = dataset.connect('sqlite:///{}'.format(constants.DB_FILE))
    kv_object_table = obj_db[constants.KVOBJECT]

    parameters = SearchSimpleParameters()
    parameters.parish = 421  # Tallinn
    result = search_new_ids(parameters, kv_object_table)
    i = 0
    id_set_size = len(result)
    for kv_ee_id in result:
        try:
            kv_object_table.insert(get_info(kv_ee_id).__dict__())
            logger.info("{} / {} done ".format(i, id_set_size))
            i += 1
        except Exception as e:
            try:  # i know it's stupid :(
                logger.exception("exception during getting info for id {} - {}".format(kv_ee_id, sys.exc_info()[0]))
                kv_object_table.insert({"kvid": kv_ee_id, "parsed_status": "error", "parsed_error_info": str(e),
                              "parsed_date": datetime.now()})
            except:
                logger.error("Error! cannot process {} ".format(kv_ee_id))
    logger.info("New objects are added")
    logger.info("Process existing objects")
    # TO BE DONE later

    logger.info("Calculating statistics")
    lasn_2 = 0
    new_3 = 0
    average = 0
    for i in obj_db.query("select sum(price) / count(*) from kv_object where rooms=2 and block='Lasnamäe'"):
        lasn_2 = i['sum(price) / count(*)']

    for i in obj_db.query("select sum(price) / count(*) from kv_object where build_year>2014 and rooms=3"):
        new_3 = i['sum(price) / count(*)']

    for i in obj_db.query("select sum(price/area) / count(*) from kv_object"):
        average = i['sum(price/area) / count(*)']

    stats_db = dataset.connect('sqlite:///{}'.format(constants.DB_FILE_STATS))
    kv_stats_table = stats_db[constants.KVSTATS]
    insert_or_update('lasn_2', lasn_2, kv_stats_table)
    insert_or_update('new_3', new_3, kv_stats_table)
    insert_or_update('average', average, kv_stats_table)
    logger.info("Synchronization finished {}".format(datetime.now()))

