import os
import customtkinter as ctk
import sounddevice as sd
import soundfile as sf
import threading
import simpleaudio as sa

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

os.makedirs("recordings", exist_ok=True)

class VoxauraApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎙️ Voxaura by Y7X")
        self.geometry("700x500")
        self.resizable(False, False)
        self.configure(fg_color="#0a0a0a")

        self.devices = [d['name'] for d in sd.query_devices() if d['max_input_channels'] > 0]
        self.selected_device = ctk.StringVar(value=self.devices[0])
        self.last_recording_path = None

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="🎧 Voxaura", font=("Poppins", 28, "bold"), text_color="#ff1a1a").pack(pady=12)

        self.device_menu = ctk.CTkOptionMenu(self, values=self.devices, variable=self.selected_device,
                                             width=520, height=42, fg_color="#161616", text_color="#ffffff",
                                             button_color="#0f0f0f", button_hover_color="#1a1a1a",
                                             dropdown_fg_color="#161616", dropdown_hover_color="#2a2a2a")
        self.device_menu.pack(pady=8)

        # Grouped row for Duration and Save As
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(pady=8)

        self.duration_entry = ctk.CTkEntry(entry_frame, placeholder_text="⏱ Duration (in seconds)", width=250,
                                           height=40, border_color="#ff1a1a", border_width=2, text_color="#ffffff",
                                           corner_radius=20)
        self.duration_entry.pack(side="left", padx=5)

        self.filename_entry = ctk.CTkEntry(entry_frame, placeholder_text="💾 Save As (e.g. my_voice)", width=250,
                                           height=40, border_color="#ff1a1a", border_width=2, text_color="#ffffff",
                                           corner_radius=20)
        self.filename_entry.pack(side="left", padx=5)

        self.record_button = ctk.CTkButton(self, text="⏺ Start Recording", command=self.start_recording_thread,
                                           width=520, height=50, fg_color="#ff1a1a", hover_color="#ff3333",
                                           border_color="#ff4d4d", border_width=2, corner_radius=25,
                                           font=("Segoe UI Semibold", 16))
        self.record_button.pack(pady=12)

        self.status_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 14), text_color="#bbbbbb")
        self.status_label.pack(pady=4)

        self.play_button = ctk.CTkButton(self, text="▶️ Play Last Recording", command=self.play_last_recording,
                                         width=520, height=44, fg_color="#222", hover_color="#333",
                                         border_color="#ff1a1a", border_width=2, corner_radius=20)
        self.play_button.pack(pady=6)

        self.explore_button = ctk.CTkButton(self, text="📂 Open Recordings Folder", command=self.open_recordings_folder,
                                            width=520, height=44, fg_color="#111", hover_color="#222",
                                            border_color="#777", border_width=2, corner_radius=20)
        self.explore_button.pack(pady=6)

        ctk.CTkLabel(self, text="🔎 Powered by Y7X 💗", font=("Segoe UI", 12, "italic"),
                     text_color="#ff1a1a").pack(side="bottom", pady=12)

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
        os.system(f"open \"{folder_path}\"")

app = VoxauraApp()
app.mainloop()