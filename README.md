# Virtual ECU / Socket Co-Simulation Demo

A small, self-contained demo of the pre-silicon validation pattern used in
production automotive firmware work: **run real firmware against a fully
simulated MCU, and let an external process talk to it over a socket instead
of a physical wire.**

This is a scaled-down, public-target rebuild of an architecture I built
professionally on an Infineon TRAVEO T2G virtual ECU — a QEMU-based platform
with a custom SPI peripheral model (register-level behavior, interrupts,
DMA/FIFO support) and a socket-based backend so the virtual ECU could talk to
external Python hardware simulators, used to validate an AUTOSAR SPI driver
before hardware was available. No proprietary code or configuration is
reused here — this rebuilds the same *technique* from scratch on public
tooling and a public target.

## What it does

1. [Renode](https://renode.io/) (an open-source MCU/SoC simulator) boots a
   real Zephyr RTOS firmware image (a CAN-networking sample) on a simulated
   ST Nucleo-H753ZI board — a real automotive-relevant MCU target, fully
   emulated, no hardware attached.
2. The firmware's CAN controller (`fdcan1`) is wired to a virtual CAN hub
   inside the simulation — the same mechanism used to build multi-node CAN
   networks entirely in software.
3. The firmware's UART is exposed over a **TCP socket**
   (`emulation CreateServerSocketTerminal`), the co-simulation seam.
4. An external Python script (`hardware_simulator.py`) connects to that
   socket like a real HIL test rig would talk to a board over a physical
   UART/SPI link, and streams the firmware's live log output.

See [`sample_run_output.log`](sample_run_output.log) for a captured run: the
Zephyr boot banner, CAN MCAN driver initialization, and periodic CAN frame
transmission, all observed from *outside* the simulation over a plain TCP
socket.

## Why this matters for embedded/automotive teams

Waiting on physical boards or silicon is one of the biggest bottlenecks in
firmware schedules. A virtual ECU environment like this lets driver and
diagnostic software be written, exercised, and partially validated before
hardware exists — and lets test infrastructure (CI, external test rigs,
protocol analyzers) hook into the simulation exactly as it would hook into
real hardware, via a socket instead of a wire.

## Running it

Requirements: [Renode](https://renode.io/) installed, Python 3.

```powershell
# Terminal 1 - start the simulated ECU
"C:\Program Files\Renode\bin\Renode.exe" --disable-gui virtual_ecu_demo.resc

# Terminal 2 - connect the external "hardware simulator"
python hardware_simulator.py 127.0.0.1 3456 15
```

You'll see the Zephyr boot log and periodic CAN frame transmissions stream
into Terminal 2, sent entirely over the TCP socket from the simulated
firmware.

## Files

- `virtual_ecu_demo.resc` — Renode script: loads the firmware, sets up the
  virtual CAN hub, and exposes the UART over a socket.
- `hardware_simulator.py` — the external co-simulation client.
- `sample_run_output.log` — a captured example run.

## Possible extensions

- Attach a second simulated CAN node to the hub and implement a minimal
  UDS diagnostic exchange (ReadDataByIdentifier / DTC read-clear) between
  the two, mirroring real ECU-to-tester diagnostic validation.
- Replace the UART-socket seam with a custom register-level peripheral
  (the SPI-style pattern from the original work) using Renode's C#
  peripheral framework.

---

*Built as a portfolio piece demonstrating pre-silicon validation tooling —
happy to discuss adapting this pattern to your target MCU/RTOS.*
