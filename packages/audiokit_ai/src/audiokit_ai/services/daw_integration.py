import asyncio
import struct
from audiokit_ai.core.config import settings
from audiokit_ai.services.exceptions import ProcessingError

class DAWServer:
    # ... existing code ...

    async def _handle_connection(self, reader, writer):
        """Handle incoming DAW connections with error handling"""
        self.connections.add(writer)
        try:
            while True:
                try:
                    # Read message length
                    size_data = await asyncio.wait_for(reader.read(4), timeout=10.0)
                    if not size_data:
                        break
                    size = struct.unpack('!I', size_data)[0]
                    
                    # Validate message size
                    if size > settings.max_daw_message_size:
                        await self._send_error(writer, 0x03, "Message too large")
                        continue
                        
                    # Read message payload
                    message = await asyncio.wait_for(reader.read(size), timeout=10.0)
                    if not message:
                        break
                        
                    # Process message
                    try:
                        processed = await self._process_message(message)
                        writer.write(struct.pack('!I', len(processed)) + processed)
                        await writer.drain()
                    except Exception as e:
                        await self._send_error(writer, 0x02, str(e))
                        
                except asyncio.TimeoutError:
                    await self._send_error(writer, 0x01, "Timeout waiting for data")
                    break
                except struct.error:
                    await self._send_error(writer, 0x01, "Invalid message format")
                    break
                    
        except ConnectionError:
            pass
        finally:
            self.connections.remove(writer)
            writer.close()
            await writer.wait_closed()

    async def _process_message(self, message: bytes) -> bytes:
        """Process incoming DAW message"""
        try:
            message_type = message[0]
            payload = message[1:]
            
            if message_type == 0x01:  # Audio data
                return await self.processor(payload)
            elif message_type == 0x02:  # MIDI data
                return await self._process_midi(payload)
            else:
                raise ValueError(f"Unsupported message type: {message_type}")
        except Exception as e:
            raise ProcessingError(f"Message processing failed: {str(e)}")

    async def _send_error(self, writer, code: int, message: str):
        """Send error message to client"""
        error_msg = struct.pack('!B', 0x06) + struct.pack('!B', code) + message.encode()
        writer.write(struct.pack('!I', len(error_msg)) + error_msg)
        await writer.drain() 