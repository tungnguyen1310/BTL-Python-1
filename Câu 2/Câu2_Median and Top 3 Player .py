import pandas as pd
import numpy as np

# Load file
df = pd.read_csv("results.csv")

# Xóa cột số thứ tự để không phải tính median và các thông số khác
if 'Rk' in df.columns:
    df = df.drop(columns=['Rk'])


# Loại bỏ các cột không phải chỉ số 
non_stat_cols = ['Player', 'Team', 'Position', 'Nation', 'Born', 'Matches']
numeric_df = df.drop(columns=[col for col in non_stat_cols if col in df.columns], errors='ignore')
numeric_df = numeric_df.apply(pd.to_numeric, errors='coerce')
df_combined = pd.concat([df[['Player', 'Team']], numeric_df], axis=1)

# Top 3 cao nhất - thấp nhất cho từng chỉ số:
top3_lines = []
for col in numeric_df.columns:
    if numeric_df[col].dropna().empty:
        continue
    top3_lines.append(f"\n--- Top 3 HIGH for {col} ---")
    top3_lines.extend(df_combined.nlargest(3, col)[['Player', 'Team', col]].to_string(index=False).split('\n'))
    top3_lines.append(f"\n--- Top 3 LOW for {col} ---")
    top3_lines.extend(
        df_combined.nsmallest(3, col)[['Player', 'Team', col]]
        .to_string(index=False).split('\n')
    )

with open("top_3.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(top3_lines))

# Tính toán median, mean và standard derivation cho các đội:
def compute_team_stats(df_subset):
    stats = {}
    for col in numeric_df.columns:
        stats[f"Median of {col}"] = df_subset[col].median()
        stats[f"Mean of {col}"] = df_subset[col].mean()
        stats[f"Std of {col}"] = df_subset[col].std()
    return stats

rows = []
overall_stats = compute_team_stats(numeric_df)
overall_stats["Team"] = "all"
rows.append(overall_stats)
for team, group in df_combined.groupby("Team"):
    stats = compute_team_stats(group[numeric_df.columns])
    stats["Team"] = team
    rows.append(stats)

# Lưu file
results2_df = pd.DataFrame(rows)
results2_df = results2_df[['Team'] + [col for col in results2_df.columns if col != 'Team']]
results2_df.to_csv("results2.csv", index=False, encoding="utf-8")
print("Saved to 'top_3.txt' and 'results2.csv'")
