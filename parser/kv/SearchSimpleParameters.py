__author__ = 'm1'


class SearchSimpleParameters:
    def __init__(self):
        self.company_id = ""
        self.page = 1
        self.orderby = "cdwl"  # newest on top
        self.page_size = 50
        self.deal_type = 1
        self.dt_select = 1
        self.county = 0
        self.parish = ""
        self.price_min = ""
        self.price_max = ""
        self.price_type = 1
        self.rooms_min = ""
        self.rooms_max = ""
        self.area_min = ""
        self.area_max = ""
        self.floor_min = ""
        self.floor_max = ""
        self.keyword = ""

    def to_url(self):
        return "company_id{}=&page={}&orderby={}&page_size={}&deal_type={}&dt_select={}&county={}&parish={}&" \
               "price_min={}&price_max={}&price_type={}&rooms_min={}&rooms_max={}&area_min={}&" \
               "area_max={}&floor_min={}&floor_max={}&keyword={}".format(self.company_id, self.page, self.orderby,
                                                                         self.page_size, self.deal_type, self.dt_select,
                                                                         self.county, self.parish, self.price_min,
                                                                         self.price_max, self.price_type,
                                                                         self.rooms_min,
                                                                         self.rooms_max, self.area_min, self.area_max,
                                                                         self.floor_min, self.floor_max, self.keyword)
