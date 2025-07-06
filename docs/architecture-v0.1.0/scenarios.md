# Architecture Diagrams: Voice-to-Text Transcriber

Below are PlantUML diagrams illustrating the architecture and module interactions for all operational scenarios of the app as described in the project's general story.

---

## 1. High-Level Architecture Overview

```plantuml
@startuml
!theme blueprint
title Voice-to-Text Transcriber: High-Level Architecture (Choreography)

actor User

package "Core Units" {
  component SharedState
  component TrayControl
  component KeyboardListener
  component SoundRecorder
  component NoiseCancelling
  component VoiceRecognition
  component OutputHandler
}

User --> TrayControl: Interacts (e.g., starts app)
User --> KeyboardListener: Interacts (e.g., hotkeys)

TrayControl --> SharedState: updates state / sends commands
KeyboardListener --> SharedState: updates state / sends commands

TrayControl ..> SharedState : observes
KeyboardListener ..> SharedState : observes
SoundRecorder ..> SharedState : observes/updates
VoiceRecognition ..> SharedState : observes/updates
OutputHandler ..> SharedState : observes

SoundRecorder --> NoiseCancelling: sends audio
NoiseCancelling --> VoiceRecognition: sends clean audio
VoiceRecognition --> OutputHandler: sends text

' Explicit command flows from SharedState or other units to SoundRecorder
SharedState --> SoundRecorder: commands (e.g., start/stop recording)

' Explicit command flows from SharedState or other units to OutputHandler
SharedState --> OutputHandler: commands (e.g., deliver text)

@enduml
```

---

## 2. Scenario 1: Bare Mode (No Tray, No Keyboard)

```plantuml
@startuml
!theme blueprint
title Scenario 1: Bare Mode (No Tray, No Keyboard)

actor User

User --> System: Start App (initializes units)

System --> SharedState: Set to "waiting"
System --> SoundRecorder: Activate (via initial event/config)

SoundRecorder -> SharedState: Voice Detected (updates state)
SoundRecorder --> SoundRecorder: Start Recording (internal action based on state)
SoundRecorder --> NoiseCancelling: (optional) Process audio
NoiseCancelling --> VoiceRecognition: Send audio
VoiceRecognition --> OutputHandler: Send text
OutputHandler --> SharedState: Text Processed (updates state)
SharedState --> System: Set to "exiting" (triggers app shutdown)
System -> User: Exit

@enduml
```

---

## 3. Scenario 2: Tray Mode (Tray, No Keyboard)

```plantuml
@startuml
!theme blueprint
title Scenario 2: Tray Mode (Tray, No Keyboard)

actor User

User --> TrayControl: Start App
TrayControl --> SharedState: Set to "waiting"
TrayControl --> SoundRecorder: Activate (via message to control queue)

SoundRecorder -> SharedState: Voice Detected (updates state)
SharedState --> TrayControl: Update Icon (recording)
SoundRecorder --> SoundRecorder: Start Recording (internal action based on state)
SoundRecorder --> NoiseCancelling: Send audio
NoiseCancelling --> VoiceRecognition: Send audio
VoiceRecognition --> OutputHandler: Send text
OutputHandler --> TrayControl: Update Icon (done)
SharedState --> SharedState: Set to "exiting" (internal state change)
TrayControl --> User: Exit (via tray menu or internal logic)

@enduml
```

---

## 4. Scenario 3: Keyboard Mode (Keyboard, No Tray)

```plantuml
!theme blueprint
title Scenario 3: Keyboard Mode (Keyboard, No Tray)

actor User

User --> System: Start App (initializes units)
System --> KeyboardListener: Activate (via initial event/config)
System --> SharedState: Set to "idle"

KeyboardListener --> SharedState: Hotkey Pressed (start recording)
SharedState --> SharedState: Set to "listening" (internal state change)
SharedState --> SoundRecorder: Activate (via message to control queue)

SoundRecorder --> SharedState: Voice Detected (updates state)
SoundRecorder --> SoundRecorder: Start Recording (internal action based on state)
SoundRecorder --> NoiseCancelling: (optional) Process
NoiseCancelling --> VoiceRecognition: Send audio
VoiceRecognition --> OutputHandler: Send text
OutputHandler --> SharedState: Text Processed (updates state)

SoundRecorder --> SharedState: Silence Detected (updates state)
SharedState --> SharedState: Set to "idle" (internal state change)
KeyboardListener --> SharedState: Hotkey Pressed (stop recording)
SharedState --> SharedState: Set to "idle" (internal state change)
User --> System: Exit App (external command)

@enduml
```

---

## 5. Scenario 4: Full Mode (Tray + Keyboard)

```plantuml
!theme blueprint
title Scenario 4: Full Mode (Tray + Keyboard)

actor User

User --> System: Start App (initializes units)
System --> TrayControl: Show Tray Icon (idle)
System --> KeyboardListener: Activate (via initial event/config)
System --> SharedState: Set to "idle"

KeyboardListener --> SharedState: Hotkey Pressed (start recording)
SharedState --> SharedState: Set to "listening" (internal state change)
SharedState --> TrayControl: Update Icon (listening)
SharedState --> SoundRecorder: Activate (via message to control queue)

SoundRecorder --> SharedState: Voice Detected (updates state)
SharedState --> SharedState: Set to "recording" (internal state change)
SharedState --> TrayControl: Update Icon (recording)
SoundRecorder --> SoundRecorder: Start Recording (internal action based on state)
SoundRecorder --> NoiseCancelling: (optional) Process
NoiseCancelling --> VoiceRecognition: Send audio
VoiceRecognition --> OutputHandler: Send text
OutputHandler --> SharedState: Text Processed (updates state)
SharedState --> TrayControl: Update Icon (done)
SharedState --> SharedState: Set to "idle" (internal state change)
SharedState --> TrayControl: Update Icon (idle)

KeyboardListener --> SharedState: Hotkey Pressed (stop recording)
SharedState --> SharedState: Set to "idle" (internal state change)
SharedState --> TrayControl: Update Icon (idle)

User -> TrayControl: Exit via Tray Menu
TrayControl --> SharedState: Exit Command
SharedState --> SharedState: Set to "exiting" (internal state change)
System -> User: Exit App

@enduml
```

---

## 6. Unit Replacement/Extensibility Overview

```plantuml
!theme blueprint
title Extensibility: How Units are Swappable

package "Units" {
  interface ITrayControl
  class GnomeTray
  class WinTray
  class MacTray

  interface IKeyboardListener
  class LinuxKeyboard
  class WinKeyboard
  class MacKeyboard

  interface ISoundRecorder
  class PyAudioRecorder
  class WasapiRecorder

  interface IVoiceRecognition
  class VoskEngine
  class WhisperAPI

  interface IOutputHandler
  class ActiveWindowOutput
  class ClipboardOutput
}

ITrayControl <|.. GnomeTray
ITrayControl <|.. WinTray
ITrayControl <|.. MacTray

IKeyboardListener <|.. LinuxKeyboard
IKeyboardListener <|.. WinKeyboard
IKeyboardListener <|.. MacKeyboard

ISoundRecorder <|.. PyAudioRecorder
ISoundRecorder <|.. WasapiRecorder

IVoiceRecognition <|.. VoskEngine
IVoiceRecognition <|.. WhisperAPI

IOutputHandler <|.. ActiveWindowOutput
IOutputHandler <|.. ClipboardOutput

@enduml
```

---

**These diagrams can be rendered using any PlantUML-compatible viewer or plugin.**
