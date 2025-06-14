# Output Action Interface

The Output Action Interface defines how recognized text is delivered to various targets such as keyboard simulation, clipboard, files, or custom callbacks.

## Interface Contract

### OutputActionTarget (Abstract Base Class)

```python
from voice_typing.interfaces import OutputActionTarget, OutputType

class MyOutputTarget(OutputActionTarget):
    def initialize(self, config: Dict[str, Any]) -> bool:
        # Setup output target with config parameters
        pass
    
    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        # Deliver text to the target
        pass
    
    def is_available(self) -> bool:
        # Return True if target is available
        pass
    
    def get_output_type(self) -> OutputType:
        # Return the type of output this target handles
        pass
    
    def supports_formatting(self) -> bool:
        # Return True if target supports text formatting
        pass
    
    def cleanup(self) -> None:
        # Clean up resources
        pass
```

## Output Types

The interface supports several output types defined in the `OutputType` enum:

- `KEYBOARD` - Simulate keyboard input to type text
- `CLIPBOARD` - Copy text to system clipboard  
- `FILE` - Write text to a file
- `CALLBACK` - Call a custom function with the text

## Configuration Parameters

The `initialize()` method expects a configuration dictionary with these parameters:

- `output_type` (OutputType): The type of output target
- `target` (str): Target specification (file path, device, etc.)
- `formatting` (dict): Text formatting options
- `append_space` (bool): Whether to append space after text
- `callback` (callable): Callback function for CALLBACK type

## Usage Examples

### Keyboard Output Implementation

```python
from voice_typing.interfaces import OutputActionTarget, OutputType

class KeyboardOutputTarget(OutputActionTarget):
    def __init__(self):
        self._append_space = True
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        self._append_space = config.get('append_space', True)
        return self.is_available()
    
    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            import subprocess
            output_text = text
            if self._append_space:
                output_text += " "
            subprocess.run(["xdotool", "type", output_text])
            return True
        except Exception as e:
            print(f"Failed to type text: {e}")
            return False
    
    def is_available(self) -> bool:
        try:
            import subprocess
            result = subprocess.run(["which", "xdotool"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_output_type(self) -> OutputType:
        return OutputType.KEYBOARD
    
    def supports_formatting(self) -> bool:
        return False
    
    def cleanup(self) -> None:
        pass
```

### Clipboard Output Implementation

```python
class ClipboardOutputTarget(OutputActionTarget):
    def initialize(self, config: Dict[str, Any]) -> bool:
        return self.is_available()
    
    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            import subprocess
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                     stdin=subprocess.PIPE, text=True)
            process.communicate(input=text)
            return process.returncode == 0
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")
            return False
    
    def is_available(self) -> bool:
        try:
            import subprocess
            result = subprocess.run(["which", "xclip"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_output_type(self) -> OutputType:
        return OutputType.CLIPBOARD
    
    def supports_formatting(self) -> bool:
        return True
    
    def cleanup(self) -> None:
        pass
```

### File Output Implementation

```python
class FileOutputTarget(OutputActionTarget):
    def __init__(self):
        self._file_path = None
        self._append_mode = True
        
    def initialize(self, config: Dict[str, Any]) -> bool:
        self._file_path = config.get('target')
        self._append_mode = config.get('append_mode', True)
        
        if not self._file_path:
            return False
            
        # Test if we can write to the file
        try:
            mode = 'a' if self._append_mode else 'w'
            with open(self._file_path, mode) as f:
                pass
            return True
        except Exception:
            return False
    
    def deliver_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            mode = 'a' if self._append_mode else 'w'
            with open(self._file_path, mode) as f:
                f.write(text)
                if not text.endswith('\n'):
                    f.write('\n')
            return True
        except Exception as e:
            print(f"Failed to write to file: {e}")
            return False
    
    def is_available(self) -> bool:
        return self._file_path is not None
    
    def get_output_type(self) -> OutputType:
        return OutputType.FILE
    
    def supports_formatting(self) -> bool:
        return True
    
    def cleanup(self) -> None:
        pass
```

## Multiple Output Targets

You can use `MultiOutputActionTarget` to deliver text to multiple targets simultaneously:

```python
from voice_typing.interfaces.output_action import MultiOutputActionTarget

# Create individual targets
keyboard_target = KeyboardOutputTarget()
clipboard_target = ClipboardOutputTarget()

# Combine them
multi_target = MultiOutputActionTarget([keyboard_target, clipboard_target])

# Configure all targets
config = {'append_space': True}
multi_target.initialize(config)

# Deliver text to all targets
multi_target.deliver_text("Hello world")
```

## Callback Output Target

For testing or custom handling, use `CallbackOutputActionTarget`:

```python
from voice_typing.interfaces.output_action import CallbackOutputActionTarget

def my_text_handler(text: str, metadata: Optional[Dict[str, Any]]):
    print(f"Received text: {text}")
    if metadata:
        print(f"Metadata: {metadata}")

callback_target = CallbackOutputActionTarget()
config = {'callback': my_text_handler}
callback_target.initialize(config)

callback_target.deliver_text("Test message", {'confidence': 0.95})
```

## Metadata

The `deliver_text()` method accepts optional metadata that can include:

- `confidence`: Recognition confidence score (0.0 to 1.0)
- `timestamp`: When the text was recognized
- `language`: Detected language of the text
- `alternatives`: Alternative recognition results

Example:
```python
metadata = {
    'confidence': 0.95,
    'timestamp': time.time(),
    'language': 'en-US',
    'alternatives': ['hello world', 'yellow world']
}

target.deliver_text("hello world", metadata)
```

## Error Handling

- Return `False` from methods that fail to indicate failure
- Use try/catch blocks around platform-specific operations
- Log errors appropriately for debugging
- Ensure `cleanup()` is always safe to call multiple times
- Check `is_available()` before attempting delivery