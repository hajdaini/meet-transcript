from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox


class MainWindowSettingsMixin:
    def whisper_languages(self):
        return [
            ("auto", "Auto"),
            ("af", "Afrikaans"),
            ("am", "Amharic"),
            ("ar", "Arabic"),
            ("as", "Assamese"),
            ("az", "Azerbaijani"),
            ("ba", "Bashkir"),
            ("be", "Belarusian"),
            ("bg", "Bulgarian"),
            ("bn", "Bengali"),
            ("bo", "Tibetan"),
            ("br", "Breton"),
            ("bs", "Bosnian"),
            ("ca", "Catalan"),
            ("cs", "Czech"),
            ("cy", "Welsh"),
            ("da", "Danish"),
            ("de", "German"),
            ("el", "Greek"),
            ("en", "English"),
            ("es", "Spanish"),
            ("et", "Estonian"),
            ("eu", "Basque"),
            ("fa", "Persian"),
            ("fi", "Finnish"),
            ("fo", "Faroese"),
            ("fr", "French"),
            ("gl", "Galician"),
            ("gu", "Gujarati"),
            ("ha", "Hausa"),
            ("haw", "Hawaiian"),
            ("he", "Hebrew"),
            ("hi", "Hindi"),
            ("hr", "Croatian"),
            ("ht", "Haitian Creole"),
            ("hu", "Hungarian"),
            ("hy", "Armenian"),
            ("id", "Indonesian"),
            ("is", "Icelandic"),
            ("it", "Italian"),
            ("ja", "Japanese"),
            ("jw", "Javanese"),
            ("ka", "Georgian"),
            ("kk", "Kazakh"),
            ("km", "Khmer"),
            ("kn", "Kannada"),
            ("ko", "Korean"),
            ("la", "Latin"),
            ("lb", "Luxembourgish"),
            ("ln", "Lingala"),
            ("lo", "Lao"),
            ("lt", "Lithuanian"),
            ("lv", "Latvian"),
            ("mg", "Malagasy"),
            ("mi", "Maori"),
            ("mk", "Macedonian"),
            ("ml", "Malayalam"),
            ("mn", "Mongolian"),
            ("mr", "Marathi"),
            ("ms", "Malay"),
            ("mt", "Maltese"),
            ("my", "Myanmar"),
            ("ne", "Nepali"),
            ("nl", "Dutch"),
            ("nn", "Norwegian Nynorsk"),
            ("no", "Norwegian"),
            ("oc", "Occitan"),
            ("pa", "Punjabi"),
            ("pl", "Polish"),
            ("ps", "Pashto"),
            ("pt", "Portuguese"),
            ("ro", "Romanian"),
            ("ru", "Russian"),
            ("sa", "Sanskrit"),
            ("sd", "Sindhi"),
            ("si", "Sinhala"),
            ("sk", "Slovak"),
            ("sl", "Slovenian"),
            ("sn", "Shona"),
            ("so", "Somali"),
            ("sq", "Albanian"),
            ("sr", "Serbian"),
            ("su", "Sundanese"),
            ("sv", "Swedish"),
            ("sw", "Swahili"),
            ("ta", "Tamil"),
            ("te", "Telugu"),
            ("tg", "Tajik"),
            ("th", "Thai"),
            ("tk", "Turkmen"),
            ("tl", "Tagalog"),
            ("tr", "Turkish"),
            ("tt", "Tatar"),
            ("uk", "Ukrainian"),
            ("ur", "Urdu"),
            ("uz", "Uzbek"),
            ("vi", "Vietnamese"),
            ("yi", "Yiddish"),
            ("yo", "Yoruba"),
            ("zh", "Chinese"),
            ("yue", "Cantonese"),
        ]

    def populate_language_combo(self):
        self.language_combo.clear()
        self.language_combo.addItem("Auto", ["auto"])
        self.language_combo.addItem("Français + Anglais", ["fr", "en"])
        for code, name in self.whisper_languages():
            if code != "auto":
                self.language_combo.addItem(name, [code])

    def load_settings_to_ui(self):
        self.set_combo(self.model_combo, self.settings.get("model", "medium"))
        self.set_combo_data(self.device_combo, self.settings.get("device", "cuda"))
        self.set_combo(self.compute_combo, self.settings.get("compute_type", "int8_float16"))
        self.mic_gain_input.setValue(float(self.settings.get("mic_gain", 1.8)))
        self.set_combo_data(self.interface_language_combo, self.settings.get("interface_language", "en"))
        self.output_dir_input.setText(self.settings.get("output_dir", str(self.storage.base_dir)))
        self.refresh_device_choices()
        self.on_device_changed()

    def bind_auto_save(self):
        self.model_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.device_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.compute_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.interface_language_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.micro_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.mic_gain_input.valueChanged.connect(self.auto_save_settings)
        self.system_output_combo.currentIndexChanged.connect(self.auto_save_settings)
        self.output_dir_input.editingFinished.connect(self.auto_save_settings)

    def refresh_device_choices(self):
        self.micro_combo.blockSignals(True)
        self.system_output_combo.blockSignals(True)
        self.micro_combo.clear()
        self.system_output_combo.clear()
        self.micro_combo.addItem(self.tr("auto"), "")
        self.system_output_combo.addItem(self.tr("auto"), "")
        for name in self.recorder.list_microphones():
            self.micro_combo.addItem(name, name)
        for name in self.recorder.list_system_outputs():
            self.system_output_combo.addItem(name, name)
        self.set_combo_data(self.micro_combo, self.settings.get("microphone", ""))
        self.set_combo_data(self.system_output_combo, self.settings.get("system_output", ""))
        self.micro_combo.blockSignals(False)
        self.system_output_combo.blockSignals(False)

    def set_combo(self, combo, value):
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def set_combo_data(self, combo, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def on_device_changed(self):
        is_gpu = self.device_combo.currentData() == "cuda"
        if is_gpu:
            if self.compute_combo.currentText() == "int8":
                self.set_combo(self.compute_combo, "int8_float16")
        else:
            self.set_combo(self.compute_combo, "int8")
        self.refresh_runtime_status()

    def apply_translations(self):
        self.record_nav.setToolTip(self.tr("recording"))
        self.settings_nav.setToolTip(self.tr("settings"))
        self.record_title.setText(self.tr("recording"))
        self.settings_title.setText(self.tr("settings"))
        if not self.recorder.running and not self.transcription_running:
            self.status_label.setText(self.tr("ready"))
            self.start_button.setText(self.tr("start"))
        self.import_button.setText(self.tr("import_audio"))
        self.recent_title.setText(self.tr("recent_sessions"))
        self.session_search_input.setPlaceholderText(self.tr("search_sessions"))
        self.recent_empty_label.setText(self.tr("empty_sessions"))
        self.transcript_title.setText(self.tr("transcript"))
        self.copy_button.setToolTip(self.tr("copy"))
        self.export_button.setToolTip(self.tr("export"))
        self.transcript_preview.setPlaceholderText(self.tr("select_session"))
        self.history_tabs.setTabText(0, self.tr("sessions_tab"))
        self.history_tabs.setTabText(1, self.tr("transcript_tab"))
        self.runtime_refresh_button.setText(self.tr("verify_gpu"))
        self.output_dir_button.setText(self.tr("browse"))
        for key, label in self.section_labels.items():
            label.setText(self.tr(key))
        for key, label in self.form_labels.items():
            label.setText(self.tr(key))
        self.interface_language_combo.blockSignals(True)
        self.interface_language_combo.setItemText(0, self.tr("english"))
        self.interface_language_combo.setItemText(1, self.tr("french"))
        self.interface_language_combo.blockSignals(False)
        self.refresh_device_choices()

    def choose_output_dir(self):
        selected = QFileDialog.getExistingDirectory(self, self.tr("choose_output_folder"), self.output_dir_input.text())
        if selected:
            self.output_dir_input.setText(selected)
            self.auto_save_settings()

    def collect_settings(self):
        return {
            "model": self.model_combo.currentText(),
            "device": self.device_combo.currentData() or "cuda",
            "compute_type": "int8" if self.device_combo.currentData() == "cpu" else self.compute_combo.currentText(),
            "require_gpu": self.device_combo.currentData() == "cuda",
            "interface_language": self.interface_language_combo.currentData() or "en",
            "microphone": self.micro_combo.currentData() or "",
            "mic_gain": round(float(self.mic_gain_input.value()), 2),
            "system_output": self.system_output_combo.currentData() or "",
            "output_dir": self.output_dir_input.text().strip() or str(Path.cwd() / "transcripts"),
        }

    def auto_save_settings(self):
        if self.loading_settings:
            return
        previous_language = self.settings.get("interface_language", "en")
        self.settings = self.collect_settings()
        self.storage.save_settings(self.settings)
        self.storage.update_base_dir(self.settings["output_dir"])
        self.transcription.configure(self.settings)
        if previous_language != self.settings.get("interface_language", "en"):
            self.apply_translations()
        self.refresh_devices()
        self.load_history()

    def refresh_devices(self):
        self.recorder.microphone = self.settings.get("microphone", "")
        self.recorder.mic_gain = float(self.settings.get("mic_gain", 1.8))
        self.recorder.system_output = self.settings.get("system_output", "")
        status = self.recorder.detect_devices()
        self.micro_badge.setText(self.tr("micro_ready", name=status.microphone_name) if status.microphone_available else self.tr("micro_missing"))
        self.micro_badge.setProperty("state", "neutral" if status.microphone_available else "blocked")
        self.system_badge.setText(self.tr("audio_ready", name=status.system_name) if status.system_audio_available else self.tr("audio_missing"))
        self.system_badge.setProperty("state", "neutral" if status.system_audio_available else "blocked")
        self.model_badge.setText(self.tr("model_badge", model=self.settings.get("model", "medium")))
        self.model_badge.setProperty("state", "neutral")
        for badge in (self.micro_badge, self.system_badge, self.model_badge):
            badge.style().unpolish(badge)
            badge.style().polish(badge)
        self.refresh_runtime_status()

    def refresh_runtime_status(self):
        if hasattr(self, "model_combo"):
            self.transcription.configure(self.collect_settings())
        status = self.transcription.runtime_status()
        self.compute_badge.setText(self.tr("transcription_backend", backend=status.backend))
        self.compute_badge.setProperty("state", "neutral" if status.backend == "GPU" else "blocked" if "bloque" in status.backend else "neutral")
        self.compute_badge.style().unpolish(self.compute_badge)
        self.compute_badge.style().polish(self.compute_badge)
        return status

    def show_gpu_status(self):
        status = self.refresh_runtime_status()
        box = QMessageBox(self)
        if status.backend == "GPU":
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle(self.tr("gpu_ready_title"))
            box.setText(self.tr("gpu_ready_text"))
            box.setInformativeText(status.message)
            box.setStyleSheet("QMessageBox { background: #101216; } QLabel { color: #62f0c8; } QPushButton { background: #143f35; color: #ffffff; padding: 8px 14px; border-radius: 8px; }")
        else:
            box.setIcon(QMessageBox.Critical)
            box.setWindowTitle(self.tr("gpu_blocked_title"))
            box.setText(self.tr("gpu_blocked_text"))
            box.setInformativeText(status.message)
            box.setStyleSheet("QMessageBox { background: #101216; } QLabel { color: #ffb4a8; } QPushButton { background: #4a1d1d; color: #ffffff; padding: 8px 14px; border-radius: 8px; }")
        box.exec()

