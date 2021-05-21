import scrapy
import sys
from statespider.items import ProvinceItem
from statespider.items import CityItem
from statespider.items import TownItem
from statespider.items import VillageItem

class StatesSpider(scrapy.Spider):
    name = 'StatesSpider'
    start_urls = ['http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/index.html']

    def errback_s1(self, failure):
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    def parse(self, response):
        province_links = response.css('.provincetr td')
        for  province_link in province_links:
            province = province_link.css('td a')
            name = province.css('::text').get()
            code = province.css('::attr(href)').get()
            to = code.rindex('.')
            code = code[:to]
            next_page = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/' + province.css('::attr(href)').get()
            province = ProvinceItem(code=code, name=name, link=next_page)
            province['cities'] = []
            yield response.follow(next_page, meta={'province': province}, callback=self.parseProvinces, errback=self.errback_s1)


    def parseProvinces(self, response):
        province = response.meta['province']
        city_links = response.css('.citytr')
        cities = []
        for city_link in city_links:
            cityInfos = city_link.css('td a')
            city_code = cityInfos[0]
            city_name = cityInfos[1]
            next_page = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2020/' + city_code.css('::attr(href)').get()
            code = city_code.css('::text').get()
            name = city_name.css('::text').get()
            if '省直辖县级行政区划' ==  name:
                to = next_page.rindex('/')
                purl = next_page[:to] + '/'
                yield scrapy.Request(next_page, meta={'province':province}, callback=self.parseCounty, cb_kwargs=dict(purl=purl))
            else:
                city = CityItem(name=name, code=code, link=next_page)
                city['towns'] = []
                cities.append(city)
        province['cities'] = cities
        for city in cities:
            yield scrapy.Request(city['link'], callback=self.parseTowns, meta={'province':province}, cb_kwargs=dict(cityCode=city['code']))
        # yield province

    def parseCounty(self, response, purl):
        county_links = response.css('.countytr')
        province = response.meta['province']
        cities = province['cities']
        for county_link in county_links:
            countyCityInfos = county_link.css('td a')
            county_city_code = countyCityInfos[0]
            county_city_name = countyCityInfos[1]
            name = county_city_name.css('::text').get()
            code = county_city_code.css('::text').get()
            next_page = purl + county_city_code.css('::attr(href)').get()
            city = CityItem(name=name, code=code, link=next_page)
            city['towns'] = []
            cities.append(city)
        province['cities'] = cities
        for city in cities:
            yield scrapy.Request(city['link'], callback=self.parseTowns, meta={'province':province}, cb_kwargs=dict(cityCode=city['code']))
        # return province

    def parseTowns(self, response, cityCode):
        townRows = response.css('.towntr')
        province = response.meta['province']
        cities = province['cities']
        for idx, city in enumerate(cities):
            if city['code'] == cityCode:
                print('parse towns of city %s %s' % (city['name'], city['link']))
                towns = []
                for townRow in townRows:
                    townCols = townRow.css('td a')
                    code = townCols[0].css('::text').get()
                    name = townCols[1].css('::text').get()
                    link = townCols[0].css('::attr(href)').get()
                    print('town %s %s' % (code, name))
                    town = TownItem(code=code, name=name,link=link)
                    town['villages'] = []
                    towns.append(town)
                cities[idx]['towns'] = towns
                break
        province['cities'] = cities
        return province

    def parseVillages(self, response, cityCode):
        villageRows = response.css('.villagetr')
        province = response.meta['province']
        cities = province['cities']
        totalCities = len(cities)
        print('%s has total %d villages' % (cityCode, len(villageRows)))
        for idx in range(totalCities):
            city = cities[idx]
            if city['code'] == cityCode:
                print('match city %s' % cityCode)
                vs = []
                for villageRow in villageRows:
                    villageCols = villageRow.css('td')
                    print('total %d cols' % len(villageCols))
                    vcode = villageCols[0].css('::text').get()
                    ccode = villageCols[1].css('::text').get()
                    name = villageCols[2].css('::text').get()
                    print("%s %s %s" % (vcode, ccode, name))
                    v = VillageItem(code=vcode,catalog=ccode,name=name)
                    vs.append(v)
                city['villages']=vs
                cities[idx] = city
                break
        province['cities'] = cities
        return province
