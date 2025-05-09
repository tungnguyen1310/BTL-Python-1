from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re
from unidecode import unidecode

# Hàm chuẩn hóa tên cầu thủ
def normalize_name(name):
    if not isinstance(name, str):
        return ""
    name = unidecode(name.strip()).lower()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^a-z0-9\s]', '', name)
    return name

# Đường dẫn đến Edge WebDriver
edge_driver_path = "C:\\Webdrivers\\msedgedriver.exe"
if not os.path.isfile(edge_driver_path):
    raise FileNotFoundError(f"WebDriver không tồn tại tại: {edge_driver_path}")

# Đọc danh sách cầu thủ từ file CSV và lưu vào set
try:
    players_df = pd.read_csv("players_over_900_minutes.csv")
    print("Dữ liệu CSV (5 dòng đầu):")
    print(players_df.head())
    print(f"Số giá trị trống trong cột Player: {players_df['Player'].isna().sum()}")
    players_df["Player"] = players_df["Player"].astype(str).str.strip()
    player_set = set(normalize_name(player) for player in players_df["Player"] if player != "nan")
    print("Danh sách cầu thủ từ CSV (chuẩn hóa):")
    for player in sorted(player_set):
        print(player)
except Exception as e:
    raise Exception(f"Lỗi khi đọc file CSV: {e}")

# Cấu hình Selenium
service = Service(edge_driver_path)
options = webdriver.EdgeOptions()
driver = webdriver.Edge(service=service, options=options)
url = "https://www.footballtransfers.com/us/players/uk-premier-league"

try:
    driver.get(url)
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    data = []
    all_players = []

    while True:
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
        except:
            print("Không tìm thấy bảng nào trên trang.")
            html = driver.page_source
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Đã lưu HTML vào page_source.html để gỡ lỗi.")
            break

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        table = None
        tables = soup.find_all("table")
        for tbl in tables:
            if tbl.find("tbody"):
                headers = [th.text.strip().lower() for th in tbl.find_all("th")]
                if any(keyword in headers for keyword in ["player", "name", "market value", "value"]):
                    table = tbl
                    break

        if not table:
            print("Không tìm thấy bảng chứa dữ liệu cầu thủ.")
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Đã lưu HTML vào page_source.html để gỡ lỗi.")
            break

        print("Đã tìm thấy bảng, đang xử lý dữ liệu...")

        rows = table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            # Thử cột đầu tiên hoặc cột thứ hai cho tên cầu thủ
            player_name = None
            for i in [0, 1]:
                if cols[i].find("a"):
                    player_name = cols[i].find("a").text.strip()
                    break
                elif cols[i].text.strip():
                    player_name = cols[i].text.strip()
            if not player_name:
                continue
            all_players.append(player_name)
            normalized_player_name = normalize_name(player_name)
            if normalized_player_name in player_set:
                market_value = cols[-1].text.strip()
                data.append({
                    "Player": player_name,
                    "Market Value": market_value
                })
            else:
                continue
            
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".pagination_next_button.btn.next-btn:not(.disabled)"))
            )
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
        except:
            print("Không tìm thấy nút Next hoặc đã đến trang cuối.")
            break

    print("Tất cả cầu thủ tìm thấy trên trang web:")
    for player in sorted(all_players):
        print(player)

    df = pd.DataFrame(data)
    if df.empty:
        print("Không tìm thấy cầu thủ nào khớp với danh sách trong file CSV.")
    else:
        print("Dữ liệu thu thập được:")
        print(df)
        df.to_csv("transfer_value.csv", index=False, encoding="utf-8")
        print("Dữ liệu đã được lưu vào transfer_value.csv")

finally:
    driver.quit()