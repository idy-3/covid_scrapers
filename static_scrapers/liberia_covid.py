import glob
import os
import re
import string
import sys

import pandas as pd
from PyPDF2 import PdfReader

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]) or '.')
resource_path = os.path.join(script_dir, 'resources')

liberia_pdf = glob.glob(f"{resource_path}\\Liberia_COVID*.pdf")[0]
reader = PdfReader(liberia_pdf)

data = ""
for datas in reader.pages:
    data += datas.extractText()

spliter1 = "New Cum New Cum New Cum"
spliter2 = "CountyConfirmed Cases Recovered Cases Active"
data = data.split(spliter1)[1].split(spliter2)[0]

data.split('\n')

counties = []
confirmed = []
recovered = []
active = []
deaths = []

alphas = string.ascii_letters
totals = {}

rows = data.split('\n')
for row in rows:
    if len(row) > 1:
        cols = re.split(r'\s(?=\d+(?!\S))', row)
        counties.append(cols[0])
        confirmed.append(cols[2])
        recovered.append(cols[4])
        active.append(cols[5])
        deaths.append(cols[7].rstrip(alphas))

totals['counties'] = counties
totals['confirmed'] = confirmed
totals['recovered'] = recovered
totals['active'] = active
totals['deaths'] = deaths

# print(totals)

csv_path = os.path.join(script_dir, '../output')
df = pd.DataFrame(totals)
df.to_csv(f'{csv_path}//covid_total(Liberia).csv', index=False)
