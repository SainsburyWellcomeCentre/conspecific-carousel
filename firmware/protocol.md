# Function Table

## Register Map

### System

| Register | Address | Type  | Description                                     |
| -------- | ------- | ----- | ----------------------------------------------- |
| LED/Sync | `0x01`  | `R/W` | `0x00`: off, `0x01`: on — controls sync_out/LED |

### Door

| Register     | Address | Type | Description                                                    |
| ------------ | ------- | ---- | -------------------------------------------------------------- |
| Door Status  | `0x10`  | `R`  | `0x00`: closed, `0x01`: opened, `0x02`: moving, `0x03`: paused |
| Door Command | `0x11`  | `W`  | `0x00`: open, `0x01`: close, `0x02`: stop                      |

### Table

| Register      | Address | Type | Description                                                                  |
| ------------- | ------- | ---- | ---------------------------------------------------------------------------- |
| Table Status  | `0x18`  | `R`  | `0x00`: stopped, `0x01`: moving                                              |
| Table Command | `0x19`  | `W`  | bit 7: direction (`0` = CW, `1` = CCW), bits 0–6: position in 1/8-turn units |

### Side Sensors

| Register     | Address | Type | Description                                         |
| ------------ | ------- | ---- | --------------------------------------------------- |
| Door Sensor  | `0x02`  | `R`  | `0x00`: no object detected, `0x01`: object detected |
| Table Sensor | `0x03`  | `R`  | `0x00`: no object detected, `0x01`: object detected |

### Peripherals — Port A / B / C

| Register         | Port A | Port B | Port C | Type  | Description                                         |
| ---------------- | ------ | ------ | ------ | ----- | --------------------------------------------------- |
| LED Status       | `0x21` | `0x24` | `0x27` | `R/W` | `0x00`: off, `0x01`: on                             |
| Valve Status     | `0x22` | `0x25` | `0x28` | `R/W` | `0x00`: off, `0x01`: on                             |
| IR Sensor Status | `0x23` | `0x26` | `0x29` | `R`   | `0x00`: no object detected, `0x01`: object detected |

### Camera

| Register    | Address | Type | Description         |
| ----------- | ------- | ---- | ------------------- |
| Cam A State | `0x04`  | `R`  | Current Cam A state |
| Cam B State | `0x05`  | `R`  | Current Cam B state |

## TX Protocol (Host → Device)

| Byte 3 | Byte 2   | Byte 1       | Byte 0 |
| ------ | -------- | ------------ | ------ |
| Header | Register | Message Type | Value  |

- **Header**: `0xCC`
- **Register**: Address from the register map
- **Message Type**: `0x01` Write, `0x02` Read
- **Value**: Data to write (ignored for Read)

## RX Protocol (Device → Host)

| Byte 3 | Byte 2   | Byte 1       | Byte 0 |
| ------ | -------- | ------------ | ------ |
| Header | Register | Message Type | Value  |

- **Header**: `0xCC`
- **Register**: Address of the register being reported
- **Message Type**: `0x02` Acknowledgement, `0x03` Event Notification
- **Value**: Current register value

### Event Notifications

Events are sent asynchronously by the device when hardware state changes:

| Source       | Register      | Trigger                     |
| ------------ | ------------- | --------------------------- |
| Door         | `0x10`        | Door status changed         |
| Table        | `0x18`        | Table started/stopped       |
| Port A–C IR  | `0x23`–`0x29` | Beambreak triggered/cleared |
| Door Sensor  | `0x02`        | Door sensor state changed   |
| Table Sensor | `0x03`        | Table sensor state changed  |
| Cam A        | `0x04`        | Cam A state changed         |
| Cam B        | `0x05`        | Cam B state changed         |

## Configuration

- TX Buffer Length: 128 bytes
- RX Buffer Length: 128 bytes
