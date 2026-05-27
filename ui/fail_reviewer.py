import base64
import io
import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image
import copy
from tkinter import messagebox

import config.common_variable as cv

ctk.set_appearance_mode("System")

_STATUS_COLORS = {
    "FAIL": "#FF4C4C",
    "Minor_Fail": "#FF8C00",
    "N/A": "#808080",
    "Error": "#FFA500"
}



class MultiCategoryFailViewer:
    def __init__(self, root_data, full_result, tc_data):
        self.btn_copy = None
        self.media_button_frame = None
        self.title_label = None
        self.title_frame = None
        self.btn_screenshot = None
        self.btn_close = None
        self.display_labels = None
        self.info_frame = None
        self.chk_confirm = None
        self.check_frame = None
        self.btn_next = None
        self.lbl_counter = None
        self.btn_prev = None
        self.nav_frame = None
        self.combo_category = None
        self.top_frame = None
        self.root = root_data
        self.root.title("ATRA Test Failures Viewer")
        self.root.geometry("750x900")  # 레이아웃 확보를 위해 크기 조정
        # 데이터 설정
        self.tc_data = tc_data
        self.full_result = full_result
        self.screenshot_data = None
        self.failed_data = {}
        self.check_vars = {}
        # 데이터 전처리
        for category, value in full_result.items():
            fails = [item for item in value if item.get('status') in ['FAIL', 'Minor_Fail', 'N/A', 'Error']]
            if fails:
                self.failed_data[category] = fails
                self.check_vars[category] = [tk.BooleanVar(value=False) for _ in fails]

        self.categories = list(self.failed_data.keys())

        if not self.categories:
            print("FAIL 항목이 없습니다.")
            self.root.destroy()
            return

        self.current_category = self.categories[0]
        self.current_index = 0

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # --- Top Frame (Category Selection) ---
        self.top_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.top_frame.pack(side="top", fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.top_frame, text="Select OS:", font=("Arial", 13, "bold")).pack(side="left", padx=15, pady=10)

        self.combo_category = ctk.CTkOptionMenu(
            self.top_frame,
            values=self.categories,
            command=self.on_category_change,
            fg_color="#F0F0F0",
            text_color="black"
        )
        self.combo_category.pack(side="left", padx=10, pady=10)
        self.combo_category.set(self.current_category)

        # --- Navigation Frame ---
        self.nav_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.nav_frame.pack(side="top", fill="x", padx=20, pady=5)

        self.btn_prev = ctk.CTkButton(self.nav_frame, text="< Prev", command=self.prev_item, width=100)
        self.btn_prev.pack(side="left", padx=10)

        self.lbl_counter = ctk.CTkLabel(self.nav_frame, text="0 / 0", font=("Arial", 17, "bold"))
        self.lbl_counter.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.nav_frame, text="Next >", command=self.next_item, width=100)
        self.btn_next.pack(side="right", padx=10)

        # --- Checkbox Frame ---
        self.check_frame = ctk.CTkFrame(self.root, corner_radius=10, cursor="hand2")
        self.check_frame.pack(side="top", fill="x", padx=20, pady=10)

        self.chk_confirm = ctk.CTkCheckBox(self.check_frame, text="수동 테스트 결과 Pass 시 체크", font=("Arial", 15, "bold"))
        self.chk_confirm.pack(pady=10)
        self.check_frame.bind("<Button-1>", self.toggle_check_from_frame)


        self.title_frame = ctk.CTkFrame(self.root, fg_color="#F0F0F0")
        self.title_frame.pack(side="top", fill="x", padx=20, pady=(10, 0))
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="Test Case Details",
            font=("Arial", 15, "bold")
        )

        self.title_label.pack(pady=10)
        # --- Info Frame (Scrollable Frame 추천) ---
        self.info_frame = ctk.CTkScrollableFrame(self.root, fg_color="#F0F0F0")
        self.info_frame.pack(side="top", fill="both", expand=True, padx=20, pady=10)
        # noinspection PyProtectedMember
        self.info_frame._scrollbar.grid_forget()

        self.display_labels = {}
        keys = [
            ("TC ID", "name"),
            ("Result", "status"),
            ("Actual Result", "content"),
            ("Middle Category", "middle_category"),
            ("Small Category", "small_category"),
            ("Detail Function", "detail_function"),
            ("Test Objective", "test_objectives"),
            ("Test Procedure", "test_procedure"),
            ("Input Specification", "input_specification"),
            ("Pre-condition", "pre_condition"),
            ("Expected Result", "expected_result")
        ]

        for idx, (label_text, key) in enumerate(keys):
            ctk.CTkLabel(self.info_frame, text=label_text, font=("Arial", 12, "bold"), anchor="nw", width=120).grid(row=idx, column=0, sticky="nw", pady=8, padx=5)

            if key == "content":
                txt = ctk.CTkTextbox(self.info_frame, width=450, height=30, wrap="word", fg_color="transparent")
                txt.grid(row=idx, column=1, sticky="nw")
                txt.configure(state="disabled")
                self.display_labels[key] = txt
                self.btn_copy = ctk.CTkButton(self.info_frame, text="📄 복사", command=self.copy_content_to_clipboard, width=80)
                self.btn_copy.grid(row=idx, column=2, sticky="ne")
            else:
                lbl = ctk.CTkLabel(self.info_frame, width=450, text="", anchor="nw", justify="left", wraplength=450)
                lbl.grid(row=idx, column=1, sticky="nw", pady=8, padx=8)
                self.display_labels[key] = lbl

        # --- Bottom Buttons ---
        self.btn_close = ctk.CTkButton(self.root, text="💾 저장 및 닫기", command=self.on_close, fg_color="gray", hover_color="#555555", height=40)
        self.btn_close.pack(side="bottom", pady=5, fill="x", padx=20)

        self.media_button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.media_button_frame.pack(side="bottom", fill="x", padx=20, pady=(5, 0))

        self.btn_screenshot = ctk.CTkButton(self.media_button_frame, text="📷 스크린샷 확인", command=self.open_screenshot_popup, fg_color="#1E90FF", hover_color="#1873CC", height=40)
        self.btn_screenshot.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.btn_screenshot = ctk.CTkButton(self.media_button_frame, text="📹 영상 확인", command=self.open_video, fg_color="#1E90FF", hover_color="#1873CC", height=40)
        self.btn_screenshot.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def toggle_check_from_frame(self, event=None):
        current_var = self.check_vars[self.current_category][self.current_index]
        current_var.set(not current_var.get())

    def open_video(self):
        current_list = self.failed_data[self.current_category]
        current_item = current_list[self.current_index]
        tc_id = current_item['name']

        video_base_folder = f"{cv.base_log_path}/{self.current_category}/{tc_id}"
        video_base_folder = video_base_folder.replace("/","\\")
        video_filename = f"recording.mp4"
        video_path = os.path.join(video_base_folder, video_filename)

        if not video_path or not os.path.exists(video_path):
            messagebox.showerror("파일 없음", f"영상 파일을 찾을 수 없습니다.\n경로: {video_path}")
            return

        try:
            os.startfile(video_path)
        except Exception as e:
            messagebox.showerror("에러", f"영상을 여는 중 오류가 발생했습니다:\n{e}")

    def open_screenshot_popup(self):
        if not self.screenshot_data:
            return

        popup = ctk.CTkToplevel(self.root)
        popup.title("문제점 스크린샷")
        popup.attributes("-topmost", True)  # 팝업이 뒤로 숨지 않게 설정

        img_data = base64.b64decode(self.screenshot_data)
        img_buffer = io.BytesIO(img_data)
        img = Image.open(img_buffer)

        # CTkImage를 사용하여 고해상도 대응
        max_size = (800, 800)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))

        screenshot_label = ctk.CTkLabel(popup, image=ctk_img, text="")
        screenshot_label.pack(padx=20, pady=20)

    def load_data(self):
        current_list = self.failed_data[self.current_category]
        if not current_list: return

        current_item = current_list[self.current_index]
        self.screenshot_data = current_item.get('screenshot_file')
        tc_id = current_item['name']
        status = current_item['status']
        tc_info = self.tc_data.get(tc_id, {})

        self.lbl_counter.configure(text=f"{self.current_index + 1} / {len(current_list)}")
        self.chk_confirm.configure(variable=self.check_vars[self.current_category][self.current_index])

        # 정보 업데이트
        self.display_labels['name'].configure(text=tc_id)

        # 상태별 색상 적용
        color = _STATUS_COLORS.get(status, "white")

        self.display_labels['status'].configure(text=status, text_color=color)
        content_widget = self.display_labels['content']
        content_text = current_item.get('content', '')
        content_widget.configure(state='normal')
        content_widget.delete("0.0", "end")
        content_widget.insert("0.0", content_text)
        self.root.update_idletasks()

        try:
            display_lines = content_widget._textbox.count("1.0", "end", "displaylines")

            if display_lines:
                num_lines = display_lines[0]
            else:
                num_lines = 1

            line_height = 20
            padding = 10
            new_height = (num_lines * line_height) + padding

            content_widget.configure(height = new_height)
        except (Exception,):
            content_widget.configure(height=100)
        content_widget.configure(state="disabled", text_color=color)
        # self.display_labels['content'].configure(text=current_item.get('content', ''), text_color=color)

        keys_to_update = ['middle_category', 'small_category', 'detail_function', 'test_objectives', 'input_specification', 'pre_condition', 'test_procedure', 'expected_result']
        for key in keys_to_update:
            self.display_labels[key].configure(text=tc_info.get(key, "N/A"))

        # 버튼 상태
        self.btn_prev.configure(state="normal" if self.current_index > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_index < len(current_list) - 1 else "disabled")

    def on_category_change(self, choice):
        if choice != self.current_category:
            self.current_category = choice
            self.current_index = 0
            self.load_data()

    def next_item(self):
        if self.current_index < len(self.failed_data[self.current_category]) - 1:
            self.current_index += 1
            self.load_data()

    def prev_item(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_data()

    def on_close(self):
        if not messagebox.askokcancel("Fail reviewer 종료 알림", "테스트 결과를 이대로 저장 하시겠습니까?"):
            return

        self.root.destroy()

    def get_reviewed_results(self, results=None):
        final_output = copy.deepcopy(self.full_result)
        removed_contents_map = {}

        for category, items in final_output.items():
            if category in self.check_vars:
                fail_tracker_index = 0
                filtered_items = []
                removed_contents_map[category] = []

                for item in items:
                    status = item.get('status')
                    if status in ['FAIL', 'Minor_Fail', 'N/A', 'Error']:
                        is_reviewed = self.check_vars[category][fail_tracker_index].get()
                        item['is_reviewed'] = is_reviewed
                        fail_tracker_index += 1

                    if status == 'Minor_Fail' and item.get('is_reviewed') is True:
                        removed_contents_map[category].append(item.get('content'))
                        continue
                    filtered_items.append(item)
                final_output[category] = filtered_items

        if results:
            for category, removed_contents in removed_contents_map.items():
                if category in results and 'test_cases' in results[category]:
                    original_cases = results[category]['test_cases']
                    new_cases = [c for c in original_cases if c.get('error_msg') not in removed_contents]
                    results[category]['test_cases'] = new_cases
                    results[category]['minor_fail'] -= (len(original_cases) - len(new_cases))

        return final_output, results

    def copy_content_to_clipboard(self):
        current_list = self.failed_data.get(self.current_category)
        if not current_list:
            return

        current_item = current_list[self.current_index]
        content_text = current_item.get('content', "")

        if content_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(content_text)
            self.root.update()
            self.btn_copy.configure(text="✅ 복사 완료")
            self.root.after(2000, self.restore_copy_button)

    def restore_copy_button(self):
        try:
            if self.btn_copy.winfo_exists():
                self.btn_copy.configure(text = "📄 복사")
        except(Exception,):
            pass