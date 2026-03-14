"""Disassembly driver for Acorn 6502 Tube Client 1.10.

Configures py8dis to produce an annotated disassembly of the Tube Client ROM.
Run via: uv run acorn-tube-client-disasm-tool disassemble 1.10

The physical ROM is 4 kB but only the upper 2 kB is mapped into the
65C02 address space at &F800-&FFFF. The lower 2 kB is not used.

This is the external 6502 second processor variant.
"""

import os
import tempfile
from pathlib import Path

from py8dis.commands import *

init(assembler_name="beebasm", lower_case=True)

_script_dirpath = Path(__file__).resolve().parent
_version_dirpath = _script_dirpath.parent
_rom_filepath = os.environ.get(
    "ACORN_TUBE_CLIENT_ROM",
    str(_version_dirpath / "rom" / "tube-6502-client-1.10.rom"),
)
_output_dirpath = Path(os.environ.get(
    "ACORN_TUBE_CLIENT_OUTPUT",
    str(_version_dirpath / "output"),
))

# Extract the upper 2 kB from the 4 kB ROM image
_full_rom = open(_rom_filepath, "rb").read()
_upper_rom = _full_rom[2048:]
_tmp = tempfile.NamedTemporaryFile(suffix=".rom", delete=False)
_tmp.write(_upper_rom)
_tmp.close()

load(0xF800, _tmp.name, "65C02")
os.unlink(_tmp.name)

# =====================================================================
# Tube I/O register constants
# =====================================================================

constant(0xFEF8, "tube_r1_status")
constant(0xFEF9, "tube_r1_data")
constant(0xFEFA, "tube_r2_status")
constant(0xFEFB, "tube_r2_data")
constant(0xFEFC, "tube_r3_status")
constant(0xFEFD, "tube_r3_data")
constant(0xFEFE, "tube_r4_status")
constant(0xFEFF, "tube_r4_data")

# =====================================================================
# Zero page workspace labels
# =====================================================================

label(0x00EE, "current_program")
label(0x00EF, "current_program_hi")
label(0x00F0, "hex_accumulator")
label(0x00F1, "hex_accumulator_hi")
label(0x00F2, "memory_top")
label(0x00F3, "memory_top_hi")
label(0x00F4, "transfer_addr_ptr")
label(0x00F5, "transfer_addr_ptr_hi")
label(0x00F6, "data_transfer_addr")
label(0x00F7, "data_transfer_addr_hi")
label(0x00F8, "string_ptr")
label(0x00F9, "string_ptr_hi")
label(0x00FA, "control_block_ptr")
label(0x00FB, "control_block_ptr_hi")
label(0x00FC, "irq_a_store")
label(0x00FD, "last_error")
label(0x00FE, "last_error_hi")
label(0x00FF, "escape_flag")

# =====================================================================
# MOS vector labels
# =====================================================================

label(0x0100, "low_memory_code")
label(0x0103, "irq_return_addr_lo")
label(0x0104, "irq_return_addr_hi")
label(0x0200, "userv")
label(0x0202, "brkv")
label(0x0203, "brkv_hi")
label(0x0204, "irq1v")
label(0x0206, "irq2v")
label(0x0208, "cliv")
label(0x020A, "bytev")
label(0x020C, "wordv")
label(0x020E, "wrchv")
label(0x0210, "rdchv")
label(0x0212, "filev")
label(0x0214, "argsv")
label(0x0216, "bgetv")
label(0x0218, "bputv")
label(0x021A, "gbpbv")
label(0x021C, "findv")
label(0x0220, "evntv")
label(0x0236, "error_buffer")
label(0x0237, "error_buffer_errnum")

# =====================================================================
# Inline string hook for print_embedded_text
# =====================================================================
# print_embedded_text (&FE98) prints an inline string following the JSR,
# terminated by a byte with bit 7 set. The terminator byte is NOT printed.

hook_subroutine(0xFE98, "print_embedded_text", stringhi_hook)

# =====================================================================
# Entry points
# =====================================================================

entry(0xF800)
entry(0xF859)
entry(0xF860)
entry(0xF88D)
entry(0xF8B5)
entry(0xF945)
entry(0xF962)
entry(0xF96C)
entry(0xF97D)
entry(0xF986)
entry(0xF9B2)
entry(0xF9CA)
entry(0xFA18)
entry(0xFA2E)
entry(0xFA5C)
entry(0xFA73)
entry(0xFAFF)
entry(0xFB77)
entry(0xFBCC)
entry(0xFC0C)
entry(0xFC2A)
entry(0xFC36)
entry(0xFC4A)
entry(0xFC53)
entry(0xFC8E)
entry(0xFCB7)
entry(0xFCE5)
entry(0xFCF0)
entry(0xFD18)
entry(0xFD3F)
entry(0xFD65)
entry(0xFE00)
entry(0xFE11)
entry(0xFE22)
entry(0xFE41)
entry(0xFE80)
entry(0xFEB3)
entry(0xFFB9)
entry(0xFFC8)
entry(0xFFCB)
entry(0xFFCE)
entry(0xFFD1)
entry(0xFFD4)
entry(0xFFD7)
entry(0xFFDA)
entry(0xFFDD)
entry(0xFFE0)
entry(0xFFE3)
entry(0xFFE7)
entry(0xFFEC)
entry(0xFFEE)
entry(0xFFF1)
entry(0xFFF4)
entry(0xFFF7)

# =====================================================================
# Labels
# =====================================================================

label(0xF800, "reset")
label(0xF859, "low_memory_startup_code")
label(0xF860, "startup_banner")
label(0xF88D, "command_prompt")
label(0xF8A7, "command_prompt_escape")
label(0xF8B5, "enter_code")
label(0xF8FA, "enter_raw_code")
label(0xF8FF, "error_not_a_language")
label(0xF922, "error_not_6502_code")
label(0xF945, "error_handler")
label(0xF95D, "rdline_control_block")
label(0xF962, "oswrch_impl")
label(0xF96C, "osrdch_impl")
label(0xF971, "wait_carry_and_byte")
label(0xF975, "wait_for_tube_r2_byte")
label(0xF97D, "null_return")
label(0xF97E, "skip_spaces_step")
label(0xF97F, "skip_spaces")
label(0xF986, "scan_hex")
label(0xF9B2, "send_string")
label(0xF9B6, "send_string_via_ptr")
label(0xF9CA, "oscli_impl")
label(0xFA17, "command_help")
label(0xFA2D, "oscli_send_to_host")
label(0xFA35, "oscli_wait_ack")
label(0xFA3E, "command_go")
label(0xFA5C, "execute_code")
label(0xFA71, "check_oscli_ack")
label(0xFA73, "osbyte_impl")
label(0xFA9C, "osbyte_high")
label(0xFAF0, "osbyte_read_himem")
label(0xFAF4, "osbyte_read_lomem")
label(0xFAF8, "osbyte_read_high_word")
label(0xFAFF, "osword_impl")
label(0xFB77, "rdline")
label(0xFBCC, "osargs_impl")
label(0xFC0C, "osfind_impl")
label(0xFC2A, "osbget_impl")
label(0xFC36, "osbput_impl")
label(0xFC4A, "send_command")
label(0xFC4A, "send_byte_to_tube_r2")
label(0xFC53, "osfile_impl")
label(0xFC8E, "osgbpb_impl")
label(0xFCB7, "unsupported")
label(0xFCBC, "osword_send_lengths")
label(0xFCD0, "osword_recv_lengths")
label(0xFCE5, "interrupt_handler")
label(0xFCF0, "irq1_handler")
label(0xFCFB, "brk_handler")
label(0xFD18, "tube_r1_interrupt")
label(0xFD39, "set_escape_flag")
label(0xFD3F, "tube_r4_interrupt")
label(0xFD65, "data_transfer_setup")
label(0xFDE7, "restore_regs_and_rti")
label(0xFDEC, "transfer_256_bytes_from_tube")
label(0xFE00, "nmi_single_byte_to_tube")
label(0xFE11, "nmi_single_byte_from_tube")
label(0xFE22, "nmi_two_bytes_to_tube")
label(0xFE41, "nmi_two_bytes_from_tube")
label(0xFE60, "transfer_addr_ptr_table")
label(0xFE68, "transfer_addr_ptr_hi_table")
label(0xFE70, "nmi_routine_addr_table")
label(0xFE78, "nmi_routine_addr_hi_table")
label(0xFE80, "wait_for_tube_r1_byte")
label(0xFE98, "print_embedded_text")
label(0xFEB3, "nmi_acknowledge")

label(0xFFB6, "vector_table_info")
label(0xFFB9, "mos_stub_unsupported_1")
label(0xFFBC, "mos_stub_unsupported_2")
label(0xFFBF, "mos_stub_unsupported_3")
label(0xFFC2, "mos_stub_unsupported_4")
label(0xFFC5, "mos_stub_unsupported_5")
label(0xFFC8, "nvrdch")
label(0xFFCB, "nvwrch")
label(0xFFCE, "osfind_entry")
label(0xFFD1, "osgbpb_entry")
label(0xFFD4, "osbput_entry")
label(0xFFD7, "osbget_entry")
label(0xFFDA, "osargs_entry")
label(0xFFDD, "osfile_entry")
label(0xFFE0, "osrdch_entry")
label(0xFFE3, "osasci_entry")
label(0xFFE7, "osnewl_entry")
label(0xFFEC, "oswrcr_entry")
label(0xFFEE, "oswrch_entry")
label(0xFFF1, "osword_entry")
label(0xFFF4, "osbyte_entry")
label(0xFFF7, "oscli_entry")
label(0xFFFA, "nmi_vector")
label(0xFFFC, "reset_vector")
label(0xFFFE, "irq_vector")

label(0xFF80, "default_vector_table")

# NMI self-modifying address labels
label(0xFE03, "nmi0_transfer_addr")
label(0xFE15, "nmi1_transfer_addr")
label(0xFDD7, "nmi6_transfer_addr")
label(0xFDF9, "nmi7_transfer_addr")

# =====================================================================
# Subroutines
# =====================================================================

subroutine(0xF800, "Power-on reset",
    """Initialise the 65C02 parasite processor.

    Copies the ROM contents to RAM, sets up the default MOS
    vectors, clears the escape flag, and jumps via low memory
    to page out the ROM and start the operating system.""")

subroutine(0xF859, "Low memory startup code",
    """Executed from &0100 after being copied from ROM.

    Reads Tube R1 status to page out the ROM, enables
    interrupts, then jumps to display the startup banner.
    On subsequent soft resets, the JMP target at &F85E is
    patched to skip the banner and enter the command prompt
    directly.""")

subroutine(0xF860, "Display startup banner and initialise",
    """Print the startup banner, patch the soft reset entry
    to skip the banner on future resets, then wait for the
    host's acknowledge byte.

    If the acknowledge has bit 7 set, the host is requesting
    code execution; otherwise enters the command prompt.""")

subroutine(0xF88D, "Command prompt loop",
    """The main supervisor command prompt.

    Prints a '*' prompt, reads a line of input using
    OSWORD 0, and passes it to OSCLI for execution.
    Handles Escape by acknowledging it and reporting
    the error.""")

subroutine(0xF8B5, "Enter code at transfer address",
    """Check whether the code at the data transfer address
    has a valid ROM header with a (C) string, and if so
    verify it is a 6502 language ROM.

    Sets the current program and memory top to the
    transfer address, then enters the code with A=1.
    If the header is missing or invalid, enters with A=1
    anyway (raw code entry). Generates an error if the
    ROM type indicates it is not a language or not 6502
    code.""")

subroutine(0xF945, "Error handler",
    """Default BRK handler. Clears the stack, prints the
    error message from the BRK instruction, and returns
    to the command prompt.""")

subroutine(0xF962, "OSWRCH implementation",
    """Send character in A to the host via Tube R1.

    On entry:
      A = character to send
    On exit:
      A preserved""")

subroutine(0xF96C, "OSRDCH implementation",
    """Read a character from the host via the Tube.

    Sends command &00 to the host, then waits for
    a carry byte and the character.

    On exit:
      A = character received
      C = Escape flag""")

subroutine(0xF97F, "Skip spaces in command string",
    """Advance past space characters in the string at
    (string_ptr),Y.

    On entry:
      Y = current offset into string
    On exit:
      A = first non-space character
      Y = offset of that character""")

subroutine(0xF986, "Parse hexadecimal number",
    """Read a hexadecimal number from the string at
    (string_ptr),Y into the hex accumulator at &F0/F1.

    On entry:
      Y = offset into string
    On exit:
      hex_accumulator/hex_accumulator_hi = parsed value
      X = non-zero if any digits were parsed
      Y = offset past last hex digit
      A = first non-hex character""")

subroutine(0xF9B2, "Send string to Tube R2",
    """Send a CR-terminated string to the host via Tube R2.

    On entry:
      X = string address low byte
      Y = string address high byte
    On exit:
      Y restored from string_ptr_hi""")

subroutine(0xF9CA, "OSCLI implementation",
    """Execute a * command. Parses the command to check for
    *GO and *HELP which are handled locally; all other
    commands are forwarded to the host via the Tube.

    On entry:
      X = command string address low byte
      Y = command string address high byte""")

subroutine(0xFA17, "Handle *HELP command",
    """Print local help text showing the Tube Client
    version, then fall through to forward the *HELP
    command to the host.""")

subroutine(0xFA2D, "Send OSCLI command to host",
    """Forward the command string at (string_ptr) to the
    host via Tube R2 with command code &02.

    Tube protocol: &02 string &0D -- &7F or &80

    If the response has bit 7 set, code needs to be
    entered (a language was selected).""")

subroutine(0xFA3E, "Handle *GO command",
    """Parse *GO [address]. If an address is given, set the
    transfer address to it. If no address given, use the
    current transfer address. Falls through to execute
    the code.

    Note: does not check for a separator after 'GO', so
    commands like *GOAD would be incorrectly matched.""")

subroutine(0xFA5C, "Execute code and restore state",
    """Save the current program pointer, call enter_code,
    then restore the current program and memory top
    on return.""")

subroutine(0xFA73, "OSBYTE implementation",
    """Handle OSBYTE calls. Functions &82-&84 are handled
    locally (memory high word, bottom/top of memory).
    Low functions (A < &80) send command &04 with X and A.
    High functions send command &06 with X, Y, and A.

    Special handling for OSBYTE &8E (select language) which
    checks for code to enter, and &9D (fast BPUT) which
    returns immediately without waiting for a response.

    On entry:
      A = function, X = parameter 1, Y = parameter 2
    On exit:
      A preserved
      X, Y, Carry = returned values (for A >= &80)""")

subroutine(0xFAFF, "OSWORD implementation",
    """Handle OSWORD calls. OSWORD 0 (read line) is handled
    specially via rdline. All other functions send the
    control block to the host and receive the response,
    with block sizes determined by lookup tables.

    On entry:
      A = function, XY => control block""")

subroutine(0xFB77, "Read line of input (OSWORD 0)",
    """Read a line of text from the host.

    Sends command &0A with the control block parameters,
    then receives the input string character by character.

    Tube protocol: &0A block -- &FF or &7F string &0D

    On exit:
      Y = length of string (excluding CR)
      C = 0 if OK, 1 if Escape""")

subroutine(0xFBCC, "OSARGS implementation",
    """Read or write information about an open file.

    Sends command &0C with handle, 4-byte data word,
    and function code. Receives result and updated data.

    On entry:
      A = function, X => data word in zero page, Y = handle
    On exit:
      A = result, data word at X updated""")

subroutine(0xFC0C, "OSFIND implementation",
    """Open or close a file.

    For close (A=0): sends command &12, function, handle.
    For open (A<>0): sends command &12, function, filename.

    On entry:
      A = function, XY => filename (open) or Y = handle (close)
    On exit:
      A = handle (open) or preserved (close)""")

subroutine(0xFC2A, "OSBGET implementation",
    """Read a byte from an open file.

    Sends command &0E with handle, waits for carry and byte.

    On entry:
      Y = handle
    On exit:
      A = byte read, C = set if EOF""")

subroutine(0xFC36, "OSBPUT implementation",
    """Write a byte to an open file.

    Sends command &10 with handle and byte.

    On entry:
      A = byte, Y = handle
    On exit:
      A preserved""")

subroutine(0xFC4A, "Send byte to Tube R2",
    """Wait for Tube R2 to be free, then send byte.

    On entry:
      A = byte to send
    On exit:
      A preserved""")

subroutine(0xFC53, "OSFILE implementation",
    """Operate on whole files (load, save, read/write attributes).

    Sends command &14 with 16-byte control block, filename,
    and function code. Receives result and updated control block.

    On entry:
      A = function, XY => control block""")

subroutine(0xFC8E, "OSGBPB implementation",
    """Multiple byte read and write.

    Sends command &16 with 13-byte control block and function.
    Receives updated control block, carry, and result.

    On entry:
      A = function, XY => control block""")

subroutine(0xFCB7, "Unsupported MOS call",
    """Generate a 'Bad' error for unsupported MOS calls.""")

subroutine(0xFCE5, "Interrupt handler entry",
    """Hardware interrupt entry point. Saves A, checks the
    break flag in the stacked processor status to distinguish
    BRK from IRQ, and dispatches accordingly.""")

subroutine(0xFCF0, "IRQ1 handler",
    """First-level IRQ handler. Checks Tube R4 for data
    transfer requests, then Tube R1 for escape/event
    notifications. Falls through to IRQ2V if neither.""")

subroutine(0xFCFB, "BRK handler dispatch",
    """Extract the return address from the stack, subtract 1
    to point to the byte after the BRK opcode, store in
    last_error, then dispatch via BRKV.""")

subroutine(0xFD18, "Handle Tube R1 interrupt",
    """Process data received via Tube R1. If bit 7 is set,
    it is an Escape state change (stored in escape_flag).
    Otherwise, it is an event notification: reads the
    event parameters (Y, X, event number) from R1 and
    dispatches via EVNTV.""")

subroutine(0xFD3F, "Handle Tube R4 interrupt",
    """Process data received via Tube R4. If bit 7 is set,
    it is an error from the host: reads the error number
    and message via R2 into the error buffer, then
    executes the error via a JMP to the buffer (which
    starts with a BRK opcode).

    If bit 7 is clear, it is a data transfer request:
    falls through to data_transfer_setup.""")

subroutine(0xFD65, "Set up data transfer via NMI",
    """Configure the NMI handler for a data transfer.

    The transfer type (0-7) from R4 selects the NMI
    routine and the address pointer. Types 0-3 are
    single/double byte transfers. Types 4-5 are release.
    Types 6-7 are 256-byte block transfers.

    Reads the 4-byte transfer address from R4 (only the
    low 2 bytes are used), configures the NMI vector and
    transfer address, then reads the sync byte from R4.""")

subroutine(0xFE00, "NMI: single byte to Tube",
    """Transfer type 0. Sends one byte from the transfer
    address to Tube R3, then increments the address.""")

subroutine(0xFE11, "NMI: single byte from Tube",
    """Transfer type 1. Reads one byte from Tube R3 and
    stores it at the transfer address, then increments
    the address.""")

subroutine(0xFE22, "NMI: two bytes to Tube",
    """Transfer type 2. Sends two consecutive bytes from
    (data_transfer_addr) to Tube R3, incrementing the
    pointer after each byte.""")

subroutine(0xFE41, "NMI: two bytes from Tube",
    """Transfer type 3. Reads two bytes from Tube R3 and
    stores them at (data_transfer_addr), incrementing
    the pointer after each byte.""")

subroutine(0xFE80, "Wait for byte in Tube R1",
    """Wait for data in Tube R1, allowing Tube R4 transfer
    requests to be serviced via IRQ while waiting.

    Polls R1 status; if R4 has data instead, briefly
    enables interrupts to let the R4 handler run, then
    resumes polling R1.

    On exit:
      A = byte from Tube R1""")

subroutine(0xFE98, "Print inline text",
    """Print the text string embedded immediately after the
    JSR to this routine. Characters are sent to OSWRCH
    until a byte with bit 7 set is encountered, which
    terminates the string. Execution resumes after the
    terminator byte.

    On exit:
      A = terminator byte (bit 7 set)""")

subroutine(0xFEB3, "NMI acknowledge",
    """Acknowledge an NMI by writing A to Tube R3, then
    return from interrupt. Used as the default NMI
    handler for transfer types 4-7.""")

# =====================================================================
# Comments
# =====================================================================

# --- Reset (&F800) ---
comment(0xF802, "Copy &FF00-&FFFF to RAM (self-copy)")
comment(0xF80B, "54 bytes = 27 default vector entries")
comment(0xF80D, "Copy default vector table to &0200-&0236")
comment(0xF816, "Clear the stack")
comment(0xF817, "X=&F0: copy &FE00-&FEEF, avoiding Tube I/O")
comment(0xF819, "Copy pages &FE-&FD to RAM, skipping Tube registers")
comment(0xF822, "Point string_ptr to start of ROM (&F800)")
comment(0xF82A, "Copy a page of ROM to RAM")
comment(0xF831, "Next page")
comment(0xF835, "Stop before I/O space at &FE00")
comment(0xF839, "17 bytes of low memory startup code")
comment(0xF83B, "Copy startup code to &0100")
comment(0xF844, "Copy current program address to transfer address")
comment(0xF84C, "Clear escape flag")
comment(0xF850, "Set low byte of memory top")
comment(0xF852, "Memory top = start of ROM code")
comment(0xF856, "Jump to low memory to page ROM out")

# --- Low memory startup code (&F859) ---
comment(0xF859, "Read Tube R1 status to page ROM out")
comment(0xF85C, "Enable IRQs for data transfers")
comment(0xF85D, "Target patched after first boot to skip banner")

# --- Startup banner (&F860) ---
comment(0xF877, "Patch the low memory JMP target to command_prompt")
comment(0xF87F, "Wait for host's acknowledge byte")
comment(0xF882, "Bit 7 set means host wants code entered")
comment(0xF884, "Otherwise enter the command prompt")

# --- Command prompt (&F88D) ---
comment(0xF88D, "Print '*' prompt")
comment(0xF892, "Point to rdline control block")
comment(0xF896, "OSWORD 0: read line")
comment(0xF89B, "Escape pressed during input")
comment(0xF89D, "Point XY to input buffer at &0236")
comment(0xF8A1, "Execute the command via OSCLI")
comment(0xF8A7, "OSBYTE &7E: acknowledge Escape")
comment(0xF8AC, "BRK with error 17: 'Escape'")

# --- Enter code (&F8B5) ---
comment(0xF8B5, "Set current program from transfer address")
comment(0xF8B9, "Also set memory top")
comment(0xF8C1, "Offset 7 in ROM header = copyright offset")
comment(0xF8C5, "Clear decimal mode, compute copyright pointer")
comment(0xF8C9, "last_error now points to copyright string")
comment(0xF8D3, "Check for &00 before '(C)'")
comment(0xF8D7, "Check for '('")
comment(0xF8DE, "Check for 'C'")
comment(0xF8E5, "Check for ')'")
comment(0xF8EC, "Offset 6 = ROM type byte")
comment(0xF8F0, "Mask to check language and 6502 bits")
comment(0xF8F2, "Bit 6 clear means not a language")
comment(0xF8F6, "Type 0 or 2 = 6502 code")
comment(0xF8FA, "Enter code with A=1")
comment(0xF8FF, "Set up error handler before reporting error")
comment(0xF909, "BRK: 'This is not a language'")
comment(0xF922, "Set up error handler before reporting error")
comment(0xF92C, "BRK: error 0, 'I cannot run this code'")

# --- Error handler (&F945) ---
comment(0xF945, "Reset the stack")
comment(0xF948, "Print newline")
comment(0xF94D, "Print error message characters")
comment(0xF957, "Print newline and return to command prompt")

# --- OSWORD 0 control block (&F95D) ---
comment(0xF95D, "Buffer at &0236, length &CA, min &20, max &FF")

# --- OSWRCH (&F962) ---
comment(0xF962, "Check Tube R1 status")
comment(0xF965, "NOP for timing")
comment(0xF966, "Wait until Tube R1 is ready for data")
comment(0xF968, "Send character to Tube R1 data register")

# --- OSRDCH (&F96C) ---
comment(0xF96C, "Send command &00 to host via R2: OSRDCH")
comment(0xF971, "Wait for carry byte from R2")
comment(0xF974, "Shift carry into C flag via ASL")

# --- Wait for Tube R2 byte (&F975) ---
comment(0xF975, "Poll Tube R2 status for data available")
comment(0xF97A, "Read byte from Tube R2")

# --- Skip spaces (&F97F) ---
comment(0xF97F, "Load character from (string_ptr),Y")
comment(0xF981, "Is it a space?")

# --- Scan hex (&F986) ---
comment(0xF986, "Clear hex accumulator")
comment(0xF98C, "Get next character")
comment(0xF98E, "Below '0': not a hex digit")
comment(0xF992, "Below ':': it's '0'-'9'")
comment(0xF996, "Force uppercase and adjust for A-F")
comment(0xF99C, "Above 'F': not a hex digit")
comment(0xF9A0, "Shift digit into upper nybble")
comment(0xF9A4, "Rotate 4 bits into accumulator")

# --- Send string (&F9B2) ---
comment(0xF9B2, "Store string address in string_ptr")
comment(0xF9B8, "Wait for Tube R2 free")
comment(0xF9BD, "Send character from (string_ptr),Y")
comment(0xF9C3, "Loop until CR sent")
comment(0xF9C7, "Restore Y from string_ptr_hi")

# --- OSCLI (&F9CA) ---
comment(0xF9CA, "Save A, store command string address")
comment(0xF9D1, "Skip leading spaces and stars")
comment(0xF9D9, "Force uppercase for command matching")
comment(0xF9DC, "Peek at next character")
comment(0xF9DE, "Check for *GO")
comment(0xF9E2, "Check for *H...")
comment(0xF9E6, "Abbreviated: H.")
comment(0xF9EC, "Check for *HE...")
comment(0xF9F3, "Abbreviated: HE.")
comment(0xF9F9, "Check for *HEL...")
comment(0xFA00, "Abbreviated: HEL.")
comment(0xFA06, "Check for *HELP...")
comment(0xFA0D, "Terminated by non-letter: it's *HELP")
comment(0xFA13, "Followed by letter: pass to host")

# --- *HELP (&FA17) ---
comment(0xFA17, "Print help text with version string")

# --- OSCLI send to host (&FA2D) ---
comment(0xFA2D, "Send command &02 to host: OSCLI")
comment(0xFA32, "Send the command string via string_ptr")
comment(0xFA35, "Wait for host acknowledgement")
comment(0xFA38, "Bit 7 set: host wants us to enter code")
comment(0xFA3C, "Restore A and return to caller")

# --- *GO (&FA3E) ---
comment(0xFA3E, "Check for 'O' after 'G'")
comment(0xFA44, "Skip past 'O' and any spaces")
comment(0xFA47, "Parse optional hex address")
comment(0xFA4A, "Skip trailing spaces")
comment(0xFA4C, "More parameters: pass to host instead")
comment(0xFA4E, "X=0 means no address given: use default")
comment(0xFA50, "Set transfer address from parsed hex value")

# --- Execute code (&FA5C) ---
comment(0xFA5C, "Save current program on stack")
comment(0xFA62, "Enter the code")
comment(0xFA63, "Restore current program and memory top")
comment(0xFA6A, "Restore A and return")

# --- Check OSCLI ack (&FA71) ---
comment(0xFA71, "If zero, wait for OSCLI ack")

# --- OSBYTE (&FA73) ---
comment(0xFA73, "Function >= &80: jump to high handler")
comment(0xFA77, "Send command &04 to host: OSBYTE low")
comment(0xFA7A, "Wait for Tube R2 free, send command")
comment(0xFA82, "Send X parameter")
comment(0xFA8B, "Send function code from A")
comment(0xFA93, "Wait for return value in X")
comment(0xFA9C, "OSBYTE &82: read memory high word")
comment(0xFA9E, "OSBYTE &83: read bottom of memory")
comment(0xFAA0, "OSBYTE &84: read top of memory")
comment(0xFAA4, "Send command &06 to host: OSBYTE high")
comment(0xFAAB, "Wait for R2 free, send command")
comment(0xFAB3, "Send X parameter")
comment(0xFABB, "Send Y parameter")
comment(0xFAC4, "Send function code from A")
comment(0xFACB, "OSBYTE &8E: select language, check for code")
comment(0xFACF, "OSBYTE &9D: fast BPUT, no response expected")
comment(0xFAD5, "Wait for carry byte from host")
comment(0xFADF, "Wait for Y return value")
comment(0xFAE7, "Wait for X return value")
comment(0xFAF0, "Return memory top from &F2/F3")
comment(0xFAF4, "Bottom of memory is always &0800")
comment(0xFAF8, "Memory high word is &0000 (16-bit address space)")

# --- OSWORD (&FAFF) ---
comment(0xFAFF, "Store control block address, check for OSWORD 0")
comment(0xFB03, "OSWORD 0: jump to read line handler")
comment(0xFB05, "Send command &08 to host: OSWORD")
comment(0xFB11, "Send function number")
comment(0xFB15, "Functions >= &80: length in control block")
comment(0xFB1F, "Functions < &80: length from lookup table")
comment(0xFB25, "Functions &15-&7F: send 16 bytes")
comment(0xFB29, "Send block length byte")
comment(0xFB2D, "Send control block bytes in reverse order")
comment(0xFB45, "Functions >= &80: receive length from control block")
comment(0xFB4F, "Functions < &80: receive length from lookup table")
comment(0xFB55, "Functions &15-&7F: receive 16 bytes")
comment(0xFB59, "Send receive block length")
comment(0xFB5D, "Receive response bytes into control block")
comment(0xFB71, "Restore registers and return")

# --- RDLINE (&FB77) ---
comment(0xFB77, "Send command &0A to host: RDLINE")
comment(0xFB7C, "Send control block bytes 4..2")
comment(0xFB8D, "Send &07 as high byte of buffer address")
comment(0xFB90, "Save buffer high byte from control block")
comment(0xFB96, "Send &00 as low byte of buffer address")
comment(0xFB9A, "Save buffer low byte from control block")
comment(0xFB9E, "Wait for response; &80+ means Escape")
comment(0xFBA7, "Set string_ptr to buffer address from stack")
comment(0xFBAF, "Receive characters into buffer until CR")
comment(0xFBBF, "Return A=0, Y=length, C=0 (OK)")
comment(0xFBC6, "Escape: return A=0, C=1")

# --- OSARGS (&FBCC) ---
comment(0xFBCC, "Send command &0C: OSARGS")
comment(0xFBD2, "Send handle")
comment(0xFBD6, "Send 4-byte data word (high to low)")
comment(0xFBED, "Send function code")
comment(0xFBF1, "Receive result byte")
comment(0xFBF5, "Receive updated 4-byte data word")

# --- OSFIND (&FC0C) ---
comment(0xFC0C, "Send command &12: OSFIND")
comment(0xFC12, "Send function code")
comment(0xFC15, "A=0 means close: send handle and wait for ack")
comment(0xFC1F, "Wait for acknowledge, restore A and return")
comment(0xFC24, "Open: send filename string")
comment(0xFC27, "Wait for and return handle")

# --- OSBGET (&FC2A) ---
comment(0xFC2A, "Send command &0E: OSBGET")
comment(0xFC2E, "Send handle")
comment(0xFC30, "Wait for carry and data byte")

# --- OSBPUT (&FC36) ---
comment(0xFC36, "Save A, send command &10: OSBPUT")
comment(0xFC3C, "Send handle")
comment(0xFC3E, "Send byte to write")
comment(0xFC40, "Wait for acknowledge, restore A and return")

# --- Send byte to Tube R2 (&FC4A) ---
comment(0xFC4A, "Wait for Tube R2 free")
comment(0xFC4F, "Send byte to Tube R2 data register")

# --- OSFILE (&FC53) ---
comment(0xFC53, "Store control block pointer in &FA/FB")
comment(0xFC57, "Send command &14: OSFILE")
comment(0xFC5F, "Send control block bytes &11..&02")
comment(0xFC69, "Get filename pointer from control block")
comment(0xFC71, "Send filename string")
comment(0xFC74, "Send function code")
comment(0xFC78, "Wait for result byte")
comment(0xFC7E, "Receive updated control block bytes &11..&02")
comment(0xFC87, "Restore XY registers")
comment(0xFC8B, "Return result in A")

# --- OSGBPB (&FC8E) ---
comment(0xFC8E, "Store control block pointer in &FA/FB")
comment(0xFC94, "Send command &16: OSGBPB")
comment(0xFC9A, "Send control block bytes &0C..&00")
comment(0xFCA2, "Send function code")
comment(0xFCA8, "Receive updated control block")
comment(0xFCB1, "Restore XY registers")
comment(0xFCB4, "Get carry and result")

# --- Unsupported (&FCB7) ---
comment(0xFCB7, "BRK with error 255: 'Bad'")

# --- Interrupt handler (&FCE5) ---
comment(0xFCE5, "Save A in irq_a_store")
comment(0xFCE7, "Pull stacked flags to check BRK bit")
comment(0xFCEA, "B flag set: BRK instruction")
comment(0xFCED, "Not BRK: dispatch via IRQ1V")

# --- IRQ1 handler (&FCF0) ---
comment(0xFCF0, "Data in Tube R4: process transfers/errors")
comment(0xFCF3, "Data in Tube R1: process escape/events")
comment(0xFCF8, "Neither: pass on via IRQ2V")

# --- BRK handler (&FCFB) ---
comment(0xFCFB, "Save X")
comment(0xFCFE, "Get return address from stack")
comment(0xFD00, "Subtract 1 to point at the BRK error block")
comment(0xFD0E, "Restore registers")
comment(0xFD12, "Re-enable interrupts, dispatch via BRKV")

# --- Tube R1 interrupt (&FD18) ---
comment(0xFD18, "Read Tube R1 data")
comment(0xFD1B, "Bit 7 set: Escape state change")
comment(0xFD1D, "Save registers for event dispatch")
comment(0xFD22, "Read event Y parameter from R1")
comment(0xFD25, "Read event X parameter from R1")
comment(0xFD28, "Read event number from R1")
comment(0xFD2A, "Dispatch event, restore registers and RTI")
comment(0xFD36, "Dispatch via EVNTV")
comment(0xFD39, "Shift bit 6 of Tube data into bit 7 of escape_flag")
comment(0xFD3C, "Restore A from irq_a_store and return")

# --- Tube R4 interrupt (&FD3F) ---
comment(0xFD3F, "Read Tube R4 data")
comment(0xFD42, "Bit 7 clear: data transfer request")
comment(0xFD44, "Re-enable interrupts during error reception")
comment(0xFD45, "Wait for error data via Tube R2")
comment(0xFD4B, "Store BRK opcode at start of error buffer")
comment(0xFD53, "Read error number into buffer")
comment(0xFD59, "Read error string bytes until NUL terminator")
comment(0xFD62, "Execute the BRK in the error buffer")

# --- Data transfer setup (&FD65) ---
comment(0xFD65, "Save transfer type, preserve Y")
comment(0xFD69, "Look up NMI routine address from table")
comment(0xFD73, "Look up transfer address pointer from table")
comment(0xFD83, "Wait for called ID byte from Tube R4")
comment(0xFD8A, "Type 5 = TubeRelease: exit immediately")
comment(0xFD8E, "Save transfer type, read 4-byte address")
comment(0xFD93, "Read and discard address byte 4 (bits 31-24)")
comment(0xFD9B, "Read and discard address byte 3 (bits 23-16)")
comment(0xFDA3, "Read address byte 2 (high), store via pointer")
comment(0xFDAE, "Read address byte 1 (low), store via pointer")
comment(0xFDB6, "Dummy reads of Tube R3 to synchronise")
comment(0xFDBE, "Wait for sync byte from Tube R4")
comment(0xFDC6, "Type < 6: not 256-byte transfer, exit")
comment(0xFDC8, "Type != 6: must be type 7 (read from Tube)")

# --- 256-byte write to Tube (&FDCB) ---
comment(0xFDCB, "Send 256 bytes from transfer address to Tube R3")
comment(0xFDCF, "Wait for Tube R3 free")
comment(0xFDD5, "Self-modifying: address patched during setup")
comment(0xFDDF, "Send final sync byte to Tube R3")

# --- 256-byte read from Tube (&FDEC) ---
comment(0xFDEE, "Wait for Tube R3 data available")
comment(0xFDF4, "Read byte from Tube R3")
comment(0xFDF7, "Self-modifying: address patched during setup")

# --- NMI single byte to Tube (&FE00) ---
comment(0xFE01, "Self-modifying: address patched during setup")
comment(0xFE06, "Send byte to Tube R3")
comment(0xFE08, "Increment transfer address (16-bit)")

# --- NMI single byte from Tube (&FE11) ---
comment(0xFE13, "Read byte from Tube R3")
comment(0xFE15, "Self-modifying: store address patched during setup")
comment(0xFE18, "Increment transfer address (16-bit)")

# --- NMI two bytes to Tube (&FE22) ---
comment(0xFE26, "Send first byte from (data_transfer_addr)")
comment(0xFE2C, "Increment transfer address")
comment(0xFE32, "Send second byte")
comment(0xFE38, "Increment transfer address")

# --- NMI two bytes from Tube (&FE41) ---
comment(0xFE46, "Read first byte from Tube R3")
comment(0xFE4C, "Increment transfer address")
comment(0xFE51, "Read second byte from Tube R3")
comment(0xFE57, "Increment transfer address")

# --- Wait for Tube R1 byte (&FE80) ---
comment(0xFE80, "Data available in Tube R1?")
comment(0xFE83, "Yes: go read it")
comment(0xFE85, "Check Tube R4 for pending transfer requests")
comment(0xFE88, "Nothing pending: keep polling R1")
comment(0xFE8A, "Save irq_a_store before enabling interrupts")
comment(0xFE8D, "Allow one IRQ through to service R4")
comment(0xFE8F, "Restore irq_a_store and continue polling")
comment(0xFE94, "Read byte from Tube R1")

# --- Print embedded text (&FE98) ---
comment(0xFE98, "Pull return address into control_block_ptr")
comment(0xFE9E, "Increment past the JSR return address")
comment(0xFEA4, "Read next character from inline string")
comment(0xFEA6, "Bit 7 set: end of string")
comment(0xFEA8, "Print character via OSWRCH")
comment(0xFEB0, "Resume execution after the string")

# --- NMI acknowledge (&FEB3) ---
comment(0xFEB3, "Write to Tube R3 to acknowledge NMI")

# --- Data tables ---

# OSWORD send/receive length tables
comment(0xFCBC, "OSWORD 1-20 send block lengths")
comment(0xFCD0, "OSWORD 1-20 receive block lengths")

# Transfer address pointer tables
comment(0xFE60, "Low bytes of transfer address pointers")
comment(0xFE68, "High bytes of transfer address pointers")

# NMI routine address tables
comment(0xFE70, "Low bytes of NMI handler addresses")
comment(0xFE78, "High bytes of NMI handler addresses")

# Spare/unused regions
comment(0xFEB5, "Unused ROM space, filled with &FF")
comment(0xFF00, "Unused ROM space, filled with &FF")

# Default vector table
comment(0xFF80, "Default MOS vector table (27 entries)")

# MOS entry point stubs
comment(0xFFB6, "Vector table info: length &36, table at &FF80")

# Hardware vectors
comment(0xFFFA, "NMI vector")
comment(0xFFFC, "RESET vector")
comment(0xFFFE, "IRQ/BRK vector")

# =====================================================================
# Data declarations
# =====================================================================

# OSWORD 0 control block at &F95D
for addr in [0xF95D, 0xF95E, 0xF95F, 0xF960, 0xF961]:
    byte(addr)

# Spare space filled with &FF
for addr in range(0xFEB5, 0xFEF0):
    byte(addr)
for addr in range(0xFEF0, 0xFF00):
    byte(addr)
for addr in range(0xFF00, 0xFF80):
    byte(addr)

# Default vector table (27 x 2-byte words)
for addr in range(0xFF80, 0xFFB6, 2):
    word(addr)

# Vector table info block
byte(0xFFB6)
word(0xFFB7)

# Hardware vectors
word(0xFFFA)
word(0xFFFC)
word(0xFFFE)

# OSWORD length tables
for addr in range(0xFCBC, 0xFCD0):
    byte(addr)
for addr in range(0xFCD0, 0xFCE4):
    byte(addr)

# Transfer address pointer tables
for addr in range(0xFE60, 0xFE68):
    byte(addr)
for addr in range(0xFE68, 0xFE70):
    byte(addr)

# NMI routine address tables
for addr in range(0xFE70, 0xFE78):
    byte(addr)
for addr in range(0xFE78, 0xFE80):
    byte(addr)

# =====================================================================
# Generate output
# =====================================================================

import json
import sys

output = go(print_output=False)

_output_dirpath.mkdir(parents=True, exist_ok=True)
output_filepath = _output_dirpath / "tube-6502-client-1.10.asm"
output_filepath.write_text(output)
print(f"Wrote {output_filepath}", file=sys.stderr)

try:
    structured = get_structured()
    json_filepath = _output_dirpath / "tube-6502-client-1.10.json"
    json_filepath.write_text(json.dumps(structured))
    print(f"Wrote {json_filepath}", file=sys.stderr)
except (AssertionError, Exception) as e:
    print(f"Warning: JSON output skipped: {e}", file=sys.stderr)
