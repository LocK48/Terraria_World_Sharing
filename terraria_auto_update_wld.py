import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

def check_and_setup_git():
    """Kiểm tra và tự động cấu hình Git nếu chưa có, hỗ trợ nhúng Personal Access Token (PAT)"""
    if not os.path.exists(".git"):
        try:
            subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
            subprocess.run(["git", "branch", "-M", "master"], check=True, capture_output=True, text=True)
            
            # Tự động gán user/email ẩn danh
            subprocess.run(["git", "config", "user.name", "Terraria Player"], capture_output=True, text=True)
            subprocess.run(["git", "config", "user.email", "player@terraria.local"], capture_output=True, text=True)
            
            repo_url = simpledialog.askstring("Cấu hình Git lần đầu", "Không tìm thấy kho Git.\nHãy nhập URL Repository GitHub của bạn\n(Ví dụ: https://github.com/username/repo.git):")
            if not repo_url:
                messagebox.showwarning("Cảnh báo", "Bạn chưa nhập URL. App có thể không kết nối được Remote.")
                return

            # Hỏi nhập Personal Access Token (PAT) tùy chọn
            pat = simpledialog.askstring("Xác thực GitHub (Tùy chọn)", "Nếu bạn dùng Personal Access Token (PAT), hãy dán vào đây (Bỏ trống nếu dùng mặc định):", show='*')
            
            final_url = repo_url.strip()
            if pat and pat.strip():
                if final_url.startswith("https://"):
                    final_url = final_url.replace("https://", f"https://{pat.strip()}@", 1)

            subprocess.run(["git", "remote", "add", "origin", final_url], check=True, capture_output=True, text=True)
            messagebox.showinfo("Thành công", "Đã cấu hình Git và Remote thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi Git Init", f"Không thể khởi tạo Git:\n{str(e)}")

def push_to_github():
    if not os.path.exists(".git"):
        check_and_setup_git()
        if not os.path.exists(".git"):
            return

    world_path = entry_path.get().strip()
    commit_msg = entry_msg.get().strip()

    if not world_path or not os.path.exists(world_path):
        messagebox.showerror("Lỗi", "Vui lòng chọn file .wld hợp lệ!")
        return

    if not commit_msg:
        commit_msg = "Update Terraria world"

    try:
        # 1. Copy file vào thư mục hiện tại của app
        filename = os.path.basename(world_path)
        dest_path = os.path.join(os.getcwd(), filename)
        
        with open(world_path, 'rb') as f_src, open(dest_path, 'wb') as f_dst:
            f_dst.write(f_src.read())

        # 2. Thực hiện git add
        add_res = subprocess.run(["git", "add", filename], capture_output=True, text=True)
        if add_res.returncode != 0:
            messagebox.showerror("Lỗi Git Add", f"Không thể add file:\n{add_res.stderr}")
            return

        # 3. Kiểm tra xem có thay đổi thực sự không
        status_res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        if not status_res.stdout.strip():
            messagebox.showinfo("Thông báo", "File thế giới này không có thay đổi gì mới so với lần lưu trước nên không cần đẩy lên!")
            return

        # 4. Tiến hành Commit thay đổi
        commit_res = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True)
        if commit_res.returncode != 0:
            full_error = commit_res.stderr.strip() if commit_res.stderr.strip() else commit_res.stdout.strip()
            messagebox.showerror("Lỗi Git Commit", f"Lệnh commit thất bại:\n{full_error}")
            return
        
        # 5. Lấy tên nhánh hiện tại
        branch_res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        current_branch = branch_res.stdout.strip()
        if not current_branch:
            current_branch = "master"

        # 6. KIỂM TRA XEM TRÊN GITHUB ĐÃ CÓ NHÁNH NÀY CHƯA TRƯỚC KHI PULL
        check_remote = subprocess.run(["git", "ls-remote", "--heads", "origin", current_branch], capture_output=True, text=True)
        remote_branch_exists = bool(check_remote.stdout.strip())

        # Nếu trên remote đã có nhánh này, tiến hành pull --rebase để đồng bộ
        if remote_branch_exists:
            pull_res = subprocess.run(["git", "pull", "--rebase", "origin", current_branch], capture_output=True, text=True)
            
            # Xử lý nếu pull lỗi do xác thực (403 / Authentication)
            if pull_res.returncode != 0:
                full_pull_error = pull_res.stderr.strip() if pull_res.stderr.strip() else pull_res.stdout.strip()
                if any(err in full_pull_error.lower() for err in ["authentication", "permission", "403", "support for password"]):
                    if messagebox.askyesno("Lỗi Xác Thực", "Xác thực Git Pull thất bại.\nBạn có muốn cập nhật lại Personal Access Token (PAT) không?"):
                        new_pat = simpledialog.askstring("Nhập PAT mới", "Dán mã Token (ghp_...) của bạn:", show='*')
                        if new_pat and new_pat.strip():
                            rem_res = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
                            old_url = rem_res.stdout.strip()
                            clean_url = old_url
                            if "@" in clean_url and "https://" in clean_url:
                                parts = clean_url.split("https://")[1]
                                clean_url = "https://" + parts.split("@")[1]
                            new_url = clean_url.replace("https://", f"https://{new_pat.strip()}@", 1)
                            subprocess.run(["git", "remote", "set-url", "origin", new_url], capture_output=True, text=True)
                            subprocess.run(["git", "pull", "--rebase", "origin", current_branch], capture_output=True, text=True)

        # 7. Thực hiện Push lên GitHub (Lần đầu sẽ dùng -u để tạo nhánh, các lần sau tự động push)
        push_res = subprocess.run(["git", "push", "-u", "origin", current_branch], capture_output=True, text=True)
        
        if push_res.returncode != 0:
            full_push_error = push_res.stderr.strip() if push_res.stderr.strip() else push_res.stdout.strip()
            
            # Nếu push lỗi do 403 / xác thực lần đầu
            if any(err in full_push_error.lower() for err in ["authentication", "permission", "403", "support for password"]):
                if messagebox.askyesno("Lỗi Xác Thực GitHub", "Push thất bại do lỗi tài khoản hoặc Token.\nBạn có muốn nhập Personal Access Token (PAT) ngay bây giờ không?"):
                    new_pat = simpledialog.askstring("Nhập Personal Access Token", "Dán mã Token (ghp_...) của bạn:", show='*')
                    if new_pat and new_pat.strip():
                        rem_res = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
                        old_url = rem_res.stdout.strip()
                        clean_url = old_url
                        if "@" in clean_url and "https://" in clean_url:
                            parts = clean_url.split("https://")[1]
                            clean_url = "https://" + parts.split("@")[1]
                        new_url = clean_url.replace("https://", f"https://{new_pat.strip()}@", 1)
                        subprocess.run(["git", "remote", "set-url", "origin", new_url], capture_output=True, text=True)
                        
                        retry_res = subprocess.run(["git", "push", "-u", "origin", current_branch], capture_output=True, text=True)
                        if retry_res.returncode == 0:
                            messagebox.showinfo("Thành công", f"Đã cấu hình Token và đẩy file lên GitHub (nhánh {current_branch}) thành công!")
                            return
                        else:
                            full_push_error = retry_res.stderr.strip()

            messagebox.showerror("Lỗi Git Push", f"Không thể đẩy lên GitHub (nhánh '{current_branch}'):\n{full_push_error}")
            return

        messagebox.showinfo("Thành công", f"Đã đẩy file .wld lên GitHub (nhánh {current_branch}) thành công!")
    except Exception as e:
        messagebox.showerror("Lỗi hệ thống", f"Đã xảy ra lỗi:\n{str(e)}")

def browse_file():
    initial_dir = os.path.expanduser(r"~\Documents\My Games\Terraria\Worlds")
    if not os.path.exists(initial_dir):
        initial_dir = "/"
    
    file_selected = filedialog.askopenfilename(
        initialdir=initial_dir,
        title="Chọn file thế giới Terraria",
        filetypes=[("Terraria World files", "*.wld"), ("All files", "*.*")]
    )
    if file_selected:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_selected)

# Tạo giao diện cửa sổ
root = tk.Tk()
root.title("Terraria World GitHub Pusher")
root.geometry("450x230")
root.resizable(False, False)

root.after(100, check_and_setup_git)

tk.Label(root, text="Đường dẫn file .wld:").pack(anchor="w", padx=20, pady=(15, 0))
frame_file = tk.Frame(root)
frame_file.pack(fill="x", padx=20, pady=5)

entry_path = tk.Entry(frame_file, width=42)
entry_path.pack(side="left", padx=(0, 5))
btn_browse = tk.Button(frame_file, text="Chọn file", command=browse_file)
btn_browse.pack(side="left")

tk.Label(root, text="Nội dung Commit (Tùy chọn):").pack(anchor="w", padx=20, pady=(10, 0))
entry_msg = tk.Entry(root, width=54)
entry_msg.pack(padx=20, pady=5)
entry_msg.insert(0, "Cập nhật thế giới mới")

btn_push = tk.Button(root, text="Push lên GitHub", bg="#28a745", fg="white", font=("Arial", 10, "bold"), command=push_to_github)
btn_push.pack(pady=15, fill="x", padx=20)

root.mainloop()