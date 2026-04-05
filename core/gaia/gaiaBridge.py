from .systemState import SystemState
from .deviceIntegration import DeviceIntegration

class GaiaBridge:
    """The unified interface connecting G CLI to the host device and environment."""
    def __init__(self):
        self.system = SystemState()
        self.device = DeviceIntegration()

    def get_full_context(self) -> str:
        sys_context = self.system.format_snapshot()
        session_context = self.device.load_session_state()
        
        ctx = sys_context + "\n"
        if session_context:
            ctx += f"[Previous Context] Last Objective: {session_context.get('last_objective', 'None')}\n"
            ctx += f"[Previous Context] Last Action: {session_context.get('last_action', 'None')}\n"
        return ctx

    def update_context(self, objective: str, action: str):
        self.device.save_session_state(objective, action)
