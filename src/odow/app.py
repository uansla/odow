"""Desktop application entry point."""

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTranslator, QLibraryInfo
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton, QTabWidget,
    QVBoxLayout, QWidget,
)

from odow.downloader import QUALITY_FORMATS, VideoDownloadWorker, is_supported_video_url


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Odow 视频下载器")
        self.resize(760, 500)
        self.worker = None
        tabs = QTabWidget()
        tabs.addTab(self._video_page(), "视频下载")
        for title in ("Hugging Face", "GitHub", "下载任务"):
            placeholder = QLabel("暂未开放")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tabs.addTab(placeholder, title)
        self.setCentralWidget(tabs)

    def _video_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()
        self.url = QLineEdit()
        self.url.setPlaceholderText("粘贴 YouTube 或哔哩哔哩视频链接")
        form.addRow("视频链接", self.url)
        self.quality = QComboBox()
        for label, key in zip(
            ("最佳画质", "最高 1080p", "最高 720p", "最高 480p", "仅音频（MP3）"),
            QUALITY_FORMATS,
        ):
            self.quality.addItem(label, key)
        form.addRow("下载画质", self.quality)
        self.destination = QLineEdit(str(Path.home() / "Videos" / "Odow"))
        choose_dir = QPushButton("浏览…")
        choose_dir.clicked.connect(self._choose_dir)
        dir_row = QHBoxLayout()
        dir_row.addWidget(self.destination, 1)
        dir_row.addWidget(choose_dir)
        form.addRow("保存位置", dir_row)
        self.cookies = QLineEdit()
        self.cookies.setPlaceholderText("可选：Netscape 格式的 cookies.txt 文件")
        choose_cookie = QPushButton("浏览…")
        choose_cookie.clicked.connect(self._choose_cookie)
        cookie_row = QHBoxLayout()
        cookie_row.addWidget(self.cookies, 1)
        cookie_row.addWidget(choose_cookie)
        form.addRow("登录凭据", cookie_row)
        layout.addLayout(form)
        buttons = QHBoxLayout()
        self.start = QPushButton("开始下载")
        self.cancel = QPushButton("取消下载")
        self.cancel.setEnabled(False)
        self.start.clicked.connect(self._start)
        self.cancel.clicked.connect(self._cancel)
        buttons.addWidget(self.start)
        buttons.addWidget(self.cancel)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.status = QLabel("就绪")
        self.status.setWordWrap(True)
        self.status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.status)
        layout.addStretch(1)
        return page

    def _choose_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "选择保存文件夹", self.destination.text())
        if folder:
            self.destination.setText(folder)

    def _choose_cookie(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "选择登录凭据文件", "", "文本文件 (*.txt);;所有文件 (*)")
        if path:
            self.cookies.setText(path)

    def _start(self) -> None:
        url = self.url.text().strip()
        folder = self.destination.text().strip()
        cookie = self.cookies.text().strip()
        if not is_supported_video_url(url) or not folder:
            QMessageBox.warning(self, "请检查输入", "请输入 YouTube 或哔哩哔哩视频链接，并选择保存位置。")
            return
        if cookie and not Path(cookie).is_file():
            QMessageBox.warning(self, "凭据文件不存在", "请选择有效的 cookies.txt 文件，或清空此项。")
            return
        self.worker = VideoDownloadWorker(url, folder, self.quality.currentData(), cookie)
        self.worker.progress.connect(self._progress)
        self.worker.completed.connect(lambda path: self.status.setText(f"下载完成：{path}"))
        self.worker.failed.connect(self._failed)
        self.worker.cancelled.connect(lambda: self.status.setText("已取消下载"))
        self.worker.finished.connect(self._finished)
        self.start.setEnabled(False)
        self.cancel.setEnabled(True)
        self.progress.setValue(0)
        self.status.setText("正在解析视频…")
        self.worker.start()

    def _progress(self, percent: int, speed: str) -> None:
        self.progress.setValue(percent)
        self.status.setText(speed)

    def _failed(self, error: str) -> None:
        self.status.setText("下载失败")
        QMessageBox.critical(self, "下载失败", "下载未能完成，请检查网络、视频链接或登录凭据。\n\n原始错误信息：\n" + error)

    def _cancel(self) -> None:
        if self.worker:
            self.worker.cancel()
            self.status.setText("正在取消…")
            self.cancel.setEnabled(False)

    def _finished(self) -> None:
        self.start.setEnabled(True)
        self.cancel.setEnabled(False)
        self.worker = None


def main() -> int:
    app = QApplication(sys.argv)
    translator = QTranslator(app)
    if translator.load("qtbase_zh_CN", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(translator)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
