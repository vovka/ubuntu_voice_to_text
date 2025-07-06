# Architecture Diagrams: Voice-to-Text Transcriber

Below are PlantUML diagrams illustrating the architecture and module interactions for all operational scenarios of the app as described in the project's general story.

---

## 1. High-Level Architecture Overview

```plantuml
@startuml
title Voice-to-Text Transcriber: High-Level Architecture

actor User

User --> Orchestrator: Starts App

package "Core Units" {
  Orchestrator
  SharedState
  TrayControl
  KeyboardListener
  SoundRecorder
  NoiseCancelling
  VoiceRecognition
  OutputHandler
}

Orchestrator --> SharedState
Orchestrator --> TrayControl
Orchestrator --> KeyboardListener
Orchestrator --> SoundRecorder
Orchestrator --> NoiseCancelling
Orchestrator --> VoiceRecognition
Orchestrator --> OutputHandler

TrayControl ..> SharedState : observes
KeyboardListener ..> SharedState : observes
SoundRecorder ..> SharedState : observes/updates
VoiceRecognition ..> SharedState : observes/updates
OutputHandler ..> SharedState : observes

SoundRecorder --> NoiseCancelling: sends audio
NoiseCancelling --> VoiceRecognition: sends clean audio
VoiceRecognition --> OutputHandler: sends text

@enduml
```

---

## 2. Scenario 1: Bare Mode (No Tray, No Keyboard)

```plantuml
@startuml
title Scenario 1: Bare Mode (No Tray, No Keyboard)

actor User

User --> Orchestrator: Start

Orchestrator --> SharedState: Set to "waiting"
Orchestrator --> SoundRecorder: Activate
SoundRecorder -> Orchestrator: Voice Detected
Orchestrator --> SoundRecorder: Start Recording
SoundRecorder --> NoiseCancelling: (optional) Process audio
NoiseCancelling --> VoiceRecognition: Send audio
VoiceRecognition -> Orchestrator: Text Ready
Orchestrator --> OutputHandler: Output text
Orchestrator --> SharedState: Set to "exiting"
Orchestrator -> User: Exit

@enduml
```

---

## 3. Scenario 2: Tray Mode (Tray, No Keyboard)

```plantuml
@startuml
title Scenario 2: Tray Mode (Tray, No Keyboard)

actor User

User --> Orchestrator: Start
Orchestrator --> TrayControl: Show Tray Icon (waiting)
Orchestrator --> SharedState: Set to "waiting"
Orchestrator --> SoundRecorder: Activate

SoundRecorder -> Orchestrator: Voice Detected
Orchestrator --> SharedState: Set to "recording"
Orchestrator --> TrayControl: Update Icon (recording)
Orchestrator --> SoundRecorder: Start Recording
SoundRecorder --> NoiseCancelling: (optional) Process
NoiseCancelling --> VoiceRecognition: Send audio
VoiceRecognition -> Orchestrator: Text Ready
Orchestrator --> OutputHandler: Output text
Orchestrator --> TrayControl: Update Icon (done)
Orchestrator --> SharedState: Set to "exiting"
Orchestrator -> User: Exit

@enduml
```

---

## 4. Scenario 3: Keyboard Mode (Keyboard, No Tray)

```plantuml
@startuml
title Scenario 3: Keyboard Mode (Keyboard, No Tray)

actor User

User --> Orchestrator: Start
Orchestrator --> KeyboardListener: Listen for Hotkey
Orchestrator --> SharedState: Set to "idle"

KeyboardListener -> Orchestrator: Hotkey Pressed (start)
Orchestrator --> SharedState: Set to "listening"
Orchestrator --> SoundRecorder: Activate

SoundRecorder -> Orchestrator: Voice Detected
Orchestrator --> SoundRecorder: Start Recording
SoundRecorder --> NoiseCancelling: (optional) Process
NoiseCancelling --> VoiceRecognition: Send audio
VoiceRecognition -> Orchestrator: Text Ready
Orchestrator --> OutputHandler: Output text

SoundRecorder -> Orchestrator: Silence Detected
Orchestrator --> SharedState: Set to "idle"
KeyboardListener -> Orchestrator: Hotkey Pressed (stop)
Orchestrator --> SharedState: Set to "idle"
User --> Orchestrator: Exit via external command

@enduml
```

---

## 5. Scenario 4: Full Mode (Tray + Keyboard)

```plantuml
@startuml
title Scenario 4: Full Mode (Tray + Keyboard)

actor User

User --> Orchestrator: Start
Orchestrator --> TrayControl: Show Tray Icon (idle)
Orchestrator --> KeyboardListener: Listen for Hotkey
Orchestrator --> SharedState: Set to "idle"

KeyboardListener -> Orchestrator: Hotkey Pressed (start)
Orchestrator --> SharedState: Set to "listening"
Orchestrator --> TrayControl: Update Icon (listening)
Orchestrator --> SoundRecorder: Activate

SoundRecorder -> Orchestrator: Voice Detected
Orchestrator --> SharedState: Set to "recording"
Orchestrator --> TrayControl: Update Icon (recording)
Orchestrator --> SoundRecorder: Start Recording
SoundRecorder --> NoiseCancelling: (optional) Process
NoiseCancelling --> VoiceRecognition: Send audio
VoiceRecognition -> Orchestrator: Text Ready
Orchestrator --> OutputHandler: Output text
Orchestrator --> TrayControl: Update Icon (done)
Orchestrator --> SharedState: Set to "idle"
Orchestrator --> TrayControl: Update Icon (idle)

KeyboardListener -> Orchestrator: Hotkey Pressed (stop)
Orchestrator --> SharedState: Set to "idle"
Orchestrator --> TrayControl: Update Icon (idle)

User -> TrayControl: Exit via Tray Menu
TrayControl -> Orchestrator: Exit Command
Orchestrator --> SharedState: Set to "exiting"
Orchestrator -> User: Exit

@enduml
```

---

## 6. Unit Replacement/Extensibility Overview

```plantuml
@startuml
title Extensibility: How Units are Swappable

package "Orchestrator" {
  class Orchestrator
}

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
}

Orchestrator --> ITrayControl
ITrayControl <|.. GnomeTray
ITrayControl <|.. WinTray
ITrayControl <|.. MacTray

Orchestrator --> IKeyboardListener
IKeyboardListener <|.. LinuxKeyboard
IKeyboardListener <|.. WinKeyboard
IKeyboardListener <|.. MacKeyboard

Orchestrator --> ISoundRecorder
ISoundRecorder <|.. PyAudioRecorder
ISoundRecorder <|.. WasapiRecorder

Orchestrator --> IVoiceRecognition
IVoiceRecognition <|.. VoskEngine
IVoiceRecognition <|.. WhisperAPI

@enduml
```

---

**These diagrams can be rendered using any PlantUML-compatible viewer or plugin.**
