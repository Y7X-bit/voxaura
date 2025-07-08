import os
import customtkinter as ctk
import sounddevice as sd
import soundfile as sf
import threading
import simpleaudio as sa

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Ensure recordings folder exists
os.makedirs("recordings", exist_ok=True)

class PremiumVoiceRecorder(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎙️ Voice Recorder Pro — Y7X")
        self.geometry("640x480")
        self.resizable(False, False)
        self.configure(fg_color="#111418")  # Rich dark graphite background

        self.devices = [d['name'] for d in sd.query_devices() if d['max_input_channels'] > 0]
        self.selected_device = ctk.StringVar(value=self.devices[0])
        self.last_recording_path = None

        self.create_widgets()

    def create_widgets(self):
        # Header
        ctk.CTkLabel(self, text="🎧 Voice Recorder Pro", font=("Segoe UI Semibold", 26), text_color="#f0f0f0").pack(pady=12)

        # Input device selector
        self.device_menu = ctk.CTkOptionMenu(self, values=self.devices, variable=self.selected_device,
                                             width=500, height=40, fg_color="#1e2227",
                                             button_color="#1e2227", button_hover_color="#2e3237",
                                             dropdown_fg_color="#1e2227", dropdown_hover_color="#2e3237",
                                             text_color="#ffffff")
        self.device_menu.pack(pady=6)

        # Recording duration input
        self.duration_entry = ctk.CTkEntry(self, placeholder_text="⏱ Duration (in seconds)", width=500,
                                           height=40, border_color="#3a3f47", border_width=2)
        self.duration_entry.pack(pady=6)

        # Filename input
        self.filename_entry = ctk.CTkEntry(self, placeholder_text="💾 Save As (e.g. my_voice)", width=500,
                                           height=40, border_color="#3a3f47", border_width=2)
        self.filename_entry.pack(pady=6)

        # Record button
        self.record_button = ctk.CTkButton(self, text="⏺ Start Recording", command=self.start_recording_thread,
                                           width=500, height=48, fg_color="#005b96", hover_color="#0074d9",
                                           border_color="#339af0", border_width=2, corner_radius=20,
                                           font=("Segoe UI Semibold", 16))
        self.record_button.pack(pady=14)

        # Status label
        self.status_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 14), text_color="#bbbbbb")
        self.status_label.pack(pady=5)

        # Play button
        self.play_button = ctk.CTkButton(self, text="▶️ Play Last Recording", command=self.play_last_recording,
                                         width=500, height=42, fg_color="#006442", hover_color="#08944a",
                                         border_color="#37c978", border_width=2, corner_radius=18)
        self.play_button.pack(pady=6)

        # Open folder button
        self.explore_button = ctk.CTkButton(self, text="📂 Open Recordings Folder", command=self.open_recordings_folder,
                                            width=500, height=42, fg_color="#353535", hover_color="#4c4c4c",
                                            border_color="#888", border_width=2, corner_radius=18)
        self.explore_button.pack(pady=6)

        # Footer
        ctk.CTkLabel(self, text="🔎 Made with 💗 by Y7X", font=("Segoe UI", 12, "italic"),
                     text_color="#666").pack(side="bottom", pady=12)

    def start_recording_thread(self):
        threading.Thread(target=self.record_audio).start()

    def record_audio(self):
        try:
            duration = float(self.duration_entry.get())
        except ValueError:
            self.status_label.configure(text="⚠️ Please enter a valid number.")
            return

        filename = self.filename_entry.get().strip() or "recording"
        file_path = os.path.join("recordings", f"{filename}.wav")

        device_name = self.selected_device.get()
        device_index = [i for i, d in enumerate(sd.query_devices()) if d['name'] == device_name][0]
        info = sd.query_devices(device_index)

        samplerate = int(info['default_samplerate'])
        channels = info['max_input_channels']

        self.status_label.configure(text="🔴 Recording in progress...")
        try:
            audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels,
                           dtype='float32', device=device_index)
            sd.wait()
            sf.write(file_path, audio, samplerate)
            self.status_label.configure(text=f"✅ Saved to: {file_path}")
            self.last_recording_path = file_path
        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {e}")

    def play_last_recording(self):
        if self.last_recording_path and os.path.exists(self.last_recording_path):
            try:
                sa.WaveObject.from_wave_file(self.last_recording_path).play()
                self.status_label.configure(text="🎵 Playing audio...")
            except Exception as e:
                self.status_label.configure(text=f"❌ Playback Error: {e}")
        else:
            self.status_label.configure(text="⚠️ No recording available.")

    def open_recordings_folder(self):
        folder_path = os.path.abspath("recordings")
        os.system(f"open \"{folder_path}\"")  # macOS open

# Run app
app = PremiumVoiceRecorder()
app.mainloop()