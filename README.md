# Reverse Engineered 23FD (Minnow) Microcode Disk

Do you have a weird/obscure early 8" floppy disk containing old microcode for a System 370 Model 135, 145, or IBM 3830 mass storage system? Then read on...


## Documented Minnow Information

* Single-sided
* 33.333kbit/s data transfer rate
* 32 tracks per inch density
* 32 tracks total
* Track width is 0.03125 inches
* Bit density is 1,594 bits per inch
* 8 sectors per track (hard sectored)
* No index hole, but the 8 sector holes are on the outside edge of the disk. Track 0 is pushed pretty far inwards compared with a standard 8" disk.
* No track 0 sensor
* Encoding is FM
* The disk spins at 90 rpm *counterclockwise* (normal 8" disks spin clockwise)

The sector format depends on the device that contains the Minnow drive. 

The System 370 Model 135 was the first to use the Minnow drive. Unfortunately, I do not have any documentation on this format.

The System 370 Model 145 has a format documented on page 336 of the [Processing Unit Theory-Maintenance (October 1971)](http://www.bitsavers.org/pdf/ibm/370/fe/3145/SY24-3581-1_3145_Processing_Unit_Theory-Maintenance_Oct71.pdf). The raw data is placed on the disk very much like asynchronous UART data, with a start bit, data byte, and parity bit.

The 3830 sector format is different, and documented starting on page 99 of the [MLM for the 3830](http://www.bitsavers.org/pdf/ibm/3830/3830-2_MLM_Vol_R02_Mar1976.pdf).

## The Disk

Someone loaned me an original Minnow disk, meant for the System 370 Model 135. The disk label reads as follows:

```
IMPL DISK                 ID 434839001917
MACH 3135  SER NO.  00191 REA     110439
MFG 97 12/14/74           APSS    2603129
PN    2600888  MMT    1815183 MES  GB9205
```

## Collecting the Data

I used an IBM 31SD floppy drive to read the disk but in theory you could use nearly any 8" single-sided drive.

There are several problems that needed to be addressed:

* The index/sector sensor needed to be *relocated* to the outside edge of the disk. Technically the sectors on the disk have enough space in between them that sector marks aren't strictly necessary. I did this by putting the disk in the drive, aligning a sector hole with the opening in the disk envelope, and putting a pin through the hole to make a mark on the inside of the drive chassis. After drilling a hole, I glued a standard T1-3/4 phototransistor into the hole from underneath. I placed a low-profile infrared LED opposing the sensor, and wired both of them into the drive's index sensor circuit, replacing the existing index sensor.

* The head stepper needed to be connected to a half-step drive circuit. Standard drives step at 48 tracks per inch. By stepping 3 half-steps at a time, the motor can be forced to move at 32 tracks per inch.

* Track 0 needed to be located since the Minnow drive has no sensor and the track is in a different location compared with standard 8" disks. I ended up doing this manually.

You might be wondering about the disk rotation speed and data rate. Since these are related, running the 90 rpm disk at the 31SD's 360 rpm meant that the data rate increased to 133.33 kbit/s. This was still close enough to the 31SD's nominal data rate of 250 kbit/s that it was within the bandwidth of the drive's read channel.

The direction-of-rotation issue was solved later, during the analysis phase.

I used a Saleae Logic analyzer to collect the track data in CSV format (included in this repository). In parallel, I also connected an oscilloscope to the raw analog (amplified) head signal. An additional Saleae channel collected the pulses from the sector sensor (formerly the index sensor connection).

To step the drive head, I wrote a quick-and-dirty Arduino program to drive four transistors connected to the 4-phase stepper motor on the 31SD. This program allowed me to half step from the outside edge of the disk until I saw the data from the 0th track. By adjusting the half steps while monitoring the analog read waveform on the oscilloscope, I was able to ensure that the head was centered on the track.

Then, I "reset" and synchronized the program's track counter so I could switch over to the automatic three-half-step mode.

I noticed that my 31SD drive ran around 9% slower than it should have, so the data came back at around 122 kbit/s instead of the predicted rate of 133.33 kbit/s.

The data signal coming from the disk was quite strong with no dropouts. After being decoded by the circuit on the 31SD floppy drive, the data bits classified nearly 100% to either short or long pulses, so I'm confident that these dumps are accurate.

## Analyzing the Data

Data analysis was done using a quick-and-dirty Python program (included in this repository). There are several parts to the program, which function as follows:

1. Parse the input CSV file into a list with the time stamp, data value, and index value.
2. Using a crude PLL, classify the incoming pulses into long and short pulses. This allows the algorithm to account for variations in the disk speed.
3. Reverse the order of the classified pulses. This is because the 31SD drive spins clockwise while the Minnow drive spins counterclockwise.
4. Decode the FM-encoded data back into binary, and attempt to parse sector data according to the IBM documentation for the Model 145.
5. Check each sector byte, which contains the track number, with the physical track number.

The Model 145's disk controller design is quite complex. The disk contains commands which are executed by the disk controller similar to how a CPU executes code. Commands can perform diagnostics of the disk controller itself, checking the parity circuitry and the read circuits to verify that they are working correctly before proceeding.

Unfortunately, the 145's disk format appears to be significantly different from the 135, so I can't use the documentation from the 145 to interpret the data from this disk. There is a chance that the 135 uses a simpler format, but even knowing that fact, the bits will mean very little unless documentation about the 135 surfaces.

This is basically where I stopped. I hope someone finds this useful.

## License Information

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License. To view a copy of this license, visit [http://creativecommons.org/licenses/by-sa/4.0/](http://creativecommons.org/licenses/by-sa/4.0/) or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

