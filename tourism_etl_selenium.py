from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
import time

def scrape_tourism_data(year, period, test_mode=False):
    url = f"https://vietnamtourism.gov.vn/en/statistic/international?year={year}&period={period}"
    print(f"🔗 Đang tải dữ liệu từ: {url}")

    chrome_driver_path = r"C:\chromedriver\chromedriver.exe"  # 👉 chỉnh đường dẫn ChromeDriver của bạn

    options = Options()
    options.add_argument("--headless")      # chạy nền, không mở cửa sổ Chrome
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
    driver.get(url)
    time.sleep(5)  # chờ trang load dữ liệu bằng JavaScript

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Tìm bảng dữ liệu
    tables = pd.read_html(str(soup))
    if len(tables) == 0:
        raise ValueError("❌ Không tìm thấy bảng dữ liệu trên trang!")

    df = tables[0]
    print("✅ Đã tải xong dữ liệu thô:")
    print(df.head())

    # Chuẩn hóa tên cột (tuỳ trang)
    df.columns = ["Market", "Arrivals"]
    df["Year"] = year
    df["Period"] = period

    # Xuất ra file CSV để test
    if test_mode:
        df.to_csv(f"tourism_{year}_{period}.csv", index=False)
        print(f"💾 Đã lưu dữ liệu vào tourism_{year}_{period}.csv")

    return df


# ==============================
# 🚀 TEST THỬ
# ==============================
if __name__ == "__main__":
    df = scrape_tourism_data(2008, "t9", test_mode=True)
    print("\n✅ Hoàn thành scrape thử!")
