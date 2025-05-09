import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from bs4 import BeautifulSoup, Comment

# === Cài đặt Edge WebDriver ===
edge_options = EdgeOptions()
edge_options.add_argument("--headless")
edge_options.add_argument("--disable-gpu")
service = EdgeService(executable_path="C:\Webdrivers\msedgedriver.exe")  
driver = webdriver.Edge(service=service, options=edge_options)

# === FBref stat URLs ===
urls = {
    "standard": "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "keepers": "https://fbref.com/en/comps/9/keepers/Premier-League-Stats",
    "shooting": "https://fbref.com/en/comps/9/shooting/Premier-League-Stats",
    "passing": "https://fbref.com/en/comps/9/passing/Premier-League-Stats",
    "gca": "https://fbref.com/en/comps/9/gca/Premier-League-Stats",
    "possession": "https://fbref.com/en/comps/9/possession/Premier-League-Stats",
    "misc": "https://fbref.com/en/comps/9/misc/Premier-League-Stats"
}

# Hàm lấy table từ các URL phía trên 
def get_table_df(url):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Tìm kiếm tất cả các phần tử có thể chứa bảng:
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment_soup = BeautifulSoup(comment, 'html.parser')
        table = comment_soup.find('table', class_='stats_table')
        if table:
            try:
                df = pd.read_html(str(table), header=1)[0]
                if 'Player' in df.columns:
                    df = df[df['Player'] != 'Player']  
                return df
            except Exception as e:
                return pd.DataFrame()
    table = soup.find('table', class_='stats_table')
    if table:
        df = pd.read_html(str(table), header=1)[0]
        if 'Player' in df.columns:
            df = df[df['Player'] != 'Player']
        return df
    return pd.DataFrame()

# Scrape tất cả các url
stat_tables = {}
for name, url in urls.items():
    df = get_table_df(url)
    stat_tables[name] = df

merged_df = stat_tables["standard"]
merged_df = merged_df.rename(columns={"Squad": "Team", "Pos": "Position"})

# Loại bỏ các cầu thủ có thời gian thi đấu < 90 phút:
merged_df["Minutes"] = pd.to_numeric(merged_df.get("Min", 0), errors='coerce')
merged_df = merged_df[merged_df["Minutes"] > 90]

# Xử lí các thông số bị trùng nhau giữa các bảng trong các URL được scrape:
for name, df in stat_tables.items():
    if name == "standard":
        continue

    df = df.loc[:, ~df.columns.duplicated()]  # Loại bỏ tất cả các cột trùng nhau
    df = df.rename(columns={"Squad": "Team", "Pos": "Position"})  

    if 'Player' in df.columns:
        # Kiểm tra xem nên giữ lại những cột nào
        key_cols = ['Player']
        if 'Team' in df.columns and 'Team' in merged_df.columns:
            key_cols.append('Team')
            join_cols = ['Player', 'Team']
        else:
            join_cols = ['Player']

        # Loại bỏ các cột đã có trong merged_df và gộp vào
        drop_cols = [col for col in df.columns if col in merged_df.columns and col not in join_cols]
        df = df.drop(columns=drop_cols)
        merged_df = pd.merge(merged_df, df, on=join_cols, how='left')

        # Xóa các cột trùng sau khi gộp
        merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]
    else:
        continue

# Sắp xếp theo thứ tự chữ cái trong tên: 
    merged_df["FirstName"] = merged_df["Player"].str.split().str[0]
    merged_df = merged_df.sort_values("FirstName").drop(columns=["FirstName"])

# Lưu file kết quả 
final_df = merged_df.fillna("N/a")
final_df.to_csv("results.csv", index=False)
driver.quit()
