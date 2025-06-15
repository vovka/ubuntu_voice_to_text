#!/usr/bin/env python3
"""
Audio Device Analysis Script

This script tests hardware audio capabilities, measures latency,
identifies optimal buffer sizes, and tests for overflow conditions
that may cause the Vosk recognition issues.
"""

import sys
import time
import threading
import statistics
from typing import Dict, List, Tuple, Any, Optional
import numpy as np


class AudioDeviceAnalyzer:
    """Comprehensive audio device analysis and testing."""
    
    def __init__(self):
        self.results = {}
        self.sd = None
        self.test_duration = 5  # seconds for each test
        self.overflow_count = 0
        self.underflow_count = 0
        self.callback_times = []
        self.test_active = False
    
    def print_section(self, title: str):
        """Print formatted section header."""
        print(f"\n{'='*60}")
        print(f" {title}")
        print('='*60)
    
    def initialize_sounddevice(self) -> bool:
        """Initialize sounddevice library."""
        try:
            import sounddevice as sd
            self.sd = sd
            print("✅ SoundDevice library loaded successfully")
            return True
        except ImportError:
            print("❌ SoundDevice library not available")
            print("   Install with: pip install sounddevice")
            return False
    
    def list_audio_devices(self) -> Dict[str, Any]:
        """List and analyze available audio devices."""
        self.print_section("AUDIO DEVICE INVENTORY")
        
        if not self.sd:
            return {'success': False, 'error': 'SoundDevice not available'}
        
        try:
            devices = self.sd.query_devices()
            input_devices = []
            output_devices = []
            
            print(f"📊 Found {len(devices)} audio devices:")
            print()
            
            for i, device in enumerate(devices):
                device_type = []
                if device['max_input_channels'] > 0:
                    device_type.append('INPUT')
                    input_devices.append(i)
                if device['max_output_channels'] > 0:
                    device_type.append('OUTPUT')
                    output_devices.append(i)
                
                default_marker = ""
                if i == self.sd.default.device[0]:
                    default_marker += " [DEFAULT INPUT]"
                if i == self.sd.default.device[1]:
                    default_marker += " [DEFAULT OUTPUT]"
                
                print(f"Device {i}: {device['name']}{default_marker}")
                print(f"   Type: {'/'.join(device_type)}")
                print(f"   Channels: In={device['max_input_channels']}, Out={device['max_output_channels']}")
                print(f"   Sample Rate: {device['default_samplerate']} Hz")
                print(f"   Low Latency: {device['default_low_input_latency']:.3f}s / {device['default_low_output_latency']:.3f}s")
                print(f"   High Latency: {device['default_high_input_latency']:.3f}s / {device['default_high_output_latency']:.3f}s")
                print()
            
            result = {
                'success': True,
                'input_devices': input_devices,
                'output_devices': output_devices,
                'default_input': self.sd.default.device[0],
                'default_output': self.sd.default.device[1],
                'total_devices': len(devices)
            }
            
            print(f"📋 Summary: {len(input_devices)} input devices, {len(output_devices)} output devices")
            return result
            
        except Exception as e:
            print(f"❌ Error querying audio devices: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_device_capabilities(self, device_id: int = None) -> Dict[str, Any]:
        """Test specific device capabilities and optimal settings."""
        if device_id is None:
            device_id = self.sd.default.device[0]
        
        self.print_section(f"TESTING DEVICE {device_id} CAPABILITIES")
        
        try:
            device_info = self.sd.query_devices(device_id)
            print(f"🎤 Testing: {device_info['name']}")
            
            # Test different sample rates
            sample_rates = [8000, 16000, 22050, 44100, 48000]
            supported_rates = []
            
            print("\n📈 Sample Rate Testing:")
            for rate in sample_rates:
                try:
                    self.sd.check_input_settings(device=device_id, samplerate=rate)
                    print(f"   ✅ {rate} Hz - Supported")
                    supported_rates.append(rate)
                except Exception:
                    print(f"   ❌ {rate} Hz - Not supported")
            
            # Test different block sizes
            block_sizes = [512, 1024, 2048, 4096, 8192]
            optimal_blocks = []
            
            print("\n📦 Block Size Testing:")
            for block_size in block_sizes:
                try:
                    # Quick test with minimal recording
                    stream = self.sd.InputStream(
                        device=device_id,
                        channels=1,
                        samplerate=16000,
                        blocksize=block_size,
                        dtype='int16'
                    )
                    stream.start()
                    time.sleep(0.1)
                    stream.stop()
                    stream.close()
                    print(f"   ✅ {block_size} samples - OK")
                    optimal_blocks.append(block_size)
                except Exception as e:
                    print(f"   ❌ {block_size} samples - {str(e)[:50]}")
            
            return {
                'success': True,
                'device_name': device_info['name'],
                'supported_rates': supported_rates,
                'optimal_blocks': optimal_blocks,
                'max_input_channels': device_info['max_input_channels'],
                'default_samplerate': device_info['default_samplerate']
            }
            
        except Exception as e:
            print(f"❌ Device capability test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_audio_callback_performance(self, device_id: int = None, 
                                      sample_rate: int = 16000,
                                      block_size: int = 8000) -> Dict[str, Any]:
        """Test audio callback performance and overflow detection."""
        if device_id is None:
            device_id = self.sd.default.device[0]
        
        self.print_section("AUDIO CALLBACK PERFORMANCE TEST")
        
        print(f"🎯 Testing with:")
        print(f"   Device: {device_id}")
        print(f"   Sample Rate: {sample_rate} Hz")
        print(f"   Block Size: {block_size} samples")
        print(f"   Duration: {self.test_duration} seconds")
        
        # Reset counters
        self.overflow_count = 0
        self.underflow_count = 0
        self.callback_times = []
        self.test_active = True
        
        def audio_callback(indata, frames, time, status):
            """Audio callback that monitors for overflow/underflow."""
            callback_start = time.inputBufferAdcTime
            
            if status:
                if status.input_overflow:
                    self.overflow_count += 1
                if status.input_underflow:
                    self.underflow_count += 1
                
                # This mimics the logging from the actual application
                print(f"[AudioDeviceAnalyzer] Audio callback status: {status}")
            
            # Record callback timing
            if self.test_active:
                self.callback_times.append(callback_start)
            
            # Simulate some processing time (like Vosk would do)
            time.sleep(0.001)  # 1ms processing simulation
        
        try:
            print("🎤 Starting audio capture test...")
            
            stream = self.sd.InputStream(
                device=device_id,
                channels=1,
                samplerate=sample_rate,
                blocksize=block_size,
                dtype='int16',
                callback=audio_callback
            )
            
            stream.start()
            print(f"🔄 Recording for {self.test_duration} seconds...")
            
            # Monitor during test
            start_time = time.time()
            while time.time() - start_time < self.test_duration:
                time.sleep(0.5)
                elapsed = time.time() - start_time
                print(f"   Progress: {elapsed:.1f}s - Overflows: {self.overflow_count}, Underflows: {self.underflow_count}")
            
            self.test_active = False
            stream.stop()
            stream.close()
            
            # Calculate statistics
            callback_intervals = []
            if len(self.callback_times) > 1:
                for i in range(1, len(self.callback_times)):
                    interval = self.callback_times[i] - self.callback_times[i-1]
                    callback_intervals.append(interval)
            
            expected_interval = block_size / sample_rate
            
            result = {
                'success': True,
                'overflow_count': self.overflow_count,
                'underflow_count': self.underflow_count,
                'total_callbacks': len(self.callback_times),
                'expected_interval': expected_interval,
                'actual_intervals': {
                    'mean': statistics.mean(callback_intervals) if callback_intervals else 0,
                    'min': min(callback_intervals) if callback_intervals else 0,
                    'max': max(callback_intervals) if callback_intervals else 0,
                    'stdev': statistics.stdev(callback_intervals) if len(callback_intervals) > 1 else 0
                }
            }
            
            print(f"\n📊 Test Results:")
            print(f"   Total Callbacks: {result['total_callbacks']}")
            print(f"   Overflow Events: {result['overflow_count']}")
            print(f"   Underflow Events: {result['underflow_count']}")
            print(f"   Expected Callback Interval: {expected_interval:.3f}s")
            if callback_intervals:
                print(f"   Actual Interval - Mean: {result['actual_intervals']['mean']:.3f}s")
                print(f"   Actual Interval - Range: {result['actual_intervals']['min']:.3f}s to {result['actual_intervals']['max']:.3f}s")
                print(f"   Timing Stability (StdDev): {result['actual_intervals']['stdev']:.4f}s")
            
            # Determine if this configuration is problematic
            if self.overflow_count > 0:
                print(f"⚠️  OVERFLOW DETECTED: {self.overflow_count} events may indicate buffer issues")
                result['recommendation'] = 'INCREASE_BUFFER_SIZE'
            elif self.underflow_count > 0:
                print(f"⚠️  UNDERFLOW DETECTED: {self.underflow_count} events")
                result['recommendation'] = 'CHECK_SYSTEM_LOAD'
            else:
                print("✅ No overflow/underflow events - configuration looks good")
                result['recommendation'] = 'CONFIGURATION_OK'
            
            return result
            
        except Exception as e:
            print(f"❌ Audio callback test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_multiple_configurations(self) -> Dict[str, Any]:
        """Test multiple audio configurations to find optimal settings."""
        self.print_section("CONFIGURATION MATRIX TESTING")
        
        test_configs = [
            {'sample_rate': 16000, 'block_size': 4096},   # Smaller buffer
            {'sample_rate': 16000, 'block_size': 8000},   # Default
            {'sample_rate': 16000, 'block_size': 16000},  # Larger buffer
            {'sample_rate': 22050, 'block_size': 8000},   # Higher sample rate
            {'sample_rate': 44100, 'block_size': 8000},   # CD quality
        ]
        
        results = []
        print("🧪 Testing multiple configurations to find optimal settings...")
        
        for i, config in enumerate(test_configs):
            print(f"\n--- Configuration {i+1}/{len(test_configs)} ---")
            
            # Shorter tests for matrix testing
            original_duration = self.test_duration
            self.test_duration = 2  # 2 second tests
            
            result = self.test_audio_callback_performance(
                sample_rate=config['sample_rate'],
                block_size=config['block_size']
            )
            
            if result['success']:
                result['config'] = config
                results.append(result)
            
            self.test_duration = original_duration
            time.sleep(1)  # Brief pause between tests
        
        # Analyze results
        best_config = None
        min_overflows = float('inf')
        
        print(f"\n📊 Configuration Comparison:")
        print(f"{'Config':<15} {'Sample Rate':<12} {'Block Size':<10} {'Overflows':<10} {'Underflows':<12} {'Status'}")
        print("-" * 70)
        
        for i, result in enumerate(results):
            config = result['config']
            status = "✅ GOOD" if result['overflow_count'] == 0 else "⚠️  ISSUES"
            
            print(f"{i+1:<15} {config['sample_rate']:<12} {config['block_size']:<10} "
                  f"{result['overflow_count']:<10} {result['underflow_count']:<12} {status}")
            
            if result['overflow_count'] < min_overflows:
                min_overflows = result['overflow_count']
                best_config = config
        
        recommendation = "No optimal configuration found"
        if best_config:
            recommendation = f"Best: {best_config['sample_rate']}Hz, {best_config['block_size']} samples"
        
        print(f"\n💡 Recommendation: {recommendation}")
        
        return {
            'success': True,
            'tested_configs': len(results),
            'best_config': best_config,
            'all_results': results,
            'recommendation': recommendation
        }
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Run complete audio device analysis."""
        print("🔍 AUDIO DEVICE ANALYSIS")
        print("Analyzing hardware capabilities and testing for overflow conditions...")
        
        if not self.initialize_sounddevice():
            return {'success': False, 'error': 'Could not initialize audio system'}
        
        # Phase 1: Device inventory
        device_results = self.list_audio_devices()
        if not device_results['success']:
            return device_results
        
        # Phase 2: Test default device capabilities
        capability_results = self.test_device_capabilities()
        
        # Phase 3: Test callback performance
        performance_results = self.test_audio_callback_performance()
        
        # Phase 4: Configuration matrix testing
        matrix_results = self.test_multiple_configurations()
        
        # Generate summary
        self.print_section("AUDIO ANALYSIS SUMMARY")
        
        total_devices = device_results.get('total_devices', 0)
        input_devices = len(device_results.get('input_devices', []))
        
        print(f"📊 Device Summary: {total_devices} total devices, {input_devices} input capable")
        
        if performance_results['success']:
            if performance_results['overflow_count'] > 0:
                print(f"⚠️  Overflow Issue Detected: {performance_results['overflow_count']} events")
                print("   This indicates the audio buffer cannot keep up with input")
            else:
                print("✅ No overflow issues detected in basic test")
        
        if matrix_results['success'] and matrix_results['best_config']:
            config = matrix_results['best_config']
            print(f"💡 Recommended Configuration: {config['sample_rate']}Hz, {config['block_size']} block size")
        
        return {
            'success': True,
            'devices': device_results,
            'capabilities': capability_results,
            'performance': performance_results,
            'matrix_test': matrix_results,
            'has_overflow_issues': performance_results.get('overflow_count', 0) > 0
        }


def run_debug():
    """Main debug function called by debug runner."""
    analyzer = AudioDeviceAnalyzer()
    return analyzer.run_complete_analysis()


def main():
    """Standalone execution."""
    return run_debug()


if __name__ == '__main__':
    result = main()
    sys.exit(0 if result['success'] else 1)