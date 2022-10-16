import os
import sys
import json
import scrapy
import pandas as pd

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
csv_path = os.path.join(script_dir, 'output')


class SaCovidSpider(scrapy.Spider):
    name = 'sa_covid'
    allowed_domains = ['nicd.ac.za']
    start_urls = ['https://www.nicd.ac.za/diseases-a-z-index/disease-index-covid-19/surveillance-reports/national'
                  '-covid-19-daily-report/']

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "nmclist.nicd.ac.za",
        "Pragma": "no-cache",
        "Referer": "https://nmclist.nicd.ac.za/DashboardExternal.html",
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / "
                      "106.0 .0.0 Safari / 537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    def parse(self, response):
        total_data_url = 'https://nmclist.nicd.ac.za/App_JSON/DashStats.json?v=2047'
        yield scrapy.Request(total_data_url, callback=self.parse_total, headers=self.headers)

        province_data_url = 'https://nmclist.nicd.ac.za/App_JSON/DashProvinceStats.json?v=2047'
        yield scrapy.Request(province_data_url, callback=self.parse_province, headers=self.headers)

    def parse_total(self, response):
        raw_data = response.body
        data = json.loads(raw_data)

        total_data = {
            'confirmed_cases': [data['cases']],
            'total_test': [data['tests']],
            'detection_rate': [data['detectionRate']],
            'incidence_rate': [data['incidenceRate']]
        }

        df = pd.DataFrame(total_data)
        yield df.to_csv(f'{csv_path}\\covid_total(SA).csv', index=False)

    def parse_province(self, response):
        raw_data = response.body
        data = json.loads(raw_data)

        provinces_data = {
            'provinces': data['categories'],
            'total_cases': data['totalCases'],
            'new_cases': data['newCases'],
            'new_cases_incidence': data['newCasesIncidence'],
            'incidences': data['incidences']
        }

        df = pd.DataFrame(provinces_data)
        yield df.to_csv(f'{csv_path}\\covid_by_provinces(SA).csv', index=False)
