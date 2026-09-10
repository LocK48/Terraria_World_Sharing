# Terraria World GitHub Pusher

Ứng dụng giao diện đồ họa (GUI) nhỏ gọn viết bằng Python, giúp bạn tự động hóa hoàn toàn quy trình lưu trữ, đồng bộ và đẩy (push) file thế giới Terraria (`.wld`) lên kho lưu trữ GitHub chỉ với vài cú click chuột.

Không cần nhớ lệnh Git phức tạp, không cần gõ Terminal thủ công mỗi lần chơi game xong!

---

## Tính năng nổi bật

* **Giao diện thân thiện (GUI):** Thao tác trực quan qua cửa sổ bấm chọn file đơn giản.
* **Tự động hóa Git hoàn toàn:** Tự động phát hiện, khởi tạo Git (`git init`), cấu hình nhánh và kết nối remote URL trong lần chạy đầu tiên.
* **Thông minh chống trùng lặp:** Tự động kiểm tra xem file thế giới có thực sự thay đổi nội dung hay không trước khi tiến hành commit, tránh lỗi rác lịch sử git.
* **Độc lập, tiện lợi:** Có thể đóng gói thành file `.exe` duy nhất để chạy nhanh mà không cần cài đặt phức tạp trên máy.

---

## Hướng dẫn cài đặt và sử dụng

### Cách 1: Sử dụng file mã nguồn Python (`app.py`)

1. Đảm bảo máy tính của bạn đã cài đặt **Python**.
2. Tải file `app.py` và đặt nó vào thư mục trống mà bạn muốn dùng làm kho lưu trữ Git cho thế giới Terraria.
3. Mở terminal/CMD tại thư mục đó và chạy lệnh:
```bash
python app.py

```



### Cách 2: Tự đóng gói thành file chạy nhanh (`.exe`)

Nếu bạn muốn tạo file chạy độc lập dạng `.exe` để bấm là chạy:

1. Cài đặt công cụ đóng gói PyInstaller:
```bash
pip install pyinstaller

```


2. Chạy lệnh đóng gói không hiện cửa sổ dòng lệnh:
```bash
pyinstaller --noconsole --onefile app.py

```


3. Lấy file `.exe` thành phẩm nằm trong thư mục **`dist/app.exe`** mang ra sử dụng bất cứ lúc nào bạn muốn.

---

## Hướng dẫn sử dụng chi tiết

1. **Khởi chạy ứng dụng** (mở `app.py` hoặc file `app.exe`).
2. **Thiết lập lần đầu:**
* Ngay khi mở app lên lần đầu tiên trong một thư mục trống, một bảng nhỏ sẽ hiện ra yêu cầu bạn nhập **URL Repository GitHub** (Ví dụ: `[https://github.com/ten-tai-khoan/terraria-worlds.git](https://github.com/ten-tai-khoan/terraria-worlds.git)`). App sẽ tự động khởi tạo kết nối.


3. **Chọn thế giới Terraria:**
* Bấm nút **Chọn file** để mở nhanh thư mục lưu trữ thế giới mặc định của game (thường nằm ở `Documents\My Games\Terraria\Worlds`).
* Chọn file `.wld` của thế giới bạn vừa chơi xong.


4. **Nhập ghi chú (Tùy chọn):**
* Nhập nội dung mô tả thay đổi ở ô *Nội dung Commit* (hoặc giữ nguyên mặc định).


5. **Đẩy lên GitHub:**
* Bấm nút lớn **Push lên GitHub**.
* Ứng dụng sẽ tự động thực hiện các bước: *Copy file vào thư mục $\rightarrow$ `git add` $\rightarrow$ `git commit` $\rightarrow$ `git push` lên GitHub*.



---

## Xử lý sự cố thường gặp

* **Lỗi xác thực Git (Authentication Failed):**
* Hãy đảm bảo máy tính của bạn đã đăng nhập tài khoản GitHub qua Git Credential Manager hoặc đã cấu hình SSH Key hợp lệ để không bị chặn quyền push code.


* **File không thay đổi:**
* Nếu app báo *"File thế giới này không có thay đổi gì mới"*, có nghĩa là bạn chưa lưu game hoặc file `.wld` chưa có thay đổi nào mới so với lần đồng bộ trước đó.
