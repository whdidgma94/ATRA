import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("System")

class PLMUpdaterApp(ctk.CTk):
    def __init__(self, input_data):
        super().__init__()

        # 1. 윈도우 설정
        self.title("ATRA Update PLM Info")
        self.geometry("1200x600")

        self.raw_data = input_data
        self.target_statuses = ["FAIL", "N/A", "Minor_Fail"]

        self.entry_map = []
        self.total_result = {
            "total":{"FAIL":0, "N/A":0},
            "SOS":{"FAIL":0, "N/A":0, "issue":[], "comment":[]},
            "TOS":{"FAIL":0, "N/A":0, "issue":[], "comment":[]},
            "UOS":{"FAIL":0, "N/A":0, "issue":[], "comment":[]},
            "VOS":{"FAIL":0, "N/A":0, "issue":[], "comment":[]},
            "BOS":{"FAIL":0, "N/A":0, "issue":[], "comment":[]},
            "COS":{"FAIL":0, "N/A":0, "issue":[], "comment":[]}
        }
        # 2. UI 구성
        self._setup_ui()
        self._load_items()

        # 3. 윈도우 닫기 이벤트 처리 (X 버튼 눌렀을 때)
        self.protocol("WM_DELETE_WINDOW", self.save_and_close)

    def _setup_ui(self):
        # 상단 타이틀
        self.lbl_title = ctk.CTkLabel(self, text="PLM 정보 입력", font=("Arial", 20, "bold"))
        self.lbl_title.pack(pady=10)

        # 스크롤 영역
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=850, height=450)
        self.scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # 저장 버튼
        self.btn_save = ctk.CTkButton(self, text="저장 및 닫기", command=self.save_and_close, height=40)
        self.btn_save.pack(pady=15)

    def _load_items(self):

        for category, items in self.raw_data.items():
            os_title = ctk.CTkLabel(self.scroll_frame, text=category, font=("Arial", 15, "bold"), fg_color="#3B8ED0", corner_radius=7, text_color="white")
            os_title.pack(fill="x", padx=10, pady=5)
            has_fail = False
            for item in items:
                # 필터 조건: Status 확인 및 is_reviewed가 False인 경우
                if item.get('status') in self.target_statuses and item.get('is_reviewed') is False:
                    self._create_row(category, item)
                    has_fail = True
            if not has_fail:
                info_text = f"문제점이 없습니다"
                no_fail = ctk.CTkLabel(self.scroll_frame, text=info_text, justify="center")
                no_fail.pack(padx=10, pady=10, expand=True, fill="x")

    def _create_row(self,  category, item_data):
        frame = ctk.CTkFrame(self.scroll_frame, fg_color="#CCCCCC")
        frame.pack(pady=5, padx=5, fill="x")

        status_colors = {
            "FAIL": "#FF4C4C",
            "Minor_Fail": "#FF8C00",
            "N/A": "#808080",
            "Error": "#FFA500"
        }
        color = status_colors.get(item_data['status'], "white")
        # 정보 텍스트
        info_text = f"{item_data['name']}\nStatus: {item_data['status']}\n{item_data['content']}"
        lbl_info = ctk.CTkLabel(frame, text=info_text, justify="left", anchor="w", text_color=color, font=("맑은 고딕", 13, "bold"))
        lbl_info.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        # 입력 필드 그룹
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(side="right", padx=10)

        # Num 입력
        lbl_plm_num = ctk.CTkLabel(input_frame, text="사례코드:", font=("맑은 고딕", 13))
        lbl_plm_num.grid(row=0, column=1, padx=5, sticky="e")
        entry_plm_num = ctk.CTkEntry(input_frame, width=300)
        entry_plm_num.grid(row=0, column=2, padx=5, pady=2)

        # Title 입력
        lbl_plm_title = ctk.CTkLabel(input_frame, text="제목:", font=("맑은 고딕", 13))
        lbl_plm_title.grid(row=1, column=1, padx=5, sticky="e")
        entry_plm_title = ctk.CTkEntry(input_frame, width=300)
        entry_plm_title.grid(row=1, column=2, padx=5, pady=2)

        if 'plm_title' in item_data: entry_plm_title.insert(0, item_data['plm_title'])
        if 'plm_num' in item_data: entry_plm_num.insert(0, item_data['plm_num'])

        append_result={
            "data_ref": item_data,
            "old_status": item_data['status'],
            "title_widget": entry_plm_title,
            "num_widget": entry_plm_num,
            "os_ver": category
        }
        if item_data['status'] == "FAIL":
            lbl_status = ctk.CTkOptionMenu(input_frame, values=["FAIL", "N/A"], width=130)
            lbl_status.set(item_data['status'])
            lbl_status.grid(row=0, column=0, padx=5, pady=2, sticky="e")
            append_result["status_widget"] =  lbl_status
        # 매핑 저장
        self.entry_map.append(append_result)

    def save_and_close(self):
        if not messagebox.askokcancel("PLM Info update 종료 알림", "Fail 항목 PLM 정보를 이대로 저장 하시겠습니까?"):
            return

        for entry in self.entry_map:

            p_title = entry["title_widget"].get()
            p_num = entry["num_widget"].get()

            try:
                old_status = entry["old_status"]
                new_status = entry["status_widget"].get()
                entry["data_ref"]["status"] = new_status
                self.total_result[entry["os_ver"]][old_status] -= 1
                self.total_result[entry["os_ver"]][new_status] += 1
                self.total_result["total"][old_status] -= 1
                self.total_result["total"][new_status] += 1


                if p_title or p_num:
                    if new_status == "FAIL":
                        entry["data_ref"]["plm_title"] = p_title.strip()
                        entry["data_ref"]["plm_num"] = p_num.strip()
                        self.total_result[entry["os_ver"]]["issue"].append(f" - [{p_num.strip()}] {p_title.strip()}")
                    elif new_status == "N/A":
                        entry["data_ref"]["plm_title"] = p_title.strip()
                        self.total_result[entry["os_ver"]]["comment"].append(f" - {p_title.strip()}")
            except KeyError:
                pass

        self.destroy()


    def get_data(self):
        return self.raw_data, self.total_result
