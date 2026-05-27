import os.path

import customtkinter as ctk
from customtkinter import filedialog
from tkinter import messagebox

class ExecutionModeSelector:
    def __init__(self):
        self.mode = None
        self.log_path = None

        self.root = ctk.CTk()
        self.root.title("ATRA - 실행 모드 선택")
        self.root.geometry("400x300")

        self.root.eval('tk::PlaceWindow . center')

        self._create_widgets()

    def _create_widgets(self):
        label = ctk.CTkLabel(
            self.root,
            text="ATRA 실행 모드를 선택해 주세요.",
            font=("Malgun Gothic", 18, "bold")
        )
        label.pack(pady=(30, 20))

        btn_run_test = ctk.CTkButton(
            self.root,
            text="자동화 테스트 실행",
            command=self.select_mode_1,
            height=45,
            font=("Malgun Gothic", 15)
        )
        btn_run_test.pack(pady=10, fill="x", padx=50)

        btn_regen_report = ctk.CTkButton(
            self.root,
            text="기존 로그로 리포트 생성",
            command=self.select_mode_2,
            height=45,
            fg_color="#5C6BC0",
            hover_color="#3F51B5",
            font=("Malgun Gothic", 15)
        )
        btn_regen_report.pack(pady=10, fill="x", padx=50)

        btn_maintenance_script = ctk.CTkButton(
            self.root,
            text="스크립트 유지보수 (미구현)",
            command=self.select_mode_3,
            height=45,
            fg_color="#5C6BC0",
            hover_color="#3F51B5",
            font=("Malgun Gothic", 15)
        )
        btn_maintenance_script.pack(pady=10, fill="x", padx=50)

    def select_mode_1(self):
        self.mode = 1
        self.root.destroy()

    def select_mode_2(self):
        selected_dir = filedialog.askdirectory(title="리포트를 생성할 기존 로그 폴더를 선택하세요")
        if os.path.exists(f"{selected_dir}/test_result.html"):
            if not messagebox.askokcancel("리포트 삭제 주의 알림", "기존 리포트가 삭제됩니다. 그대로 진행하시겠습니까?"):
                return
        if selected_dir:
            self.mode = 2
            self.log_path = selected_dir
            self.root.destroy()

    def select_mode_3(self):
        self.mode = 3
        self.root.destroy()

    def show_and_get_mode(self):
        self.root.mainloop()
        return self.mode, self.log_path
