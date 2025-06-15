#!/usr/bin/env python3
"""
Environment and Setup Verification Script

This script verifies system compatibility and dependencies for the Vosk
voice recognition system. It checks Python version, audio systems,
required packages, and system resources.
"""

import sys
import os
import subprocess
import platform
import importlib
from typing import Dict, List, Tuple, Any


class EnvironmentChecker:
    """System environment verification for Vosk voice recognition."""
    
    def __init__(self):
        self.results = {
            'system': {},
            'python': {},
            'audio': {},
            'dependencies': {},
            'resources': {}
        }
        self.issues = []
        self.warnings = []
    
    def print_section(self, title: str):
        """Print formatted section header."""
        print(f"\n{'='*60}")
        print(f" {title}")
        print('='*60)
    
    def check_item(self, description: str, check_func, critical=True) -> bool:
        """Run a check and display results."""
        try:
            result = check_func()
            if result['success']:
                print(f"✅ {description}: {result['value']}")
                return True
            else:
                print(f"❌ {description}: {result['error']}")
                if critical:
                    self.issues.append(f"{description}: {result['error']}")
                else:
                    self.warnings.append(f"{description}: {result['error']}")
                return False
        except Exception as e:
            print(f"❌ {description}: Exception - {str(e)}")
            if critical:
                self.issues.append(f"{description}: Exception - {str(e)}")
            else:
                self.warnings.append(f"{description}: Exception - {str(e)}")
            return False
    
    def run_command(self, command: str) -> Dict[str, Any]:
        """Run system command and return result."""
        try:
            result = subprocess.run(command, shell=True, 
                                  capture_output=True, text=True, timeout=10)
            return {
                'success': result.returncode == 0,
                'value': result.stdout.strip() if result.returncode == 0 else None,
                'error': result.stderr.strip() if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'value': None, 'error': 'Command timeout'}
        except Exception as e:
            return {'success': False, 'value': None, 'error': str(e)}
    
    def check_system_info(self):
        """Check basic system information."""
        self.print_section("SYSTEM INFORMATION")
        
        def check_os():
            info = platform.uname()
            return {
                'success': True,
                'value': f"{info.system} {info.release} ({info.machine})"
            }
        
        def check_kernel():
            result = self.run_command("uname -r")
            return result if result['success'] else {'success': True, 'value': 'Unknown'}
        
        def check_distro():
            # Try multiple ways to get distro info
            for cmd in ["lsb_release -d", "cat /etc/os-release", "cat /etc/issue"]:
                result = self.run_command(cmd)
                if result['success']:
                    return {'success': True, 'value': result['value'].split('\n')[0]}
            return {'success': True, 'value': 'Unknown Linux distribution'}
        
        self.check_item("Operating System", check_os)
        self.check_item("Kernel Version", check_kernel, critical=False)
        self.check_item("Distribution", check_distro, critical=False)
    
    def check_python_environment(self):
        """Check Python version and environment."""
        self.print_section("PYTHON ENVIRONMENT")
        
        def check_python_version():
            version = sys.version_info
            if version.major == 3 and version.minor >= 8:
                return {'success': True, 'value': f"{version.major}.{version.minor}.{version.micro}"}
            else:
                return {'success': False, 'error': f"Python {version.major}.{version.minor} (requires 3.8+)"}
        
        def check_pip():
            result = self.run_command("pip --version")
            return result
        
        def check_virtual_env():
            venv = os.environ.get('VIRTUAL_ENV')
            if venv:
                return {'success': True, 'value': f"Active: {venv}"}
            else:
                return {'success': True, 'value': "None (using system Python)"}
        
        self.check_item("Python Version", check_python_version)
        self.check_item("Pip Version", check_pip, critical=False)
        self.check_item("Virtual Environment", check_virtual_env, critical=False)
    
    def check_audio_system(self):
        """Check audio system availability."""
        self.print_section("AUDIO SYSTEM")
        
        def check_pulseaudio():
            result = self.run_command("pulseaudio --version")
            return result
        
        def check_alsa():
            result = self.run_command("aplay -l")
            if result['success']:
                devices = len([line for line in result['value'].split('\n') 
                             if 'card' in line.lower()])
                return {'success': True, 'value': f"{devices} audio devices found"}
            return result
        
        def check_recording_devices():
            result = self.run_command("arecord -l")
            if result['success']:
                devices = len([line for line in result['value'].split('\n') 
                             if 'card' in line.lower()])
                return {'success': True, 'value': f"{devices} recording devices found"}
            return result
        
        def check_permissions():
            # Check if user is in audio group
            result = self.run_command("groups")
            if result['success'] and 'audio' in result['value']:
                return {'success': True, 'value': 'User in audio group'}
            else:
                return {'success': False, 'error': 'User not in audio group'}
        
        self.check_item("PulseAudio", check_pulseaudio, critical=False)
        self.check_item("ALSA Playback Devices", check_alsa)
        self.check_item("ALSA Recording Devices", check_recording_devices)
        self.check_item("Audio Permissions", check_permissions, critical=False)
    
    def check_dependencies(self):
        """Check required Python packages."""
        self.print_section("PYTHON DEPENDENCIES")
        
        required_packages = [
            ('vosk', 'Vosk speech recognition'),
            ('sounddevice', 'Audio input/output'),
            ('numpy', 'Numerical computing'),
            ('keyboard', 'Keyboard handling'),
            ('pynput', 'Input control'),
            ('pystray', 'System tray'),
            ('PIL', 'Image processing')
        ]
        
        for package, description in required_packages:
            def check_package(pkg=package, desc=description):
                try:
                    module = importlib.import_module(pkg)
                    version = getattr(module, '__version__', 'unknown')
                    return {'success': True, 'value': f"{desc} v{version}"}
                except ImportError:
                    return {'success': False, 'error': f"{desc} not installed"}
            
            self.check_item(f"{package.capitalize()} Package", check_package)
    
    def check_system_resources(self):
        """Check system resources and performance."""
        self.print_section("SYSTEM RESOURCES")
        
        def check_memory():
            result = self.run_command("free -h")
            if result['success']:
                lines = result['value'].split('\n')
                mem_line = next((line for line in lines if 'Mem:' in line), None)
                if mem_line:
                    parts = mem_line.split()
                    total = parts[1]
                    available = parts[6] if len(parts) > 6 else parts[3]
                    return {'success': True, 'value': f"Total: {total}, Available: {available}"}
            return {'success': False, 'error': 'Could not determine memory info'}
        
        def check_cpu():
            result = self.run_command("nproc")
            if result['success']:
                cores = result['value']
                return {'success': True, 'value': f"{cores} CPU cores"}
            return {'success': False, 'error': 'Could not determine CPU info'}
        
        def check_disk_space():
            result = self.run_command("df -h .")
            if result['success']:
                lines = result['value'].split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    available = parts[3]
                    return {'success': True, 'value': f"{available} available"}
            return {'success': False, 'error': 'Could not check disk space'}
        
        def check_load_average():
            result = self.run_command("uptime")
            if result['success'] and 'load average' in result['value']:
                load_part = result['value'].split('load average:')[1].strip()
                return {'success': True, 'value': f"Load average: {load_part}"}
            return {'success': False, 'error': 'Could not get load average'}
        
        self.check_item("Memory Status", check_memory, critical=False)
        self.check_item("CPU Cores", check_cpu, critical=False)
        self.check_item("Disk Space", check_disk_space, critical=False)
        self.check_item("System Load", check_load_average, critical=False)
    
    def check_vosk_models(self):
        """Check for Vosk models availability."""
        self.print_section("VOSK MODELS")
        
        # Common model paths
        model_paths = [
            '/usr/share/vosk-models',
            '/opt/vosk-models',
            os.path.expanduser('~/vosk-models'),
            './models',
            './vosk-models'
        ]
        
        def check_model_directory():
            found_models = []
            for path in model_paths:
                if os.path.exists(path):
                    try:
                        models = [d for d in os.listdir(path) 
                                if os.path.isdir(os.path.join(path, d))]
                        if models:
                            found_models.extend([(path, models)])
                    except PermissionError:
                        pass
            
            if found_models:
                result = []
                for path, models in found_models:
                    result.append(f"{path}: {', '.join(models)}")
                return {'success': True, 'value': '; '.join(result)}
            else:
                return {'success': False, 'error': 'No Vosk models found in common locations'}
        
        self.check_item("Vosk Model Directories", check_model_directory, critical=False)
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all environment checks."""
        print("🔍 VOSK ENVIRONMENT VERIFICATION")
        print("Checking system compatibility and dependencies...")
        
        self.check_system_info()
        self.check_python_environment()
        self.check_audio_system()
        self.check_dependencies()
        self.check_system_resources()
        self.check_vosk_models()
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate verification summary."""
        self.print_section("VERIFICATION SUMMARY")
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        if total_issues == 0:
            print("🎉 Environment verification PASSED!")
            print("   All critical requirements are met.")
            status = "PASS"
        else:
            print(f"❌ Environment verification FAILED!")
            print(f"   {total_issues} critical issues found.")
            status = "FAIL"
        
        if total_warnings > 0:
            print(f"⚠️  {total_warnings} warnings found.")
        
        if self.issues:
            print("\n🚨 Critical Issues:")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if total_issues > 0:
            print("\n💡 Recommended Actions:")
            if any('python' in issue.lower() for issue in self.issues):
                print("   • Install Python 3.8 or higher")
            if any('audio' in issue.lower() for issue in self.issues):
                print("   • Install audio system packages: sudo apt install pulseaudio alsa-utils")
            if any('not installed' in issue for issue in self.issues):
                print("   • Install missing Python packages: pip install -r requirements.txt")
            if any('audio group' in issue for issue in self.issues):
                print("   • Add user to audio group: sudo usermod -a -G audio $USER")
        
        return {
            'status': status,
            'issues': self.issues,
            'warnings': self.warnings,
            'summary': f"{total_issues} issues, {total_warnings} warnings"
        }


def run_debug():
    """Main debug function called by debug runner."""
    checker = EnvironmentChecker()
    return checker.run_all_checks()


def main():
    """Standalone execution."""
    return run_debug()


if __name__ == '__main__':
    result = main()
    sys.exit(0 if result['status'] == 'PASS' else 1)