import json
import logging
import asyncio
import threading
from typing import Callable, Dict, Any

class RepatchClient:
    """
    Repatch Python Client SDK (v1.0.0)
    Allows other Python services, agents, or CLI tools to connect to a Repatch 
    server to stream or publish real-time surgical UI mutations.
    """
    def __init__(self, url: str = "ws://localhost:8083/repatch"):
        self.url = url
        self.listeners: list[Callable[[Dict[str, Any]], None]] = []
        self._loop = None
        self._thread = None
        self._ws = None

    def on_patch(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback to be notified when a patch is broadcasted."""
        self.listeners.append(callback)

    def start(self) -> None:
        """Start the WebSocket listener in a background thread."""
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

    def _run_event_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect_and_listen())

    async def _connect_and_listen(self) -> None:
        try:
            import websockets
        except ImportError:
            logging.error("[Repatch SDK] 'websockets' library is required to run Python Client SDK. Please run: pip install websockets")
            return

        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    self._ws = ws
                    logging.info(f"[Repatch SDK] Connected to patch stream at {self.url}")
                    async for message in ws:
                        try:
                            payload = json.loads(message)
                            if "dsl" in payload:
                                dsl = payload["dsl"]
                                self._trigger_listeners({"success": True, "dsl": dsl})
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                logging.warning(f"[Repatch SDK] Connection lost or failed: {e}. Retrying in 3s...")
                await asyncio.sleep(3)

    def _trigger_listeners(self, data: Dict[str, Any]) -> None:
        for cb in self.listeners:
            try:
                cb(data)
            except Exception as e:
                logging.error(f"[Repatch SDK] Listener error: {e}")

    def send_patch(self, dsl: str) -> None:
        """Surgically send a Repatch DSL command to the stream."""
        if self._loop and self._ws:
            asyncio.run_coroutine_threadsafe(
                self._ws.send(json.dumps({"dsl": dsl})), 
                self._loop
            )
        else:
            logging.error("[Repatch SDK] Cannot send patch, client is not started or connected.")
