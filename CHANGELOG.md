# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.1.0/), phiên bản theo [SemVer](https://semver.org/lang/vi/).

## [0.1.0] - 2026-10-23

### Thêm mới
- 7 DocType (SP Product Spec, SP Board Grade, SP Paper, SP Flute, SP Box Style, SP Tooling, SP Settings) và 3 child table (SP Board Grade Layer, SP Spec Color, SP Spec Operation); nhãn tiếng Việt.
- Tính khổ phôi và m²/thùng (RSC_0201, FOL_0203, MANUAL) từ hệ số trong master SP Flute.
- Workflow "SP Product Spec Approval" (Nháp → Chờ duyệt mẫu → Đã duyệt → Ngưng), 4 role SP, phân quyền theo nhóm trường.
- Khóa sửa sau khi duyệt (danh sách cấu hình trong SP Settings), nút "Tạo phiên bản mới", tự chuyển bản cũ sang Ngưng.
- Tự tạo/cập nhật Item ERPNext khi duyệt; ghi nhận số lần dùng khuôn/bản in.
- Báo cáo SP Spec Register, SP Tooling Life; 3 Number Card; Workspace + Sidebar; Print Format "Phiếu Kỹ thuật Sản phẩm" (A4).
- Fixtures: 7 loại sóng, 6 kiểu hộp, role, workflow, UOM Thùng. Demo: `sp_frappe.demo.make_demo_data`.
- Test tích hợp (IntegrationTestCase) và test thuần (pytest/unittest); CI GitHub Actions; pre-commit (ruff, prettier, eslint).
- Tài liệu: README, USER_GUIDE, DATA_DICTIONARY (sinh tự động), DECISIONS, CLAUDE.md.
