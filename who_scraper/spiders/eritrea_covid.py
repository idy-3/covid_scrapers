import os
import sys
import scrapy
import re
import pandas as pd

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')


class EritreaCovidSpider(scrapy.Spider):
    name = 'eritrea_covid'
    allowed_domains = ['shabait.com']
    start_urls = ['https://shabait.com/2022/05/09/announcement-from-the-ministry-of-health-470']

    def parse(self, response):
        print(response)
        output = response.xpath("//div[@class='entry-content clearfix single-post-content']/p/text()").getall()

        total_data = {}
        pat = '[\d]+[.,\d]+'
        for data in output:
            num = data.find("confirmed")
            if num != -1:
                total_data["confirmed"] = [re.findall(pat, data[num:])[0].replace(',', '').replace(".", "")]

            num = data.find("recovered")
            if num != -1:
                total_data["recovered"] = [re.findall(pat, data[num:])[0].replace(',', '').replace(".", "")]

            num = data.find("deaths")
            if num != -1:
                total_data["deaths"] = [re.findall(pat, data[num:])[0].replace(',', '').replace(".", "")]

        csv_path = os.path.join(script_dir, 'output')
        df = pd.DataFrame(total_data)
        yield df.to_csv(f'{csv_path}\\covid_total(Eritrea).csv', index=False)
