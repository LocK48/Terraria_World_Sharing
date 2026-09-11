import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "TerrariaWorldGitHubPusher")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def load_saved_paths():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        saved_world_path = config.get("world_path", "")
        saved_pull_directory = config.get("pull_directory", "")
        if saved_world_path:
            entry_path.insert(0, saved_world_path)
        if saved_pull_directory:
            entry_pull_directory.insert(0, saved_pull_directory)
        else:
            choose_pull_directory()
        update_repository_display()
    except (OSError, json.JSONDecodeError, AttributeError):
        choose_pull_directory()


def save_paths(world_path=None, pull_directory=None, repo_url=None):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        config = {}
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
        if world_path:
            config["world_path"] = world_path
        if pull_directory:
            config["pull_directory"] = pull_directory
        if repo_url:
            config["repo_url"] = repo_url
        with open(CONFIG_PATH, "w", encoding="utf-8") as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=2)
    except OSError as error:
        messagebox.showwarning("Cảnh báo", f"Không thể ghi nhớ đường dẫn:\n{error}")


def choose_pull_directory():
    pull_directory = filedialog.askdirectory(title="Chọn thư mục nhận file khi Pull")
    if pull_directory:
        entry_pull_directory.delete(0, tk.END)
        entry_pull_directory.insert(0, pull_directory)
        save_paths(pull_directory=pull_directory)
        check_and_setup_git(pull_directory)


def get_repo_directory():
    return entry_pull_directory.get().strip()


def get_remote_url(repo_directory=None):
    repo_directory = repo_directory or get_repo_directory()
    if not repo_directory or not os.path.isdir(repo_directory):
        return ""
    remote_res = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        cwd=repo_directory,
    )
    remote_url = remote_res.stdout.strip()
    if "@" in remote_url and "https://" in remote_url:
        remote_url = "https://" + remote_url.split("https://", 1)[1].split("@", 1)[1]
    return remote_url


def update_repository_display():
    entry_repo_url.delete(0, tk.END)
    entry_repo_url.insert(0, get_remote_url())


def change_repository():
    repo_directory = get_repo_directory()
    if not repo_directory:
        messagebox.showwarning("Thiếu thư mục", "Vui lòng chọn thư mục Pull trước.")
        return

    repo_url = simpledialog.askstring(
        "Đổi Repository",
        "Nhập URL Repository GitHub mới:",
        initialvalue=entry_repo_url.get().strip(),
    )
    if not repo_url or not repo_url.strip():
        return

    clean_url = repo_url.strip()
    pat = simpledialog.askstring(
        "Xác thực GitHub (Tùy chọn)",
        "Nếu repository cần PAT, hãy dán token vào đây (bỏ trống nếu đã lưu xác thực):",
        show="*",
    )
    remote_url = clean_url
    if pat and pat.strip() and remote_url.startswith("https://"):
        remote_url = remote_url.replace("https://", f"https://{pat.strip()}@", 1)

    try:
        remote_exists = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            cwd=repo_directory,
        ).returncode == 0
        command = ["git", "remote", "set-url", "origin", remote_url] if remote_exists else [
            "git", "remote", "add", "origin", remote_url
        ]
        remote_res = subprocess.run(command, capture_output=True, text=True, cwd=repo_directory)
        if remote_res.returncode != 0:
            error_text = remote_res.stderr.strip() or remote_res.stdout.strip()
            messagebox.showerror("Lỗi đổi Repository", f"Không thể cập nhật Repository:\n{error_text}")
            return

        entry_repo_url.delete(0, tk.END)
        entry_repo_url.insert(0, clean_url)
        messagebox.showinfo("Thành công", "Đã đổi Repository cho thư mục Pull hiện tại.")
    except OSError as error:
        messagebox.showerror("Lỗi đổi Repository", f"Không thể chạy Git:\n{error}")


def get_current_branch(repo_directory):
    branch_res = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        cwd=repo_directory,
    )
    return branch_res.stdout.strip() or "master"


def sync_latest_world_from_github():
    """Tải commit mới và cập nhật file thế giới đã ghi nhớ nếu remote có bản mới."""
    world_path = entry_path.get().strip()
    pull_directory = entry_pull_directory.get().strip()
    if not world_path or not pull_directory:
        messagebox.showwarning("Thiếu đường dẫn", "Vui lòng chọn file .wld và thư mục nhận file khi Pull.")
        return
    if not check_and_setup_git(pull_directory):
        return

    filename = os.path.basename(world_path)
    current_branch = get_current_branch(pull_directory)
    fetch_res = subprocess.run(
        ["git", "fetch", "origin", current_branch],
        capture_output=True,
        text=True,
        cwd=pull_directory,
    )
    if fetch_res.returncode != 0:
        return

    remote_ref = f"origin/{current_branch}"
    remote_head = subprocess.run(
        ["git", "rev-parse", remote_ref],
        capture_output=True,
        text=True,
        cwd=pull_directory,
    )
    if remote_head.returncode != 0:
        messagebox.showwarning(
            "Không tìm thấy nhánh",
            f"Repository không có nhánh '{current_branch}'.",
        )
        return

    remote_file = subprocess.run(
        ["git", "show", f"{remote_ref}:{filename}"],
        capture_output=True,
        cwd=pull_directory,
    )
    if remote_file.returncode != 0:
        messagebox.showwarning(
            "Không tìm thấy file thế giới",
            f"Repository không có file {filename} trên nhánh '{current_branch}'.",
        )
        return

    try:
        destination_path = os.path.join(pull_directory, filename)
        with open(destination_path, "wb") as destination_file:
            destination_file.write(remote_file.stdout)
        messagebox.showinfo("Đã cập nhật", f"Đã pull file {filename} vào:\n{pull_directory}")
    except OSError as error:
        messagebox.showerror("Lỗi cập nhật file", f"Không thể ghi file thế giới:\n{error}")

def check_and_setup_git(repo_directory=None):
    """Kiểm tra và tự động cấu hình Git nếu chưa có, hỗ trợ nhúng Personal Access Token (PAT)"""
    repo_directory = repo_directory or get_repo_directory()
    if not repo_directory:
        messagebox.showwarning("Thiếu thư mục", "Vui lòng chọn thư mục Pull trước.")
        return False

    try:
        os.makedirs(repo_directory, exist_ok=True)
    except OSError as error:
        messagebox.showerror("Lỗi thư mục", f"Không thể tạo thư mục repository:\n{error}")
        return False

    if not os.path.exists(os.path.join(repo_directory, ".git")):
        try:
            subprocess.run(["git", "init"], check=True, capture_output=True, text=True, cwd=repo_directory)
            subprocess.run(["git", "branch", "-M", "master"], check=True, capture_output=True, text=True, cwd=repo_directory)
            
            # Tự động gán user/email ẩn danh
            subprocess.run(["git", "config", "user.name", "Terraria Player"], capture_output=True, text=True, cwd=repo_directory)
            subprocess.run(["git", "config", "user.email", "player@terraria.local"], capture_output=True, text=True, cwd=repo_directory)
            
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

            subprocess.run(["git", "remote", "add", "origin", final_url], check=True, capture_output=True, text=True, cwd=repo_directory)
            entry_repo_url.delete(0, tk.END)
            entry_repo_url.insert(0, repo_url.strip())
            messagebox.showinfo("Thành công", "Đã cấu hình Git và Remote thành công!")
            return True
        except Exception as e:
            messagebox.showerror("Lỗi Git Init", f"Không thể khởi tạo Git:\n{str(e)}")
            return False

    update_repository_display()
    return bool(get_remote_url(repo_directory))

def push_to_github():
    world_path = entry_path.get().strip()
    repo_directory = get_repo_directory()
    commit_msg = entry_msg.get().strip()

    if not world_path or not os.path.exists(world_path) or not repo_directory:
        messagebox.showerror("Lỗi", "Vui lòng chọn file .wld hợp lệ và thư mục Pull.")
        return
    if not check_and_setup_git(repo_directory):
        return

    if not messagebox.askyesno(
        "Xác nhận Push",
        "Bạn sắp gửi file world trên máy lên GitHub.\n\n"
        "Đây là PUSH, không phải PULL. Bạn có muốn tiếp tục không?",
    ):
        return

    save_paths(world_path=world_path)

    if not commit_msg:
        commit_msg = "Update Terraria world"

    try:
        with open(world_path, "rb") as source_file:
            world_data = source_file.read()

        # 1. Đồng bộ nhánh local với remote trước khi tạo commit mới.
        current_branch = get_current_branch(repo_directory)
        fetch_res = subprocess.run(
            ["git", "fetch", "origin", current_branch],
            capture_output=True,
            text=True,
            cwd=repo_directory,
        )
        if fetch_res.returncode != 0:
            error_text = fetch_res.stderr.strip() or fetch_res.stdout.strip()
            messagebox.showerror("Lỗi Git Fetch", f"Không thể lấy thay đổi mới từ repository:\n{error_text}")
            return

        remote_ref = f"origin/{current_branch}"
        remote_branch_res = subprocess.run(
            ["git", "rev-parse", "--verify", remote_ref],
            capture_output=True,
            text=True,
            cwd=repo_directory,
        )
        if remote_branch_res.returncode == 0:
            reset_res = subprocess.run(
                ["git", "reset", "--hard", remote_ref],
                capture_output=True,
                text=True,
                cwd=repo_directory,
            )
            if reset_res.returncode != 0:
                error_text = reset_res.stderr.strip() or reset_res.stdout.strip()
                messagebox.showerror("Lỗi đồng bộ Git", f"Không thể đồng bộ với repository:\n{error_text}")
                return

        # 2. Copy file vào repository của thư mục Pull
        filename = os.path.basename(world_path)
        dest_path = os.path.join(repo_directory, filename)
        
        with open(dest_path, "wb") as destination_file:
            destination_file.write(world_data)

        # 3. Thực hiện git add
        add_res = subprocess.run(
            ["git", "add", filename],
            capture_output=True,
            text=True,
            cwd=repo_directory,
        )
        if add_res.returncode != 0:
            messagebox.showerror("Lỗi Git Add", f"Không thể add file:\n{add_res.stderr}")
            return

        # 4. Kiểm tra xem có thay đổi thực sự không
        status_res = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_directory,
        )
        if not status_res.stdout.strip():
            messagebox.showinfo("Thông báo", "File thế giới này không có thay đổi gì mới so với lần lưu trước nên không cần đẩy lên!")
            return

        # 5. Tiến hành Commit thay đổi
        commit_res = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            capture_output=True,
            text=True,
            cwd=repo_directory,
        )
        if commit_res.returncode != 0:
            full_error = commit_res.stderr.strip() if commit_res.stderr.strip() else commit_res.stdout.strip()
            messagebox.showerror("Lỗi Git Commit", f"Lệnh commit thất bại:\n{full_error}")
            return
        
        # 6. Thực hiện Push lên GitHub (Lần đầu sẽ dùng -u để tạo nhánh, các lần sau tự động push)
        push_res = subprocess.run(
            ["git", "push", "-u", "origin", current_branch],
            capture_output=True,
            text=True,
            cwd=repo_directory,
        )
        
        if push_res.returncode != 0:
            full_push_error = push_res.stderr.strip() if push_res.stderr.strip() else push_res.stdout.strip()
            
            # Nếu push lỗi do 403 / xác thực lần đầu
            if any(err in full_push_error.lower() for err in ["authentication", "permission", "403", "support for password"]):
                if messagebox.askyesno("Lỗi Xác Thực GitHub", "Push thất bại do lỗi tài khoản hoặc Token.\nBạn có muốn nhập Personal Access Token (PAT) ngay bây giờ không?"):
                    new_pat = simpledialog.askstring("Nhập Personal Access Token", "Dán mã Token (ghp_...) của bạn:", show='*')
                    if new_pat and new_pat.strip():
                        rem_res = subprocess.run(
                            ["git", "remote", "get-url", "origin"],
                            capture_output=True,
                            text=True,
                            cwd=repo_directory,
                        )
                        old_url = rem_res.stdout.strip()
                        clean_url = old_url
                        if "@" in clean_url and "https://" in clean_url:
                            parts = clean_url.split("https://")[1]
                            clean_url = "https://" + parts.split("@")[1]
                        new_url = clean_url.replace("https://", f"https://{new_pat.strip()}@", 1)
                        subprocess.run(
                            ["git", "remote", "set-url", "origin", new_url],
                            capture_output=True,
                            text=True,
                            cwd=repo_directory,
                        )
                        
                        retry_res = subprocess.run(
                            ["git", "push", "-u", "origin", current_branch],
                            capture_output=True,
                            text=True,
                            cwd=repo_directory,
                        )
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
        save_paths(world_path=file_selected)


def save_selected_pull_directory():
    pull_directory = entry_pull_directory.get().strip()
    if pull_directory:
        save_paths(pull_directory=pull_directory)


def initialize_selected_repository():
    pull_directory = get_repo_directory()
    if pull_directory:
        check_and_setup_git(pull_directory)

# Tạo giao diện cửa sổ
root = tk.Tk()
root.title("Terraria World GitHub Pusher")
root.geometry("450x390")
root.resizable(False, False)

tk.Label(root, text="Repository GitHub hiện tại:").pack(anchor="w", padx=20, pady=(15, 0))
frame_repo = tk.Frame(root)
frame_repo.pack(fill="x", padx=20, pady=5)

entry_repo_url = tk.Entry(frame_repo, width=42)
entry_repo_url.pack(side="left", padx=(0, 5))
btn_change_repo = tk.Button(frame_repo, text="Đổi repo", command=change_repository)
btn_change_repo.pack(side="left")

tk.Label(root, text="Đường dẫn file .wld:").pack(anchor="w", padx=20, pady=(10, 0))
frame_file = tk.Frame(root)
frame_file.pack(fill="x", padx=20, pady=5)

entry_path = tk.Entry(frame_file, width=42)
entry_path.pack(side="left", padx=(0, 5))
btn_browse = tk.Button(frame_file, text="Chọn file", command=browse_file)
btn_browse.pack(side="left")

tk.Label(root, text="Thư mục nhận file khi Pull:").pack(anchor="w", padx=20, pady=(10, 0))
frame_pull_directory = tk.Frame(root)
frame_pull_directory.pack(fill="x", padx=20, pady=5)

entry_pull_directory = tk.Entry(frame_pull_directory, width=42)
entry_pull_directory.pack(side="left", padx=(0, 5))
btn_browse_pull_directory = tk.Button(
    frame_pull_directory,
    text="Chọn thư mục",
    command=choose_pull_directory,
)
btn_browse_pull_directory.pack(side="left")

tk.Label(root, text="Nội dung Commit (Tùy chọn):").pack(anchor="w", padx=20, pady=(10, 0))
entry_msg = tk.Entry(root, width=54)
entry_msg.pack(padx=20, pady=5)
entry_msg.insert(0, "Cập nhật thế giới mới")

frame_actions = tk.Frame(root)
frame_actions.pack(fill="x", padx=20, pady=15)

btn_pull = tk.Button(frame_actions, text="Pull từ GitHub", bg="#1976d2", fg="white", font=("Arial", 10, "bold"), command=sync_latest_world_from_github)
btn_pull.pack(side="left", fill="x", expand=True, padx=(0, 5))

btn_push = tk.Button(frame_actions, text="Push lên GitHub", bg="#28a745", fg="white", font=("Arial", 10, "bold"), command=push_to_github)
btn_push.pack(side="left", fill="x", expand=True, padx=(5, 0))

root.after(100, load_saved_paths)
root.after(300, initialize_selected_repository)

root.mainloop()