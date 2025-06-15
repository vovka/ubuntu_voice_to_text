#!/usr/bin/env python3
"""
Vosk Performance Analysis Script

This script measures Vosk recognition processing speed, model loading times,
and identifies performance bottlenecks that could cause audio buffer overflows.
"""

import sys
import time
import os
import threading
import json
import statistics
from typing import Dict, List, Tuple, Any, Optional
import tempfile


class VoskPerformanceAnalyzer:
    """Comprehensive Vosk recognition performance analysis."""
    
    def __init__(self):
        self.vosk = None
        self.model = None
        self.recognizer = None
        self.results = {}
        self.sample_rate = 16000
    
    def print_section(self, title: str):
        """Print formatted section header."""
        print(f"\n{'='*60}")
        print(f" {title}")
        print('='*60)
    
    def initialize_vosk(self) -> bool:
        """Initialize Vosk library."""
        try:
            import vosk
            self.vosk = vosk
            print("✅ Vosk library loaded successfully")
            return True
        except ImportError:
            print("❌ Vosk library not available")
            print("   Install with: pip install vosk")
            return False
    
    def find_vosk_models(self) -> List[str]:
        """Find available Vosk models."""
        model_paths = [
            '/usr/share/vosk-models',
            '/opt/vosk-models', 
            os.path.expanduser('~/vosk-models'),
            './models',
            './vosk-models'
        ]
        
        found_models = []
        for base_path in model_paths:
            if os.path.exists(base_path):
                try:
                    for item in os.listdir(base_path):
                        model_path = os.path.join(base_path, item)
                        if os.path.isdir(model_path):
                            # Check if it looks like a Vosk model
                            required_files = ['final.mdl', 'HCLG.fst', 'words.txt']
                            if all(os.path.exists(os.path.join(model_path, f)) for f in required_files):
                                found_models.append(model_path)
                except PermissionError:
                    pass
        
        return found_models
    
    def measure_model_loading_time(self, model_path: str) -> Dict[str, Any]:
        """Measure time to load a Vosk model."""
        print(f"📂 Testing model: {os.path.basename(model_path)}")
        
        try:
            # Measure model loading time
            start_time = time.time()
            model = self.vosk.Model(model_path)
            load_time = time.time() - start_time
            
            # Measure recognizer creation time
            start_time = time.time()
            recognizer = self.vosk.KaldiRecognizer(model, self.sample_rate)
            recognizer_time = time.time() - start_time
            
            total_time = load_time + recognizer_time
            
            print(f"   📊 Model loading: {load_time:.3f}s")
            print(f"   📊 Recognizer creation: {recognizer_time:.3f}s")
            print(f"   📊 Total initialization: {total_time:.3f}s")
            
            # Store for later use
            self.model = model
            self.recognizer = recognizer
            
            return {
                'success': True,
                'model_path': model_path,
                'load_time': load_time,
                'recognizer_time': recognizer_time, 
                'total_time': total_time
            }
            
        except Exception as e:
            print(f"   ❌ Failed to load model: {e}")
            return {
                'success': False,
                'error': str(e),
                'model_path': model_path
            }
    
    def generate_test_audio_data(self, duration_seconds: float = 1.0) -> bytes:
        """Generate test audio data for performance testing."""
        try:
            import numpy as np
            
            # Generate sine wave test audio
            samples = int(self.sample_rate * duration_seconds)
            t = np.linspace(0, duration_seconds, samples, False)
            
            # Mix of frequencies to simulate speech
            frequency1 = 440.0  # A4 note
            frequency2 = 880.0  # A5 note
            wave1 = np.sin(frequency1 * 2 * np.pi * t)
            wave2 = np.sin(frequency2 * 2 * np.pi * t)
            
            # Combine and add some noise
            audio = (wave1 * 0.3 + wave2 * 0.2) * 0.7
            audio += np.random.normal(0, 0.1, samples) * 0.1
            
            # Convert to int16 format
            audio_int16 = (audio * 32767).astype(np.int16)
            
            return audio_int16.tobytes()
            
        except ImportError:
            print("⚠️  NumPy not available - using silent audio")
            # Generate silent audio as fallback
            samples = int(self.sample_rate * duration_seconds)
            return b'\x00\x00' * samples
    
    def measure_recognition_speed(self, test_duration: float = 5.0) -> Dict[str, Any]:
        """Measure Vosk recognition processing speed."""
        if not self.recognizer:
            return {'success': False, 'error': 'No recognizer available'}
        
        print(f"🎯 Testing recognition speed with {test_duration}s of audio...")
        
        # Generate test audio chunks
        chunk_duration = 0.1  # 100ms chunks (typical for real-time)
        chunk_size_bytes = int(self.sample_rate * chunk_duration * 2)  # 2 bytes per sample for int16
        total_chunks = int(test_duration / chunk_duration)
        
        processing_times = []
        chunk_audio = self.generate_test_audio_data(chunk_duration)
        
        print(f"   Chunk size: {len(chunk_audio)} bytes ({chunk_duration*1000:.0f}ms)")
        print(f"   Total chunks: {total_chunks}")
        
        # Process chunks and measure timing
        start_total = time.time()
        
        for i in range(total_chunks):
            start_chunk = time.time()
            
            # This is the actual Vosk processing call
            self.recognizer.AcceptWaveform(chunk_audio)
            
            end_chunk = time.time()
            processing_time = end_chunk - start_chunk
            processing_times.append(processing_time)
            
            if (i + 1) % 10 == 0:  # Progress every 10 chunks
                print(f"   Progress: {i+1}/{total_chunks} chunks, "
                      f"avg processing: {statistics.mean(processing_times[-10:]) * 1000:.2f}ms")
        
        # Get final result
        final_start = time.time()
        final_result = self.recognizer.Result()
        final_time = time.time() - final_start
        
        total_time = time.time() - start_total
        
        # Calculate statistics
        stats = {
            'mean_processing_time': statistics.mean(processing_times),
            'max_processing_time': max(processing_times),
            'min_processing_time': min(processing_times),
            'stdev_processing_time': statistics.stdev(processing_times) if len(processing_times) > 1 else 0,
            'total_processing_time': sum(processing_times),
            'final_result_time': final_time,
            'total_elapsed_time': total_time
        }
        
        print(f"\n📊 Recognition Performance Results:")
        print(f"   Total audio processed: {test_duration:.1f}s")
        print(f"   Total chunks: {len(processing_times)}")
        print(f"   Mean processing time per chunk: {stats['mean_processing_time']*1000:.2f}ms")
        print(f"   Max processing time per chunk: {stats['max_processing_time']*1000:.2f}ms")
        print(f"   Min processing time per chunk: {stats['min_processing_time']*1000:.2f}ms")
        print(f"   Processing time stability: {stats['stdev_processing_time']*1000:.2f}ms stddev")
        print(f"   Final result generation: {stats['final_result_time']*1000:.2f}ms")
        
        # Analyze real-time performance
        expected_chunk_time = chunk_duration
        real_time_factor = stats['mean_processing_time'] / expected_chunk_time
        
        print(f"\n🎯 Real-time Performance Analysis:")
        print(f"   Expected chunk time: {expected_chunk_time*1000:.0f}ms")
        print(f"   Actual processing time: {stats['mean_processing_time']*1000:.2f}ms")
        print(f"   Real-time factor: {real_time_factor:.2f}x")
        
        if real_time_factor <= 1.0:
            print("   ✅ Processing is FASTER than real-time - should not cause overflows")
            recommendation = "PERFORMANCE_OK"
        elif real_time_factor <= 1.5:
            print("   ⚠️  Processing is slower than real-time but may be acceptable")
            recommendation = "MONITOR_PERFORMANCE"
        else:
            print("   ❌ Processing is MUCH slower than real-time - likely causing overflows")
            recommendation = "PERFORMANCE_ISSUE"
        
        # Parse final result
        try:
            result_data = json.loads(final_result)
            recognized_text = result_data.get('text', '')
            print(f"   Recognition result: '{recognized_text}'")
        except:
            print("   Recognition result: (could not parse)")
        
        return {
            'success': True,
            'statistics': stats,
            'real_time_factor': real_time_factor,
            'recommendation': recommendation,
            'chunk_duration': chunk_duration,
            'total_chunks': len(processing_times)
        }
    
    def test_concurrent_processing(self) -> Dict[str, Any]:
        """Test how Vosk performs under concurrent processing load."""
        self.print_section("CONCURRENT PROCESSING TEST")
        
        if not self.recognizer:
            return {'success': False, 'error': 'No recognizer available'}
        
        print("🔄 Testing concurrent audio processing simulation...")
        
        # Simulate multiple audio streams or rapid processing
        test_chunk = self.generate_test_audio_data(0.1)  # 100ms chunk
        
        # Test burst processing (simulating buffer catch-up)
        burst_sizes = [1, 5, 10, 20]  # Number of chunks to process in burst
        burst_results = {}
        
        for burst_size in burst_sizes:
            print(f"\n   Testing burst of {burst_size} chunks...")
            
            processing_times = []
            start_time = time.time()
            
            for i in range(burst_size):
                chunk_start = time.time()
                self.recognizer.AcceptWaveform(test_chunk)
                chunk_end = time.time()
                processing_times.append(chunk_end - chunk_start)
            
            total_time = time.time() - start_time
            mean_time = statistics.mean(processing_times)
            
            print(f"      Total time: {total_time*1000:.2f}ms")
            print(f"      Mean per chunk: {mean_time*1000:.2f}ms")
            print(f"      Throughput: {burst_size/total_time:.1f} chunks/sec")
            
            burst_results[burst_size] = {
                'total_time': total_time,
                'mean_time': mean_time,
                'throughput': burst_size / total_time
            }
        
        return {
            'success': True,
            'burst_results': burst_results
        }
    
    def benchmark_model_comparison(self, model_paths: List[str]) -> Dict[str, Any]:
        """Compare performance across different Vosk models."""
        if len(model_paths) <= 1:
            return {'success': False, 'error': 'Need multiple models for comparison'}
        
        self.print_section("MODEL PERFORMANCE COMPARISON")
        
        model_results = []
        test_audio = self.generate_test_audio_data(2.0)  # 2 seconds of test audio
        
        for model_path in model_paths[:3]:  # Limit to 3 models to avoid long runtime
            print(f"\n🔍 Testing model: {os.path.basename(model_path)}")
            
            try:
                # Load model
                start_time = time.time()
                model = self.vosk.Model(model_path)
                recognizer = self.vosk.KaldiRecognizer(model, self.sample_rate)
                load_time = time.time() - start_time
                
                # Test recognition speed
                start_time = time.time()
                recognizer.AcceptWaveform(test_audio)
                result = recognizer.Result()
                recognition_time = time.time() - start_time
                
                model_results.append({
                    'model_path': model_path,
                    'model_name': os.path.basename(model_path),
                    'load_time': load_time,
                    'recognition_time': recognition_time,
                    'total_time': load_time + recognition_time
                })
                
                print(f"   Load time: {load_time:.3f}s")
                print(f"   Recognition time: {recognition_time:.3f}s")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        if model_results:
            # Find fastest model
            fastest = min(model_results, key=lambda x: x['recognition_time'])
            print(f"\n🏆 Fastest model: {fastest['model_name']}")
            print(f"   Recognition time: {fastest['recognition_time']:.3f}s")
        
        return {
            'success': True,
            'model_results': model_results,
            'fastest_model': fastest['model_name'] if model_results else None
        }
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run complete Vosk performance analysis."""
        print("🔍 VOSK PERFORMANCE ANALYSIS")
        print("Measuring recognition speed and identifying bottlenecks...")
        
        if not self.initialize_vosk():
            return {'success': False, 'error': 'Could not initialize Vosk'}
        
        # Find available models
        model_paths = self.find_vosk_models()
        print(f"\n📂 Found {len(model_paths)} Vosk models:")
        for path in model_paths:
            print(f"   {path}")
        
        if not model_paths:
            print("❌ No Vosk models found!")
            print("💡 Install a model with:")
            print("   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
            print("   unzip vosk-model-small-en-us-0.15.zip")
            return {'success': False, 'error': 'No Vosk models available'}
        
        # Test first available model
        model_path = model_paths[0]
        
        # Phase 1: Model loading performance
        self.print_section("MODEL LOADING PERFORMANCE")
        loading_result = self.measure_model_loading_time(model_path)
        
        if not loading_result['success']:
            return loading_result
        
        # Phase 2: Recognition speed testing
        self.print_section("RECOGNITION SPEED TESTING")
        recognition_result = self.measure_recognition_speed()
        
        # Phase 3: Concurrent processing test
        concurrent_result = self.test_concurrent_processing()
        
        # Phase 4: Model comparison (if multiple models available)
        comparison_result = None
        if len(model_paths) > 1:
            comparison_result = self.benchmark_model_comparison(model_paths)
        
        # Generate summary
        self.print_section("VOSK PERFORMANCE SUMMARY")
        
        print(f"📊 Model: {os.path.basename(model_path)}")
        print(f"   Loading time: {loading_result['total_time']:.3f}s")
        
        if recognition_result['success']:
            rtf = recognition_result['real_time_factor']
            print(f"   Real-time factor: {rtf:.2f}x")
            
            if rtf <= 1.0:
                print("✅ Vosk processing is fast enough for real-time")
                overall_status = "PERFORMANCE_OK"
            else:
                print("⚠️  Vosk processing may be too slow for real-time")
                overall_status = "PERFORMANCE_ISSUE"
                
                print("\n💡 Performance Optimization Suggestions:")
                print("   • Try a smaller/faster Vosk model")
                print("   • Increase audio buffer size to allow more processing time")
                print("   • Use threading to separate audio capture from recognition")
                print("   • Consider using partial results instead of final results")
        else:
            overall_status = "TEST_FAILED"
        
        return {
            'success': True,
            'model_loading': loading_result,
            'recognition_performance': recognition_result,
            'concurrent_processing': concurrent_result,
            'model_comparison': comparison_result,
            'overall_status': overall_status,
            'available_models': len(model_paths)
        }


def run_debug():
    """Main debug function called by debug runner."""
    analyzer = VoskPerformanceAnalyzer()
    return analyzer.run_complete_analysis()


def main():
    """Standalone execution."""
    return run_debug()


if __name__ == '__main__':
    result = main()
    sys.exit(0 if result['success'] else 1)