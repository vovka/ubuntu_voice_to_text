import queue


class GlobalState:
    q = queue.Queue()
    state = "idle"  # 'idle', 'listening', 'finish_listening'
    icon = None
    current_keys = set()
