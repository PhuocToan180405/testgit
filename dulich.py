import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://www.tourism.gov.vn/statistics/2012/12"  # ví dụ link thật
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# tìm bảng
table = soup.find("table")
df = pd.read_html(str(table))[0]  # đọc bảng thành DataFrame

# lưu ra file Excel
df.to_excel("tourism_2012_12.xlsx", index=False)

print("✅ Đã lưu bảng vào tourism_2012_12.xlsx")
