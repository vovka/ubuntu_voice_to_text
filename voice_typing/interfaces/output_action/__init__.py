"""
Output Action Interface Package

Contains all output action related interfaces and implementations.
"""

from .output_type import OutputType
from .output_action_target import OutputActionTarget
from .multi_output_action_target import MultiOutputActionTarget
from .callback_output_action_target import CallbackOutputActionTarget
from .output_dispatcher import OutputDispatcher
from .keyboard_output_action_target import KeyboardOutputActionTarget

__all__ = [
    "OutputType",
    "OutputActionTarget",
    "MultiOutputActionTarget", 
    "CallbackOutputActionTarget",
    "OutputDispatcher",
    "KeyboardOutputActionTarget",
]