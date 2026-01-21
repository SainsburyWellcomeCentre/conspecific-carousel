# Conspecific Carousel

![GitHub release](https://img.shields.io/github/v/release/SainsburyWellcomeCentre/conspecific-carousel.svg)

An automated behavioral apparatus for rat social interaction experiments with rotating arena and multiple nose-poke ports.

> **Note:** This system uses Dynamixel servos requiring appropriate power supply (12V recommended). Ensure proper motor calibration before experimental use.

<img src=".img/carousel-overview.png" alt="Conspecific Carousel System" width="800"/>

The Conspecific Carousel is a behavioral testing apparatus designed for rodent social interaction studies. It features a computer-controlled rotating platform (8 positions), automated door mechanism, and three nose-poke ports with beambreak detection, LED cues, and water/reward delivery. The system enables precise control of animal access and position while synchronizing with external recording equipment.

## 🔧 Features

- **8-Position Rotary Table** - Dynamixel servo-driven platform with 45° indexing
- **Automated Door Control** - Dynamixel servo with position feedback for entry/exit control
- **Three Nose Poke Ports** - Individual LED illumination, valve control, and beambreak detection (Ports A, B, C)
- **Camera Synchronization** - BNC outputs for frame-accurate event timing
- **Real-time Event Monitoring** - Async sensor monitoring with immediate event reporting
- **USB Serial Protocol** - Simple hex command interface for integration with experimental control software
- **MicroPython Firmware** - Open-source, easily customizable control system
- **Modular Beambreak Arrays** - Available in L (large) and S (small) configurations

## 🌐 View Online (eCAD)

View the complete electronic design project online via [Altium 365 Viewer](https://sainsburywellcomecentre.github.io/fablabs-documentation/#conspecific-carousel)

## 🚀 Getting Started

### Hardware Assembly

1. **Assemble PCBs** - Order and assemble all five PCBs (main controller + 4 beambreak arrays) using provided fabrication files
2. **Install Motors** - Mount Dynamixel servos for door and table rotation mechanisms
3. **Connect Sensors** - Wire beambreak arrays to nose poke ports and position sensors to door/table
4. **Power Up** - Connect 12V power supply for motors and USB for control/communication

### Firmware Installation

1. **Enter bootloader mode** - Hold BOOTSEL button while connecting USB
2. **Copy firmware** - Transfer all files from `firmware/` folder to the device
3. **Verify** - Device should appear as USB serial port and respond to commands

### Basic Operation

1. **Open serial connection** - Connect at 9600 baud via USB
2. **Send test commands** - Try `0x01` (LED on) or `0x10` (open door)
3. **Monitor events** - Observe ASCII event messages for sensor state changes

<img src=".img/nose-poke-detail.png" alt="Nose Poke Port Assembly" width="300"/>

For detailed assembly instructions, motor calibration, and complete command reference, see [firmware/protocol.md](firmware/protocol.md) and the release notes.

All event messages are sent as newline-terminated ASCII strings. Commands are single-byte hex values sent via serial.

## ⚙️ Configuration & Tuning

### Motor Calibration Guidelines

- **Door Servo** - Adjust open/close position limits in `door.py` to match mechanical stops
- **Table Servo** - Verify 2048 units = 45° rotation; adjust in `table.py` if needed
- **Speed Settings** - Modify movement speed parameters for smooth, quiet operation
- **Torque Limits** - Set appropriate torque limits to prevent mechanical damage

### Sensor Alignment

- **Beambreak Arrays** - Position emitter/receiver boards for reliable nose detection without false triggers
- **Position Sensors** - Mount door and table sensors to trigger at correct mechanical positions
- **Test All Ports** - Verify each nose poke port independently before experiments

  > **Important:** Always test door operation with safety stops engaged before live animal use. Verify servo torque limits are appropriate.

<div align="center">
  <img src=".img/motor-calibration.png" alt="Motor Position Calibration" width="600"/>
</div>

## 💻 Software Requirements

To access the source design files:

- **Altium Designer 20.0** or newer _(for electronic design files)_  
  Academic licenses available via [Altium Education](https://www.altium.com/education)
- **SolidWorks 2020** or newer _(for mechanical design files, if applicable)_  
  Academic licenses via [SolidWorks Education](https://www.solidworks.com/product/students)
- **Python 3.8+** with pyserial _(for host-side communication)_
- **MicroPython** _(firmware runtime on microcontroller)_

## 📜 License

**Sainsbury Wellcome Centre hardware is released under** [Creative Commons Attribution-ShareAlike 4.0 International](http://creativecommons.org/licenses/by-sa/4.0/).

You are free to:

- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose

Under the following terms:

- **Attribution** — Give appropriate credit, link to the license, and indicate changes.
- **ShareAlike** — Distribute your contributions under the same license.
- **No additional restrictions** — Don't apply legal or technological measures that prevent others from doing anything the license permits.

> For the full legal text, see [LICENSE](LICENSE).

## 📚 References _(if applicable)_

If your research uses this apparatus, please cite:

```bibtex
@misc{ConspecificCarousel2026,
  title     = "Conspecific Carousel: Automated Behavioral Apparatus for Rodent Social Interaction",
  author    = "Sainsbury Wellcome Centre",
  year      = "2026",
  publisher = "GitHub",
  url       = "https://github.com/SainsburyWellcomeCentre/conspecific-carousel"
}
```
