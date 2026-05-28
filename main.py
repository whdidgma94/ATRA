import multiprocessing
import sys

# 구형 TC 스크립트의 `import main` 호환성 유지를 위해 api.actions를 main으로 등록
import api.actions
sys.modules['main'] = api.actions

import config.common_variable  # noqa: F401  (side-effect: sets application_path)
# PyQt6 임포트는 main() 안에서만 — Windows spawn 시 자식 프로세스가 main.py를
# 재임포트해도 Qt DLL이 불필요하게 로드되지 않도록 지연 임포트


def main():
    multiprocessing.freeze_support()

    from PyQt6.QtWidgets import QApplication
    from ui.theme import DARK_THEME
    from ui.app_window import AppWindow

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
