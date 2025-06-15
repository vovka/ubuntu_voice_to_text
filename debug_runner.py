#!/usr/bin/env python3
"""
Master Debug Runner for Vosk Audio Overflow Investigation

This script provides a comprehensive debugging interface for investigating
the Vosk backend audio input overflow issue. It can run individual debug
phases or execute the complete investigation workflow.

Usage:
    python debug_runner.py --all                    # Run all debug phases
    python debug_runner.py --phase 1                # Run specific phase
    python debug_runner.py --quick                  # Run quick diagnostic
    python debug_runner.py --list                   # List available phases
"""

import argparse
import sys
import os
import importlib.util
from pathlib import Path
from typing import Dict, List, Callable
import traceback


class DebugRunner:
    """Main debug runner coordinating all investigation phases."""
    
    def __init__(self):
        self.phases = {
            1: {
                'name': 'Environment and Setup Verification',
                'script': 'debug_environment.py',
                'description': 'Verify system compatibility and dependencies'
            },
            2: {
                'name': 'Audio Device Analysis',
                'script': 'debug_audio_devices.py', 
                'description': 'Test hardware audio capabilities and overflow rates'
            },
            3: {
                'name': 'Vosk Performance Testing',
                'script': 'debug_vosk_performance.py',
                'description': 'Measure Vosk recognition processing speed'
            },
            4: {
                'name': 'Minimal Overflow Reproduction', 
                'script': 'minimal_overflow_repro.py',
                'description': 'Create minimal reproduction of the overflow issue'
            },
            5: {
                'name': 'Audio Configuration Optimization',
                'script': 'optimize_audio_config.py',
                'description': 'Find optimal audio buffer configurations'
            },
            6: {
                'name': 'Backend Comparison',
                'script': 'compare_backends.py',
                'description': 'Test if issue affects other recognition backends'
            }
        }
        self.results = {}
    
    def print_header(self, title: str):
        """Print formatted section header."""
        print("\n" + "="*80)
        print(f" {title}")
        print("="*80)
    
    def print_phase_header(self, phase_num: int):
        """Print formatted phase header."""
        phase = self.phases[phase_num]
        print(f"\n🔍 Phase {phase_num}: {phase['name']}")
        print(f"📝 {phase['description']}")
        print("-" * 60)
    
    def run_script(self, script_path: str) -> Dict:
        """Execute a debug script and capture results."""
        if not os.path.exists(script_path):
            return {
                'success': False,
                'error': f'Script not found: {script_path}',
                'output': None
            }
        
        try:
            # Import and run the script
            spec = importlib.util.spec_from_file_location("debug_module", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for main function or run_debug function
            if hasattr(module, 'run_debug'):
                result = module.run_debug()
            elif hasattr(module, 'main'):
                result = module.main()
            else:
                return {
                    'success': False,
                    'error': 'No main() or run_debug() function found in script',
                    'output': None
                }
            
            return {
                'success': True,
                'error': None,
                'output': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': traceback.format_exc()
            }
    
    def run_phase(self, phase_num: int) -> bool:
        """Run a specific debug phase."""
        if phase_num not in self.phases:
            print(f"❌ Invalid phase number: {phase_num}")
            return False
        
        phase = self.phases[phase_num]
        self.print_phase_header(phase_num)
        
        script_path = os.path.join(os.path.dirname(__file__), phase['script'])
        result = self.run_script(script_path)
        
        self.results[phase_num] = result
        
        if result['success']:
            print(f"✅ Phase {phase_num} completed successfully")
            if result['output']:
                print(f"📊 Results: {result['output']}")
        else:
            print(f"❌ Phase {phase_num} failed: {result['error']}")
            if result['output']:
                print(f"🔍 Details:\n{result['output']}")
        
        return result['success']
    
    def run_all_phases(self):
        """Run all debug phases in sequence."""
        self.print_header("VOSK AUDIO OVERFLOW - COMPLETE DEBUG INVESTIGATION")
        
        success_count = 0
        for phase_num in sorted(self.phases.keys()):
            if self.run_phase(phase_num):
                success_count += 1
        
        self.print_summary(success_count)
    
    def run_quick_diagnostic(self):
        """Run quick diagnostic covering essential checks."""
        self.print_header("VOSK AUDIO OVERFLOW - QUICK DIAGNOSTIC")
        
        quick_phases = [1, 2, 4]  # Environment, Audio, Minimal Repro
        success_count = 0
        
        for phase_num in quick_phases:
            if self.run_phase(phase_num):
                success_count += 1
        
        self.print_summary(success_count, len(quick_phases))
    
    def print_summary(self, success_count: int, total_count: int = None):
        """Print investigation summary."""
        if total_count is None:
            total_count = len(self.phases)
        
        self.print_header("DEBUG INVESTIGATION SUMMARY")
        
        print(f"📊 Phases completed: {success_count}/{total_count}")
        print(f"🎯 Success rate: {(success_count/total_count)*100:.1f}%")
        
        if success_count == total_count:
            print("🎉 All phases completed successfully!")
        else:
            print("⚠️  Some phases failed - check individual phase results above")
        
        # Print phase-by-phase results
        print("\n📋 Phase Results:")
        for phase_num, result in self.results.items():
            phase = self.phases[phase_num]
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  Phase {phase_num}: {status} - {phase['name']}")
        
        if success_count < total_count:
            print("\n💡 Recommended next steps:")
            print("   1. Review failed phase details above")
            print("   2. Check system requirements and dependencies")
            print("   3. Run individual phases with --phase <number> for detailed analysis")
            print("   4. Check the debug plan document: vosk_overflow_debug_plan.md")
    
    def list_phases(self):
        """List all available debug phases."""
        self.print_header("AVAILABLE DEBUG PHASES")
        
        for phase_num, phase in self.phases.items():
            print(f"Phase {phase_num}: {phase['name']}")
            print(f"  📝 {phase['description']}")
            print(f"  📄 Script: {phase['script']}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Debug runner for Vosk audio overflow investigation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug_runner.py --all         # Run complete investigation
  python debug_runner.py --quick       # Run quick diagnostic
  python debug_runner.py --phase 2     # Run audio device analysis only
  python debug_runner.py --list        # List all available phases
        """
    )
    
    parser.add_argument('--all', action='store_true',
                       help='Run all debug phases')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick diagnostic (phases 1, 2, 4)')
    parser.add_argument('--phase', type=int, metavar='N',
                       help='Run specific phase number')
    parser.add_argument('--list', action='store_true',
                       help='List available phases')
    
    args = parser.parse_args()
    
    runner = DebugRunner()
    
    if args.list:
        runner.list_phases()
    elif args.all:
        runner.run_all_phases()
    elif args.quick:
        runner.run_quick_diagnostic()
    elif args.phase:
        if not runner.run_phase(args.phase):
            sys.exit(1)
    else:
        parser.print_help()
        print("\n💡 Tip: Start with 'python debug_runner.py --quick' for a fast diagnostic")


if __name__ == '__main__':
    main()