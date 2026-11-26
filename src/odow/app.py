"""Desktop application entry point."""

import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Odow")
        self.resize(900, 620)
        tabs = QTabWidget()
        for title, detail in (
            ("Video", "YouTube and Bilibili downloads powered by yt-dlp"),
            ("Hugging Face", "Download model repository files"),
            ("GitHub", "Browse releases and download assets"),
            ("Tasks", "Review active and completed downloads"),
        ):
            page = QWidget()
            layout = QVBoxLayout(page)
            label = QLabel(detail)
            label.setWordWrap(True)
            layout.addWidget(label)
            layout.addStretch(1)
            tabs.addTab(page, title)
        self.setCentralWidget(tabs)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
