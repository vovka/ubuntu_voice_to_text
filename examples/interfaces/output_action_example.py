"""
Example implementations of OutputActionTarget for different output methods.

This demonstrates how to implement the OutputAction interface
for keyboard, clipboard, and file output targets.
"""

import subprocess
from typing import Dict, Any, Optional
from voice_typing.interfaces import OutputActionTarget, OutputType


class KeyboardOutputTarget(OutputActionTarget):
    """
    Output target that types text using keyboard simulation (xdotool).
    """

    def __init__(self):
        self._append_space = True
        self._initialized = False

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize keyboard output target."""
        self._append_space = config.get('append_space', True)
        self._initialized = self.is_available()
        
        if self._initialized:
            print("[KeyboardOutputTarget] Initialized successfully")
        else:
            print("[KeyboardOutputTarget] xdotool not available")
            
        return self._initialized

    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Type text using xdotool."""
        if not self._initialized:
            return False

        try:
            output_text = text
            if self._append_space:
                output_text += " "
            
            result = subprocess.run(["xdotool", "type", output_text], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"[KeyboardOutputTarget] Typed: '{text}'")
                return True
            else:
                print(f"[KeyboardOutputTarget] xdotool error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[KeyboardOutputTarget] Error typing text: {e}")
            return False

    def is_available(self) -> bool:
        """Check if xdotool is available."""
        try:
            result = subprocess.run(["which", "xdotool"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def get_output_type(self) -> OutputType:
        """Return keyboard output type."""
        return OutputType.KEYBOARD

    def supports_formatting(self) -> bool:
        """Keyboard output doesn't support rich formatting."""
        return False

    def cleanup(self) -> None:
        """No cleanup needed for keyboard output."""
        pass


class ClipboardOutputTarget(OutputActionTarget):
    """
    Output target that copies text to system clipboard using xclip.
    """

    def __init__(self):
        self._initialized = False

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize clipboard output target."""
        self._initialized = self.is_available()
        
        if self._initialized:
            print("[ClipboardOutputTarget] Initialized successfully")
        else:
            print("[ClipboardOutputTarget] xclip not available")
            
        return self._initialized

    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Copy text to clipboard using xclip."""
        if not self._initialized:
            return False

        try:
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                     stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)
            
            if process.returncode == 0:
                print(f"[ClipboardOutputTarget] Copied to clipboard: '{text}'")
                return True
            else:
                print(f"[ClipboardOutputTarget] xclip failed with code {process.returncode}")
                return False
                
        except Exception as e:
            print(f"[ClipboardOutputTarget] Error copying to clipboard: {e}")
            return False

    def is_available(self) -> bool:
        """Check if xclip is available."""
        try:
            result = subprocess.run(["which", "xclip"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def get_output_type(self) -> OutputType:
        """Return clipboard output type."""
        return OutputType.CLIPBOARD

    def supports_formatting(self) -> bool:
        """Clipboard can support some formatting."""
        return True

    def cleanup(self) -> None:
        """No cleanup needed for clipboard output."""
        pass


class FileOutputTarget(OutputActionTarget):
    """
    Output target that writes text to a file.
    """

    def __init__(self):
        self._file_path = None
        self._append_mode = True
        self._initialized = False

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize file output target."""
        self._file_path = config.get('target')
        self._append_mode = config.get('append_mode', True)
        
        if not self._file_path:
            print("[FileOutputTarget] No target file specified")
            return False

        # Test if we can write to the file
        try:
            mode = 'a' if self._append_mode else 'w'
            with open(self._file_path, mode) as f:
                f.write("")  # Test write
            
            self._initialized = True
            print(f"[FileOutputTarget] Initialized with file: {self._file_path}")
            return True
            
        except Exception as e:
            print(f"[FileOutputTarget] Cannot write to file {self._file_path}: {e}")
            return False

    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Write text to file."""
        if not self._initialized:
            return False

        try:
            mode = 'a' if self._append_mode else 'w'
            with open(self._file_path, mode) as f:
                # Add timestamp if metadata is available
                if metadata and 'timestamp' in metadata:
                    import datetime
                    timestamp = datetime.datetime.fromtimestamp(metadata['timestamp'])
                    f.write(f"[{timestamp}] ")
                
                f.write(text)
                if not text.endswith('\n'):
                    f.write('\n')
            
            print(f"[FileOutputTarget] Wrote to file: '{text}'")
            return True
            
        except Exception as e:
            print(f"[FileOutputTarget] Error writing to file: {e}")
            return False

    def is_available(self) -> bool:
        """Check if file output is available."""
        return self._initialized

    def get_output_type(self) -> OutputType:  
        """Return file output type."""
        return OutputType.FILE

    def supports_formatting(self) -> bool:
        """File output can support formatting."""
        return True

    def cleanup(self) -> None:
        """No cleanup needed for file output."""
        pass


# Example usage
if __name__ == "__main__":
    import time
    from voice_typing.interfaces.output_action import MultiOutputActionTarget
    
    # Test individual targets
    print("=== Testing Individual Targets ===")
    
    # Keyboard target
    keyboard_target = KeyboardOutputTarget()
    keyboard_config = {'append_space': True}
    if keyboard_target.initialize(keyboard_config):
        print("NOTE: This will type 'Hello from keyboard' - make sure cursor is in safe location!")
        input("Press Enter to continue...")
        keyboard_target.deliver_text("Hello from keyboard")
    
    # Clipboard target
    clipboard_target = ClipboardOutputTarget()
    clipboard_config = {}
    if clipboard_target.initialize(clipboard_config):
        clipboard_target.deliver_text("Hello from clipboard")
        print("Text should now be in clipboard - try pasting!")
    
    # File target
    file_target = FileOutputTarget()
    file_config = {
        'target': '/tmp/voice_typing_test.txt',
        'append_mode': True
    }
    if file_target.initialize(file_config):
        metadata = {'timestamp': time.time()}
        file_target.deliver_text("Hello from file", metadata)
        print(f"Check file: {file_config['target']}")
    
    # Test multiple targets
    print("\n=== Testing Multiple Targets ===")
    available_targets = []
    if clipboard_target.is_available():
        available_targets.append(clipboard_target)
    if file_target.is_available():
        available_targets.append(file_target)
    
    if available_targets:
        multi_target = MultiOutputActionTarget(available_targets)
        multi_config = {}
        if multi_target.initialize(multi_config):
            multi_target.deliver_text("Hello from multiple targets")
            print("Text delivered to all available targets!")
    
    # Cleanup
    keyboard_target.cleanup()
    clipboard_target.cleanup()
    file_target.cleanup()
    print("\nExample completed!")