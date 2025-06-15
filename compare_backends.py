#!/usr/bin/env python3
"""
Backend Comparison Script

This script compares the performance of different recognition backends
(Vosk vs Whisper) to determine if the overflow issue is specific to Vosk
or affects all backends.
"""

import sys
import time
import threading
import queue
import statistics
from typing import Dict, List, Any, Optional


class BackendComparator:
    """Compare performance between different recognition backends."""
    
    def __init__(self):
        self.sd = None
        self.backends = {}
        self.test_results = {}
        self.audio_config = {
            'sample_rate': 16000,
            'block_size': 8000,
            'channels': 1,
            'dtype': 'int16'
        }
    
    def print_section(self, title: str):
        """Print formatted section header."""
        print(f"\n{'='*60}")
        print(f" {title}")
        print('='*60)
    
    def initialize_sounddevice(self) -> bool:
        """Initialize SoundDevice library."""
        try:
            import sounddevice as sd
            self.sd = sd
            print("✅ SoundDevice initialized")
            return True
        except ImportError:
            print("❌ SoundDevice not available")
            return False
    
    def initialize_vosk_backend(self) -> bool:
        """Initialize Vosk recognition backend."""
        try:
            import vosk
            import os
            
            # Find a Vosk model
            model_paths = [
                '/usr/share/vosk-models',
                '/opt/vosk-models',
                os.path.expanduser('~/vosk-models'),
                './models',
                './vosk-models'
            ]
            
            model_path = None
            for base_path in model_paths:
                if os.path.exists(base_path):
                    try:
                        for item in os.listdir(base_path):
                            candidate_path = os.path.join(base_path, item)
                            if os.path.isdir(candidate_path):
                                required_files = ['final.mdl', 'HCLG.fst', 'words.txt']
                                if all(os.path.exists(os.path.join(candidate_path, f)) for f in required_files):
                                    model_path = candidate_path
                                    break
                    except PermissionError:
                        continue
                    if model_path:
                        break
            
            if not model_path:
                print("❌ No Vosk models found")
                return False
            
            # Load model
            model = vosk.Model(model_path)
            recognizer = vosk.KaldiRecognizer(model, self.audio_config['sample_rate'])
            
            self.backends['vosk'] = {
                'name': 'Vosk',
                'model': model,
                'recognizer': recognizer,
                'process_func': self.process_vosk_audio
            }
            
            print(f"✅ Vosk backend initialized with model: {os.path.basename(model_path)}")
            return True
            
        except ImportError:
            print("❌ Vosk not available")
            return False
        except Exception as e:
            print(f"❌ Vosk initialization failed: {e}")
            return False
    
    def initialize_whisper_backend(self) -> bool:
        """Initialize Whisper recognition backend."""
        try:
            import openai
            
            # Check if OpenAI API key is available
            import os
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                print("⚠️  OpenAI API key not found - skipping Whisper backend")
                return False
            
            client = openai.OpenAI(api_key=api_key)
            
            self.backends['whisper'] = {
                'name': 'Whisper (OpenAI)',
                'client': client,
                'process_func': self.process_whisper_audio
            }
            
            print("✅ Whisper backend initialized")
            return True
            
        except ImportError:
            print("❌ OpenAI library not available")
            return False
        except Exception as e:
            print(f"❌ Whisper initialization failed: {e}")
            return False
    
    def initialize_mock_backend(self) -> bool:
        """Initialize a mock backend for comparison."""
        self.backends['mock'] = {
            'name': 'Mock (No Processing)',
            'process_func': self.process_mock_audio
        }
        print("✅ Mock backend initialized")
        return True
    
    def process_vosk_audio(self, audio_data: bytes, backend_data: Dict) -> float:
        """Process audio with Vosk backend."""
        start_time = time.time()
        
        recognizer = backend_data['recognizer']
        recognizer.AcceptWaveform(audio_data)
        
        end_time = time.time()
        return end_time - start_time
    
    def process_whisper_audio(self, audio_data: bytes, backend_data: Dict) -> float:
        """Process audio with Whisper backend."""
        start_time = time.time()
        
        # For Whisper, we would typically need to accumulate audio and send chunks
        # This is a simplified version that just measures API latency
        try:
            import tempfile
            import os
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Write WAV header (simplified)
                import struct
                
                # WAV header for 16kHz, 16-bit, mono
                header = struct.pack('<4sI4s4sIHHIIHH4sI',
                    b'RIFF', 36 + len(audio_data), b'WAVE', b'fmt ', 16,
                    1, 1, 16000, 32000, 2, 16, b'data', len(audio_data))
                
                temp_file.write(header)
                temp_file.write(audio_data)
                temp_file.flush()
                
                # Process with Whisper (note: this is expensive for real-time)
                client = backend_data['client']
                with open(temp_file.name, 'rb') as audio_file:
                    client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                
                os.unlink(temp_file.name)
        
        except Exception:
            # If Whisper fails, just simulate processing time
            time.sleep(0.1)  # Simulate network latency
        
        end_time = time.time()
        return end_time - start_time
    
    def process_mock_audio(self, audio_data: bytes, backend_data: Dict) -> float:
        """Process audio with mock backend (no actual processing)."""
        start_time = time.time()
        
        # Simulate minimal processing time
        time.sleep(0.001)  # 1ms
        
        end_time = time.time()
        return end_time - start_time
    
    def test_backend_performance(self, backend_name: str, test_duration: float = 5.0) -> Dict[str, Any]:
        """Test performance of a specific backend."""
        if backend_name not in self.backends:
            return {'success': False, 'error': f'Backend {backend_name} not available'}
        
        backend = self.backends[backend_name]
        print(f"🧪 Testing {backend['name']} backend...")
        
        # Test variables
        overflow_count = 0
        underflow_count = 0
        callback_times = []
        processing_times = []
        audio_queue = queue.Queue()
        
        def audio_callback(indata, frames, time, status):
            """Audio callback for testing."""
            callback_start = time.time()
            
            nonlocal overflow_count, underflow_count
            
            if status:
                if status.input_overflow:
                    overflow_count += 1
                if status.input_underflow:
                    underflow_count += 1
            
            # Queue audio for processing
            audio_bytes = bytes(indata)
            try:
                audio_queue.put_nowait(audio_bytes)
            except queue.Full:
                pass  # Drop frame if queue is full
            
            callback_end = time.time()
            callback_times.append(callback_end - callback_start)
        
        def processing_worker():
            """Worker thread for audio processing."""
            while True:
                try:
                    audio_data = audio_queue.get(timeout=1.0)
                    process_time = backend['process_func'](audio_data, backend)
                    processing_times.append(process_time)
                    audio_queue.task_done()
                except queue.Empty:
                    break
                except Exception as e:
                    print(f"   Processing error: {e}")
                    break
        
        # Start processing worker
        worker_thread = threading.Thread(target=processing_worker, daemon=True)
        worker_thread.start()
        
        # Run audio capture test
        try:
            print(f"   Capturing audio for {test_duration} seconds...")
            
            with self.sd.RawInputStream(
                callback=audio_callback,
                **self.audio_config
            ) as stream:
                time.sleep(test_duration)
            
            # Wait for processing to complete
            time.sleep(1.0)
            
            # Calculate statistics
            expected_callbacks = int(test_duration * self.audio_config['sample_rate'] / self.audio_config['block_size'])
            
            result = {
                'success': True,
                'backend_name': backend_name,
                'backend_display_name': backend['name'],
                'overflow_count': overflow_count,
                'underflow_count': underflow_count,
                'expected_callbacks': expected_callbacks,
                'actual_callbacks': len(callback_times),
                'processed_chunks': len(processing_times),
                'queue_final_size': audio_queue.qsize()
            }
            
            if callback_times:
                result.update({
                    'mean_callback_time': statistics.mean(callback_times),
                    'max_callback_time': max(callback_times),
                    'callback_time_stdev': statistics.stdev(callback_times) if len(callback_times) > 1 else 0
                })
            
            if processing_times:
                result.update({
                    'mean_processing_time': statistics.mean(processing_times),
                    'max_processing_time': max(processing_times),
                    'processing_time_stdev': statistics.stdev(processing_times) if len(processing_times) > 1 else 0
                })
                
                # Calculate real-time performance
                expected_chunk_duration = self.audio_config['block_size'] / self.audio_config['sample_rate']
                real_time_factor = statistics.mean(processing_times) / expected_chunk_duration
                result['real_time_factor'] = real_time_factor
            
            # Print results
            print(f"   Results: {overflow_count} overflows, {len(callback_times)} callbacks, {len(processing_times)} processed")
            if 'mean_processing_time' in result:
                print(f"   Processing: {result['mean_processing_time']*1000:.2f}ms avg, RTF: {result.get('real_time_factor', 0):.2f}x")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def compare_all_backends(self) -> Dict[str, Any]:
        """Compare performance across all available backends."""
        self.print_section("BACKEND PERFORMANCE COMPARISON")
        
        print(f"🎯 Audio Configuration:")
        for key, value in self.audio_config.items():
            print(f"   {key}: {value}")
        
        print(f"\n📊 Available backends: {list(self.backends.keys())}")
        
        results = {}
        for backend_name in self.backends:
            result = self.test_backend_performance(backend_name, test_duration=3.0)
            if result['success']:
                results[backend_name] = result
                self.test_results[backend_name] = result
        
        return {
            'success': True,
            'backend_results': results,
            'tested_backends': len(results)
        }
    
    def analyze_comparison(self) -> Dict[str, Any]:
        """Analyze comparison results and identify problematic backends."""
        if not self.test_results:
            return {'success': False, 'error': 'No test results to analyze'}
        
        self.print_section("BACKEND COMPARISON ANALYSIS")
        
        # Create comparison table
        print(f"📊 BACKEND PERFORMANCE COMPARISON:")
        print(f"{'Backend':<20} {'Overflows':<10} {'Callbacks':<12} {'Processed':<10} {'RTF':<8} {'Status'}")
        print("-" * 75)
        
        overflow_backends = []
        clean_backends = []
        
        for backend_name, result in self.test_results.items():
            backend_display = result['backend_display_name']
            overflows = result['overflow_count']
            callbacks = result['actual_callbacks']
            processed = result['processed_chunks']
            rtf = result.get('real_time_factor', 0)
            
            if overflows > 0:
                status = "❌ HAS OVERFLOWS"
                overflow_backends.append(backend_name)
            else:
                status = "✅ CLEAN"
                clean_backends.append(backend_name)
            
            print(f"{backend_display:<20} {overflows:<10} {callbacks:<12} {processed:<10} {rtf:<8.2f} {status}")
        
        # Analysis
        print(f"\n🔍 ANALYSIS RESULTS:")
        
        if len(overflow_backends) == len(self.test_results):
            print("   ❌ ALL backends show overflow issues")
            print("   📝 Likely cause: System-wide audio configuration or hardware issue")
            root_cause = "SYSTEM_WIDE_ISSUE"
        elif len(overflow_backends) > 0:
            print(f"   ⚠️  {len(overflow_backends)} backend(s) show overflow issues: {', '.join(overflow_backends)}")
            print(f"   ✅ {len(clean_backends)} backend(s) work correctly: {', '.join(clean_backends)}")
            if 'vosk' in overflow_backends:
                print("   📝 Vosk backend specifically affected")
            root_cause = "BACKEND_SPECIFIC_ISSUE"
        else:
            print("   ✅ NO backends show overflow issues")
            print("   📝 Cannot reproduce overflow under current conditions")
            root_cause = "NO_OVERFLOW_DETECTED"
        
        # Performance comparison
        if len(self.test_results) > 1:
            print(f"\n⚡ PERFORMANCE COMPARISON:")
            
            # Sort by real-time factor
            sorted_backends = sorted(
                [(name, result) for name, result in self.test_results.items() if 'real_time_factor' in result],
                key=lambda x: x[1]['real_time_factor']
            )
            
            if sorted_backends:
                print("   Fastest to slowest (real-time factor):")
                for backend_name, result in sorted_backends:
                    rtf = result['real_time_factor']
                    status = "✅ Fast" if rtf <= 1.0 else "⚠️ Slow"
                    print(f"   • {result['backend_display_name']}: {rtf:.2f}x {status}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if root_cause == "SYSTEM_WIDE_ISSUE":
            print("   • Check system audio configuration and hardware")
            print("   • Increase audio buffer sizes globally")
            print("   • Check system load and resource usage")
        elif root_cause == "BACKEND_SPECIFIC_ISSUE":
            if 'vosk' in overflow_backends and clean_backends:
                print("   • Vosk backend has specific performance issues")
                print("   • Consider using alternative backends from clean list")
                print("   • Or optimize Vosk configuration (model size, threading)")
        else:
            print("   • Current test conditions do not reproduce the issue")
            print("   • Try testing under higher system load")
            print("   • Test with different audio input sources")
        
        return {
            'success': True,
            'root_cause': root_cause,
            'overflow_backends': overflow_backends,
            'clean_backends': clean_backends,
            'total_tested': len(self.test_results)
        }
    
    def run_complete_comparison(self) -> Dict[str, Any]:
        """Run complete backend comparison."""
        print("🔍 BACKEND COMPARISON ANALYSIS")
        print("Comparing recognition backends to isolate overflow issues...")
        
        if not self.initialize_sounddevice():
            return {'success': False, 'error': 'Could not initialize audio system'}
        
        # Initialize available backends
        backends_initialized = 0
        
        if self.initialize_vosk_backend():
            backends_initialized += 1
        
        if self.initialize_whisper_backend():
            backends_initialized += 1
        
        if self.initialize_mock_backend():
            backends_initialized += 1
        
        if backends_initialized == 0:
            return {'success': False, 'error': 'No backends could be initialized'}
        
        print(f"✅ Initialized {backends_initialized} backend(s)")
        
        # Run comparison
        comparison_result = self.compare_all_backends()
        if not comparison_result['success']:
            return comparison_result
        
        # Analyze results
        analysis_result = self.analyze_comparison()
        
        return {
            'success': True,
            'comparison': comparison_result,
            'analysis': analysis_result,
            'backends_tested': backends_initialized
        }


def run_debug():
    """Main debug function called by debug runner."""
    comparator = BackendComparator()
    return comparator.run_complete_comparison()


def main():
    """Standalone execution."""
    return run_debug()


if __name__ == '__main__':
    result = main()
    sys.exit(0 if result['success'] else 1)