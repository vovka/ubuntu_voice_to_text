# Project Story: An Elegant Voice-to-Text Transcriber

## Introduction

Imagine a tool that quietly sits in the background, waiting for your command — not by button or menu, but by your very voice. Whether you want to dictate notes, transcribe a meeting, or just capture a thought, this app is designed to do one thing with precision: take your spoken words and turn them into text, seamlessly and flexibly, on any major desktop platform.

This is the story of building such a system, from a desire for simplicity and reliability, shaped by real-world lessons from a too-complex first attempt.

---

## Architecture: Units and Orchestration

At its heart, the app is a single, solid Python program, but it is built from modular, independent parts — "units" — each handling a distinct concern. These units are orchestrated by a central controller, which binds them together and manages their interactions.

### The Units

1. **Shared State Unit**
   The living memory of the app. It holds the current state (listening, idle, recording, recognizing, outputting, etc.), and exposes this to all other units. Changes ripple through the system in a controlled and observable way.

2. **Tray Control Unit**
   An optional UI element: a system tray icon that reflects the app’s status (waiting, listening, recording, etc.). It may offer a menu for actions like exit or about. The tray is built to be replaceable — the initial implementation targets Gnome, but the system is designed for easy adaptation to Windows, Mac, and beyond.

3. **Keyboard Listener Unit**
   Also optional. This unit listens for global hotkeys to control the app: start listening, stop, pause, resume. Like the tray, it’s designed to be swappable for different OS needs.

4. **Sound Recorder Unit**
   This unit captures audio from the system microphone when the app is in the appropriate state. It is sensitive to transitions — it starts and stops recording as the orchestrator commands. The implementation abstracts over audio backends to allow for cross-platform support.

5. **Voice Recognition Unit**
   The core of the app. Given audio, it converts speech to text. The first supported engines are Vosk (offline) and OpenAI Whisper API (online), but the architecture allows for easy extension with other engines in the future.

6. **Output Handler Unit**
   Once text is recognized, it must go somewhere. This unit handles that, whether it’s inserting into the active window, copying to the clipboard, or another single destination. For now, one output at a time is supported.

7. **Noise Cancelling Unit (Optional)**
   To improve transcription quality, this unit can preprocess audio input, using configurable noise reduction techniques. Its presence is optional and pluggable.

Planned interfaces are described in the `docs/architecture v0.1.0/draft interfaces.md`. Find diagrams in the `docs/architecture v0.1.0/images` directory.

---

## Scenarios: How the App Works

The app can run in several modes, each defined by which units are active:

1. **Bare Mode**
   No tray, no keyboard. The app starts, listens for speech, records when voice is detected, transcribes, outputs the result, then exits.

2. **Tray Mode**
   Tray enabled, keyboard disabled. The tray icon shows the app’s state. Otherwise works as bare mode.

3. **Keyboard Mode**
   Keyboard enabled, tray disabled. The app waits for a hotkey to start listening. It records and transcribes on voice input, outputs, then idles. Hotkeys can toggle listening/idle, and the app stays alive until explicitly exited.

4. **Full Mode**
   Both tray and keyboard enabled. Tray icon reflects state (with colors/animations), keyboard controls recording. Exiting is only via tray menu.

All these scenarios are also described in the `docs/architecture v0.1.0/scenarios.md` and images can be found in the `docs/architecture v0.1.0/images` directory.

---

## Design Principles

- **Modularity:**
  Every unit is replaceable and testable. Implementations can be swapped for different OS environments or technologies.

- **Dependency Injection:**
  Units are constructed via dependency injection. This makes them easy to test, mock, and extend.

- **Cross-Platform:**
  Tray, keyboard, audio, and recognition units are designed with abstraction layers to enable platform-specific implementations.

- **Configuration:**
  All settings (engine selection, hotkeys, tray style, etc.) are in a single config file, loaded at startup. No live config reloading is required.

- **Simplicity:**
  No CLI, no runtime language switching, no multi-user. The focus is on doing one thing well for a single user, single stream.

- **Docker-First:**
  The primary deployment target is Docker, ensuring reproducibility and ease of setup across environments.

- **Queue-Based Communication:**
  To ensure loose coupling, flexibility, and scalability, each unit communicates with others primarily through queues. These queues act as message channels, allowing data (such as audio chunks or recognized text) to flow asynchronously between units without requiring direct method calls or tight integration. This approach enables each unit to be developed, replaced, or scaled independently, and supports a variety of concurrency and parallelism strategies across different environments.

---

## Queue-Based Communication:

To ensure loose coupling, flexibility, and scalability, each unit communicates with others primarily through queues. These queues act as message channels, allowing data (such as audio chunks or recognized text) to flow asynchronously between units without requiring direct method calls or tight integration. This approach enables each unit to be developed, replaced, or scaled independently, and supports a variety of concurrency and parallelism strategies across different environments.

---

## What’s Not Included (Yet)

- No GUI configuration editor (just a config file for now)
- No live error notifications (errors are logged, but not surfaced via UI)
- No authentication/secrets handling (for now, Whisper API keys go in config)
- No multi-output or multi-stream support
- No language switching on the fly

---

## The User Experience

The user launches the app (usually via Docker). Depending on configuration, they may see a tray icon, or just use hotkeys. When ready, the app listens for voice, records, recognizes, and outputs — all invisibly, if desired. The app adapts to the environment and preferences, but always strives to stay out of the way, fast and accurate.

---

## Conclusion

By focusing on modularity, testability, and cross-platform support — and by learning from past complexity — this project aims to be the most elegant, reliable, and adaptable voice-to-text transcriber for desktop users. Its architecture is simple, but its flexibility and power come from the thoughtful composition of independent units, orchestrated to work together in perfect harmony.
