# CLAUDE.md - SP Frappe

## Bối cảnh
App Frappe `sp_frappe` (module "SP Frappe"): Spec Sản phẩm carton (Technical Data Sheet) cho King Group, nhà máy thùng carton sóng 3/5/7 lớp, in flexo và offset bồi (Cần Thơ). Xương sống dữ liệu cho kế hoạch ERP: Spec → Item ERPNext. Chủ dự án làm quản lý nhà máy; giao diện tiếng Việt, tên trường (fieldname) tiếng Anh snake_case, tài liệu tiếng Việt.

Đọc trước khi sửa: `docs/DECISIONS.md` (mọi giả định, kể cả danh sách [GIẢ ĐỊNH]), `docs/DATA_DICTIONARY.md`, `README.md`.

## Nền tảng
Frappe/ERPNext **version-16**, Python 3.14, Node 24, MariaDB. Gốc repo = gốc app.

## Bản đồ mã
| Đường dẫn | Nội dung |
| --- | --- |
| `sp_frappe/sp_frappe/doctype/*` | DocType (JSON + controller + test + JS) |
| `sp_frappe/sp_frappe/doctype/sp_product_spec/sp_product_spec.py` | Logic chính: đặt tên, validate, khóa sửa, duyệt, tạo Item, `create_new_revision` |
| `sp_frappe/utils/blank.py`, `utils/naming.py` | Hàm thuần (không import frappe) - công thức khổ phôi, mã khách hàng/kết cấu |
| `sp_frappe/fixtures/*.json` | Role, workflow, loại sóng, kiểu hộp, UOM (nạp qua `hooks.fixtures`, thứ tự quan trọng) |
| `sp_frappe/sp_frappe/{report,number_card,workspace,sidebar,print_format}` | Báo cáo, thẻ số, workspace, sidebar (doctype `Sidebar` của v16), mẫu in |
| `sp_frappe/install.py` | `after_install`/`after_migrate`: UOM, nhóm Item, SP Settings mặc định |
| `sp_frappe/demo.py` | `bench --site X execute sp_frappe.demo.make_demo_data` (idempotent) |
| `sp_frappe/tests/` | `unit/` (pytest thuần), `utils.py` (helper dùng chung test + demo), test báo cáo/in/demo |
| `scripts/` | `gen_data_dictionary.py`, `build_print_format.py` |

## Lệnh thường dùng
```bash
bench --site <site> set-config allow_tests true
bench --site <site> run-tests --app sp_frappe
bench --site <site> run-tests --module sp_frappe.sp_frappe.doctype.sp_product_spec.test_sp_product_spec
python -m pytest sp_frappe/tests/unit -q          # không cần bench
python scripts/gen_data_dictionary.py             # sau khi đổi DocType JSON
python scripts/build_print_format.py              # sau khi sửa template.html
pre-commit run --all-files                        # ruff + prettier + eslint
bench --site <site> migrate                       # đồng bộ JSON/fixtures
```

## Quy ước
- Code Python thụt bằng tab (cấu hình ruff của Frappe). Commit theo Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `ci:`).
- Hệ số kỹ thuật (bù khổ, mép dán) nằm ở master SP Flute, **không hard-code** trong Python. Giá trị chưa xác nhận gắn nhãn [GIẢ ĐỊNH].
- Mọi giả định/lựa chọn mới ghi vào `docs/DECISIONS.md`.
- Không đưa secret hoặc dữ liệu khách hàng thật vào repo.

## Bẫy đã gặp
- File JSON chuẩn (DocType, Print Format, Workspace...) chỉ được `migrate` đồng bộ lại khi `modified` mới hơn bản trong DB; sửa tay thì tăng `modified`.
- Single doctype được lưu lúc cài app trước khi fixtures nạp: không đặt giá trị mặc định cho Link trỏ tới bản ghi do app tạo.
- Test: `IntegrationTestCase` chỉ rollback cuối class → dùng savepoint trong `setUp` (xem `test_sp_product_spec.py`); `IGNORE_TEST_RECORD_DEPENDENCIES` chỉ dùng được cho test nằm trong thư mục doctype.
- Site chưa chạy setup wizard không có Customer Group/Territory lá: dùng `tests.utils.ensure_erp_roots()`.
- `frappe.get_all(..., fields=["max(x)"])`/`get_value` với hàm SQL dạng chuỗi bị chặn ở v16: dùng `pluck` rồi `max()`.
- Dựng bench trong sandbox cloud: `bench` không chạy bằng root; cần user thường, Node 24 (`n 24`), Python 3.14 (`uv python install 3.14`), `bench get-app` bằng URL đầy đủ.

## Việc tiếp theo (v0.2)
Liên kết Quotation (giá theo m²), BOM giấy tự động từ kết cấu, ghi nhận sử dụng khuôn từ Job Card, thêm mã sóng 7 lớp + hệ số thực tế, trường thời điểm duyệt cho Number Card.
