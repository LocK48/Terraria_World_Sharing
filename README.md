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

### Cách 1: Sử dụng file mã nguồn Python (`terraria_auto_update_wld.py`)

1. Đảm bảo máy tính của bạn đã cài đặt **Python**.
2. Tải file `terraria_auto_update_wld.py` và đặt nó vào thư mục trống mà bạn muốn dùng làm kho lưu trữ Git cho thế giới Terraria.
3. Mở terminal/CMD tại thư mục đó và chạy lệnh:
```bash
python terraria_auto_update_wld.py

```

### Cách 2: Tự đóng gói thành file chạy nhanh (`.exe`)

Nếu bạn muốn tạo file chạy độc lập dạng `.exe` để bấm là chạy:

1. Cài đặt công cụ đóng gói PyInstaller:
```bash
pip install pyinstaller

```

2. Chạy lệnh đóng gói không hiện cửa sổ dòng lệnh:
```bash
pyinstaller --noconsole --onefile terraria_auto_update_wld.py

```


3. Lấy file `.exe` thành phẩm nằm trong thư mục **`dist/terraria_auto_update_wld.exe`** mang ra sử dụng bất cứ lúc nào bạn muốn.

---

## Hướng dẫn sử dụng cho người chơi

1. **Khởi chạy ứng dụng:** Mở file ứng dụng (hoặc chạy file `.exe` nếu đã được đóng gói).
2. **Cấu hình lần đầu (Chỉ cần làm 1 lần duy nhất):**
* Ngay khi mở lên, app sẽ yêu cầu bạn nhập **URL Repository GitHub** (Ví dụ: `[https://github.com/ten-tai-khoan/terraria-worlds.git](https://github.com/ten-tai-khoan/terraria-worlds.git)`).
* Tiếp theo, app sẽ hỏi nhập **Personal Access Token (PAT)**. Bạn có thể dán mã Token của mình vào đây (hoặc bỏ trống nếu muốn dùng cơ chế đăng nhập trình duyệt sẵn có của Git).


3. **Chọn thế giới cần lưu:**
* Bấm nút **Chọn file** $\rightarrow$ App sẽ tự động trỏ thẳng vào thư mục chứa thế giới mặc định của game (`Documents\My Games\Terraria\Worlds`).
* Chọn file `.wld` của thế giới bạn vừa chơi xong.


4. **Nhập ghi chú và Đẩy lên:**
* Nhập nội dung mô tả vào ô *Nội dung Commit* (hoặc giữ nguyên mặc định).
* Bấm nút lớn **Push lên GitHub** màu xanh lá và chờ thông báo thành công!


---

## 🛠️ Hướng dẫn lấy Personal Access Token (PAT) trên GitHub

Nếu gặp lỗi xác thực khi push, bạn có thể tạo một Token riêng để app hoạt động mượt mà:

1. Đăng nhập vào [GitHub](https://github.com) -> Vào **Settings** (Cài đặt tài khoản) -> **Developer settings**.
2. Chọn **Personal access tokens** -> **Tokens (classic)** -> Bấm **Generate new token (classic)**.
3. Đặt tên gợi nhớ và **bắt buộc tích chọn ô `repo**` (Full control of private repositories).
4. Kéo xuống dưới cùng bấm **Generate token** và copy đoạn mã bắt đầu bằng `ghp_...` để dán vào ứng dụng khi được hỏi.


---

## Xử lý sự cố thường gặp

* **Lỗi xác thực Git (Authentication Failed):**
* Hãy đảm bảo máy tính của bạn đã đăng nhập tài khoản GitHub qua Git Credential Manager hoặc đã cấu hình SSH Key hợp lệ để không bị chặn quyền push code.


* **File không thay đổi:**
* Nếu terraria_auto_update_wld báo *"File thế giới này không có thay đổi gì mới"*, có nghĩa là bạn chưa lưu game hoặc file `.wld` chưa có thay đổi nào mới so với lần đồng bộ trước đó.


* **Lỗi 403 Forbidden / Xác thực thất bại:**
* Do Windows đang lưu cache tài khoản cũ trong *Credential Manager*. Hãy mở *Credential Manager* trên Windows $\rightarrow$ chọn *Windows Credentials* $\rightarrow$ tìm và xóa các dòng liên quan đến `git:[https://github.com](https://github.com)`, sau đó chạy lại app và nhập Token mới.


* **Lỗi không tìm thấy file `.wld`:**
* Hãy chắc chắn bạn đã thoát game hoặc game đã lưu (save) thế giới hoàn tất trước khi bấm chọn file.
