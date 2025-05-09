import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load file:
df = pd.read_csv("results.csv")

# Loại những chỉ số không liên quan:
non_numeric = ['Player', 'Team', 'Position', 'Nation', 'Comp', 'Age']
df_numeric = df.drop(columns=[col for col in non_numeric if col in df.columns], errors='ignore')

# Chuyển sang dạng số học:
df_numeric = df_numeric.apply(pd.to_numeric, errors='coerce').fillna(0)

# Chuẩn hóa số liệu:
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_numeric)

# Phương pháp elbow để tìm k:
inertias = []
k_range = range(1, 11)

for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

# Vẽ đồ thị elbow:
plt.figure(figsize=(8, 5))
plt.plot(k_range, inertias, 'bo-')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia (Within-Cluster Sum of Squares)')
plt.title('Elbow Method For Optimal k')
plt.grid(True)
plt.show()

# K-means clustering với số k:
k = 4  
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_scaled)

# Hiển thị cầu thủ theo từng cụm:
for i in range(k):
    players_in_cluster = df[df['Cluster'] == i]['Player'].tolist()
    print(f"\n🧩 Cluster {i} ({len(players_in_cluster)} players):")
    for player in players_in_cluster:
        print(f" - {player}")
