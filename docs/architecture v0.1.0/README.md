# Project Story: An Elegant Voice-to-Text Transcriber

## Introduction

Imagine a tool that quietly sits in the background, waiting for your command — not by button or menu, but by your very voice. Whether you want to dictate notes, transcribe a meeting, or just capture a thought, this app is designed to do one thing with precision: take your spoken words and turn them into text, seamlessly and flexibly, on any major desktop platform.

This is the story of building such a system, from a desire for simplicity and reliability, shaped by real-world lessons from a too-complex first attempt.

---

## Architecture: Units and Event-Driven Communication

At its heart, the app is a single, solid Python program, built from modular, independent "units," each handling a distinct concern. These units communicate primarily through asynchronous queues, reacting to events and messages from other units to achieve the application's overall functionality. This design emphasizes loose coupling and decentralized control.

### The Units

1. **Shared State Unit**
   The living memory of the app. It holds the current state (listening, idle, recording, recognizing, outputting, etc.), and exposes this to all other units. Changes ripple through the system in a controlled and observable way.

2. **Tray Control Unit**
   An optional UI element: a system tray icon that reflects the app’s status (waiting, listening, recording, etc.). It may offer a menu for actions like exit or about. The tray is built to be replaceable — the initial implementation targets Gnome, but the system is designed for easy adaptation to Windows, Mac, and beyond.

3. **Keyboard Listener Unit**
   Also optional. This unit listens for global hotkeys to control the app: start listening, stop, pause, resume. Like the tray, it’s designed to be swappable for different OS needs.

4. **Sound Recorder Unit**
   This unit captures audio from the system microphone when the app is in the appropriate state. It is sensitive to transitions — it starts and stops recording based on messages received on its control queue. The implementation abstracts over audio backends to allow for cross-platform support.

5. **Voice Recognition Unit**
   The core of the app. Given audio, it converts speech to text. The first supported engines are Vosk (offline) and OpenAI Whisper API (online), but the architecture allows for easy extension with other engines in the future.

6. **Output Handler Unit**
   Once text is recognized, it must go somewhere. This unit handles that, whether it’s inserting into the active window, copying to the clipboard, or another single destination. For now, one output at a time is supported.

7. **Noise Cancelling Unit (Optional)**
   To improve transcription quality, this unit can preprocess audio input, using configurable noise reduction techniques. Its presence is optional and pluggable.

Planned interfaces are described in the `docs/architecture v0.1.0/draft interfaces.md`. Find diagrams in the `docs/architecture v0.1.0/images` directory.

---

## Scenarios: How the App Works

The app can run in several modes, each defined by which units are active and how they interact through queues:

1. **Bare Mode**
   No tray, no keyboard. The app starts, units are initialized, and they react to internal events (e.g., voice detection) to record, transcribe, and output, then the application exits.

2. **Tray Mode**
   Tray enabled, keyboard disabled. The tray icon reflects the app’s state, updated by messages from the Shared State unit. Otherwise, it operates similarly to bare mode, with units reacting to events.

3. **Keyboard Mode**
   Keyboard enabled, tray disabled. The Keyboard Listener unit waits for hotkeys, publishing events that other units (like Sound Recorder) react to. The app idles until hotkeys trigger actions, and remains alive until explicitly exited.

4. **Full Mode**
   Both tray and keyboard enabled. The Tray Control unit reflects state changes, and the Keyboard Listener unit publishes events, with other units reacting to these events to manage recording, transcription, and output. Exiting is typically via the tray menu.

All these scenarios are also described in the `docs/architecture v0.1.0/scenarios.md` and images can be found in the `docs/architecture v0.1.0/images` directory. Note that the PlantUML diagrams in `scenarios.md` conceptually illustrate the flow, and while they may depict an "Orchestrator" for clarity of sequence, the underlying implementation relies on the event-driven, queue-based communication described herein.

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

## High-Level Overview: How Interfaces and Queues Work Together

### Modular Units

The application is divided into several independent "units" (modules), each responsible for a specific part of the voice-to-text pipeline. Examples include:
- `TrayControl`: Handles tray icon and user controls.
- `KeyboardListener`: Detects hotkeys.
- `SoundRecorder`: Captures audio.
- `NoiseCancelling`: Processes audio to remove noise.
- `VoiceRecognition`: Converts audio to text.
- `OutputHandler`: Delivers recognized text to the user or system.
- `SharedState`: Maintains and distributes global state.

Each unit is defined by an interface, specifying what it can do and what data it sends/receives.

---

### Communication via Queues

- **Message Passing:**
  Units do not call each other’s methods directly. Instead, they communicate exclusively via asynchronous queues. These queues act as channels for messages, commands, and data.
- **Input/Output Queues:**
  Each unit exposes one or more input/output queues (e.g., `audio_output_queue`, `input_queue`). Other units send messages to these queues as needed.

---

### Asynchronous Operation

- **Independent Execution:**
  Every unit runs its own asynchronous loop (`run()`), where it waits for new messages on its input queue(s), processes them, and sends results to output queue(s).
- **Parallel Processing:**
  This design allows multiple units to operate at the same time, enabling real-time or near-real-time voice transcription and efficient resource usage.

---

### Example Data Flow

1. `KeyboardListener` detects a hotkey and sends a “start recording” command to `SharedState`’s queue.
2. `SoundRecorder` receives the command on its control queue, starts capturing audio, and sends audio chunks to `NoiseCancelling`'s input queue.
3. `NoiseCancelling` processes audio and sends cleaned chunks to `VoiceRecognition`.
4. `VoiceRecognition` transcribes audio and sends text to `OutputHandler`.
5. `OutputHandler` delivers the text to the appropriate destination (clipboard, active window, etc.).

---

### Benefits

- **Loose Coupling:**
  Units are decoupled—each one only needs to know about its own queues and message formats, not the internal workings of other units.
- **Extensibility:**
  You can swap out or upgrade any unit (e.g., use a different speech engine or recording method) as long as it respects the same interface and queue-based protocol.
- **Scalability:**
  Queues make it easy to adjust, parallelize, or buffer processing between units, supporting high throughput and responsiveness.
- **Testability:**
  Dummy or mock units can be plugged in for testing, allowing early verification of system wiring and message flow.

---

**Summary:**
Each unit in the application is an independent actor that processes messages asynchronously, communicating only through queues. This leads to a robust, modular, and flexible architecture that is easy to maintain, test, and extend.---

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

By focusing on modularity, testability, and cross-platform support — and by learning from past complexity — this project aims to be the most elegant, reliable, and adaptable voice-to-text transcriber for desktop users. Its architecture is simple, but its flexibility and power come from the thoughtful composition of independent units, communicating through event-driven, queue-based interactions to work together in perfect harmony.
