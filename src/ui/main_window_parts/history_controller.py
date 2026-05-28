import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.resources import asset_path


class MainWindowHistoryMixin:
    def load_history(self):
        self.sessions = self.storage.load_sessions()
        self.render_sessions(self.filtered_sessions())

    def filter_sessions(self):
        self.render_sessions(self.filtered_sessions())

    def filtered_sessions(self):
        query = self.session_search_input.text().strip().lower() if hasattr(self, "session_search_input") else ""
        if not query:
            return self.sessions
        return [session for session in self.sessions if self.session_matches_query(session, query)]

    def session_matches_query(self, session, query):
        values = (
            session.title,
            session.transcript,
            session.created_at.strftime("%d/%m/%Y %H:%M"),
            session.language,
        )
        return any(query in str(value or "").lower() for value in values)

    def render_sessions(self, sessions):
        selected_id = self.selected_session_id()
        self.recent_list.clear()
        has_sessions = bool(sessions)
        has_search = bool(self.session_search_input.text().strip()) if hasattr(self, "session_search_input") else False
        self.recent_empty_label.setText(self.tr("no_search_results") if has_search and not has_sessions else self.tr("empty_sessions"))
        self.recent_empty_label.setVisible(not has_sessions)
        self.recent_list.setVisible(has_sessions)
        for session in sessions:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, session.id)
            row = self.session_row(session)
            item.setSizeHint(row.minimumSizeHint())
            self.recent_list.addItem(item)
            self.recent_list.setItemWidget(item, row)
            if session.id == selected_id:
                self.recent_list.setCurrentItem(item)
        self.update_session_selection_styles()

    def selected_session_id(self):
        item = self.recent_list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def session_row(self, session):
        row = QWidget()
        row.setObjectName("sessionRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(4)
        duration = self.format_duration(session.duration_seconds)
        date_text = session.created_at.strftime("%d/%m/%Y %H:%M")
        content = QWidget()
        content.setObjectName("sessionContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        label = QPushButton(session.title)
        label.setObjectName("sessionButton")
        label.setCursor(Qt.PointingHandCursor)
        label.clicked.connect(lambda: self.select_session(session.id))
        meta = QWidget()
        meta.setObjectName("sessionMeta")
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(5, 0, 0, 0)
        meta_layout.setSpacing(5)
        calendar_icon = QLabel()
        calendar_icon.setPixmap(QIcon(str(asset_path("calendar.svg"))).pixmap(12, 12))
        date_label = QLabel(date_text)
        date_label.setObjectName("sessionMetaText")
        clock_icon = QLabel()
        clock_icon.setPixmap(QIcon(str(asset_path("clock.svg"))).pixmap(12, 12))
        duration_label = QLabel(duration)
        duration_label.setObjectName("sessionMetaText")
        meta_layout.addWidget(calendar_icon, 0, Qt.AlignVCenter)
        meta_layout.addWidget(date_label, 0, Qt.AlignVCenter)
        meta_layout.addSpacing(8)
        meta_layout.addWidget(clock_icon, 0, Qt.AlignVCenter)
        meta_layout.addWidget(duration_label, 0, Qt.AlignVCenter)
        meta_layout.addStretch()
        content_layout.addWidget(label)
        content_layout.addWidget(meta)
        play_button = self.svg_icon_button("play.svg", self.tr("listen"))
        rename_button = self.svg_icon_button("edit.svg", self.tr("rename"))
        delete_button = self.svg_icon_button("trash.svg", self.tr("delete"))
        play_button.setProperty("role", "action")
        rename_button.setProperty("role", "action")
        delete_button.setProperty("role", "delete")
        play_button.setProperty("normalIcon", "play.svg")
        play_button.setProperty("hoverIcon", "play-hover.svg")
        rename_button.setProperty("normalIcon", "edit.svg")
        rename_button.setProperty("hoverIcon", "edit-hover.svg")
        delete_button.setProperty("normalIcon", "trash.svg")
        delete_button.setProperty("hoverIcon", "trash-hover.svg")
        play_button.clicked.connect(lambda: self.play_session(session.id))
        rename_button.clicked.connect(lambda: self.rename_session(session.id))
        delete_button.clicked.connect(lambda: self.delete_session(session.id))
        row.mousePressEvent = lambda event: self.select_session(session.id)
        layout.addWidget(content, 1, Qt.AlignVCenter)
        layout.addWidget(play_button, 0, Qt.AlignVCenter)
        layout.addWidget(rename_button, 0, Qt.AlignVCenter)
        layout.addWidget(delete_button, 0, Qt.AlignVCenter)
        row.setMinimumHeight(54)
        return row

    def format_duration(self, seconds):
        seconds = int(seconds)
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def select_session(self, session_id):
        for index in range(self.recent_list.count()):
            item = self.recent_list.item(index)
            if item.data(Qt.UserRole) == session_id:
                self.recent_list.setCurrentItem(item)
                self.show_selected_session()
                self.history_tabs.setCurrentIndex(1)
                self.update_session_selection_styles()
                return

    def selected_session(self):
        item = self.recent_list.currentItem()
        if not item:
            return None
        session_id = item.data(Qt.UserRole)
        return next((session for session in self.sessions if session.id == session_id), None)

    def show_selected_session(self):
        session = self.selected_session()
        has_transcript = bool(session and session.transcript)
        self.transcript_preview.setPlainText(session.transcript if session else "")
        self.copy_button.setEnabled(has_transcript)
        self.export_button.setEnabled(has_transcript)
        self.update_session_selection_styles()

    def update_session_selection_styles(self):
        current = self.recent_list.currentItem()
        for index in range(self.recent_list.count()):
            item = self.recent_list.item(index)
            row = self.recent_list.itemWidget(item)
            selected = item is current
            if row:
                row.setProperty("selected", selected)
                row.style().unpolish(row)
                row.style().polish(row)

    def copy_transcript(self):
        session = self.selected_session()
        if session:
            QApplication.clipboard().setText(session.transcript)

    def export_transcript(self):
        session = self.selected_session()
        if not session or not session.transcript:
            return
        default_path = self.storage.text_dir / f"{self.safe_export_filename(session.title)}.txt"
        selected, _ = QFileDialog.getSaveFileName(self, self.tr("export_transcript"), str(default_path), self.tr("txt_files"))
        if not selected:
            return
        path = Path(selected)
        if path.suffix.lower() != ".txt":
            path = path.with_suffix(".txt")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(session.transcript, encoding="utf-8")
        except OSError as exc:
            QMessageBox.warning(self, self.tr("error"), f"{self.tr('export_error')}\n{exc}")

    def safe_export_filename(self, value):
        keep = []
        for char in value.strip():
            keep.append(char if char.isalnum() or char in (" ", "-", "_") else "_")
        filename = "".join(keep).strip().replace(" ", "_")
        return filename or "transcript"

    def rename_session(self, session_id):
        session = next((item for item in self.sessions if item.id == session_id), None)
        if not session:
            return
        title, ok = QInputDialog.getText(self, self.tr("rename_title"), self.tr("recording_name"), text=session.title)
        title = title.strip()
        if ok and title:
            self.storage.rename_session(session.id, title)
            self.load_history()

    def play_session(self, session_id):
        session = next((item for item in self.sessions if item.id == session_id), None)
        if not session:
            return
        if not session.audio_path.exists():
            QMessageBox.warning(self, self.tr("audio_missing_title"), self.tr("audio_missing_message"))
            return
        os.startfile(session.audio_path)

    def delete_session(self, session_id):
        session = next((item for item in self.sessions if item.id == session_id), None)
        if not session:
            return
        answer = QMessageBox.question(self, self.tr("delete"), self.tr("delete_confirm", title=session.title))
        if answer == QMessageBox.Yes:
            self.storage.delete_session(session.id)
            self.load_history()
            self.transcript_preview.clear()
            self.copy_button.setEnabled(False)
            self.export_button.setEnabled(False)

