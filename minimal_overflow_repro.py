#!/usr/bin/env python3
"""
Minimal Overflow Reproduction Script

This script creates a minimal reproduction of the Vosk backend audio 
overflow issue by simulating the exact conditions from the voice typing
application but with detailed debugging output.
"""

import sys
import time
import threading
import queue
from typing import Dict, Any, Optional
import traceback


class MinimalOverflowReproducer:
    """Minimal reproduction of the audio overflow issue."""
    
    def __init__(self):
        self.sd = None
        self.vosk = None
        self.model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.overflow_count = 0
        self.processing_times = []
        self.active = False
        self.stats = {}
    
    def print_section(self, title: str):
        """Print formatted section header."""
        print(f"\n{'='*60}")
        print(f" {title}")
        print('='*60)
    
    def initialize_libraries(self) -> bool:
        """Initialize required libraries."""
        print("🔧 Initializing libraries...")
        
        try:
            import sounddevice as sd
            self.sd = sd
            print("✅ SoundDevice initialized")
        except ImportError:
            print("❌ SoundDevice not available")
            return False
        
        try:
            import vosk
            self.vosk = vosk
            print("✅ Vosk initialized")
        except ImportError:
            print("❌ Vosk not available")
            return False
        
        return True
    
    def find_and_load_model(self) -> bool:
        """Find and load a Vosk model."""
        import os
        
        model_paths = [
            '/usr/share/vosk-models',
            '/opt/vosk-models',
            os.path.expanduser('~/vosk-models'),
            './models',
            './vosk-models'
        ]
        
        print("🔍 Searching for Vosk models...")
        
        for base_path in model_paths:
            if os.path.exists(base_path):
                try:
                    for item in os.listdir(base_path):
                        model_path = os.path.join(base_path, item)
                        if os.path.isdir(model_path):
                            required_files = ['final.mdl', 'HCLG.fst', 'words.txt']
                            if all(os.path.exists(os.path.join(model_path, f)) for f in required_files):
                                print(f"📂 Found model: {model_path}")
                                return self.load_model(model_path)
                except PermissionError:
                    continue
        
        print("❌ No Vosk models found")
        return False
    
    def load_model(self, model_path: str) -> bool:
        """Load a specific Vosk model."""
        try:
            print(f"📖 Loading model from: {model_path}")
            start_time = time.time()
            
            self.model = self.vosk.Model(model_path)
            self.recognizer = self.vosk.KaldiRecognizer(self.model, 16000)
            
            load_time = time.time() - start_time
            print(f"✅ Model loaded in {load_time:.3f}s")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False
    
    def audio_callback(self, indata, frames, time, status):
        """Audio callback that mimics the original application behavior."""
        callback_start = time.time()
        
        # This is the exact log message from the original issue
        if status:
            self.overflow_count += 1
            print(f"[SoundDeviceAudioInput] Audio callback status: {status}")
        
        # Convert data to bytes (mimicking the original code)
        try:
            audio_bytes = bytes(indata)
            
            # Put audio data in queue for processing (non-blocking)
            try:
                self.audio_queue.put_nowait((audio_bytes, callback_start))
            except queue.Full:
                print("⚠️  Audio queue full - dropping frame")
        
        except Exception as e:
            print(f"❌ Audio callback error: {e}")
        
        callback_end = time.time()
        callback_duration = callback_end - callback_start
        
        # Track callback performance
        if len(self.processing_times) < 1000:  # Limit memory usage
            self.processing_times.append(callback_duration)
    
    def recognition_worker(self):
        """Worker thread that processes audio data with Vosk."""
        print("🔄 Recognition worker started")
        
        while self.active:
            try:
                # Get audio data from queue (with timeout)
                audio_data, callback_time = self.audio_queue.get(timeout=1.0)
                
                # Measure Vosk processing time
                process_start = time.time()
                
                # This is the actual Vosk processing call from the original code
                self.recognizer.AcceptWaveform(audio_data)
                
                process_end = time.time()
                process_duration = process_end - process_start
                
                # Check if processing is too slow
                audio_duration = len(audio_data) / (16000 * 2)  # 16kHz, 16-bit
                real_time_factor = process_duration / audio_duration
                
                if real_time_factor > 1.0:
                    print(f"🐌 Slow processing: {process_duration*1000:.1f}ms for {audio_duration*1000:.1f}ms audio (factor: {real_time_factor:.2f})")
                
                # Store results
                self.results_queue.put({
                    'callback_time': callback_time,
                    'process_start': process_start,
                    'process_duration': process_duration,
                    'audio_duration': audio_duration,
                    'real_time_factor': real_time_factor
                })
                
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Recognition worker error: {e}")
                traceback.print_exc()
    
    def run_reproduction_test(self, duration: int = 10) -> Dict[str, Any]:
        """Run the overflow reproduction test."""
        self.print_section("MINIMAL OVERFLOW REPRODUCTION")
        
        print(f"🎯 Running reproduction test for {duration} seconds...")
        print("This simulates the exact conditions from the voice typing application")
        
        # Configure audio settings (matching the original application)
        audio_config = {
            'samplerate': 16000,
            'blocksize': 8000,
            'dtype': 'int16',
            'channels': 1
        }
        
        print(f"🎚️  Audio Configuration:")
        for key, value in audio_config.items():
            print(f"   {key}: {value}")
        
        # Reset counters
        self.overflow_count = 0
        self.processing_times = []
        self.active = True
        
        # Clear queues
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.results_queue.empty():
            try:
                self.results_queue.get_nowait()
            except queue.Empty:
                break
        
        # Start recognition worker thread
        worker_thread = threading.Thread(target=self.recognition_worker, daemon=True)
        worker_thread.start()
        
        # Start audio capture
        print("🎤 Starting audio capture...")
        
        try:
            with self.sd.RawInputStream(
                callback=self.audio_callback,
                **audio_config
            ) as stream:
                print(f"🔄 Capturing audio for {duration} seconds...")
                print("   (Speak into microphone or make noise to generate audio)")
                
                start_time = time.time()
                last_report = start_time
                
                while time.time() - start_time < duration:
                    time.sleep(0.5)
                    
                    # Report progress every 2 seconds
                    if time.time() - last_report >= 2.0:
                        elapsed = time.time() - start_time
                        print(f"   Progress: {elapsed:.1f}s - Overflows: {self.overflow_count}, Queue size: {self.audio_queue.qsize()}")
                        last_report = time.time()
                
                print("🛑 Stopping capture...")
                self.active = False
                
        except Exception as e:
            print(f"❌ Audio capture failed: {e}")
            self.active = False
            return {'success': False, 'error': str(e)}
        
        # Wait for processing to complete
        print("⏳ Waiting for processing to complete...")
        time.sleep(2)
        
        # Collect results
        results = []
        while not self.results_queue.empty():
            try:
                result = self.results_queue.get_nowait()
                results.append(result)
            except queue.Empty:
                break
        
        return self.analyze_results(results)
    
    def analyze_results(self, results: list) -> Dict[str, Any]:
        """Analyze the reproduction test results."""
        self.print_section("OVERFLOW REPRODUCTION ANALYSIS")
        
        print(f"📊 Test Results:")
        print(f"   Total overflow events: {self.overflow_count}")
        print(f"   Total audio callbacks: {len(self.processing_times)}")
        print(f"   Total recognition results: {len(results)}")
        print(f"   Audio queue final size: {self.audio_queue.qsize()}")
        
        if self.overflow_count > 0:
            print(f"\n⚠️  OVERFLOW ISSUE REPRODUCED!")
            print(f"   {self.overflow_count} overflow events detected")
            overflow_rate = self.overflow_count / len(self.processing_times) * 100
            print(f"   Overflow rate: {overflow_rate:.1f}%")
        else:
            print(f"\n✅ No overflow events detected")
        
        # Analyze callback performance
        if self.processing_times:
            import statistics
            mean_callback = statistics.mean(self.processing_times)
            max_callback = max(self.processing_times)
            
            print(f"\n🔄 Audio Callback Performance:")
            print(f"   Mean callback time: {mean_callback*1000:.2f}ms")
            print(f"   Max callback time: {max_callback*1000:.2f}ms")
            
            if max_callback > 0.010:  # 10ms threshold
                print(f"   ⚠️  Callbacks taking too long (max: {max_callback*1000:.1f}ms)")
        
        # Analyze recognition performance
        if results:
            import statistics
            
            processing_times = [r['process_duration'] for r in results]
            real_time_factors = [r['real_time_factor'] for r in results]
            
            mean_processing = statistics.mean(processing_times)
            max_processing = max(processing_times)
            mean_rtf = statistics.mean(real_time_factors)
            max_rtf = max(real_time_factors)
            
            print(f"\n🧠 Recognition Performance:")
            print(f"   Mean processing time: {mean_processing*1000:.2f}ms")
            print(f"   Max processing time: {max_processing*1000:.2f}ms")
            print(f"   Mean real-time factor: {mean_rtf:.2f}x")
            print(f"   Max real-time factor: {max_rtf:.2f}x")
            
            slow_processing = sum(1 for rtf in real_time_factors if rtf > 1.0)
            if slow_processing > 0:
                print(f"   ⚠️  {slow_processing}/{len(results)} chunks processed slower than real-time")
        
        # Root cause analysis
        print(f"\n🔍 Root Cause Analysis:")
        
        if self.overflow_count > 0:
            print("   ✅ OVERFLOW ISSUE REPRODUCED")
            
            if results and statistics.mean([r['real_time_factor'] for r in results]) > 1.0:
                print("   📝 Likely cause: Vosk processing too slow")
                print("      Recognition takes longer than audio buffer duration")
            elif self.audio_queue.qsize() > 0:
                print("   📝 Likely cause: Processing thread cannot keep up")
                print("      Audio data backing up in queue")
            else:
                print("   📝 Likely cause: Audio callback blocking")
                print("      Callback spending too much time in processing")
        else:
            print("   ❌ Could not reproduce overflow issue")
            print("   📝 Possible reasons:")
            print("      • Audio input level too low")
            print("      • System not under enough load") 
            print("      • Different audio hardware characteristics")
        
        return {
            'success': True,
            'overflow_reproduced': self.overflow_count > 0,
            'overflow_count': self.overflow_count,
            'total_callbacks': len(self.processing_times),
            'recognition_results': len(results),
            'mean_callback_time': statistics.mean(self.processing_times) if self.processing_times else 0,
            'mean_rtf': statistics.mean([r['real_time_factor'] for r in results]) if results else 0,
            'queue_backup': self.audio_queue.qsize()
        }
    
    def run_complete_reproduction(self) -> Dict[str, Any]:
        """Run complete overflow reproduction test."""
        print("🔍 MINIMAL OVERFLOW REPRODUCTION")
        print("Attempting to reproduce the exact audio overflow conditions...")
        
        if not self.initialize_libraries():
            return {'success': False, 'error': 'Could not initialize required libraries'}
        
        if not self.find_and_load_model():
            return {'success': False, 'error': 'Could not load Vosk model'}
        
        # Run the reproduction test
        return self.run_reproduction_test(duration=10)


def run_debug():
    """Main debug function called by debug runner."""
    reproducer = MinimalOverflowReproducer()
    return reproducer.run_complete_reproduction()


def main():
    """Standalone execution."""
    return run_debug()


if __name__ == '__main__':
    result = main()
    if result['success'] and result.get('overflow_reproduced'):
        print("\n🎯 SUCCESS: Overflow issue reproduced!")
        sys.exit(0)
    elif result['success']:
        print("\n⚠️  Could not reproduce overflow issue")
        sys.exit(0)
    else:
        print(f"\n❌ Test failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)