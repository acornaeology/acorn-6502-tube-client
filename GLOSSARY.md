# Glossary

Terms used in this project's documentation and annotations related to the
Acorn Tube system and the 65C02 second processor.

## Tube system

**Tube** (Tube Interface)
: The communication interface between the BBC Micro host processor and a
second (co-)processor. The Tube ULA (Ferranti custom chip) provides a set
of FIFO registers for bidirectional data transfer between the two processors.

**Host** (Host Processor)
: The 6502A processor in the BBC Micro that manages I/O and communicates
with the second processor over the Tube interface. The host runs the Tube
Host software in MOS ROM.

**Parasite** (Parasite Processor)
: The second processor (in this case a 65C02) that runs user programs.
The parasite relies on the host for all I/O, communicating requests over
the Tube interface.

**Tube Client** (Tube Client ROM)
: The small ROM (2 kB) in the second processor that provides the
operating system environment. It implements the MOS API by forwarding
calls to the host processor over the Tube interface.

## Processor

**65C02** (WDC 65C02)
: The CMOS version of the MOS Technology 6502 processor used in the
Acorn second processor. Adds several instructions and addressing modes
over the original NMOS 6502.

## MOS API

**OSRDCH** (OS Read Character)
: MOS call to read a single character from the current input stream.

**OSWRCH** (OS Write Character)
: MOS call to write a single character to the current output stream.

**OSCLI** (OS Command Line Interpreter)
: MOS call to execute a * command string.

**OSBYTE** (OS Byte)
: MOS call for miscellaneous operations selected by the A register.

**OSWORD** (OS Word)
: MOS call for operations requiring a parameter block, selected by the
A register.

**OSFILE** (OS File)
: MOS call for whole-file operations (load, save, read attributes).

**OSFIND** (OS Find)
: MOS call to open or close a file.

**OSBGET** (OS Byte Get)
: MOS call to read a byte from an open file.

**OSBPUT** (OS Byte Put)
: MOS call to write a byte to an open file.

**OSARGS** (OS Arguments)
: MOS call to read or write an open file's arguments (position, extent).

**OSGBPB** (OS Get/Put Bytes Block)
: MOS call for block transfers to/from an open file.
