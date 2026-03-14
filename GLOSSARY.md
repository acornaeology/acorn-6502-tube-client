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

**Tube ULA**
: The Ferranti custom chip that implements the Tube interface. It
provides four register pairs (R1-R4), each consisting of a status
register and a data register, which handle bidirectional communication
between host and parasite via FIFO buffering.

**Tube R1** (Tube Register 1)
: Used for escape and event notifications from the host. If the received
byte has bit 7 set, it signals an Escape state change; otherwise it
carries event parameters (Y, X, event number).

**Tube R2** (Tube Register 2)
: The main command/response channel. The parasite sends MOS call
commands and parameters to the host via R2, and receives results and
acknowledgement bytes back through R2.

**Tube R3** (Tube Register 3)
: Used for NMI-driven data transfers. Single-byte and double-byte
transfer types read from or write to R3, and 256-byte block transfers
also use R3.

**Tube R4** (Tube Register 4)
: Used for data transfer setup and error reporting. The host signals
transfer requests (types 0-7) or errors via R4. Transfer requests
include the transfer type, address, and sync byte. Errors include an
error number and message string sent via R2.

**Data Transfer Types** (Tube Transfer Types 0-7)
: The Tube protocol defines eight transfer types, selected by a type
byte received via Tube R4. Types 0-1 are single-byte transfers (to and
from the Tube). Types 2-3 are double-byte transfers. Types 4-5 are
release operations. Types 6-7 are 256-byte block transfers. Each type
has a corresponding NMI handler routine and transfer address pointer.

## MOS

**MOS** (Machine Operating System)
: The operating system for the BBC Micro and second processor. Provides
a standard API of system calls (OSWRCH, OSBYTE, etc.) accessed via
fixed entry points in high memory. On the parasite, the Tube Client ROM
implements the MOS API by forwarding calls to the host.

**Supervisor**
: The command prompt mode of the Tube Client. Prints a '*' prompt,
reads a line of input using OSWORD 0, and passes it to OSCLI for
execution. The supervisor loop is the default state when no language
ROM is running.

**Escape** (Escape Flag)
: The mechanism for user interruption of running programs. The host
signals Escape state changes to the parasite via Tube R1. The escape
flag is stored at zero page location &FF; bit 7 set indicates Escape
is active. Programs check the flag or receive it via the carry flag
from OSRDCH.

**Control Block**
: A block of parameters in memory passed to MOS calls such as OSWORD,
OSFILE, and OSGBPB. The caller places parameters at an address and
passes a pointer (typically in X and Y) to the MOS routine. The Tube
Client sends the control block contents to the host and receives
updated values back.

**Language ROM**
: A ROM that provides a programming language environment (such as
BASIC or BCPL). Identified by a ROM header containing a (C) string
and a type byte indicating it is a language suitable for the
processor. The Tube Client enters a language ROM by jumping to its
start address with A=1.

**ROM Header**
: The standard identification block near the start of a sideways ROM.
Contains a copyright string starting with "(C)" and a ROM type byte.
The Tube Client checks for this header when entering code to verify
that the code is a valid language ROM and is suitable for a 6502
processor.

## Processor

**65C02** (WDC 65C02)
: The CMOS version of the MOS Technology 6502 processor used in the
Acorn second processor. Adds several instructions and addressing modes
over the original NMOS 6502.

**Zero Page**
: The first 256 bytes of memory (&00-&FF) on the 6502. Zero page
addresses use shorter instructions and faster addressing modes,
making them valuable workspace. The Tube Client uses zero page
locations &EE-&FF for pointers, accumulators, and flags.

**NMI** (Non-Maskable Interrupt)
: A hardware interrupt that cannot be disabled by the processor.
On the parasite, NMI is used by the Tube system for data transfers.
The NMI vector at &FFFA points to the current transfer handler,
which is patched at runtime to select the appropriate routine for
the active transfer type (0-7).

**IRQ** (Interrupt Request)
: A maskable hardware interrupt. On the parasite, IRQs are generated
by the Tube ULA when data arrives in R1 or R4. The interrupt handler
checks these registers to service escape notifications, event
dispatch, and data transfer setup.

**BRK**
: A 6502 software interrupt instruction used by MOS for error
handling. When executed, the processor pushes the return address
and status register, then vectors through the IRQ vector. The
interrupt handler distinguishes BRK from hardware IRQ by checking
the break flag in the stacked status. The byte following BRK is
the error number, followed by a null-terminated error message.

**Self-Modifying Code**
: A technique where a program modifies its own instruction operands
at runtime. The Tube Client uses this extensively for NMI data
transfer routines, where the target address in LDA/STA instructions
is patched to point to the current transfer location, avoiding the
overhead of indirect addressing.

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

**OSASCI** (OS ASCII)
: MOS entry point that writes a character, converting carriage return
(&0D) to a CR+LF sequence by falling through to OSNEWL. All other
characters are passed directly to OSWRCH.

**OSNEWL** (OS Newline)
: MOS entry point that sends a newline sequence: line feed (&0A)
followed by carriage return (&0D), both via OSWRCH.

**OSWRCR** (OS Write CR)
: MOS entry point that sends a carriage return (&0D) via OSWRCH.

**NVRDCH** (Non-Vectored RDCH)
: MOS entry point that calls the OSRDCH implementation directly,
bypassing the RDCHV indirection vector. Used when the caller needs
to guarantee the default character input behaviour.

**NVWRCH** (Non-Vectored WRCH)
: MOS entry point that calls the OSWRCH implementation directly,
bypassing the WRCHV indirection vector. Used when the caller needs
to guarantee the default character output behaviour.

**RDLINE** (Read Line)
: The OSWORD 0 function, handled specially by the Tube Client rather
than using the generic OSWORD send/receive mechanism. Sends the
control block parameters to the host via Tube R2 with command code
&0A, then receives the input string character by character.

## MOS Vectors

**Vector Table**
: A block of 27 two-byte address entries at &0200-&0235 that provide
indirection for MOS calls and interrupt handling. Each MOS entry point
dispatches through its corresponding vector, allowing programs to
intercept or replace system calls. The table is initialised from a
default table in the ROM at reset.

**BRKV** (BRK Vector)
: The vector at &0202 dispatched when a BRK instruction is executed.
Points to the current error handler. The Tube Client's default error
handler prints the error message and returns to the supervisor prompt.

**IRQ1V** (IRQ1 Vector)
: The vector at &0204 dispatched for the first-level IRQ handler.
The default handler checks Tube R4 and R1 for data transfer requests
and escape/event notifications.

**IRQ2V** (IRQ2 Vector)
: The vector at &0206 dispatched when an IRQ is not claimed by the
IRQ1 handler. Acts as a second-level handler for any additional
interrupt sources.

**EVNTV** (Event Vector)
: The vector at &0220 dispatched when the host sends an event
notification via Tube R1. The default handler is an RTS (no action).
Programs can intercept events by redirecting this vector.

**USERV** (User Vector)
: The vector at &0200 dispatched for OSWORD calls with function
numbers &E0-&FF (user-defined). The default handler in the Tube
Client generates a 'Bad' error.
