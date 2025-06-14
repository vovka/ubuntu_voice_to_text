import os
from typing import Optional, Callable
from .interfaces.state_manager import StateManager, StateTransition, VoiceTypingState


class TrayIconManager:
    def __init__(self, state_manager: StateManager, 
                 exit_callback: Optional[Callable[[], None]] = None):
        """
        Initialize TrayIconManager as a pure UI subscriber.
        
        Args:
            state_manager: StateManager instance to subscribe to state changes
            exit_callback: Callback function to handle exit requests
        """
        self.state_manager = state_manager
        self.exit_callback = exit_callback
        self.icon = None
        self._current_state = VoiceTypingState.IDLE
        
        # Subscribe to state changes
        self.state_manager.register_state_listener(self._on_state_change)
        print("[TrayIconManager] Subscribed to state changes via StateManager")

    def create_image_text(self, state="idle"):
        try:
            from PIL import Image, ImageDraw

            width, height = 32, 32
            image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
            dc = ImageDraw.Draw(image)

            if state == "finish_listening":
                color = (40, 150, 150)  # blue
            elif state == "listening":
                color = (40, 255, 40)  # green
            else:
                color = (120, 120, 120)  # grey

            # Draw a filled circle
            dc.ellipse(
                [(4, 4), (width - 4, height - 4)],
                fill=color,
                outline=(60, 60, 60),
                width=2,
            )

            return image
        except ImportError:
            print(
                "[TrayIconManager] PIL not available, tray icon functionality disabled"
            )
            return None

    def _on_state_change(self, transition: StateTransition) -> None:
        """
        React to state changes by updating the tray icon.
        
        This is the core event subscription that makes TrayIconManager
        a pure subscriber to state changes.
        
        Args:
            transition: StateTransition object containing state change details
        """
        print(f"[TrayIconManager] State changed: {transition.from_state.value} → {transition.to_state.value}")
        self._current_state = transition.to_state
        self._update_icon_for_state(self._current_state)

    def _update_icon_for_state(self, state: VoiceTypingState) -> None:
        """
        Update icon appearance based on the current state.
        
        Args:
            state: Current VoiceTypingState to display
        """
        if self.icon:
            print(f"[TrayIconManager] Updating icon for state: {state.value}")
            self.icon.icon = self.create_image_text(state.value)
            
            # Update title based on state
            if state == VoiceTypingState.FINISH_LISTENING:
                self.icon.title = "Voice Typing: finish_listening"
            elif state == VoiceTypingState.LISTENING:
                self.icon.title = "Voice Typing: ON"
            else:
                self.icon.title = "Voice Typing: OFF"

    def exit_application(self, icon, item):
        """
        Handle exit request from tray menu.
        
        This delegates to the exit callback to avoid business logic in UI layer.
        """
        print("[TrayIconManager] Exit requested from tray menu")
        icon.stop()
        if self.exit_callback:
            self.exit_callback()
        else:
            # Default exit behavior
            os._exit(0)

    def tray_thread(self):
        print("[TrayIconManager] Starting tray icon thread")
        try:
            import pystray

            # Create menu with Exit item
            menu = pystray.Menu(pystray.MenuItem("Exit", self.exit_application))
            self.icon = pystray.Icon("voice_typing", menu=menu)
            
            # Initialize icon with current state
            self._update_icon_for_state(self._current_state)
            self.icon.run()
        except ImportError:
            print(
                "[TrayIconManager] pystray not available, "
                "tray icon functionality disabled"
            )
