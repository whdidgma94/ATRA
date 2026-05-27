import os
import customtkinter as tk
from tkinter import messagebox
import subprocess
from config.common_variable import os_version_dic

_UI_POLL_INTERVAL_MS = 500

COLORS = {
    'Pending': '#e0e0e0',
    'Running': '#ffff00',
    'Pass': '#90ee90',
    'Fail': '#ff6b6b',
    'Error': '#ffa500',
    'N/T': '#0000ff',
    'N/A': '#a9a9a9'
}


class MatrixDashboard:
    def __init__(self, root1, devices, scripts, manager_dict, process_list):
        self.root = root1
        self.root.title("ATRA")
        self.root.geometry(f"{200+(150*len(devices))}x600")
        self.manager_dict = manager_dict
        sorted_devices = sorted(devices, key=lambda x: int(x[1].split(".")[0]) if x[1].split(".")[0].isdigit() else 99)
        self.devices = [os_version_dic[d[1].split(".")[0]] for d in sorted_devices if d[1].split(".")[0] in os_version_dic]
        self.device_models = self._fetch_device_models(sorted_devices)
        self.scripts = scripts
        self.process_list = process_list
        self.cells = {}

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._setup_control_panel()
        self._setup_scroll_frame()
        self._create_widgets()
        self._start_update_loop()

    @staticmethod
    def _fetch_device_models(sorted_devices):
        device_models = {}
        for device in sorted_devices:
            udid = device[0]
            os_name = os_version_dic.get(device[1].split(".")[0], device[1])
            try:
                kwargs = {}
                if os.name == "nt":
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    kwargs["startupinfo"] = si
                model = subprocess.check_output(
                    f"adb -s {udid} shell getprop ro.product.model",
                    shell=True,
                    stderr=subprocess.STDOUT,
                    **kwargs
                ).decode('utf-8').strip()
            except (Exception,):
                model = "Unknown"
            device_models[os_name] = model
        return device_models

    def _setup_control_panel(self):
        frame = tk.CTkFrame(self.root)
        frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        btn_exit = tk.CTkButton(frame, text="테스트 종료", fg_color="red", text_color="white", command=self.on_close)
        btn_exit.pack(pady=5)

    def on_close(self):
        if not messagebox.askokcancel("테스트 종료 알림", "자동화 테스트를 종료하시겠습니까?"):
            return
        for process in self.process_list:
            if process.is_alive():
                process.terminate()
        self.root.destroy()

    def _setup_scroll_frame(self):
        main_frame = tk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.CTkCanvas(main_frame, bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.CTkScrollbar(main_frame, orientation=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_frame = tk.CTkFrame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        pass

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _create_widgets(self):
        self.table_frame = tk.CTkFrame(self.scroll_frame, fg_color="black", corner_radius=0, border_width=1, border_color="black")
        self.table_frame.pack(padx=20, pady=20, fill="both", expand=True)

        tk.CTkLabel(self.table_frame, text="Scripts \\ Devices", width=20, height=30, fg_color="lightgray", padx=10, pady=5).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        for col, dev_id in enumerate(self.devices, start=1):
            model = self.device_models.get(dev_id, "")
            header_text = f"{dev_id}\n{model}" if model else dev_id
            lbl = tk.CTkLabel(self.table_frame, text=header_text, fg_color="lightblue", text_color="black", height=45, padx=10, pady=5)
            lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        for row, script in enumerate(self.scripts, start=1):
            tk.CTkLabel(self.table_frame, text=script, anchor="w", fg_color="white", text_color="black", padx=10, pady=5).grid(row=row, column=0, sticky="nsew", padx=1, pady=1)

            for col, dev_id in enumerate(self.devices, start=1):
                cell = tk.CTkLabel(self.table_frame, text="Pending", fg_color=COLORS['Pending'], width=80, height=30, padx=10, pady=5)
                cell.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                self.cells[(dev_id, script)] = cell

    def _start_update_loop(self):
        self.update_ui()

    def update_ui(self):
        for dev_id in self.devices:
            if dev_id not in self.manager_dict:
                continue

            dev_status = self.manager_dict[dev_id]

            for script in self.scripts:
                status = dev_status.get(script, 'Pending')
                cell_widget = self.cells.get((dev_id, script))
                if cell_widget:
                    current_bg = cell_widget.cget("fg_color")
                    target_bg = COLORS.get(status, 'white')
                    if current_bg != target_bg:
                        cell_widget.configure(text=status, fg_color=target_bg)

        self.root.after(_UI_POLL_INTERVAL_MS, self.update_ui)
