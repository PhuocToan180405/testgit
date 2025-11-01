import pandas as pd
from sqlalchemy import create_engine, text

# ======================
# Bước 1: Extract (Trích xuất dữ liệu từ CSV)
# ======================
print("Extracting data from CSV files...")

df_customer = pd.read_csv("customer.csv")
df_product = pd.read_csv("product.csv")

print("Extraction complete.")

# ======================
# Bước 2: Transform (Làm sạch và biến đổi dữ liệu)
# ======================
print("Transforming data...")

# Chuyển đổi kiểu dữ liệu UnitPrice sang số
df_product["UnitPrice"] = pd.to_numeric(df_product["UnitPrice"], errors="coerce")

# Loại bỏ trùng lặp
df_customer.drop_duplicates(subset=["CustomerID"], inplace=True)
df_product.drop_duplicates(subset=["ProductID"], inplace=True)

# Thay giá trị NULL email bằng giá trị mặc định
df_customer["Email"].fillna("unknown@example.com", inplace=True)

print("Transformation complete.")

# ======================
# Bước 3: Load (Đẩy dữ liệu vào SQL Server)
# ======================
print("Loading data into SQL Server...")

server_name = "localhost"       # thay bằng server SQL của bạn
database_name = "lab3"          # thay bằng database của bạn

connection_string = f"mssql+pyodbc://@{server_name}/{database_name}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(connection_string)

try:
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM FactSales;"))   # xóa bảng fact trước (nếu có)
        conn.execute(text("DELETE FROM DimCustomer;"))
        conn.execute(text("DELETE FROM DimProduct;"))

        # Insert lại dữ liệu sạch
        df_customer.to_sql("DimCustomer", con=conn, if_exists="append", index=False)
        df_product.to_sql("DimProduct", con=conn, if_exists="append", index=False)

    print("✅ Data loaded successfully (no duplicates).")

except Exception as e:
    print(f"An error occurred: {e}")
