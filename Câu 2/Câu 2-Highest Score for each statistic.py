from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

EDGE_DRIVER_PATH = 'C:/Webdrivers/msedgedriver.exe' 

# Cấu hình driver cho trình duyệt Edge:
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
service = Service(EDGE_DRIVER_PATH)
driver = webdriver.Edge(service=service, options=options)

# URLs và các table class tương ứng:
sources = {
    "Stats": ("https://fbref.com/en/comps/9/stats/Premier-League-Stats", 
              "stats_table sortable min_width now_sortable"),
    "Keepers": ("https://fbref.com/en/comps/9/keepers/Premier-League-Stats", 
                "stats_table sortable min_width now_sortable sticky_table eq1 re1 le1"),
    "Shooting": ("https://fbref.com/en/comps/9/shooting/Premier-League-Stats", 
                 "stats_table sortable min_width now_sortable sticky_table eq1 re1 le1"),
    "Passing": ("https://fbref.com/en/comps/9/passing/Premier-League-Stats", 
                "stats_table sortable min_width now_sortable sticky_table eq1 re1 le1"),
    "GCA": ("https://fbref.com/en/comps/9/gca/Premier-League-Stats", 
            "stats_table sortable min_width now_sortable"),
    "Possession": ("https://fbref.com/en/comps/9/possession/Premier-League-Stats", 
                   "stats_table sortable min_width now_sortable"),
    "Misc": ("https://fbref.com/en/comps/9/misc/Premier-League-Stats", 
             "stats_table sortable min_width now_sortable"),
}

def extract_max_stats(url, table_class):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.find('table', class_=table_class)
    df = pd.read_html(str(table))[0]
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)

    df = df[df['Squad'].notna()] 

    results = {}
    for col in df.columns:
        if col != 'Squad' and pd.api.types.is_numeric_dtype(df[col]):
            try:
                max_row = df.loc[df[col].idxmax()]
                results[col.strip()] = (max_row['Squad'], max_row[col])
            except Exception:
                continue
    return results

# Cào dữ liệu và thu thập kết quả
all_results = {}
for category, (url, table_class) in sources.items():
    print(f"Processing {category}...")
    all_results[category] = extract_max_stats(url, table_class)

driver.quit()
final_stats = {}
for category, stats in all_results.items():
    for stat, (team, value) in stats.items():
        stat_lower = stat.lower()
        if 'vs' in stat_lower:
            stat_without_vs = stat.replace('vs', '').strip()
            if stat_without_vs not in final_stats or value > final_stats[stat_without_vs][1]:
                final_stats[stat_without_vs] = (team, value)
        else:
            if stat not in final_stats or value > final_stats[stat][1]:
                final_stats[stat] = (team, value)

# Lưu vào file txt:
with open("max_stats_output.txt", "w", encoding="utf-8") as f:
    for stat, (team, _) in final_stats.items():
        f.write(f"{stat}: {team}\n")

print("All done! Output written to max_stats_output.txt")
