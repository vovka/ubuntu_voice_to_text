#!/usr/bin/env python3
"""
Audio Configuration Optimization Script

This script tests multiple audio configurations to find optimal settings
that minimize overflow while maintaining good recognition performance.
"""

import sys
import time
import itertools
import statistics
from typing import Dict, List, Tuple, Any, Optional


class AudioConfigOptimizer:
    """Optimize audio configuration to prevent overflow issues."""
    
    def __init__(self):
        self.sd = None
        self.vosk = None
        self.model = None
        self.recognizer = None
        self.test_results = []
    
    def print_section(self, title: str):
        """Print formatted section header."""
        print(f"\n{'='*60}")
        print(f" {title}")
        print('='*60)
    
    def initialize_libraries(self) -> bool:
        """Initialize required libraries."""
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
    
    def load_vosk_model(self) -> bool:
        """Load the first available Vosk model."""
        import os
        
        model_paths = [
            '/usr/share/vosk-models',
            '/opt/vosk-models',
            os.path.expanduser('~/vosk-models'),
            './models', 
            './vosk-models'
        ]
        
        for base_path in model_paths:
            if os.path.exists(base_path):
                try:
                    for item in os.listdir(base_path):
                        model_path = os.path.join(base_path, item)
                        if os.path.isdir(model_path):
                            required_files = ['final.mdl', 'HCLG.fst', 'words.txt']
                            if all(os.path.exists(os.path.join(model_path, f)) for f in required_files):
                                print(f"📖 Loading model: {model_path}")
                                self.model = self.vosk.Model(model_path)
                                self.recognizer = self.vosk.KaldiRecognizer(self.model, 16000)
                                return True
                except PermissionError:
                    continue
        
        print("❌ No Vosk models found")
        return False
    
    def test_configuration(self, config: Dict[str, Any], test_duration: float = 3.0) -> Dict[str, Any]:
        """Test a specific audio configuration."""
        print(f"🧪 Testing: SR={config['sample_rate']}, BS={config['block_size']}, "
              f"CH={config['channels']}, DT={config['dtype']}")
        
        # Configuration validation
        try:
            self.sd.check_input_settings(
                samplerate=config['sample_rate'],
                blocksize=config['block_size'],
                channels=config['channels'],
                dtype=config['dtype']
            )
        except Exception as e:
            return {
                'success': False,
                'error': f'Invalid configuration: {e}',
                'config': config
            }
        
        # Test variables
        overflow_count = 0
        underflow_count = 0
        callback_times = []
        processing_times = []
        
        # Update recognizer for new sample rate if needed
        if hasattr(self, 'recognizer') and self.recognizer:
            if config['sample_rate'] != 16000:
                self.recognizer = self.vosk.KaldiRecognizer(self.model, config['sample_rate'])
        
        def audio_callback(indata, frames, time, status):
            """Audio callback for testing."""
            callback_start = time.time()
            
            nonlocal overflow_count, underflow_count
            
            if status:
                if status.input_overflow:
                    overflow_count += 1
                if status.input_underflow:
                    underflow_count += 1
            
            # Simulate Vosk processing
            if self.recognizer:
                process_start = time.time()
                try:
                    # Convert to bytes and process
                    audio_bytes = bytes(indata)
                    self.recognizer.AcceptWaveform(audio_bytes)
                except Exception:
                    pass  # Ignore processing errors for testing
                process_end = time.time()
                processing_times.append(process_end - process_start)
            
            callback_end = time.time()
            callback_times.append(callback_end - callback_start)
        
        # Run test
        try:
            with self.sd.RawInputStream(
                samplerate=config['sample_rate'],
                blocksize=config['block_size'],
                channels=config['channels'],
                dtype=config['dtype'],
                callback=audio_callback
            ) as stream:
                time.sleep(test_duration)
            
            # Calculate statistics
            expected_callbacks = int(test_duration * config['sample_rate'] / config['block_size'])
            actual_callbacks = len(callback_times)
            
            stats = {
                'expected_callbacks': expected_callbacks,
                'actual_callbacks': actual_callbacks,
                'overflow_count': overflow_count,
                'underflow_count': underflow_count,
                'callback_completion_rate': actual_callbacks / expected_callbacks if expected_callbacks > 0 else 0
            }
            
            if callback_times:
                stats.update({
                    'mean_callback_time': statistics.mean(callback_times),
                    'max_callback_time': max(callback_times),
                    'callback_time_stdev': statistics.stdev(callback_times) if len(callback_times) > 1 else 0
                })
            
            if processing_times:
                stats.update({
                    'mean_processing_time': statistics.mean(processing_times),
                    'max_processing_time': max(processing_times),
                    'processing_time_stdev': statistics.stdev(processing_times) if len(processing_times) > 1 else 0
                })
            
            # Calculate expected vs actual timing
            expected_interval = config['block_size'] / config['sample_rate']
            stats['expected_interval'] = expected_interval
            
            # Score the configuration
            score = self.score_configuration(config, stats)
            
            result = {
                'success': True,
                'config': config,
                'stats': stats,
                'score': score,
                'recommendation': self.get_recommendation(stats)
            }
            
            # Print results
            print(f"   Overflows: {overflow_count}, Callbacks: {actual_callbacks}/{expected_callbacks}")
            if callback_times:
                print(f"   Callback time: {stats['mean_callback_time']*1000:.2f}ms avg, {stats['max_callback_time']*1000:.2f}ms max")
            print(f"   Score: {score:.2f}")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'config': config
            }
    
    def score_configuration(self, config: Dict[str, Any], stats: Dict[str, Any]) -> float:
        """Score a configuration based on performance metrics."""
        score = 100.0  # Start with perfect score
        
        # Penalize overflows heavily
        if stats['overflow_count'] > 0:
            score -= stats['overflow_count'] * 20  # -20 points per overflow
        
        # Penalize underflows
        if stats['underflow_count'] > 0:
            score -= stats['underflow_count'] * 5  # -5 points per underflow
        
        # Penalize low callback completion rate
        completion_rate = stats.get('callback_completion_rate', 0)
        if completion_rate < 0.95:
            score -= (1.0 - completion_rate) * 50  # Up to -50 points
        
        # Penalize very slow callbacks
        if 'mean_callback_time' in stats:
            expected_interval = stats.get('expected_interval', 0.1)
            if stats['mean_callback_time'] > expected_interval * 0.5:
                score -= 30  # -30 points for slow callbacks
        
        # Penalize very slow processing
        if 'mean_processing_time' in stats:
            expected_interval = stats.get('expected_interval', 0.1)
            if stats['mean_processing_time'] > expected_interval:
                score -= 40  # -40 points for processing slower than real-time
        
        # Bonus for larger buffer sizes (more stable)
        if config['block_size'] >= 8192:
            score += 5
        
        # Bonus for standard sample rates
        if config['sample_rate'] in [16000, 22050, 44100]:
            score += 5
        
        return max(0, score)  # Don't go below 0
    
    def get_recommendation(self, stats: Dict[str, Any]) -> str:
        """Generate recommendation based on test results."""
        if stats['overflow_count'] == 0 and stats['underflow_count'] == 0:
            return "EXCELLENT"
        elif stats['overflow_count'] == 0:
            return "GOOD"
        elif stats['overflow_count'] <= 2:
            return "ACCEPTABLE"
        else:
            return "POOR"
    
    def run_configuration_matrix(self) -> Dict[str, Any]:
        """Test multiple configurations and find optimal settings."""
        self.print_section("AUDIO CONFIGURATION MATRIX TESTING")
        
        # Define test configurations
        test_matrix = {
            'sample_rate': [16000, 22050, 44100],
            'block_size': [2048, 4096, 8000, 16000],
            'channels': [1],  # Mono for voice recognition
            'dtype': ['int16', 'float32']
        }
        
        print("🧪 Testing configuration matrix:")
        for key, values in test_matrix.items():
            print(f"   {key}: {values}")
        
        # Generate all combinations
        keys = test_matrix.keys()
        values = test_matrix.values()
        configurations = [dict(zip(keys, combo)) for combo in itertools.product(*values)]
        
        print(f"\n📊 Total configurations to test: {len(configurations)}")
        
        # Test each configuration
        results = []
        for i, config in enumerate(configurations):
            print(f"\n--- Configuration {i+1}/{len(configurations)} ---")
            result = self.test_configuration(config, test_duration=2.0)  # Shorter tests for matrix
            if result['success']:
                results.append(result)
                self.test_results.append(result)
            
            # Brief pause between tests
            time.sleep(0.5)
        
        return {
            'success': True,
            'total_tested': len(results),
            'results': results
        }
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze all test results and provide recommendations."""
        if not self.test_results:
            return {'success': False, 'error': 'No test results to analyze'}
        
        self.print_section("CONFIGURATION ANALYSIS")
        
        # Sort by score
        sorted_results = sorted(self.test_results, key=lambda x: x['score'], reverse=True)
        
        # Find best configurations
        best_configs = sorted_results[:5]  # Top 5
        
        print("🏆 TOP 5 CONFIGURATIONS:")
        print(f"{'Rank':<5} {'Score':<8} {'Sample Rate':<12} {'Block Size':<10} {'Dtype':<10} {'Overflows':<10}")
        print("-" * 70)
        
        for i, result in enumerate(best_configs):
            config = result['config']
            stats = result['stats']
            print(f"{i+1:<5} {result['score']:<8.1f} {config['sample_rate']:<12} "
                  f"{config['block_size']:<10} {config['dtype']:<10} {stats['overflow_count']:<10}")
        
        # Analyze patterns
        print(f"\n📈 PATTERN ANALYSIS:")
        
        # Overflow analysis
        overflow_configs = [r for r in self.test_results if r['stats']['overflow_count'] > 0]
        no_overflow_configs = [r for r in self.test_results if r['stats']['overflow_count'] == 0]
        
        print(f"   Configurations with overflows: {len(overflow_configs)}/{len(self.test_results)}")
        print(f"   Configurations without overflows: {len(no_overflow_configs)}/{len(self.test_results)}")
        
        if no_overflow_configs:
            # Find common characteristics of good configurations
            good_block_sizes = [r['config']['block_size'] for r in no_overflow_configs]
            good_sample_rates = [r['config']['sample_rate'] for r in no_overflow_configs]
            
            print(f"\n💡 SUCCESSFUL CONFIGURATIONS:")
            print(f"   Block sizes: {sorted(set(good_block_sizes))}")
            print(f"   Sample rates: {sorted(set(good_sample_rates))}")
            
            # Most common successful settings
            from collections import Counter
            common_block_size = Counter(good_block_sizes).most_common(1)[0][0]
            common_sample_rate = Counter(good_sample_rates).most_common(1)[0][0]
            
            print(f"   Most successful block size: {common_block_size}")
            print(f"   Most successful sample rate: {common_sample_rate}")
        
        if overflow_configs:
            # Find common characteristics of problematic configurations
            bad_block_sizes = [r['config']['block_size'] for r in overflow_configs]
            bad_sample_rates = [r['config']['sample_rate'] for r in overflow_configs]
            
            print(f"\n⚠️  PROBLEMATIC CONFIGURATIONS:")
            print(f"   Block sizes: {sorted(set(bad_block_sizes))}")
            print(f"   Sample rates: {sorted(set(bad_sample_rates))}")
        
        # Generate final recommendation
        best_config = best_configs[0] if best_configs else None
        
        if best_config:
            config = best_config['config']
            recommendation = {
                'sample_rate': config['sample_rate'],
                'block_size': config['block_size'],
                'channels': config['channels'],
                'dtype': config['dtype'],
                'score': best_config['score'],
                'expected_overflows': best_config['stats']['overflow_count']
            }
            
            print(f"\n🎯 FINAL RECOMMENDATION:")
            print(f"   Sample Rate: {recommendation['sample_rate']} Hz")
            print(f"   Block Size: {recommendation['block_size']} samples")
            print(f"   Channels: {recommendation['channels']}")
            print(f"   Data Type: {recommendation['dtype']}")
            print(f"   Expected Performance Score: {recommendation['score']:.1f}/100")
            
            if recommendation['expected_overflows'] == 0:
                print("   ✅ Should eliminate overflow issues")
            else:
                print(f"   ⚠️  May still have {recommendation['expected_overflows']} overflow events")
        
        return {
            'success': True,
            'best_config': best_config,
            'total_tested': len(self.test_results),
            'successful_configs': len(no_overflow_configs),
            'recommendation': recommendation if best_config else None
        }
    
    def run_complete_optimization(self) -> Dict[str, Any]:
        """Run complete audio configuration optimization."""
        print("🔍 AUDIO CONFIGURATION OPTIMIZATION")
        print("Testing multiple configurations to find optimal settings...")
        
        if not self.initialize_libraries():
            return {'success': False, 'error': 'Could not initialize libraries'}
        
        if not self.load_vosk_model():
            return {'success': False, 'error': 'Could not load Vosk model'}
        
        # Run configuration matrix
        matrix_result = self.run_configuration_matrix()
        if not matrix_result['success']:
            return matrix_result
        
        # Analyze results
        analysis_result = self.analyze_results()
        
        return {
            'success': True,
            'matrix_results': matrix_result,
            'analysis': analysis_result,
            'total_configurations': len(self.test_results)
        }


def run_debug():
    """Main debug function called by debug runner."""
    optimizer = AudioConfigOptimizer()
    return optimizer.run_complete_optimization()


def main():
    """Standalone execution."""
    return run_debug()


if __name__ == '__main__':
    result = main()
    sys.exit(0 if result['success'] else 1)