# Function Table

## Command Codes

| Code                | Value  | Description                              |
| ------------------- | ------ | ---------------------------------------- |
| LED/Sync On         | `0x01` | Turn sync_out and LED ON                 |
| LED/Sync Off        | `0x02` | Turn sync_out and LED OFF                |
| Table Turn CCW 45   | `0x08` | Turn table 45 degrees counter-clockwise  |
| Table Turn CW 45    | `0x09` | Turn table 45 degrees clockwise          |
| Door Open           | `0x10` | Open the door                            |
| Door Close          | `0x11` | Close the door                           |
| Port A LED On       | `0x21` | Turn on Port A LED                       |
| Port A LED Off      | `0x22` | Turn off Port A LED                      |
| Port A Valve On     | `0x23` | Turn on Port A valve                     |
| Port A Valve Off    | `0x24` | Turn off Port A valve                    |
| Port B LED On       | `0x25` | Turn on Port B LED                       |
| Port B LED Off      | `0x26` | Turn off Port B LED                      |
| Port B Valve On     | `0x27` | Turn on Port B valve                     |
| Port B Valve Off    | `0x28` | Turn off Port B valve                    |
| Port C LED On       | `0x29` | Turn on Port C LED                       |
| Port C LED Off      | `0x2A` | Turn off Port C LED                      |
| Port C Valve On     | `0x2B` | Turn on Port C valve                     |
| Port C Valve Off    | `0x2C` | Turn off Port C valve                    |
| Table Turn CCW 90   | `0x2D` | Turn table 90 degrees counter-clockwise  |
| Table Turn CW 90    | `0x2E` | Turn table 90 degrees clockwise          |
| Table Turn CCW 180  | `0x2F` | Turn table 180 degrees counter-clockwise |
| Table Turn CW 180   | `0x30` | Turn table 180 degrees clockwise         |
| Table Turn CCW 270  | `0x31` | Turn table 270 degrees counter-clockwise |
| Table Turn CW 270   | `0x32` | Turn table 270 degrees clockwise         |
| Door Interlock On   | `0x33` | Enable door interlock                    |
| Door Interlock Off  | `0x34` | Disable door interlock                   |
| Table Interlock On  | `0x35` | Enable table interlock                   |
| Table Interlock Off | `0x36` | Disable table interlock                  |

## Event Messages

| Event Source | Message Format                   | Trigger                    |
| ------------ | -------------------------------- | -------------------------- |
| Door         | `"Door error orcurred"`          | Door error condition       |
| Door         | `"Door paused"`                  | Door status = 3 (paused)   |
| Door         | `"Door moving"`                  | Door status = 2 (moving)   |
| Door         | `"Door opened"`                  | Door status = 1 (opened)   |
| Door         | `"Door closed"`                  | Door status = 0 (closed)   |
| Table        | `"Turn table error door.status"` | Table error condition      |
| Table        | `"Table moving"`                 | Table is moving            |
| Table        | `"Table stopped"`                | Table has stopped          |
| Port A       | `"Port A beambreak cleared"`     | Port A beambreak value = 1 |
| Port A       | `"Port A beambreak triggered"`   | Port A beambreak value = 0 |
| Port B       | `"Port B beambreak cleared"`     | Port B beambreak value = 1 |
| Port B       | `"Port B beambreak triggered"`   | Port B beambreak value = 0 |
| Port C       | `"Port C beambreak cleared"`     | Port C beambreak value = 1 |
| Port C       | `"Port C beambreak triggered"`   | Port C beambreak value = 0 |
| Door Sensor  | `"Door sensor cleared"`          | Door sensor value = 1      |
| Door Sensor  | `"Door sensor triggered"`        | Door sensor value = 0      |
| Table Sensor | `"Table sensor cleared"`         | Table sensor value = 1     |
| Table Sensor | `"Table sensor triggered"`       | Table sensor value = 0     |
| Cam A        | `"Cam A state: {value}"`         | Cam A state change         |
| Cam B        | `"Cam B state: {value}"`         | Cam B state change         |

## Configuration

- TX Buffer Length: 128 bytes
- RX Buffer Length: 128 bytes
