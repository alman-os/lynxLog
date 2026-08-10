![almanOS_lynxLog_app](https://github.com/alman-os/lynxLog/blob/main/LYNX_image_1.png)

# LynxLog

**Drag in an `.mp4`, get a clean text transcript — all on your Mac, no cloud, no account.**

LynxLog is a tiny macOS app that pulls the audio out of a video file and transcribes it to text using OpenAI's Whisper model running locally. Point it at a screen recording, a lecture, a voice memo you exported as video — and copy the text or save it as Markdown. Nothing leaves your machine.

<table>
  <tr>
    <td>
      <a href="https://youtu.be/W4TQU8brNbg">
        <img src="https://github.com/alman-os/lynxLog/blob/main/yt-thumbnail.png" alt="Watch the video" width="300">
      </a>
    </td>
    <td>
      <h3>Turn Any Video into Searchable Markdown (FREE Local Tool for macOS)</h3>
      <p> 👈🏻 Watch the Youtube Explainer here!
</p>
    </td>
  </tr>
</table>


---

## Table of Contents

- [What Does This Do](#what-does-this-do)
- [Installation](#installation)
- [Usage](#usage)
- [What Can You Do With This](#what-can-you-do-with-this)
- [Privacy](#privacy)
- [Tech Details](#tech-details)
- [Building From Source](#building-from-source)
- [Contributing](#contributing)
- [License](#license)

---

## What Does This Do

- Transcribes the audio track of any `.mp4` to text — runs the Whisper model on your own hardware.
- Drag-and-drop or click to pick a file. Either works.
- Copy the transcript to your clipboard or export it as a `.md` file in one click.
- Works fully offline after a one-time model download (~140 MB) on first run.
- Bundles its own `ffmpeg`, so there's nothing else to install.
- Native macOS app — no terminal, no Python setup, no API keys.

---

## Installation

**Requirements:** macOS 11 or later, Apple Silicon (M1/M2/M3/M4).

**1. Download the app.** Grab the latest `LynxLog_macOS-silicon` zip from the [Releases page](https://github.com/alman-os/lynxLog/releases), unzip it, and drag `LynxLog.app` into your Applications folder.

**2. First launch — get past the Gatekeeper warning.** The app isn't notarized by Apple yet, so a plain double-click will say it "can't be opened" or is "damaged." This is expected for indie apps and doesn't mean anything's wrong. Two ways around it:

- **Easy way:** Right-click (or Control-click) `LynxLog.app` → **Open** → **Open** again in the dialog. You only do this once.
- **If macOS still blocks it** (common on newer macOS, which flags downloaded unsigned apps as "damaged"), clear the quarantine flag in Terminal:

```bash
xattr -cr /Applications/LynxLog.app
```

Then open it normally.

**3. First transcribe downloads the model.** The first time you hit Transcribe, LynxLog downloads the Whisper `base` model (~140 MB) with a progress bar. After that it's cached at `~/.cache/whisper` and you're fully offline.

---

## Usage

**Quick start:**

1. Open LynxLog.
2. Drop an `.mp4` onto the drop zone, or click **Click to insert .mp4 file** to browse.
3. Click **Transcribe**. First run downloads the model; after that it goes straight to work.
4. When it's done, you'll see the transcript. Use **Copy text**, **Export as .md**, or **Start over**.

**Output format.** Exported and copied text is Markdown with a title line derived from the filename:

```markdown
# title: my-recording

Full transcript text goes here...
```

That's it — no settings to wrangle. The app uses Whisper's `base` model, which is the sweet spot of speed and accuracy for local use.

---

## What Can You Do With This

- Turn screen recordings and demos into searchable notes.
- Transcribe lectures, talks, or webinars you've saved as video.
- Pull quotes out of interviews or podcasts without scrubbing the timeline.
- Draft captions or show notes from raw footage.
- Keep a text log of voice memos you've exported as `.mp4`.

Anything where you have a video and want the words out of it as plain text.

---

## Privacy

Your audio never leaves your computer. Transcription runs entirely on your Mac via local Whisper — there are no API calls, no uploads, and no account.

The one network request the app makes is the **first-run model download** from OpenAI's public model host. After that download, you can run LynxLog with the network off and it works exactly the same.

---

## Tech Details

- **Language:** Python
- **UI:** [customtkinter](https://github.com/TomSchimansky/CustomTkinter) with [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) for drag-and-drop
- **Transcription:** [openai-whisper](https://github.com/openai/whisper) (`base` model)
- **Audio extraction:** bundled `ffmpeg` binary
- **Packaging:** [PyInstaller](https://pyinstaller.org/) → standalone `.app`
- **Model cache:** `~/.cache/whisper`

---

## Building From Source

You'll need Python 3, a virtual environment, and an Apple Silicon Mac.

**1. Clone and set up:**

```bash
git clone https://github.com/alman-os/lynxLog.git
cd lynxLog
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Add the ffmpeg binary.** The build expects an `ffmpeg` binary at `bin/ffmpeg`. Drop a static Apple Silicon build there (e.g. from [evermeet.cx/ffmpeg](https://evermeet.cx/ffmpeg/)) and make it executable:

```bash
chmod +x bin/ffmpeg
```

**3. Run it directly** (for development):

```bash
python main.py
```

**4. Build the `.app`:**

```bash
./build.sh
```

The bundled app lands at `dist/LynxLog.app`.

**Heads up:** the build is unsigned (`codesign_identity=None` in `lynxlog.spec`). If you have an Apple Developer account, plug your signing identity and notarization into the spec to skip the Gatekeeper warning for your users.

---

## Contributing

Issues and pull requests are welcome at [github.com/alman-os/lynxLog](https://github.com/alman-os/lynxLog). If you hit a bug, include your macOS version and the exact error text from the app's status line.

---

## License

LynxLog is licensed under the **PolyForm Noncommercial License 1.0.0** — free for any noncommercial use. Commercial use requires a separate license. See [LICENSE.md](LICENSE.md) for the full terms.
