import customtkinter as ctk
from tkinter import filedialog
import threading
from pathlib import Path
import os
import sys
import requests

# Set ffmpeg path for bundled app
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configure ffmpeg path for Whisper
ffmpeg_path = get_resource_path("ffmpeg")
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ.get("PATH", "")

# Check for DnD library (graceful fallback for PyInstaller)
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
except ImportError:
    print("tkinterdnd2 not found. Drag & Drop will be disabled.")
    TkinterDnD = None
    DND_FILES = None

# Create base class with optional DnD support
if TkinterDnD:
    class BaseCTk(ctk.CTk, TkinterDnD.DnDWrapper):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.TkdndVersion = TkinterDnD._require(self)
else:
    class BaseCTk(ctk.CTk):
        pass


class LynxLogApp(BaseCTk):
    def __init__(self):
        super().__init__()

        self.title("LynxLog")
        self.geometry("500x450")
        self.resizable(False, False)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.selected_file = None
        self.transcript_text = ""
        self.model = None

        self.create_upload_view()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_upload_view(self):
        self.clear_window()

        # Title
        title_label = ctk.CTkLabel(
            self, text="LynxLog", font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10), anchor="w", padx=20)

        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=40, pady=20)

        # Status
        self.status_label = ctk.CTkLabel(
            container, text="Ready to log scripts.", font=ctk.CTkFont(size=16)
        )
        self.status_label.pack(pady=(20, 10))

        # Drop zone (above button) - only show if DnD is available
        if TkinterDnD:
            self.drop_zone = ctk.CTkLabel(
                container,
                text="Drop .mp4 here",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                width=250,
                height=40,
                corner_radius=8,
                fg_color="#f0f0f0"
            )
            self.drop_zone.pack(pady=(10, 15))

            # Register drop zone for drag-and-drop
            self.drop_zone.drop_target_register(DND_FILES)
            self.drop_zone.dnd_bind("<<Drop>>", self.on_drop)
            self.drop_zone.dnd_bind("<<DragEnter>>", self.on_drag_enter)
            self.drop_zone.dnd_bind("<<DragLeave>>", self.on_drag_leave)
        else:
            self.drop_zone = None

        # File select button (orange)
        self.file_btn = ctk.CTkButton(
            container,
            text="Click to insert .mp4 file",
            command=self.select_file,
            width=250,
            height=45,
            corner_radius=20,
            fg_color="#F5A623",
            hover_color="#D4891A",
            text_color="white",
            font=ctk.CTkFont(size=14)
        )
        self.file_btn.pack(pady=10)

        # Transcribe button (green, disabled initially)
        self.transcribe_btn = ctk.CTkButton(
            container,
            text="Transcribe",
            command=self.transcribe,
            width=250,
            height=45,
            corner_radius=20,
            fg_color="#7ED321",
            hover_color="#6BBF1A",
            text_color="white",
            font=ctk.CTkFont(size=14),
            state="disabled"
        )
        self.transcribe_btn.pack(pady=10)

        # Progress bar (hidden initially)
        self.progress_bar = ctk.CTkProgressBar(
            container, width=250, height=15, corner_radius=5
        )
        self.progress_bar.set(0)

        # Progress label
        self.progress_label = ctk.CTkLabel(
            container, text="", font=ctk.CTkFont(size=11)
        )

    def select_file(self):
        filepath = filedialog.askopenfilename(
            title="Select MP4 file",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if filepath:
            self._set_selected_file(filepath)

    def _set_selected_file(self, filepath):
        """Set the selected file and update UI."""
        self.selected_file = Path(filepath)
        self.file_btn.configure(text=self.selected_file.name)
        self.transcribe_btn.configure(state="normal")
        if self.drop_zone:
            self.drop_zone.configure(text=self.selected_file.name, text_color="#333")

    def on_drop(self, event):
        """Handle file drop."""
        # Parse the dropped file path
        # On macOS, paths with spaces are wrapped in {}
        # Multiple files are separated by spaces
        filepath = event.data.strip()

        # Extract the first file if multiple files are dropped
        if filepath.startswith("{"):
            # Find matching closing brace
            end_idx = filepath.find("}")
            if end_idx > 0:
                filepath = filepath[1:end_idx]
        else:
            # If no braces, split by space and take first part
            filepath = filepath.split()[0] if filepath else ""

        # Verify the file exists and is an mp4
        if filepath and os.path.exists(filepath) and filepath.lower().endswith(".mp4"):
            self._set_selected_file(filepath)
            self.drop_zone.configure(fg_color="#d4edda")  # Green tint
        else:
            error_msg = "Please drop an .mp4 file"
            if filepath and not os.path.exists(filepath):
                error_msg = f"File not found"
            self.drop_zone.configure(text=error_msg, text_color="red")
            self.after(2000, lambda: self.drop_zone.configure(
                text="Drop .mp4 here", text_color="gray"
            ))

    def on_drag_enter(self, event):
        """Highlight drop zone on drag enter."""
        self.drop_zone.configure(fg_color="#e3f2fd")  # Light blue highlight

    def on_drag_leave(self, event):
        """Reset drop zone on drag leave."""
        if self.selected_file:
            self.drop_zone.configure(fg_color="#d4edda")  # Keep green if file selected
        else:
            self.drop_zone.configure(fg_color="#f0f0f0")

    def transcribe(self):
        self.status_label.configure(text="Transcribing... please wait")
        self.transcribe_btn.configure(state="disabled")
        self.file_btn.configure(state="disabled")

        thread = threading.Thread(target=self._transcribe_worker)
        thread.start()

    def _download_model_with_progress(self, model_name="base"):
        """Download Whisper model with progress bar updates."""
        import whisper

        # Model URLs from whisper source
        model_urls = {
            "tiny": "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt",
            "base": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt",
            "small": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt",
            "medium": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt",
            "large": "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt",
        }

        # Cache directory
        cache_dir = Path(os.path.expanduser("~/.cache/whisper"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        model_path = cache_dir / f"{model_name}.pt"

        # Check if already downloaded
        if model_path.exists():
            return model_path

        # Download with progress
        url = model_urls.get(model_name)
        if not url:
            raise ValueError(f"Unknown model: {model_name}")

        self.after(0, lambda: self.status_label.configure(text="Downloading model..."))
        self.after(0, lambda: self.progress_bar.pack(pady=(15, 5)))
        self.after(0, lambda: self.progress_label.pack())

        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(model_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                progress = downloaded / total_size if total_size > 0 else 0
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                self.after(0, lambda p=progress: self.progress_bar.set(p))
                self.after(0, lambda d=mb_downloaded, t=mb_total: self.progress_label.configure(
                    text=f"{d:.1f} MB / {t:.1f} MB ({d/t*100:.0f}%)" if t > 0 else ""
                ))

        return model_path

    def _transcribe_worker(self):
        try:
            import whisper

            # Verify file exists before processing
            if not self.selected_file.exists():
                raise FileNotFoundError(f"File not found: {self.selected_file}")

            if self.model is None:
                # Download model with progress if needed
                model_path = self._download_model_with_progress("base")

                self.after(0, lambda: self.status_label.configure(text="Loading model..."))
                self.after(0, lambda: self.progress_bar.pack_forget())
                self.after(0, lambda: self.progress_label.pack_forget())
                self.model = whisper.load_model("base")

            self.after(0, lambda: self.status_label.configure(text="Transcribing..."))
            result = self.model.transcribe(str(self.selected_file), verbose=False)

            filename = self.selected_file.stem
            self.transcript_text = f"# title: {filename}\n\n{result['text'].strip()}"

            self.after(0, self.create_results_view)

        except Exception as e:
            # Show full error message in status
            error_msg = f"Error: {str(e)}"
            self.after(0, lambda msg=error_msg: self.status_label.configure(text=msg))
            self.after(0, lambda: self.transcribe_btn.configure(state="normal"))
            self.after(0, lambda: self.file_btn.configure(state="normal"))
            self.after(0, lambda: self.progress_bar.pack_forget())
            self.after(0, lambda: self.progress_label.pack_forget())
            # Print full error to console for debugging
            print(f"Transcription error: {e}")
            import traceback
            traceback.print_exc()

    def create_results_view(self):
        self.clear_window()

        # Title
        title_label = ctk.CTkLabel(
            self, text="LynxLog", font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 5), anchor="w", padx=20)

        # Status
        status_label = ctk.CTkLabel(
            self, text="Parsed successfully!", font=ctk.CTkFont(size=14)
        )
        status_label.pack(pady=(0, 10))

        # Text area frame
        text_frame = ctk.CTkFrame(self, corner_radius=10)
        text_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Text area
        self.text_area = ctk.CTkTextbox(
            text_frame, wrap="word", font=ctk.CTkFont(size=12)
        )
        self.text_area.pack(padx=10, pady=10, fill="both", expand=True)
        self.text_area.insert("1.0", self.transcript_text)

        # Button container
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.pack(pady=15)

        # Copy text button (green)
        copy_btn = ctk.CTkButton(
            btn_container,
            text="Copy text",
            command=self.copy_text,
            width=120,
            height=35,
            corner_radius=15,
            fg_color="#7ED321",
            hover_color="#6BBF1A",
            text_color="white"
        )
        copy_btn.pack(side="left", padx=5)

        # Export as .md button (blue)
        export_btn = ctk.CTkButton(
            btn_container,
            text="Export as .md",
            command=self.export_md,
            width=120,
            height=35,
            corner_radius=15,
            fg_color="#4A90D9",
            hover_color="#3A7BC8",
            text_color="white"
        )
        export_btn.pack(side="left", padx=5)

        # Start over button (orange)
        start_over_btn = ctk.CTkButton(
            btn_container,
            text="Start over",
            command=self.start_over,
            width=120,
            height=35,
            corner_radius=15,
            fg_color="#F5A623",
            hover_color="#D4891A",
            text_color="white"
        )
        start_over_btn.pack(side="left", padx=5)

    def copy_text(self):
        self.clipboard_clear()
        text = self.text_area.get("1.0", "end-1c")
        self.clipboard_append(text)

    def export_md(self):
        if self.selected_file:
            default_name = f"{self.selected_file.stem}.md"
        else:
            default_name = "transcript.md"

        filepath = filedialog.asksaveasfilename(
            title="Export as Markdown",
            defaultextension=".md",
            initialfile=default_name,
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if filepath:
            text = self.text_area.get("1.0", "end-1c")
            Path(filepath).write_text(text, encoding="utf-8")

    def start_over(self):
        self.selected_file = None
        self.transcript_text = ""
        self.create_upload_view()


if __name__ == "__main__":
    app = LynxLogApp()
    app.mainloop()
