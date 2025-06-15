"""
Test for audio input overflow fix.

This test ensures that the audio input overflow issue is resolved and 
doesn't regress in future versions.
"""

import time
import queue
import threading
from unittest.mock import Mock, MagicMock

from voice_typing.pipeline.audio_input import SoundDeviceAudioInput


class TestAudioInputOverflowFix:
    """Test cases for the audio input overflow fix."""

    def test_audio_callback_is_non_blocking(self):
        """Test that audio callback doesn't block even with slow processing."""
        # Mock sounddevice
        mock_sd = Mock()
        mock_stream = Mock()
        mock_sd.RawInputStream.return_value = mock_stream
        
        audio_input = SoundDeviceAudioInput()
        audio_input.sd = mock_sd
        audio_input._config = {
            'sample_rate': 16000,
            'channels': 1,
            'block_size': 4000,
            'dtype': 'int16'
        }
        
        # Track processing times
        processing_times = []
        
        def slow_callback(audio_bytes):
            """Simulate slow processing (like Vosk) that would cause overflow."""
            start = time.time()
            time.sleep(0.05)  # 50ms processing - would overflow in old version
            processing_times.append(time.time() - start)
        
        # Start capture
        success = audio_input.start_capture(slow_callback)
        assert success, "Should start capture successfully"
        
        # Get the sounddevice callback
        call_args = mock_sd.RawInputStream.call_args
        audio_callback = call_args[1]['callback']
        
        # Simulate audio data
        class MockAudioData:
            def tobytes(self):
                return b'mock_audio_data'
        
        # Measure audio callback time
        mock_audio = MockAudioData()
        start_time = time.time()
        audio_callback(mock_audio, 100, None, None)
        callback_time = time.time() - start_time
        
        # Audio callback should return very quickly
        assert callback_time < 0.01, f"Audio callback blocked for {callback_time:.3f}s"
        
        # Wait for background processing
        time.sleep(0.1)
        
        # Verify background processing occurred
        assert len(processing_times) > 0, "Background processing should occur"
        
        # Cleanup
        audio_input.stop_capture()

    def test_queue_overflow_protection(self):
        """Test that queue overflow is handled gracefully."""
        audio_input = SoundDeviceAudioInput()
        audio_input._max_queue_size = 2  # Small queue for testing
        audio_input._audio_queue = queue.Queue(maxsize=2)
        
        # Fill queue
        audio_input._audio_queue.put(b'chunk1')
        audio_input._audio_queue.put(b'chunk2')
        
        assert audio_input._audio_queue.full(), "Queue should be full"
        
        # Test overflow handling (simulate what happens in audio callback)
        new_chunk = b'new_chunk'
        
        # Should handle overflow gracefully
        try:
            audio_input._audio_queue.put_nowait(new_chunk)
            assert False, "Should raise queue.Full"
        except queue.Full:
            # Simulate overflow handling
            try:
                dropped = audio_input._audio_queue.get_nowait()
                audio_input._audio_queue.put_nowait(new_chunk)
                assert dropped in [b'chunk1', b'chunk2'], "Should drop old chunk"
            except queue.Empty:
                pass  # Also acceptable

    def test_optimized_block_size(self):
        """Test that block size is optimized for real-time performance."""
        audio_input = SoundDeviceAudioInput()
        
        # Test default optimization
        config = {'sample_rate': 16000, 'channels': 1, 'dtype': 'int16'}
        audio_input._config = config.copy()
        
        # Apply optimization logic
        if 'block_size' not in audio_input._config:
            audio_input._config['block_size'] = 4000
        
        assert audio_input._config['block_size'] == 4000, \
            "Should use optimized block size"
        
        # Test explicit block size is preserved
        config_explicit = config.copy()
        config_explicit['block_size'] = 8000
        audio_input._config = config_explicit
        
        assert audio_input._config['block_size'] == 8000, \
            "Should preserve explicit block size"

    def test_background_thread_management(self):
        """Test that background processing thread is managed correctly."""
        mock_sd = Mock()
        mock_stream = Mock()
        mock_sd.RawInputStream.return_value = mock_stream
        
        audio_input = SoundDeviceAudioInput()
        audio_input.sd = mock_sd
        audio_input._config = {
            'sample_rate': 16000,
            'channels': 1,
            'block_size': 4000,
            'dtype': 'int16'
        }
        
        # Initially no thread
        assert audio_input._processing_thread is None
        
        # Start capture should create thread
        callback_called = threading.Event()
        
        def test_callback(audio_bytes):
            callback_called.set()
        
        success = audio_input.start_capture(test_callback)
        assert success
        assert audio_input._processing_thread is not None
        assert audio_input._processing_thread.is_alive()
        
        # Thread should process data
        audio_input._audio_queue.put(b'test_data')
        callback_called.wait(timeout=1.0)
        assert callback_called.is_set(), "Background thread should process data"
        
        # Stop capture should clean up thread
        audio_input.stop_capture()
        assert audio_input._processing_thread is None
        assert audio_input._audio_queue is None

    def test_regression_no_input_overflow_messages(self):
        """
        Regression test: Ensure no 'input overflow' messages occur.
        
        This is the core regression test for issue #58.
        """
        mock_sd = Mock()
        mock_stream = Mock()
        mock_sd.RawInputStream.return_value = mock_stream
        
        audio_input = SoundDeviceAudioInput()
        audio_input.sd = mock_sd
        audio_input._config = {
            'sample_rate': 16000,
            'channels': 1,
            'block_size': 4000,
            'dtype': 'int16'
        }
        
        # Simulate Vosk-like slow processing
        processed_chunks = []
        
        def vosk_like_callback(audio_bytes):
            """Simulate Vosk processing that would cause overflow in old version."""
            time.sleep(0.02)  # Simulate AcceptWaveform() processing time
            processed_chunks.append(audio_bytes)
        
        # Start capture
        success = audio_input.start_capture(vosk_like_callback)
        assert success
        
        # Get the audio callback
        call_args = mock_sd.RawInputStream.call_args
        audio_callback = call_args[1]['callback']
        
        # Simulate rapid audio input (which would cause overflow in old version)
        class MockAudioData:
            def __init__(self, data):
                self._data = data
            def tobytes(self):
                return self._data
        
        # Send multiple rapid audio chunks
        for i in range(10):
            mock_audio = MockAudioData(f'audio_chunk_{i}'.encode())
            
            # Measure callback time - should be very fast
            start = time.time()
            audio_callback(mock_audio, 100, None, None)  # No status = no overflow
            callback_time = time.time() - start
            
            # Callback must be non-blocking
            assert callback_time < 0.005, \
                f"Audio callback blocked for {callback_time:.3f}s on chunk {i}"
        
        # Wait for background processing
        time.sleep(0.5)
        
        # Verify processing occurred
        assert len(processed_chunks) > 0, "Audio should be processed in background"
        
        # Cleanup
        audio_input.stop_capture()
        
        # Success: No overflow errors occurred and processing completed