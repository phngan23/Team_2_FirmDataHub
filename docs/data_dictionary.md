# Từ điển dữ liệu (Data Dictionary) - Project FirmHub

Tài liệu này mô tả chi tiết cấu trúc cơ sở dữ liệu `team2_firmhub`, giúp hiểu rõ ý nghĩa các cột và mối liên hệ giữa Database với file Excel gốc.

## 1. Các bảng Danh mục (Dimension Tables)
Lưu trữ các thông tin định danh, ít thay đổi.

| Tên bảng | Ý nghĩa | Các cột chính |
| :--- | :--- | :--- |
| `dim_firm` | Danh sách công ty | `ticker`, `company_name`, `founded_year` |
| `dim_exchange` | Sàn giao dịch | `exchange_code` (HOSE, HNX) |
| `dim_industry_l2` | Ngành cấp 2 | `industry_l2_name` (Dược phẩm, Hóa chất...) |
| `dim_data_source` | Nguồn dữ liệu | `source_name` (Vietstock, FiinPro, BCTC) |

---

## 2. Các bảng Dữ liệu (Fact Tables)
Lưu trữ các con số biến đổi theo năm, được ánh xạ từ các biến trong file Excel.

### 2.1 Bảng `fact_financial_year` (Số liệu tài chính)
*Chứa dữ liệu từ Biến 6 đến Biến 37 trong Excel.*

| Cột trong DB | Biến Excel | Mô tả |
| :--- | :--- | :--- |
| `net_sales` | (6) | Doanh thu thuần |
| `total_assets` | (7) | Tổng tài sản |
| `net_income` | (21) | Lợi nhuận ròng |
| `total_equity` | (22) | Vốn chủ sở hữu |
| `cash_and_equivalents` | (28) | Tiền và tương đương tiền |
| `inventory` | (33) | Hàng tồn kho |

### 2.2 Bảng `fact_ownership_year` (Sở hữu)
| Cột trong DB | Biến Excel | Mô tả |
| :--- | :--- | :--- |
| `managerial_inside_own` | (1) | Tỷ lệ sở hữu của Ban lãnh đạo |
| `state_own` | (2) | Tỷ lệ sở hữu Nhà nước |
| `foreign_own` | (4) | Tỷ lệ sở hữu nước ngoài |

### 2.3 Các bảng Fact khác
- `fact_market_year`: Giá cổ phiếu, Vốn hóa, EPS (Biến 5, 23, 35).
- `fact_innovation_year`: Biến giả về đổi mới sản phẩm/quy trình (Biến 19, 20).
- `fact_data_snapshot`: Lưu vết mỗi lần bạn chạy script nạp dữ liệu (ETL).

---

## 3. Sơ đồ quan hệ (Entity Relationship)

- **dim_firm** là bảng trung tâm.
- Các bảng **Fact** nối với **dim_firm** qua `firm_id`.
- Các bảng **Fact** nối với **fact_data_snapshot** qua `snapshot_id` để quản lý phiên bản.



---

## 4. Ghi chú về đơn vị (Units)
- Các giá trị tiền tệ: Mặc định lưu theo đơn vị **Tỷ VNĐ** (Unit Scale = 1,000,000,000) để bảng dữ liệu gọn gàng hơn.
- Tỷ lệ sở hữu: Lưu dưới dạng số thập phân (ví dụ 0.45 tương đương 45%).