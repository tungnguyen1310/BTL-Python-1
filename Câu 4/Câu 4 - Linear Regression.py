import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Đọc dữ liệu từ tệp CSV
data = pd.read_csv('final_result.csv')

# Hàm chuyển đổi Market Value từ chuỗi sang số (triệu euro)
def convert_market_value(value):
    if pd.isna(value):
        return np.nan
    value = value.replace('€', '').replace('M', '')
    try:
        return float(value)
    except:
        return np.nan

# Áp dụng hàm chuyển đổi cho cột Market Value
data['Market Value'] = data['Market Value'].apply(convert_market_value)

# Xử lý giá trị thiếu bằng cách điền 0 cho các cột số
numeric_columns = data.select_dtypes(include=[np.number]).columns
data[numeric_columns] = data[numeric_columns].fillna(0)

# Chọn các đặc trưng số để làm biến độc lập
features = numeric_columns.drop(['Market Value', 'Rk'])  # Loại bỏ Market Value và Rk
X = data[features]
y = data['Market Value']

# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Khởi tạo và huấn luyện mô hình hồi quy tuyến tính
model = LinearRegression()
model.fit(X_train, y_train)

# Dự đoán trên tập kiểm tra
y_pred = model.predict(X_test)

# Đánh giá mô hình
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f'Mean Squared Error: {mse:.2f}')
print(f'R² Score: {r2:.2f}')

# Tạo DataFrame chứa kết quả
# Lấy chỉ số của tập kiểm tra để truy xuất thông tin cầu thủ
test_indices = X_test.index
result_df = pd.DataFrame({
    'Player': data.loc[test_indices, 'Player'],
    'Team': data.loc[test_indices, 'Team'],
    'Actual Market Value (€M)': y_test.values,
    'Predicted Market Value (€M)': y_pred
})

# Lưu kết quả vào tệp CSV
result_df.to_csv('Linear_regression_result.csv', index=False)
print("Kết quả đã được lưu vào tệp 'Linear_regression_result.csv'")