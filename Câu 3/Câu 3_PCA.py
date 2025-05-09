import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Tải file kết quả:
df = pd.read_csv("results.csv")

# Loại bỏ các cột không cần thiết
non_numeric = ['Player', 'Team', 'Position', 'Nation', 'Comp', 'Age']
df_numeric = df.drop(columns=[col for col in non_numeric if col in df.columns], errors='ignore')

# Số hóa các cột dữ liệu
df_numeric = df_numeric.apply(pd.to_numeric, errors='coerce').fillna(0)

# Chuẩn hóa dữ liệu
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_numeric)

# Giảm chiều dữ liệu về 2D sử dụng PCA:
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Cluster sử dụng KMeans:
k = 4  
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_pca)

# Vẽ biểu đồ các cụm
plt.figure(figsize=(10, 7))
for i in range(k):
    plt.scatter(
        X_pca[clusters == i, 0],
        X_pca[clusters == i, 1],
        label=f'Cluster {i}'
    )

plt.title('Player Clusters (PCA-reduced to 2D)')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
