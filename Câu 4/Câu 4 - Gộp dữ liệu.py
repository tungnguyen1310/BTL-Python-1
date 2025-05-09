import pandas as pd
import os
from unidecode import unidecode
import re

# Hàm chuẩn hóa tên cầu thủ
def normalize_name(name):
    if not isinstance(name, str):
        return ""
    name = unidecode(name.strip()).lower()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^a-z0-9\s]', '', name)
    return name

# Đường dẫn đến các file CSV
filtered_file = "filtered_premier_league_players.csv"
result_file = "results.csv"
output_file = "final_result.csv"

try:
    # Đọc file filtered_premier_league_players.csv
    if not os.path.isfile(filtered_file):
        raise FileNotFoundError(f"File not found: {filtered_file}")
    filtered_df = pd.read_csv(filtered_file)
    print(f"Data from {filtered_file} (first 5 rows):")
    print(filtered_df.head())

    # Kiểm tra và tạo file result.csv nếu không tồn tại
    if not os.path.isfile(result_file):
        print(f"File {result_file} not found. Creating an empty {result_file} with 'Player' column.")
        # Giả sử result.csv cần cột 'Player' để gộp, có thể thêm các cột khác nếu cần
        empty_df = pd.DataFrame(columns=['Player'])
        empty_df.to_csv(result_file, index=False, encoding='utf-8')
    
    # Đọc file result.csv
    result_df = pd.read_csv(result_file)
    print(f"Data from {result_file} (first 5 rows):")
    print(result_df.head())

    # Chuẩn hóa tên cầu thủ trong cả hai DataFrame
    filtered_df['Normalized_Player'] = filtered_df['Player'].apply(normalize_name)
    result_df['Normalized_Player'] = result_df['Player'].apply(normalize_name)

    # Gộp giá trị chuyển nhượng vào result_df
    result_df = result_df.merge(
        filtered_df[['Normalized_Player', 'Market Value']],
        on='Normalized_Player',
        how='left'
    )

    # Xóa cột Normalized_Player
    result_df = result_df.drop(columns=['Normalized_Player'])

    # Tạo và lưu kết quả vào final_result.csv
    result_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data has been merged and saved to {output_file}")
    print(f"Data after merging (first 5 rows):")
    print(result_df.head())

except Exception as e:
    print(f"Error during processing: {e}")