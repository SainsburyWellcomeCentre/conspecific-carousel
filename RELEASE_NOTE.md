# Release Notes

**Rat Social Box Extension:** v1.0  
**Beambreak Array L - Emitter:** v1.0  
**Beambreak Array L - Receiver:** v1.0  
**Beambreak Array S - Emitter:** v1.0  
**Beambreak Array S - Receiver:** v1.0  
**Firmware Version:** v1.0

## 🔧 Key Changes

- Initial release of Conspecific Carousel system
- Integrated door control with Dynamixel servo
- Rotary table with 45° indexing (8 positions)
- Three-port nose poke array with beambreak detection
- Camera synchronization outputs
- USB serial communication protocol
- MicroPython-based firmware with async event handling

## 🛠️ Assembly Instructions

### BOM List

Refer to individual PCB assembly files in each eCAD subfolder:

- [Rat Social Box Extension BOM](eCAD/Rat%20Social%20Box%20Extension/)
- [Beambreak Array L - Emitter BOM](eCAD/Beambreak%20Array%20L%20-%20Emmiter/)
- [Beambreak Array L - Receiver BOM](eCAD/Beambreak%20Array%20L%20-%20Receiver/)
- [Beambreak Array S - Emitter BOM](eCAD/Beambreak%20Array%20S%20-%20Emmiter/)
- [Beambreak Array S - Receiver BOM](eCAD/Beambreak%20Array%20S%20-%20Receiver/)

### Get the PCBA

- **PCBA**: Order from [JLCPCB](https://jlcpcb.com/) (includes assembly service). Refer to the Bill of Materials (BOM) in each PCB's Assembly folder for manual assembly.
- **3D Prints**: _(If applicable)_ Print mechanical components using any 3D printing service.

See the [JLCPCB Assembly Tutorial](https://github.com/SainsburyWellcomeCentre/fablabs-documentation/blob/master/jlcpcb_ordering.md) for step-by-step instructions.

### PCB Fabrication Parameters

**Rat Social Box Extension:**

| Parameter                  | Value           |
| -------------------------- | --------------- |
| Layer Count                | 2               |
| Dimensions                 | 100mm x 80mm    |
| Delivery Format            | Panel by JLCPCB |
| PCB Thickness              | 1.6mm           |
| Material Type              | FR4 TG130       |
| Surface Finish             | ENIG            |
| Gold Thickness             | 2U"             |
| Outer Copper Weight        | 1oz             |
| Inner Copper Weight        | N/A             |
| Specify Stackup            | N/A             |
| Impedance Control          | N/A             |
| Via Covering               | Tented          |
| Min via hole size/diameter | 0.3mm           |
| Board Outline Tolerance    | ±0.2mm          |
| Mark on PCB                | Remove Mark     |

**Beambreak Array L - Emitter:**

| Parameter                  | Value           |
| -------------------------- | --------------- |
| Layer Count                | 2               |
| Dimensions                 | 50mm x 20mm     |
| Delivery Format            | Panel by JLCPCB |
| PCB Thickness              | 1.6mm           |
| Material Type              | FR4 TG130       |
| Surface Finish             | ENIG            |
| Gold Thickness             | 2U"             |
| Outer Copper Weight        | 1oz             |
| Inner Copper Weight        | N/A             |
| Specify Stackup            | N/A             |
| Impedance Control          | N/A             |
| Via Covering               | Tented          |
| Min via hole size/diameter | 0.3mm           |
| Board Outline Tolerance    | ±0.2mm          |
| Mark on PCB                | Remove Mark     |

**Beambreak Array L - Receiver:**

| Parameter                  | Value           |
| -------------------------- | --------------- |
| Layer Count                | 2               |
| Dimensions                 | 50mm x 20mm     |
| Delivery Format            | Panel by JLCPCB |
| PCB Thickness              | 1.6mm           |
| Material Type              | FR4 TG130       |
| Surface Finish             | ENIG            |
| Gold Thickness             | 2U"             |
| Outer Copper Weight        | 1oz             |
| Inner Copper Weight        | N/A             |
| Specify Stackup            | N/A             |
| Impedance Control          | N/A             |
| Via Covering               | Tented          |
| Min via hole size/diameter | 0.3mm           |
| Board Outline Tolerance    | ±0.2mm          |
| Mark on PCB                | Remove Mark     |

**Beambreak Array S - Emitter:**

| Parameter                  | Value           |
| -------------------------- | --------------- |
| Layer Count                | 2               |
| Dimensions                 | 30mm x 10mm     |
| Delivery Format            | Panel by JLCPCB |
| PCB Thickness              | 1.6mm           |
| Material Type              | FR4 TG130       |
| Surface Finish             | ENIG            |
| Gold Thickness             | 2U"             |
| Outer Copper Weight        | 1oz             |
| Inner Copper Weight        | N/A             |
| Specify Stackup            | N/A             |
| Impedance Control          | N/A             |
| Via Covering               | Tented          |
| Min via hole size/diameter | 0.3mm           |
| Board Outline Tolerance    | ±0.2mm          |
| Mark on PCB                | Remove Mark     |

**Beambreak Array S - Receiver:**

| Parameter                  | Value           |
| -------------------------- | --------------- |
| Layer Count                | 2               |
| Dimensions                 | 30mm x 10mm     |
| Delivery Format            | Panel by JLCPCB |
| PCB Thickness              | 1.6mm           |
| Material Type              | FR4 TG130       |
| Surface Finish             | ENIG            |
| Gold Thickness             | 2U"             |
| Outer Copper Weight        | 1oz             |
| Inner Copper Weight        | N/A             |
| Specify Stackup            | N/A             |
| Impedance Control          | N/A             |
| Via Covering               | Tented          |
| Min via hole size/diameter | 0.3mm           |
| Board Outline Tolerance    | ±0.2mm          |
| Mark on PCB                | Remove Mark     |

### Assembly & Installation

1. Assemble the Rat Social Box Extension PCB first, as it is the main control board.
2. Connect the Dynamixel servo to the designated header on the Rat Social Box Extension.
3. Assemble the Beambreak Array PCBs next. Ensure correct orientation of the IR emitters and receivers.
4. Connect the Beambreak Arrays to the Rat Social Box Extension using the provided connectors.
5. Install the rotary table onto the Rat Social Box Extension, ensuring it can rotate freely.
6. Attach the camera module to the designated mount, if applicable.
7. Finally, enclose the assembly in the provided casing, ensuring all components are securely fitted.

   Use `drill-template].dxf` or refer to the manual dimensions below:

   <p align="center">
       <img src="./img/[assembly-diagram].png" alt="[Assembly Description]" height="500"/>
   </p>

8. Test the assembly by powering on the Rat Social Box Extension and checking for correct operation of the servo, beambreak arrays, and rotary table.

## ⚙️ Configuration & Tuning _(if applicable)_

- Configure the USB serial settings to match the host computer.
- Calibrate the beambreak arrays by adjusting the sensitivity settings in the firmware.
- Test the camera synchronization output with the connected camera system.

## 🔧 [Configuration/Calibration] Guidelines

- Adjust the Dynamixel servo ID and baud rate in the firmware to match your specific servo model.
- Fine-tune the rotary table indexing by modifying the stepper motor parameters in the firmware.
- Set the correct number of positions (8 for 45° indexing) in the firmware configuration.

<div align="center">
  <img src=".img/[configuration-image].png" alt="[Configuration Description]" width="600"/>
</div>

## 💻 Firmware Upload _(if applicable)_

1. Connect the Rat Social Box Extension to your computer via USB.
2. Put the device in firmware upload mode by connecting the designated boot pins.
3. Use a compatible flashing tool (e.g., `esptool.py` for ESP32) to upload the firmware binary.
4. Monitor the upload process for any errors.
5. Once completed, disconnect and reconnect the device to exit boot mode.

## 📁 Attachement

```bash
├── Rat Social Box Extension.zip                    # Electronic CAD files
│   ├── Assembly/
│   │   ├── BOM.xlsx         # Bill of Materials
│   │   └── pick and place.csv
│   ├── Drawing/
│   │   ├── 2d.dxf          # 2D technical drawings
│   │   └── 3d.step         # 3D models
│   ├── Fabrication/
│   │   ├── Gerber/         # PCB fabrication files
│   │   └── NC Drill/       # Drill files
├── Beambreak Array L - Emitter.zip                    # Electronic CAD files
│   ├── Assembly/
│   │   ├── BOM.xlsx         # Bill of Materials
│   │   └── pick and place.csv
│   ├── Drawing/
│   │   ├── 2d.dxf          # 2D technical drawings
│   │   └── 3d.step         # 3D models
│   ├── Fabrication/
│   │   ├── Gerber/         # PCB fabrication files
│   │   └── NC Drill/       # Drill files
├── Beambreak Array L - Receiver.zip                    # Electronic CAD files
│   ├── Assembly/
│   │   ├── BOM.xlsx         # Bill of Materials
│   │   └── pick and place.csv
│   ├── Drawing/
│   │   ├── 2d.dxf          # 2D technical drawings
│   │   └── 3d.step         # 3D models
│   ├── Fabrication/
│   │   ├── Gerber/         # PCB fabrication files
│   │   └── NC Drill/       # Drill files
├── Beambreak Array S - Emitter.zip                    # Electronic CAD files
│   ├── Assembly/
│   │   ├── BOM.xlsx         # Bill of Materials
│   │   └── pick and place.csv
│   ├── Drawing/
│   │   ├── 2d.dxf          # 2D technical drawings
│   │   └── 3d.step         # 3D models
│   ├── Fabrication/
│   │   ├── Gerber/         # PCB fabrication files
│   │   └── NC Drill/       # Drill files
├── Beambreak Array S - Receiver.zip                    # Electronic CAD files
│   ├── Assembly/
│   │   ├── BOM.xlsx         # Bill of Materials
│   │   └── pick and place.csv
│   ├── Drawing/
│   │   ├── 2d.dxf          # 2D technical drawings
│   │   └── 3d.step         # 3D models
│   ├── Fabrication/
│   │   ├── Gerber/         # PCB fabrication files
│   │   └── NC Drill/       # Drill files
├── 3DP.zip                  # Mechanical CAD files
│   ├── [part1].stl          # 3D printable parts
│   ├── [part2].stl
│   └── [part3].stl
├── Schematic-1.pdf       # Circuit schematic
├── Schematic-2.pdf       # Circuit schematic
├── firmware.[uf2/bin/hex]          # [If applicable] Microcontroller firmware
└── source_code.zip                 # Source design files
```

### `Schematic.pdf`

Contains the complete PCB schematic, drawings, and layer stackup.

### `PCB.zip`

Contains PCB drawings, fabrication outputs, and assembly documentation.

### `3DP.zip`

Contains printable STL models.

### `firmware.[extension]` _(if applicable)_

Contains microcontroller firmware in the appropriate format (.uf2, .bin, .hex, etc.).

### `source_code.zip`

Contains [CAD Software] source files, 3D mechanical designs ([CAD Software]), and firmware source code (C++/MicroPython/Arduino).
