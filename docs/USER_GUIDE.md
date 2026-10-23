# Hướng dẫn sử dụng SP Frappe

Mở **Spec Sản phẩm** trên thanh điều hướng (Workspace). Tại đây có 3 thẻ số (Spec chờ duyệt, Spec đã duyệt tháng này, Công cụ sắp hết tuổi) và lối tắt tới mọi danh mục, báo cáo.

## Vai trò và quyền

| Vai trò | Được làm | Không được làm |
| --- | --- | --- |
| **SP Kỹ thuật** | Tạo/sửa spec Nháp, sửa master (giấy, sóng, kết cấu, kiểu hộp, công cụ), gửi duyệt, tạo phiên bản mới | Duyệt, ngưng, sửa spec đã duyệt |
| **SP Kinh doanh** | Xem spec, duyệt hoặc trả lại spec "Chờ duyệt mẫu" | Sửa thông số kỹ thuật |
| **SP QC** | Xem; sửa nhóm **Chất lượng** (ECT, BCT, bục, độ ẩm, FSC) kể cả khi spec đã duyệt | Sửa kích thước, kết cấu, in, công cụ |
| **SP Quản lý** | Toàn quyền, gồm Ngưng sử dụng và SP Settings | - |

## 1. SP Kỹ thuật - lập spec

**Chuẩn bị danh mục (một lần):** SP Paper → SP Board Grade (chọn số lớp, loại sóng, rồi từng lớp giấy) → SP Tooling (khuôn bế, bản in, anilox).

**Lập spec:**
1. Mở **SP Product Spec** → *Thêm mới*. Chọn **Khách hàng** (mã viết tắt tự sinh, sửa được).
2. Chọn **Kiểu hộp**, **Số lớp**, **Loại sóng**, **Kết cấu giấy** (danh sách tự lọc theo số lớp/sóng). Đổi số lớp thì sóng và kết cấu bị xóa để chọn lại.
3. Nhập **Dài/Rộng/Cao trong** (50-2500 mm). Lưu: hệ thống tính **Khổ phôi** và **m²/thùng**. Kiểu hộp MANUAL (DIECUT, SHEET, 0300, 0427) thì nhập tay khổ phôi.
4. **Gia công:** chọn mối nối, phương pháp in. Có in thì khai bảng màu (mã mực, Pantone, độ phủ 0-100%, mặt in); số màu tự đếm. Thêm các công đoạn theo thứ tự.
5. **Công cụ:** chọn khuôn bế (bắt buộc với kiểu hộp có khuôn như 0427, DIECUT) và bản in.
6. Nhập yêu cầu chất lượng, quy cách đóng gói, đính kèm **artwork**, ghi **ngày duyệt mẫu**.
7. Bấm **Gửi duyệt** (nút Hành động). Spec sang "Chờ duyệt mẫu".

Thông báo lỗi thường gặp:

| Thông báo | Cách xử lý |
| --- | --- |
| Loại sóng X là sóng N lớp, không khớp | Chọn lại số lớp hoặc loại sóng |
| Kiểu hộp X bắt buộc phải có khuôn bế | Chọn khuôn bế loại "Khuôn bế" |
| Có in thì phải khai báo bảng màu | Thêm dòng vào Bảng màu hoặc đổi "Không in" |
| Trước khi duyệt phải có: ... | Bổ sung artwork, ngày duyệt mẫu, quy cách đóng gói rồi gửi lại |

## 2. SP Kinh doanh - duyệt mẫu

1. Mở thẻ **Spec chờ duyệt** hoặc báo cáo SP Spec Register lọc "Chờ duyệt mẫu".
2. Kiểm tra artwork, kích thước, kết cấu. Bấm **Duyệt** hoặc **Trả lại** (spec về Nháp để kỹ thuật sửa).
3. Khi duyệt, hệ thống: ghi người duyệt, tạo/cập nhật **Item ERPNext** (mã = mã spec), cộng số lần dùng cho khuôn/bản in, chuyển bản đã duyệt trước đó sang Ngưng.

## 3. SP QC - chỉ tiêu chất lượng

Mở spec (kể cả đã duyệt), sửa mục **Chất lượng**, lưu. Các mục khác bị chặn với thông báo "Vai trò của bạn không được sửa".

## 4. SP Quản lý - quản trị

- **Ngưng sử dụng** một spec đã duyệt (nút Hành động).
- **SP Settings:** bật/tắt tạo Item tự động, nhóm Item, đơn vị tính; **danh sách trường khóa** sau khi duyệt (mỗi dòng một fieldname).
- Theo dõi công cụ: báo cáo **SP Tooling Life** liệt kê khuôn/bản in dùng ≥ 80% tuổi thọ hoặc đang Sửa chữa/Hết hạn.

## Sửa spec đã duyệt: tạo phiên bản mới

Spec đã duyệt khóa các trường kỹ thuật. Để thay đổi:
1. Mở spec đã duyệt → bấm **Tạo phiên bản mới** (SP Kỹ thuật hoặc SP Quản lý). Hệ thống tạo R2 ở trạng thái Nháp, copy toàn bộ nội dung, xóa ngày duyệt mẫu.
2. Sửa R2, gửi duyệt, duyệt như bình thường.
3. Khi R2 được duyệt, R1 tự chuyển **Ngưng**; Item ERPNext được cập nhật theo R2.

Mỗi mã spec chỉ có một phiên bản đang soạn/chờ duyệt cùng lúc.

## In phiếu kỹ thuật

Mở spec → **In** → chọn mẫu **Phiếu Kỹ thuật Sản phẩm** (A4, một trang, có ô ký Lập/Kiểm tra/Duyệt, mã tài liệu và revision ở chân trang).

## Báo cáo

| Báo cáo | Bộ lọc | Dùng để |
| --- | --- | --- |
| SP Spec Register | Khách hàng, trạng thái, kiểu hộp, khoảng ngày tạo | Tra cứu spec theo khách; xuất Excel |
| SP Tooling Life | Loại công cụ | Lên kế hoạch làm khuôn/bản in mới |

## Hiệu chỉnh khổ phôi với thực tế

1. Lập spec thử cho 3 mã hàng thật (thùng 0201 3 lớp, thùng 5 lớp, hộp 0203) với kích thước thật.
2. So khổ phôi hệ thống với khổ phôi xưởng đang cắt. Lệch > 5 mm: sửa **Bù khổ dài/rộng**, **Mép dán** ở master SP Flute tương ứng, bỏ tick "Hệ số giả định".
3. Spec nháp tự tính lại khi lưu; spec đã duyệt giữ nguyên, muốn áp số mới thì tạo phiên bản mới.
