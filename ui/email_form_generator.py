# ui.py
import customtkinter as ctk

from tkinter import messagebox

from email_feature.template_generator import generate_html, generate_title


class EmailTemplateApp(ctk.CTk):
    def __init__(self, table_form):
        super().__init__()
        self.table_form = table_form
        self.title("이메일 템플릿 생성기")
        self.geometry("500x600")
        ctk.set_appearance_mode("System")

        # 1. 발신 정보 (이름 + 직급 드롭다운)
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(pady=(30, 10), padx=20)

        self.name_entry = ctk.CTkEntry(self.info_frame, width=140, placeholder_text="이름 입력")
        self.name_entry.insert(0,"김혜숙")
        self.name_entry.pack(side="left", padx=(0, 10))

        self.rank_var = ctk.StringVar(value="선임")
        self.rank_dropdown = ctk.CTkOptionMenu(
            self.info_frame,
            width=90,
            values=["연구원", "주임","선임", "책임", "수석"],
            variable=self.rank_var
        )
        self.rank_dropdown.pack(side="left")

        # 2. 테스트명 입력
        self.release_entry = ctk.CTkEntry(self, width=420, placeholder_text="release 버전 입력 *예시:2026 R1")
        self.release_entry.pack(pady=5)

        # 2. 테스트명 입력
        self.application_entry = ctk.CTkEntry(self, width=420, placeholder_text="SmartThings 버전 입력 *예시:1.8.45.17 RC1")
        self.application_entry.pack(pady=5)

        # 4. 생성 및 클립보드 복사 버튼
        self.generate_title_btn = ctk.CTkButton(
            self,
            text="Email Title 생성 및 복사",
            width=240,
            height=45,
            font=("Default", 15, "bold"),
            command=self.on_generate_title_and_copy
        )
        self.generate_title_btn.pack(pady=(30, 5))

        self.generate_btn = ctk.CTkButton(
            self,
            text="HTML 생성 및 복사",
            width=240,
            height=45,
            font=("Default", 15, "bold"),
            command=self.on_generate_and_copy
        )
        self.generate_btn.pack(pady=(30, 5))

        # 5. 상태 알림 라벨
        self.status_label = ctk.CTkLabel(self, text="", text_color="#28a745", font=("Default", 12))
        self.status_label.pack()




    def on_generate_and_copy(self):
        name = self.name_entry.get()
        rank = self.rank_var.get()
        release = self.release_entry.get()
        application = self.application_entry.get()
        table_form = self.table_form
        if name == "":
            messagebox.showerror("입력 오류", "이름을 입력해 주세요")
            return
        elif rank == "직급":
            messagebox.showerror("입력 오류", "직급을 선택해 주세요")
            return
        elif release == "":
            messagebox.showerror("입력 오류", "Release 버전을 입력해 주세요")
            return
        elif application == "":
            messagebox.showerror("입력 오류", "SmartThings 버전을 입력해 주세요")
            return

        # HTML 생성 로직 호출
        html_result = generate_html(name, rank, release, application, table_form)

        # 클립보드 초기화 및 복사
        self.clipboard_clear()
        self.clipboard_append(html_result)
        self.update()

        # 복사 완료 알림
        self.show_status_message("✅ 메일 본문 HTML이 클립보드에 복사되었습니다!")

    def on_generate_title_and_copy(self):
        release = self.release_entry.get()
        application = self.application_entry.get()
        if release == "":
            messagebox.showerror("입력 오류", "Release 버전을 입력해 주세요")
            return
        elif application == "":
            messagebox.showerror("입력 오류", "SmartThings 버전을 입력해 주세요")
            return

        # HTML 생성 로직 호출
        html_result = generate_title(release, application)

        # 클립보드 초기화 및 복사
        self.clipboard_clear()
        self.clipboard_append(html_result)
        self.update()

        # 복사 완료 알림
        self.show_status_message("✅ 메일 제목이 클립보드에 복사되었습니다!")

    def show_status_message(self, message):
        self.status_label.configure(text=message)
        self.after(2000, lambda: self.status_label.configure(text=""))
