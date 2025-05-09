# Code để lấy dữ liệu các cầu thủ chơi trên 900 phút dựa trên kết quả từ câu 1:
import pandas as pd
df = pd.read_csv("results.csv")

# Đảm bảo phút là dạng số
df["Minutes"] = pd.to_numeric(df["Minutes"], errors='coerce')

# Lọc cầu thủ trên 900 phút và lưu vào 1 file csv:
players_over_900 = df[df["Minutes"] > 900]
players_over_900[["Player"]].to_csv("players_over_900_minutes.csv", index=False)
