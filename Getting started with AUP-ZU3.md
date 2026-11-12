# Getting Started with AUP-ZU3

This guide will show you how to set up your computer and AUP-ZU3 board using PYNQ.

Source: https://xilinx.github.io/AUP-ZU3/getting_started.html

---

## Prerequisites

Before getting started, prepare the following:

- AUP-ZU3 board
- Micro SD card
  - 16 GB or more recommended
- 1x USB-C to USB-C cable for power
- Suitable USB-C power source

### For Connection to the Board

Use one of the following:

- 1x USB-C to USB-C cable for USB Gadget connection
- USB Ethernet adapter
- Wi-Fi dongle
  - USB-C type, or
  - USB adapter for connection to the board

### Optional

- USB-C cable for serial terminal access


---

# Setup Instructions

## 1. Prepare a Micro SD Card

Download the **AUP-ZU3 v3.1 PYNQ image**:

http://www.pynq.io/boards.html

Write the downloaded image to a Micro SD card.

---

## 2. Setup the Board
<img width="600" height="559" alt="image" src="https://github.com/user-attachments/assets/37d6b9c0-4bb6-4ec8-a679-501346e5bdb4" /> <br>


1. Set the **BOOT** switch to the **SD** position to boot from the SD card.

2. Insert the Micro SD card that has been pre-loaded with the PYNQ AUP-ZU3 image.

3. Use a USB-C cable to connect the AUP-ZU3 board to your computer.

4. Connect another USB-C cable from the board to a power source.

The power source can be:

- A USB-C power adapter capable of providing:

  **9 V @ 3 A**

- A USB-C port on your laptop or PC.

  Make sure the USB-C port can provide enough power for the board.

---

# PYNQ Boot Sequence

After setting up and powering on the board, you should see the following boot sequence.


## Step 1: Power LEDs

The power LEDs will turn on.

Check that the **ON** LED is illuminated.

You should also see:

- PS LED0 turns on
- PS LED1 turns on
- PS LED1 flashes in a "heartbeat" pattern

The heartbeat pattern indicates that the board is operating and the boot process is in progress.

## Step 2: DONE LED

After approximately:

**30–60 seconds**

the **DONE** LED should turn on.

This is the FPGA `DONE` signal and indicates that a bitstream has been downloaded to the FPGA.

## Step 3: PYNQ Ready Indication

A few seconds later, the PYNQ image will flash:

- 8 white user LEDs
  - LD0–LD7
- 4 RGB LEDs
  - RGB0–RGB3

The RGB LEDs will flash alternating colors.

This indicates that the AUP-ZU3 board is ready.

---

## Troubleshooting

If the board does not boot correctly, refer to the troubleshooting section:

https://xilinx.github.io/AUP-ZU3/support.html#troubleshooting

---

# Connect to the Board

On your computer, open a supported web browser, such as:

- Chrome
- Safari
- Firefox

If you are using the **Ethernet Gadget** connection, browse to:

http://192.168.3.1/lab
This should open the Jupyter login screen.
<img width="645" height="276" alt="image" src="https://github.com/user-attachments/assets/7a9b48df-9e8c-45cb-928e-3316145c3b02" /> <br>



---

## Jupyter Login

Enter the following password:

```text
xilinx
```
This should bring you to the Jupyter home area where you can start to explore your board with the getting started notebooks.
<img width="645" height="444" alt="image" src="https://github.com/user-attachments/assets/6fb61071-508a-4a3e-93d2-cab65e3d0f8d" />
