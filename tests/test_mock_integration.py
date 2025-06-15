"""
End-to-end testing example using centralized mocks.

This demonstrates how to use all mock implementations together 
to test complex interactions between system components.
"""

import pytest
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_complete_voice_typing_flow_with_mocks():
    """Test complete voice typing flow using all centralized mocks."""
    from voice_typing.testing import (
        MockAudioInputSource,
        MockVoiceRecognitionSource,
        MockOutputActionTarget,
        MockStateManager
    )
    from voice_typing.interfaces import VoiceTypingState, OutputType
    
    # Create all mock components
    audio_input = MockAudioInputSource()
    recognition = MockVoiceRecognitionSource()
    output_target = MockOutputActionTarget(OutputType.KEYBOARD)
    state_manager = MockStateManager()
    
    # Initialize all components
    assert audio_input.initialize({'sample_rate': 16000}) == True
    assert recognition.initialize({}) == True
    assert output_target.initialize({}) == True
    
    # Set up state listener to track transitions
    state_transitions = []
    def track_transitions(transition):
        state_transitions.append((transition.from_state, transition.to_state))
    
    state_manager.register_state_listener(track_transitions)
    
    # Simulate voice typing workflow
    
    # 1. Start listening
    assert state_manager.set_state(VoiceTypingState.LISTENING) == True
    
    # 2. Start audio capture
    audio_chunks = []
    def audio_callback(chunk: bytes):
        audio_chunks.append(chunk)
        # Feed audio to recognition
        recognition.process_audio_chunk(chunk)
    
    assert audio_input.start_capture(audio_callback) == True
    
    # 3. Simulate receiving audio data
    test_audio_data = [
        b'audio_chunk_1',
        b'audio_chunk_2', 
        b'audio_chunk_3',
        b'audio_chunk_4'  # 4th chunk triggers recognition result
    ]
    
    for chunk in test_audio_data:
        audio_input.simulate_audio_chunk(chunk)
    
    # 4. Check that audio was captured
    assert len(audio_chunks) == 4
    assert audio_chunks == test_audio_data
    
    # 5. Get recognition result
    result = recognition.get_result()
    assert result is not None
    assert result['text'] == 'hello world'  # Default mock result
    assert result['confidence'] == 0.95
    
    # 6. Deliver recognized text to output
    assert output_target.deliver_text(
        result['text'], 
        {'confidence': result['confidence']}
    ) == True
    
    # 7. Verify output was delivered
    delivered = output_target.get_delivered_texts()
    assert len(delivered) == 1
    assert delivered[0][0] == 'hello world'
    assert delivered[0][1]['confidence'] == 0.95
    
    # 8. Transition to processing state
    assert state_manager.set_state(VoiceTypingState.PROCESSING) == True
    
    # 9. Complete processing, return to idle
    assert state_manager.set_state(VoiceTypingState.IDLE) == True
    
    # 10. Stop audio capture
    audio_input.stop_capture()
    assert audio_input.is_capturing() == False
    
    # Verify state transitions were tracked
    expected_transitions = [
        (VoiceTypingState.IDLE, VoiceTypingState.LISTENING),
        (VoiceTypingState.LISTENING, VoiceTypingState.PROCESSING),
        (VoiceTypingState.PROCESSING, VoiceTypingState.IDLE)
    ]
    assert state_transitions == expected_transitions
    
    # Cleanup all components
    audio_input.cleanup()
    recognition.cleanup()
    output_target.cleanup()
    
    # Verify cleanup
    assert len(output_target.get_delivered_texts()) == 0
    assert not audio_input.is_capturing()


def test_mock_customization_and_flexibility():
    """Test that mocks can be customized for specific test scenarios."""
    from voice_typing.testing import MockVoiceRecognitionSource, MockOutputActionTarget
    from voice_typing.interfaces import OutputType
    
    # Test custom recognition results
    recognition = MockVoiceRecognitionSource()
    custom_results = [
        {'text': 'first result', 'confidence': 0.8, 'final': True},
        {'text': 'second result', 'confidence': 0.9, 'final': True},
        {'text': 'third result', 'confidence': 0.7, 'final': False}
    ]
    recognition.set_recognition_results(custom_results)
    recognition.initialize({})
    
    # Process enough chunks to trigger results
    for i in range(4):
        recognition.process_audio_chunk(f'chunk_{i}'.encode())
    
    # Get first custom result
    result1 = recognition.get_result()
    assert result1['text'] == 'first result'
    assert result1['confidence'] == 0.8
    
    # Test direct result injection
    recognition.add_pending_result({'text': 'injected', 'confidence': 1.0, 'final': True})
    result2 = recognition.get_result()
    assert result2['text'] == 'injected'
    
    # Test output target customization
    output = MockOutputActionTarget(OutputType.FILE)
    output.set_supports_formatting(True)
    output.initialize({})
    
    assert output.get_output_type() == OutputType.FILE
    assert output.supports_formatting() == True
    
    # Test delivery and checking
    output.deliver_text("formatted text", {'format': 'markdown'})
    delivered = output.get_delivered_texts()
    assert len(delivered) == 1
    assert delivered[0][1]['format'] == 'markdown'
    
    # Test clear functionality
    output.clear_delivered_texts()
    assert len(output.get_delivered_texts()) == 0


def test_error_condition_handling():
    """Test mock behavior in error conditions."""
    from voice_typing.testing import MockAudioInputSource, MockVoiceRecognitionSource
    
    # Test uninitialized components
    audio_input = MockAudioInputSource()
    
    # Should fail to start capture without initialization
    assert audio_input.start_capture(lambda x: None) == False
    assert audio_input.is_capturing() == False
    
    # Test recognition with no results
    recognition = MockVoiceRecognitionSource()
    recognition.initialize({})
    
    # Process chunks but don't generate enough for a result
    recognition.process_audio_chunk(b'chunk1')
    recognition.process_audio_chunk(b'chunk2')
    
    # Should return None (no result available yet)
    assert recognition.get_result() is None
    
    # Test output target error conditions
    from voice_typing.testing import MockOutputActionTarget
    
    output = MockOutputActionTarget()
    # Don't initialize
    
    # Should fail to deliver without initialization
    assert output.deliver_text("test") == False
    assert len(output.get_delivered_texts()) == 0


if __name__ == "__main__":
    # Run tests manually if called directly
    test_complete_voice_typing_flow_with_mocks()
    test_mock_customization_and_flexibility()
    test_error_condition_handling()
    
    print("✅ All end-to-end mock integration tests passed!")