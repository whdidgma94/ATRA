import multiprocessing
import sys

# 구형 TC 스크립트의 `import main` 호환성 유지를 위해 api.actions를 main으로 등록
import api.actions
sys.modules['main'] = api.actions

import config.common_variable  # noqa: F401  (side-effect: sets application_path)

from PyQt6.QtWidgets import QApplication
from ui.theme import DARK_THEME
from ui.app_window import AppWindow


def main():
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
