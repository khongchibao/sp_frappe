# Từ điển dữ liệu SP Frappe

> Tệp này sinh tự động bằng `python scripts/gen_data_dictionary.py` - không sửa tay.

## SP Product Spec

*DocType*

**Quyền:** System Manager (read/write/create/delete); SP Quản lý (read/write/create/delete); SP Kỹ thuật (read/write/create); SP Kinh doanh (read/write); SP QC (read/write)

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `spec_code` | Mã spec | Data |  | không copy khi nhân bản; chỉ đọc | Mã định danh spec, giữ nguyên qua các phiên bản |
| `customer_code` | Mã khách hàng (viết tắt) | Data |  | tối đa 8 ký tự; không copy khi nhân bản | Tự sinh từ tên khách hàng nếu để trống. Dùng trong mã spec KG-<mã>-####. |
| `revision` | Phiên bản | Int |  | mặc định: 1; không copy khi nhân bản; chỉ đọc | Số phiên bản (R1, R2...) |
| `previous_revision` | Phiên bản trước | Link |  | → SP Product Spec; không copy khi nhân bản; chỉ đọc | Phiên bản trước |
| `spec_status` | Trạng thái | Select |  | Chọn: Nháp / Chờ duyệt mẫu / Đã duyệt / Ngưng; mặc định: Nháp; không copy khi nhân bản; chỉ đọc | Trạng thái do Workflow điều khiển |
| `customer` | Khách hàng | Link | Có | → Customer | Khách hàng |
| `customer_item_code` | Mã hàng của khách | Data |  |  | Mã hàng của khách |
| `item_name` | Tên sản phẩm | Data | Có |  | Tên sản phẩm |
| `erpnext_item` | Item ERPNext | Link |  | → Item; không copy khi nhân bản; chỉ đọc | Item ERPNext được tạo khi duyệt |
| `box_style` | Kiểu hộp | Link | Có | → SP Box Style | Kiểu hộp |
| `blank_formula` | Công thức khổ phôi | Data |  | lấy từ box_style.blank_formula; chỉ đọc | Công thức khổ phôi |
| `ply` | Số lớp | Select | Có | Chọn: 3 / 5 / 7 | Số lớp |
| `flute` | Loại sóng | Link | Có | → SP Flute | Loại sóng |
| `board_grade` | Kết cấu giấy | Link | Có | → SP Board Grade | Kết cấu giấy |
| `inner_l` | Dài trong (L) | Int | Có |  | Dài trong (L) |
| `inner_w` | Rộng trong (W) | Int | Có |  | Rộng trong (W) |
| `inner_h` | Cao trong (H) | Int | Có |  | Cao trong (H) |
| `blank_l` | Khổ phôi dài | Float |  | chỉ đọc khi `eval:doc.blank_formula!='MANUAL'`; 1 chữ số thập phân | Khổ phôi dài; tự tính (nhập tay khi công thức MANUAL) |
| `blank_w` | Khổ phôi rộng | Float |  | chỉ đọc khi `eval:doc.blank_formula!='MANUAL'`; 1 chữ số thập phân | Khổ phôi rộng; tự tính (nhập tay khi công thức MANUAL) |
| `area_per_box_m2` | Diện tích phôi (m²/thùng) | Float |  | 4 chữ số thập phân; chỉ đọc | Diện tích phôi cho một thùng, dùng tính giá/định mức giấy |
| `joint_type` | Kiểu mối nối | Select |  | Chọn: Dán keo / Ghim / Băng keo / Không; mặc định: Dán keo | Kiểu mối nối |
| `print_method` | Phương pháp in | Select |  | Chọn: Không in / Flexo trực tiếp / Offset bồi; mặc định: Không in | Phương pháp in |
| `color_count` | Số màu | Int |  | chỉ đọc | Số màu |
| `colors` | Bảng màu | Table |  | → SP Spec Color; hiện khi `eval:doc.print_method!='Không in'` | Bảng màu |
| `operations` | Quy trình công đoạn | Table |  | → SP Spec Operation | Quy trình công đoạn |
| `cutting_die` | Khuôn bế | Link |  | → SP Tooling | Bắt buộc khi kiểu hộp có đánh dấu 'Bắt buộc khuôn bế'. |
| `printing_plate` | Bản in | Link |  | → SP Tooling | Bản in |
| `ect_min` | ECT tối thiểu (kN/m) | Float |  | 2 chữ số thập phân | ECT tối thiểu (kN/m) |
| `bct_min` | BCT tối thiểu (N) | Float |  | 1 chữ số thập phân | BCT tối thiểu (N) |
| `burst_min` | Bục tối thiểu (kPa) | Float |  | 1 chữ số thập phân | Bục tối thiểu (kPa) |
| `moisture_max` | Độ ẩm tối đa (%) | Float |  | 1 chữ số thập phân | Độ ẩm tối đa (%) |
| `fsc_claim` | FSC | Select |  | Chọn: Không / FSC Mix / FSC Recycled; mặc định: Không | FSC |
| `qty_per_bundle` | Số thùng / bó | Int |  |  | Số thùng / bó |
| `bundles_per_pallet` | Số bó / pallet | Int |  |  | Số bó / pallet |
| `artwork_file` | File artwork | Attach |  |  | File artwork |
| `approved_sample_date` | Ngày duyệt mẫu | Date |  |  | Ngày duyệt mẫu |
| `approved_by` | Người duyệt | Link |  | → User; không copy khi nhân bản; chỉ đọc | Người duyệt |
| `usage_counted` | Đã ghi nhận sử dụng công cụ | Check |  | không copy khi nhân bản; chỉ đọc | Cờ nội bộ: đã cộng usage_count cho công cụ |

**Quy tắc nghiệp vụ**

- Tên document = `{spec_code}-R{revision}`; `spec_code` = `KG-{customer_code}-####`, `customer_code` tự sinh từ tên khách hàng nếu để trống.
- `ply` phải khớp loại sóng và kết cấu giấy; kết cấu giấy phải dùng đúng loại sóng của spec.
- Kích thước trong 50-2500 mm. Khổ phôi và m²/thùng tự tính từ công thức của kiểu hộp + hệ số bù của loại sóng.
- Có in (Flexo/Offset) thì bảng màu không được rỗng, độ phủ 0-100; không in thì bảng màu phải rỗng.
- Kiểu hộp đánh dấu `requires_die` thì bắt buộc có khuôn bế; khuôn bế/bản in phải đúng loại công cụ.
- Trước khi duyệt: bắt buộc `artwork_file`, `approved_sample_date`, `qty_per_bundle`, `bundles_per_pallet`.
- Spec Đã duyệt/Ngưng: các trường trong SP Settings > `revision_lock_fields` không được sửa; dùng 'Tạo phiên bản mới'.
- SP QC chỉ sửa nhóm Chất lượng; SP Kinh doanh chỉ thao tác workflow; SP Kỹ thuật/Quản lý sửa tự do khi chưa khóa.
- Khi duyệt: tạo/cập nhật Item ERPNext (nếu bật), cộng usage_count khuôn/bản in (một lần cho mỗi spec_code + công cụ), chuyển bản đã duyệt trước đó sang Ngưng.

## SP Spec Color

*Child table*

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `ink_code` | Mã mực | Data | Có |  | Mã mực |
| `pantone` | Pantone | Data |  |  | Pantone |
| `coverage_percent` | Độ phủ (%) | Float |  | mặc định: 100; 1 chữ số thập phân | Độ phủ (%) |
| `print_side` | Mặt in | Select |  | Chọn: Ngoài / Trong; mặc định: Ngoài | Mặt in |

## SP Spec Operation

*Child table*

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `seq` | Thứ tự | Int | Có |  | Thứ tự |
| `operation` | Công đoạn | Select | Có | Chọn: Máy sóng / In flexo / In offset / Bồi / Bế / Dán/Ghim / Đóng gói | Công đoạn |
| `note` | Ghi chú | Data |  |  | Ghi chú |

## SP Board Grade

*DocType*

**Quyền:** System Manager (read/write/create/delete); SP Quản lý (read/write/create/delete); SP Kỹ thuật (read/write/create); SP Kinh doanh (read); SP QC (read)

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `ply` | Số lớp | Select | Có | Chọn: 3 / 5 / 7 | Số lớp |
| `flute` | Loại sóng | Link | Có | → SP Flute | Loại sóng |
| `active` | Đang sử dụng | Check |  | mặc định: 1 | Đang sử dụng |
| `ect_target` | ECT mục tiêu (kN/m) | Float |  | 2 chữ số thập phân | ECT mục tiêu (kN/m) |
| `bursting_target` | Bục mục tiêu (kPa) | Float |  | 1 chữ số thập phân | Bục mục tiêu (kPa) |
| `layers` | Lớp giấy | Table | Có | → SP Board Grade Layer | Lớp giấy |

**Quy tắc nghiệp vụ**

- Tên tự sinh `<số lớp><sóng>-<gsm các lớp>`, ví dụ `3B-125/100/125`; trùng thì thêm hậu tố `-2`, `-3`.
- Số dòng lớp = số lớp; lớp đầu là Mặt, lớp cuối là Đáy; số lớp Sóng = số lớp // 2 và xen kẽ lớp phẳng.

## SP Board Grade Layer

*Child table*

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `layer_no` | Lớp | Int | Có |  | Lớp |
| `layer_role` | Vai trò | Select | Có | Chọn: Mặt / Sóng / Lót giữa / Đáy | Vai trò |
| `paper` | Mã giấy | Link | Có | → SP Paper | Mã giấy |
| `gsm` | Định lượng (gsm) | Int |  | lấy từ paper.gsm; chỉ đọc | Định lượng (gsm) |

## SP Paper

*DocType* - đặt tên: `field:paper_code`

**Quyền:** System Manager (read/write/create/delete); SP Quản lý (read/write/create/delete); SP Kỹ thuật (read/write/create); SP Kinh doanh (read); SP QC (read)

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `paper_code` | Mã giấy | Data | Có | duy nhất | Mã giấy |
| `paper_type` | Loại giấy | Select | Có | Chọn: Kraft / Test liner / Medium / Duplex / Ivory / Khác | Loại giấy |
| `gsm` | Định lượng (gsm) | Int | Có |  | Định lượng (gsm) |
| `color` | Màu giấy | Select |  | Chọn: Nâu / Trắng; mặc định: Nâu | Màu giấy |
| `supplier` | Nhà cung cấp | Link |  | → Supplier | Nhà cung cấp |
| `active` | Đang sử dụng | Check |  | mặc định: 1 | Đang sử dụng |

## SP Flute

*DocType* - đặt tên: `field:flute_code`

**Quyền:** System Manager (read/write/create/delete); SP Quản lý (read/write/create/delete); SP Kỹ thuật (read/write/create); SP Kinh doanh (read); SP QC (read)

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `flute_code` | Mã sóng | Data | Có | duy nhất | Mã sóng |
| `ply` | Số lớp | Select | Có | Chọn: 3 / 5 / 7 | Số lớp |
| `thickness_mm` | Độ dày (mm) | Float |  | 1 chữ số thập phân | Độ dày (mm) |
| `length_allowance_mm` | Bù khổ dài (mm) | Float |  | 1 chữ số thập phân | Hệ số bù khổ dài theo loại sóng [GIẢ ĐỊNH] |
| `width_allowance_mm` | Bù khổ rộng (mm) | Float |  | 1 chữ số thập phân | Hệ số bù khổ rộng theo loại sóng [GIẢ ĐỊNH] |
| `glue_flap_mm` | Mép dán (mm) | Int |  | mặc định: 35 | Mép dán/ghim cộng vào chiều dài phôi [GIẢ ĐỊNH] |
| `is_assumed` | Hệ số giả định - cần xác nhận | Check |  | mặc định: 1 | Đánh dấu hệ số chưa được xưởng xác nhận |
| `description` | Mô tả | Small Text |  |  | Mô tả |

**Quy tắc nghiệp vụ**

- Hệ số bù khổ và mép dán là [GIẢ ĐỊNH]; sửa trực tiếp ở master, không cần sửa code.

## SP Box Style

*DocType* - đặt tên: `field:style_code`

**Quyền:** System Manager (read/write/create/delete); SP Quản lý (read/write/create/delete); SP Kỹ thuật (read/write/create); SP Kinh doanh (read); SP QC (read)

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `style_code` | Mã kiểu hộp (FEFCO) | Data | Có | duy nhất | Mã kiểu hộp (FEFCO) |
| `style_name` | Tên kiểu hộp | Data | Có |  | Tên kiểu hộp |
| `blank_formula` | Công thức khổ phôi | Select | Có | Chọn: RSC_0201 / FOL_0203 / MANUAL | Công thức khổ phôi |
| `requires_die` | Bắt buộc khuôn bế | Check |  |  | Bắt buộc khuôn bế |
| `description` | Mô tả | Small Text |  |  | Mô tả |

## SP Tooling

*DocType*

**Quyền:** System Manager (read/write/create/delete); SP Quản lý (read/write/create/delete); SP Kỹ thuật (read/write/create); SP Kinh doanh (read); SP QC (read)

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `tooling_type` | Loại công cụ | Select | Có | Chọn: Khuôn bế / Bản in / Anilox | Loại công cụ |
| `status` | Trạng thái | Select |  | Chọn: Sẵn sàng / Đang dùng / Sửa chữa / Hết hạn; mặc định: Sẵn sàng | Trạng thái |
| `customer` | Khách hàng | Link |  | → Customer | Khách hàng |
| `storage_location` | Vị trí lưu kho | Data |  |  | Vị trí lưu kho |
| `last_used_on` | Ngày dùng gần nhất | Date |  |  | Ngày dùng gần nhất |
| `usage_count` | Số lần đã dùng | Int |  | mặc định: 0; chỉ đọc | Số lần đã dùng |
| `max_life` | Tuổi thọ tối đa (lần) | Int |  |  | Tuổi thọ tối đa (lần) |
| `life_percent` | Đã dùng (%) | Percent |  | chỉ đọc | Mức tuổi thọ đã dùng, dùng cho báo cáo SP Tooling Life |
| `notes` | Ghi chú | Small Text |  |  | Ghi chú |

**Quy tắc nghiệp vụ**

- Tên theo loại: `KB-####` (khuôn bế), `BI-####` (bản in), `AN-####` (anilox).
- `life_percent` = usage_count / max_life; đạt 100% thì trạng thái tự chuyển Hết hạn.

## SP Settings

*Single*

**Quyền:** System Manager (read/write/create/delete); SP Quản lý (read/write/create); SP Kỹ thuật (read); SP Kinh doanh (read); SP QC (read)

| fieldname | Nhãn | Kiểu | Bắt buộc | Ràng buộc | Mục đích |
| --- | --- | --- | --- | --- | --- |
| `auto_create_item` | Tự tạo Item ERPNext khi duyệt | Check |  | mặc định: 1 | Tự tạo Item ERPNext khi duyệt |
| `item_group` | Nhóm Item | Link |  | → Item Group | Mặc định: Products (tự tạo khi cài app). |
| `stock_uom` | Đơn vị tính | Link |  | → UOM | Mặc định: Thùng (tự tạo khi cài app). |
| `revision_lock_fields` | Các trường bị khóa sau khi duyệt | Small Text |  | mặc định: customer
customer_code
box_style
ply
flute
board_grade
inner_l
inner_w
inner_h
blank_l
blank_w
joint_type
print_method
cutting_die
printing_plate
colors
operations | Danh sách trường bị khóa sau khi duyệt |

**Quy tắc nghiệp vụ**

- `revision_lock_fields`: mỗi dòng một fieldname của SP Product Spec; lưu sai tên sẽ báo lỗi.
