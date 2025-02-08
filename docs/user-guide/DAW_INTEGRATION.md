# AudioKit DAW Integration Protocol

## Version: 1.0
## Date: [Insert Date]

---

## 1. Message Format
All messages follow this binary format:
```
[4 bytes: message length][N bytes: message payload]
```

## 2. Message Types
| Type Code | Description          | Payload Format                     |
|-----------|----------------------|------------------------------------|
| 0x01      | Audio Data           | Raw audio samples (32-bit float)   |
| 0x02      | MIDI Data            | Standard MIDI message               |
| 0x03      | Control Change       | [2 bytes: param][4 bytes: value]  |
| 0x04      | Status Request       | None                               |
| 0x05      | Status Response      | [1 byte: status][N bytes: info]    |
| 0x06      | Error                | [1 byte: code][N bytes: message]  |

---

## 3. Error Codes
| Code | Description               |
|------|---------------------------|
| 0x01 | Invalid message format    |
| 0x02 | Processing error          |
| 0x03 | Resource limit exceeded   |
| 0x04 | Unsupported operation     |
| 0x05 | Authentication failed     |

---

## 4. Example Message Flow
1. Client connects to Unix domain socket
2. Client sends audio data (Type 0x01)
3. Server processes and returns audio
4. Client can send control changes (Type 0x03)
5. Either side can terminate connection 