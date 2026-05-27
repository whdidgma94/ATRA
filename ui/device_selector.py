import customtkinter as tk
from tkinter import ttk, messagebox
import subprocess
import config.common_variable as cv

class ADBMonitorApp:
    def __init__(self, root):
        self.tree = None
        self.root = root
        self.root.title("ATRA Device Monitor")
        self.root.geometry("600x450")
        self.final_data = []
        self.device_cache = {}

        self.setup_ui()
        self.start_monitoring()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))

        title_label = tk.CTkLabel(self.root, text="기기 선택 및 확인", font=("맑은 고딕", 16, "bold"), pady=10)
        title_label.pack()

        columns = ("serial", "model", "version", "status")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        self.tree.heading("serial", text="Serial Number")
        self.tree.heading("model", text="Model Name")
        self.tree.heading("version", text="Android Ver")
        self.tree.heading("status", text="Status")

        self.tree.column("serial", width=150, anchor="center")
        self.tree.column("model", width=200, anchor="center")
        self.tree.column("version", width=100, anchor="center")
        self.tree.column("status", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # 버튼 영역
        btn_frame = tk.CTkFrame(self.root)
        btn_frame.pack(pady=10)

        check_btn = tk.CTkButton(btn_frame,
                              text="자동화 테스트 구동 시작",
                              command=self.on_check_button_click,
                              font=("맑은 고딕", 11, "bold"),
                              fg_color="#4a90e2")
        check_btn.pack()


    def on_check_button_click(self):
        collected_data = []
        for serial, info in self.device_cache.items():
            if info['status'] == 'device':
                collected_data.append((serial,info['version']))

        if not collected_data:
            messagebox.showwarning("경고", "연결된 기기가 없습니다.")
            return
        self.final_data = collected_data
        for serial, version in collected_data:
            version_key = version.split(".")[0]
            os_name = cv.os_version_dic.get(version_key, version_key)
            model = self. device_cache.get(serial, {}).get('model', 'Unknown')
            cv.device_model_map[os_name] = model
        self.root.destroy()

    @staticmethod
    def run_adb_command(command):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, startupinfo=startupinfo).decode('utf-8').strip()
            return output
        except (Exception,):
            return None

    def get_device_detail(self, serial):
        model = self.run_adb_command(f"adb -s {serial} shell getprop ro.product.model")
        version = self.run_adb_command(f"adb -s {serial} shell getprop ro.build.version.release")
        return {"model": model if model else "Unknown", "version": version if version else "?"}

    def refresh_device_list(self):
        try:
            if not self.root.winfo_exists():
                return
        except (Exception,):
            return

        raw_output = self.run_adb_command("adb devices")
        if raw_output:
            lines = raw_output.split('\n')[1:]
            current_serials = []
            for line in lines:
                if not line.strip(): continue
                parts = line.split()
                serial, status = parts[0], parts[1]
                current_serials.append(serial)

                if serial not in self.device_cache:
                    if status == 'device':
                        details = self.get_device_detail(serial)
                        self.device_cache[serial] = {"model": details['model'], "version": details['version'], "status": status}
                    else:
                        self.device_cache[serial] = {"model": "-", "version": "-", "status": status}
                else:
                    self.device_cache[serial]["status"] = status

            for s in [k for k in self.device_cache if k not in current_serials]:
                del self.device_cache[s]

            self.update_treeview()

        self.root.after(2000, self.refresh_device_list)

    def update_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        sorted_cache = sorted(
            self.device_cache.items(),
            key=lambda x: int(x[1]['version'].split(".")[0]) if x[1]['version'].split(".")[0].isdigit() else 99
        )
        for serial, info in sorted_cache:
            self.tree.insert("", "end", values=(serial, info['model'], info['version'], info['status']))

    def start_monitoring(self):
        self.refresh_device_list()



def get_connected_devices_gui():
    root = tk.CTk()
    app = ADBMonitorApp(root)
    root.mainloop()

    return app.final_data