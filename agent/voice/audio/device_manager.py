from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("AURA_OS.AudioDeviceManager")

class AudioDeviceManager:
    def __init__(self):
        self.selected_device: str = "default"
        self.is_connected: bool = True

    def get_input_devices(self) -> List[Dict[str, Any]]:
        """List available microphone input devices."""
        devices = [
            {"id": "default", "name": "System Default Microphone", "is_default": True, "channels": 2, "sample_rate": 44100},
            {"id": "mic_array_01", "name": "Realtek High Definition Audio Mic Array", "is_default": False, "channels": 2, "sample_rate": 48000},
            {"id": "virtual_mic", "name": "AURA Virtual Voice Device", "is_default": False, "channels": 1, "sample_rate": 16000}
        ]
        
        # Try PyAudio if installed
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            pa_devices = []
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0:
                    pa_devices.append({
                        "id": str(i),
                        "name": info.get('name'),
                        "is_default": (i == p.get_default_input_device_info().get('index')),
                        "channels": info.get('maxInputChannels'),
                        "sample_rate": int(info.get('defaultSampleRate', 44100))
                    })
            p.terminate()
            if pa_devices:
                return pa_devices
        except Exception:
            pass

        return devices

    def set_device(self, device_id: str) -> bool:
        devices = [d["id"] for d in self.get_input_devices()]
        if device_id in devices:
            self.selected_device = device_id
            logger.info(f"Microphone device changed to: {device_id}")
            return True
        return False

    def check_health(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self.is_connected else "disconnected",
            "selected_device": self.selected_device,
            "device_count": len(self.get_input_devices())
        }

device_manager = AudioDeviceManager()
