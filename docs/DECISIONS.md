# Quyết định thiết kế (DECISIONS)

Mọi giả định và lựa chọn kỹ thuật của v0.1, ghi ngày 2026-10-23. Mục có nhãn **[GIẢ ĐỊNH]** cần xưởng xác nhận.

## 1. Nền tảng và môi trường

| # | Quyết định | Lý do | Phương án bỏ |
| --- | --- | --- | --- |
| 1.1 | Frappe/ERPNext **version-16** (Frappe 16.53.0, ERPNext 16.52.1 lúc build); Python 3.14, Node 24 | Nhánh stable mới nhất đọc từ GitHub (`git ls-remote`); `required_apps = ["erpnext"]` | version-15 (cũ hơn, thiếu tính năng v16) |
| 1.2 | Dựng **bench thật** trong sandbox (MariaDB 10.11 + Redis, user `frappe` không phải root) để chạy test cục bộ; CI dùng MariaDB 11.8 | Dựng được trong giới hạn 45 phút nên không cần chế độ "CI-first" | Chỉ chạy pytest thuần |
| 1.3 | Gốc repo = gốc app (`pyproject.toml`, `sp_frappe/` ngang hàng), đúng cấu trúc `bench new-app` | `bench get-app <repo>` hoạt động trực tiếp | Thư mục con |
| 1.4 | `bench get-app erpnext` dùng URL đầy đủ trong CI | Tên ngắn tra qua GitHub API, bị chặn trong sandbox | Tên ngắn |
| 1.5 | Làm việc trên nhánh `claude/sp-frappe-v0.1`, mở Pull Request vào `main` | Phiên không merge vào `main` khi chưa được yêu cầu | Đẩy thẳng `main` |

## 2. Mô hình dữ liệu

| # | Quyết định | Lý do |
| --- | --- | --- |
| 2.1 | Thêm trường `customer_code` (Data, ≤ 8 ký tự) trên spec; tự sinh từ tên khách hàng (bỏ dấu, bỏ "Công ty/TNHH/CP...", lấy chữ cái đầu, tối đa 4) | Prompt dùng `{customer_code}` nhưng Customer của ERPNext không có trường này; tránh tạo Custom Field trên doctype lõi |
| 2.2 | `spec_code` = `KG-<customer_code>-####`, tên document = `<spec_code>-R<revision>`; các phiên bản dùng chung `spec_code` và **một Item ERPNext** (`item_code = spec_code`) | Item đại diện mã hàng, spec là thông số theo phiên bản |
| 2.3 | SP Board Grade đặt tên `<ply><sóng>-<gsm các lớp>`; trùng tên thì thêm `-2`, `-3` | Cùng gsm có thể khác mã giấy/ECT |
| 2.4 | Kết cấu giấy: lớp đầu Mặt, lớp cuối Đáy, số lớp Sóng = ply // 2, sóng xen kẽ lớp phẳng (Lót giữa). Một Board Grade có **một** `flute` (mã sóng gộp như BC) | Đúng cấu tạo carton 3/5/7 lớp |
| 2.5 | Seed 7 loại sóng đúng đề bài (A, B, C, E = 3 lớp; BC, BE, CE = 5 lớp). **Chưa seed sóng 7 lớp**; người dùng tự thêm vào SP Flute | Đề bài không nêu mã sóng 7 lớp |
| 2.6 | SP Tooling đặt tên bằng `autoname()` theo loại (KB-/BI-/AN-), `tooling_type` chỉ chọn một lần | Naming theo giá trị trường không biểu diễn được bằng format JSON |
| 2.7 | `life_percent` lưu thành cột (không tính khi đọc) và tự chuyển trạng thái Hết hạn khi ≥ 100% | Báo cáo/Number Card lọc được bằng SQL |
| 2.8 | Link mặc định (`item_group`, `stock_uom`) **không** đặt trong JSON của SP Settings; `after_install` tạo UOM `Thùng`, nhóm Item `Products` rồi gán | `init_singles` lưu Settings trước khi fixture nạp, link chưa tồn tại sẽ làm cài app lỗi |

## 3. Nghiệp vụ

| # | Quyết định | Lý do |
| --- | --- | --- |
| 3.1 | **Khóa sửa** áp dụng cho trạng thái Đã duyệt **và** Ngưng; danh sách trường khóa nằm ở SP Settings (mặc định: khách hàng, kiểu hộp, kết cấu, kích thước, khổ phôi, mối nối, in, công cụ, bảng màu, công đoạn). Bảng con so sánh theo nội dung dòng | Đúng "chặn sản xuất sai spec", chỉnh được không cần code |
| 3.2 | Spec bị khóa **không tính lại khổ phôi** | Nếu sửa hệ số master sau khi duyệt, spec cũ không đổi và không bị lỗi khóa |
| 3.3 | Phân quyền theo trường làm ở controller: SP QC chỉ sửa nhóm Chất lượng; SP Kinh doanh chỉ thao tác workflow; SP Kỹ thuật/Quản lý/System Manager sửa tự do khi chưa khóa | Frappe không phân quyền theo nhóm trường mà vẫn cho workflow chạy; permlevel không phù hợp |
| 3.4 | Workflow cho phép tự duyệt (`allow_self_approval`) | Nhà máy nhỏ, một người có thể giữ nhiều vai trò |
| 3.5 | Bắt buộc `artwork_file`, `approved_sample_date` **và** quy cách đóng gói (`qty_per_bundle`, `bundles_per_pallet` > 0) chỉ khi chuyển sang Đã duyệt | Không làm chậm nhập liệu bản nháp |
| 3.6 | `usage_count` của khuôn/bản in cộng **một lần cho mỗi cặp spec_code + công cụ**, không cộng lại ở các phiên bản sau | "Duyệt lần đầu" theo đề bài |
| 3.7 | Tạo phiên bản mới chỉ từ spec Đã duyệt và chỉ khi chưa có bản Nháp/Chờ duyệt cùng `spec_code`; xóa `approved_sample_date`, giữ artwork | Tránh nhiều bản đang soạn song song; mẫu mới phải được duyệt lại |
| 3.8 | Cập nhật Item khi duyệt phiên bản mới không đổi `stock_uom` (ERPNext chặn đổi UOM khi đã có giao dịch) | An toàn dữ liệu kho |
| 3.9 | Tên Item = tên sản phẩm; mô tả Item là HTML ngắn (khách, kiểu hộp, kích thước, kết cấu, khổ phôi, phiên bản) | Đủ để tra cứu trong ERPNext |

## 4. Báo cáo, giao diện

| # | Quyết định | Lý do |
| --- | --- | --- |
| 4.1 | SP Spec Register lọc khoảng ngày theo **ngày tạo** spec | Spec nháp chưa có ngày duyệt; cột "Ngày duyệt mẫu" vẫn hiển thị |
| 4.2 | Number Card "Spec đã duyệt tháng này" đếm theo `approved_sample_date` trong tháng | Chưa có trường thời điểm duyệt; có thể bổ sung ở v0.2 |
| 4.3 | Frappe 16.53 dùng doctype `Sidebar` (thư mục `sidebar/` trong module) thay `Workspace Sidebar`; **không** gửi `Desktop Icon` | Desktop Icon chỉ nạp ở chế độ lưới biểu tượng; Workspace + Sidebar là đủ |
| 4.4 | Print Format viết ở `template.html`, nhúng vào JSON bằng `scripts/build_print_format.py` (script bump `modified`) | Frappe không đọc file `.html` cho format Jinja chuẩn; file `.html` dễ sửa và review |
| 4.5 | Tên Print Format/Workspace giữ tiếng Việt có dấu; thư mục ASCII (`phieu_ky_thuat_san_pham`, `spec_sản_phẩm`) | Đúng tên hiển thị theo đề bài |

## 5. Chất lượng mã và test

| # | Quyết định | Lý do |
| --- | --- | --- |
| 5.1 | Prettier chỉ áp cho JS; JSON kiểm bằng `check-json` | Frappe xuất JSON thụt 1 khoảng trắng; Prettier sẽ đổi định dạng ở mỗi lần export |
| 5.2 | Test tích hợp dùng `IntegrationTestCase` (không phải `FrappeTestCase` đã cũ), rollback bằng savepoint sau từng test, khai báo `IGNORE_TEST_RECORD_DEPENDENCIES` để khỏi nạp bản ghi test của Customer/Item (tốn hàng chục giây và lỗi Payment Gateway) | Nhanh, độc lập thứ tự |
| 5.3 | Helper tạo dữ liệu test dùng chung với demo (`sp_frappe/tests/utils.py`); site mới chưa chạy setup wizard nên helper tự tạo Customer Group "Commercial", Territory "Vietnam", nhóm gốc | ERPNext cấm gán nhóm gốc (is_group) cho Customer |
| 5.4 | Hàm tính khổ phôi (`utils/blank.py`) và đặt mã (`utils/naming.py`) không import frappe | Chạy pytest không cần bench (CI job `unit`) |

## 6. Danh sách [GIẢ ĐỊNH] cần xác nhận

| Master | Trường | Giá trị mặc định |
| --- | --- | --- |
| SP Flute A (3 lớp) | thickness_mm / length_allowance_mm / width_allowance_mm | 4.8 / 19 / 10 |
| SP Flute B (3 lớp) | thickness_mm / length_allowance_mm / width_allowance_mm | 2.5 / 10 / 5 |
| SP Flute C (3 lớp) | thickness_mm / length_allowance_mm / width_allowance_mm | 3.6 / 14 / 7 |
| SP Flute E (3 lớp) | thickness_mm / length_allowance_mm / width_allowance_mm | 1.5 / 6 / 3 |
| SP Flute BC (5 lớp) | thickness_mm / length_allowance_mm / width_allowance_mm | 6.1 / 24 / 12 |
| SP Flute BE (5 lớp) | thickness_mm / length_allowance_mm / width_allowance_mm | 4.0 / 16 / 8 |
| SP Flute CE (5 lớp) | thickness_mm / length_allowance_mm / width_allowance_mm | 5.1 / 20 / 10 |
| SP Flute (cả 7 mã) | glue_flap_mm | 35 |
| SP Box Style 0203 | blank_formula | FOL_0203: rộng = H + 2W + bù rộng (theo đề bài, chưa đối chiếu thực tế) |
| SP Box Style 0300, 0427, DIECUT, SHEET | blank_formula | MANUAL (nhập tay khổ phôi) |
| SP Box Style 0427, DIECUT | requires_die | Có |

Quy ước bù khổ mặc định: bù dài ≈ 4 × độ dày sóng, bù rộng ≈ 2 × độ dày sóng (làm tròn). Sau khi xưởng xác nhận, sửa số trong SP Flute rồi bỏ tick `is_assumed`.
