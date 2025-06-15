# Vosk Audio Overflow Debug Scripts

This directory contains executable debug scripts to systematically investigate and resolve the Vosk backend audio input overflow issue. These scripts are designed to provide comprehensive diagnostic information about the audio processing pipeline.

## Problem Description

The issue manifests as:
- No text recognition with Vosk backend
- Repeated `[SoundDeviceAudioInput] Audio callback status: input overflow` messages
- Audio buffer overflow preventing proper voice recognition

## Quick Start

### Option 1: Run Complete Investigation (Recommended)
```bash
# Run all debug phases
python debug_runner.py --all

# Or run quick diagnostic (phases 1, 2, 4)
python debug_runner.py --quick
```

### Option 2: Run Individual Scripts
```bash
# Check system environment
python debug_environment.py

# Test audio hardware
python debug_audio_devices.py

# Measure Vosk performance  
python debug_vosk_performance.py

# Reproduce the overflow issue
python minimal_overflow_repro.py

# Find optimal audio settings
python optimize_audio_config.py

# Compare different backends
python compare_backends.py
```

## Script Descriptions

### 1. `debug_runner.py` - Master Debug Coordinator
**Purpose**: Orchestrates all debug phases and provides unified reporting.

**Usage**:
```bash
python debug_runner.py --all         # Complete investigation
python debug_runner.py --quick       # Essential checks only
python debug_runner.py --phase 2     # Run specific phase
python debug_runner.py --list        # Show available phases
```

**What it tests**:
- Coordinates execution of all debug phases
- Provides progress tracking and summary reports
- Handles errors and provides troubleshooting guidance

---

### 2. `debug_environment.py` - System Environment Verification
**Purpose**: Verify system compatibility and dependencies.

**What it checks**:
- ✅ Operating system and kernel version
- ✅ Python version (requires 3.8+)
- ✅ Audio system (PulseAudio, ALSA)
- ✅ Required Python packages (vosk, sounddevice, numpy, etc.)
- ✅ System resources (memory, CPU, disk space)
- ✅ Audio device permissions
- ✅ Vosk model availability

**Expected output**:
```
✅ Operating System: Linux 5.15.0 (x86_64)
✅ Python Version: 3.12.0
✅ ALSA Recording Devices: 2 recording devices found
✅ Vosk Package: Vosk speech recognition v0.3.45
⚠️  Vosk Model Directories: No Vosk models found in common locations
```

---

### 3. `debug_audio_devices.py` - Audio Hardware Analysis
**Purpose**: Test hardware audio capabilities and identify overflow-prone configurations.

**What it tests**:
- 🎤 Audio device inventory and capabilities
- 📊 Sample rate and block size compatibility
- ⏱️ Real-time callback performance with overflow detection
- 🧪 Multiple configuration matrix testing
- 📈 Optimal buffer size recommendations

**Key measurements**:
- Audio callback timing and stability
- Hardware buffer overflow/underflow events
- Supported sample rates and block sizes
- Real-time processing capability

**Expected output**:
```
🎤 Testing: USB Audio Device
   ✅ 16000 Hz - Supported
   ✅ 8000 samples - OK
   
📊 Test Results:
   Total Callbacks: 156
   Overflow Events: 12
   ⚠️  OVERFLOW DETECTED: 12 events may indicate buffer issues
```

---

### 4. `debug_vosk_performance.py` - Vosk Performance Profiling
**Purpose**: Measure Vosk recognition processing speed and identify bottlenecks.

**What it measures**:
- 📖 Model loading time
- ⚡ Recognition processing speed per audio chunk
- 🎯 Real-time factor (processing time vs audio duration)
- 🔄 Concurrent processing capability
- 🏆 Model comparison (if multiple models available)

**Key metrics**:
- Mean processing time per chunk
- Real-time factor (should be ≤ 1.0 for real-time)
- Processing time stability (standard deviation)
- Model initialization overhead

**Expected output**:
```
📊 Recognition Performance Results:
   Mean processing time per chunk: 45.23ms
   Real-time factor: 0.45x
   ✅ Processing is FASTER than real-time - should not cause overflows
```

---

### 5. `minimal_overflow_repro.py` - Issue Reproduction
**Purpose**: Create minimal reproduction of the exact overflow conditions.

**What it simulates**:
- 🎤 Exact audio callback behavior from the application
- 🧠 Vosk processing in separate thread (mimicking real usage)  
- 📊 Queue-based audio processing pipeline
- ⚠️ Overflow event detection and logging

**Reproduction scenarios**:
- Real-time audio capture with Vosk processing
- Threading model identical to main application
- Buffer overflow condition triggering
- Performance bottleneck identification

**Expected output**:
```
🎯 OVERFLOW ISSUE REPRODUCED!
   12 overflow events detected
   📝 Likely cause: Vosk processing too slow
      Recognition takes longer than audio buffer duration
```

---

### 6. `optimize_audio_config.py` - Configuration Optimization
**Purpose**: Test multiple audio configurations to find optimal settings.

**What it optimizes**:
- 🔧 Sample rates (16kHz, 22kHz, 44kHz)
- 📦 Block sizes (2048, 4096, 8000, 16000 samples)
- 🎚️ Data types (int16, float32)
- 📊 Performance scoring system

**Optimization criteria**:
- Zero or minimal overflow events
- Good callback timing stability
- Real-time processing capability
- Hardware compatibility

**Expected output**:
```
🏆 TOP 5 CONFIGURATIONS:
Rank  Score    Sample Rate  Block Size  Dtype      Overflows
1     95.0     16000        16000       int16      0
2     90.5     16000        8000        int16      0

🎯 FINAL RECOMMENDATION:
   Sample Rate: 16000 Hz
   Block Size: 16000 samples
   ✅ Should eliminate overflow issues
```

---

### 7. `compare_backends.py` - Backend Comparison
**Purpose**: Compare Vosk against other recognition backends to isolate the issue.

**Backends tested**:
- 🗣️ Vosk (local speech recognition)
- 🤖 Whisper (OpenAI API) - if API key available
- 🎯 Mock (no processing baseline)

**Comparison metrics**:
- Overflow event counts per backend
- Processing speed and real-time factors
- System resource usage patterns
- Root cause isolation

**Expected output**:
```
📊 BACKEND PERFORMANCE COMPARISON:
Backend              Overflows  Callbacks    RTF      Status
Vosk                 12         156          1.2x     ❌ HAS OVERFLOWS  
Mock (No Processing) 0          156          0.01x    ✅ CLEAN

🔍 ANALYSIS RESULTS:
   ⚠️  Vosk backend specifically affected
   📝 Vosk backend has specific performance issues
```

---

## Interpreting Results

### Success Indicators ✅
- **No overflow events** in audio tests
- **Real-time factor ≤ 1.0** for recognition processing
- **All required dependencies** present and working
- **Stable callback timing** with low standard deviation

### Warning Signs ⚠️
- **Overflow events detected** but infrequent (< 5% of callbacks)
- **Real-time factor > 1.0 but < 1.5** (may work but unstable)
- **Missing optional components** (models, API keys)
- **High callback timing variance**

### Critical Issues ❌
- **Frequent overflow events** (> 5% of callbacks)
- **Real-time factor > 1.5** (cannot keep up with audio)
- **Missing required dependencies** (vosk, sounddevice)
- **No compatible audio devices**

## Common Solutions

Based on debug results, try these fixes:

### If Vosk is too slow:
```bash
# Try smaller/faster model
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

# Increase buffer size in voice_typing/pipeline/audio_input.py:
blocksize=16000  # Instead of 8000
```

### If audio system issues:
```bash
# Install audio packages
sudo apt install pulseaudio alsa-utils

# Add user to audio group
sudo usermod -a -G audio $USER

# Test audio devices
arecord -l
```

### If system performance issues:
```bash
# Check system load
top
iostat

# Reduce system load
# Close unnecessary applications
```

## Troubleshooting

### Script fails to run:
```bash
# Install missing dependencies
pip install vosk sounddevice numpy

# Check Python version (requires 3.8+)
python --version
```

### No audio devices found:
```bash
# Check hardware
lsusb  # For USB audio devices
arecord -l  # List recording devices

# Check permissions
groups  # Should include 'audio'
```

### No Vosk models found:
```bash
# Download a model
mkdir -p ~/vosk-models
cd ~/vosk-models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

### Still getting overflows after fixes:
```bash
# Try the optimized configuration from optimize_audio_config.py
# Apply settings to voice_typing/pipeline/audio_input.py
# Test with minimal_overflow_repro.py again
```

## Advanced Usage

### Custom Configuration Testing:
```python
# Edit optimize_audio_config.py test matrix:
test_matrix = {
    'sample_rate': [16000, 32000],    # Test higher sample rates
    'block_size': [16000, 32000],     # Test larger buffers
    'channels': [1],
    'dtype': ['int16']
}
```

### Detailed Profiling:
```python
# Add profiling to debug scripts:
import cProfile
cProfile.run('run_debug()', 'profile_output.prof')

# Analyze with:
python -m pstats profile_output.prof
```

### Custom Backend Testing:
```python
# Add your own backend to compare_backends.py:
def initialize_custom_backend(self):
    # Your backend initialization
    self.backends['custom'] = {
        'name': 'Custom Backend',
        'process_func': self.process_custom_audio
    }
```

## Getting Help

If the debug scripts don't resolve your issue:

1. **Run the complete investigation**: `python debug_runner.py --all`
2. **Save the output**: `python debug_runner.py --all > debug_results.txt 2>&1`
3. **Check the debug plan**: Review `vosk_overflow_debug_plan.md` for additional manual steps
4. **Report results**: Include debug output when reporting the issue

The scripts provide comprehensive diagnostics to identify whether the overflow stems from:
- Vosk processing speed limitations
- Audio buffer configuration problems  
- Threading and synchronization issues
- Hardware compatibility problems
- System resource constraints

Good luck debugging! 🔍