# 🎧 macwrap

**Your Mac. Wrapped.**
A Spotify Wrapped–style yearly analytics experience for your macOS — entirely in the terminal.

`macwrap` analyzes your real macOS usage data (Screen Time, app sessions, focus patterns, late nights, command usage, file creation, and more) and presents it as a **beautiful, animated terminal story**.

No accounts.
No tracking.
No cloud.
Just *your Mac*, unwrapped.

---

## ✨ Features

* 📊 **Real macOS Screen Time analytics**

  * Total hours used
  * Top apps
  * App launch counts
  * Longest sessions
* 🔥 **Streaks & habits**

  * Longest usage streak
  * Weekend vs weekday usage
  * Late-night sessions
  * Deep focus sessions (2+ hours)
* 🧠 **Personality detection**

  * “Night Owl Code Wizard”
  * “Professional Tab Hoarder”
  * “Deep Focus Digital Professional”
* 📈 **Visual terminal experience**

  * Animated transitions
  * Hourly heatmaps
  * ASCII charts
* ⌨️ **Developer stats**

  * Shell command count
  * File creation stats
* ⚡ **System insights**

  * Sleep / wake cycles
  * Power events
* 🔒 **Privacy-first**

  * Runs completely locally
  * Reads only your machine’s data
  * Nothing is sent anywhere

---

## 🖥 Demo

Run:

```bash
macwrap
```

And experience your year unfold, screen by screen, directly in your terminal.

---

## 📦 Installation (Homebrew)

### Install via Homebrew (recommended)

```bash
brew install arinagrawal05/labs/macwrap
```

Then run:

```bash
macwrap
```

---

## 🧪 Requirements

* macOS (Screen Time must be enabled)
* Python 3.12+ (automatically installed via Homebrew)
* Terminal with UTF-8 + color support

---

## 🔐 Permissions & Privacy

MacWrap reads data from:

* macOS Screen Time database (`knowledgeC.db`)
* Local shell history
* Local file metadata

⚠️ **No network access**
⚠️ **No analytics**
⚠️ **No telemetry**

Your data never leaves your machine.

---

## 🛠 Project Structure

```
macwrap/
├─ macwrap.py          # Main entrypoint
├─ bin/
│  └─ macwrap          # Homebrew launcher
└─ app/
   ├─ screens/         # All TUI screens
   └─ utils/           # Data extraction + analytics
```

---

## 🧩 How it works

1. Reads macOS Screen Time data safely
2. Aggregates usage patterns
3. Derives insights & personality traits
4. Presents everything using a Textual-based terminal UI

---

## 🧑‍💻 Development

Clone the repo:

```bash
git clone https://github.com/arinagrawal05/macwrap
cd macwrap
```

Run locally:

```bash
python3 macwrap.py
```

---

## 🚀 Roadmap

* 🎵 Optional background music
* 🖼 Exportable share card (PNG)
* 📆 Monthly / weekly wraps
* 🤖 AI-generated insights
* 🌐 Community personality leaderboard (opt-in)

---

## 📜 License

MIT License
Feel free to fork, modify, and build on top of it.

---

## 💡 Inspiration

Inspired by:

* Spotify Wrapped
* Terminal UIs
* macOS power users
* Developers who live in their terminal

---

## 🙌 Author

Built by **Arin Agrawal**
GitHub: [https://github.com/arinagrawal05](https://github.com/arinagrawal05)
