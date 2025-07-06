```
from abc import ABC, abstractmethod
from typing import Any, Protocol, Dict, Optional


class QueueProtocol(Protocol):
    """
    A generic queue protocol for async communication between units.
    Implementations must provide async put() and get() methods.
    """
    async def put(self, item: Any) -> None: ...
    async def get(self) -> Any: ...


class ISharedState(ABC):
    """
    Interface for a shared state unit.
    Typically used for propagating and observing global state changes.
    """
    @property
    @abstractmethod
    def state_queue(self) -> QueueProtocol:
        """A queue for state change events/messages."""
        ...


class ITrayControl(ABC):
    """
    Interface for the tray icon/control unit.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None): ...

    @property
    @abstractmethod
    def input_queue(self) -> QueueProtocol:
        """Queue for commands or state updates directed to tray."""
        ...

    async def run(self) -> None:
        """
        Main async loop to process incoming messages from the input_queue.
        """
        ...


class IKeyboardListener(ABC):
    """
    Interface for the keyboard hotkey listener unit.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None): ...

    @property
    @abstractmethod
    def output_queue(self) -> QueueProtocol:
        """Queue for publishing detected hotkey events."""
        ...

    async def run(self) -> None:
        """
        Main async loop to listen for keyboard input and post events to output_queue.
        """
        ...


class ISoundRecorder(ABC):
    """
    Interface for the sound recorder unit.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None): ...

    @property
    @abstractmethod
    def audio_output_queue(self) -> QueueProtocol:
        """Queue for sending audio chunks or streams."""
        ...

    @property
    @abstractmethod
    def control_queue(self) -> QueueProtocol:
        """Queue for receiving control commands (start, stop, etc.)."""
        ...

    async def run(self) -> None:
        """
        Main async loop to process control commands and emit audio to audio_output_queue.
        """
        ...


class INoiseCancelling(ABC):
    """
    Interface for the noise cancelling/preprocessing unit.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None): ...

    @property
    @abstractmethod
    def audio_input_queue(self) -> QueueProtocol:
        """Queue for receiving raw audio."""
        ...

    @property
    @abstractmethod
    def audio_output_queue(self) -> QueueProtocol:
        """Queue for sending processed audio."""
        ...

    async def run(self) -> None:
        """
        Main async loop to process audio from input_queue and send to output_queue.
        """
        ...


class IVoiceRecognition(ABC):
    """
    Interface for the voice/speech recognition unit.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None): ...

    @property
    @abstractmethod
    def audio_input_queue(self) -> QueueProtocol:
        """Queue for receiving audio to recognize."""
        ...

    @property
    @abstractmethod
    def text_output_queue(self) -> QueueProtocol:
        """Queue for sending out recognized text."""
        ...

    async def run(self) -> None:
        """
        Main async loop to process audio from input_queue and send recognized text to output_queue.
        """
        ...


class IOutputHandler(ABC):
    """
    Interface for the output handler unit (clipboard, active window, file, etc.).
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None): ...

    @property
    @abstractmethod
    def input_queue(self) -> QueueProtocol:
        """Queue for receiving recognized text."""
        ...

    async def run(self) -> None:
        """
        Main async loop to process recognized text and deliver it to the chosen output.
        """
        ...
```
