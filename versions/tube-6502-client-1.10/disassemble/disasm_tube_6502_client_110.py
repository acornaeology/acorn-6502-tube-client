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

# Tube I/O registers are labelled rather than constant() because the
# addresses fall within the loaded ROM range. The actual hardware
# registers overlay these ROM addresses when the Tube ULA is active.

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
entry(0xFA17)
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

# NMI self-modifying address operands (low byte of the abs address)
label(0xFE02, "nmi0_transfer_addr")
label(0xFE16, "nmi1_transfer_addr")
label(0xFDD7, "nmi6_transfer_addr")
label(0xFDF9, "nmi7_transfer_addr")

# Auto-generated labels renamed to meaningful names
label(0xF802, "copy_page_ff_loop")
label(0xF80D, "copy_vectors_loop")
label(0xF819, "copy_io_page_loop")
label(0xF82A, "copy_rom_page")
label(0xF83B, "copy_startup_code_loop")
label(0xF85D, "soft_reset_jmp")
label(0xF94D, "print_error_loop")
label(0xF957, "print_error_done")
label(0xF98C, "scan_hex_next_char")
label(0xF9A0, "scan_hex_got_digit")
label(0xF9A6, "scan_hex_shift_loop")
label(0xF9B1, "scan_hex_return")
label(0xF9B8, "send_string_loop")
label(0xF9D1, "oscli_skip_stars_loop")
label(0xFA71, "osbyte_check_ack")
label(0xFA7A, "osbyte_low_wait_r2_1")
label(0xFA82, "osbyte_low_wait_r2_2")
label(0xFA8B, "osbyte_low_wait_r2_3")
label(0xFA93, "osbyte_low_wait_result")
label(0xFAAB, "osbyte_high_wait_r2_1")
label(0xFAB3, "osbyte_high_wait_r2_2")
label(0xFABB, "osbyte_high_wait_r2_3")
label(0xFAC4, "osbyte_high_wait_r2_4")
label(0xFAD5, "osbyte_high_wait_carry")
label(0xFADF, "osbyte_high_wait_y")
label(0xFAE7, "osbyte_high_wait_x")
label(0xFAEF, "osbyte_high_return")
label(0xFAF5, "osbyte_read_lomem_impl")
label(0xFAFA, "osbyte_read_high_word_impl")
label(0xFB09, "osword_wait_r2_cmd")
label(0xFB11, "osword_wait_r2_func")
label(0xFB24, "osword_send_low_lookup")
label(0xFB2D, "osword_send_block")
label(0xFB38, "osword_send_bytes_loop")
label(0xFB45, "osword_recv_get_length")
label(0xFB50, "osword_recv_low_lookup")
label(0xFB59, "osword_recv_block")
label(0xFB64, "osword_recv_bytes_loop")
label(0xFB71, "osword_restore_regs")
label(0xFB7E, "rdline_send_block_loop")
label(0xFB96, "rdline_send_addr_low")
label(0xFBB2, "rdline_recv_loop")
label(0xFBC7, "rdline_escape")
label(0xFBD2, "osargs_wait_r2_handle")
label(0xFC24, "osfind_open")
label(0xFC5F, "osfile_send_block_loop")
label(0xFC7E, "osfile_recv_block_loop")
label(0xFC9A, "osgbpb_send_block_loop")
label(0xFCA8, "osgbpb_recv_block_loop")
label(0xFCFD, "brk_handler_entry")
label(0xFD36, "dispatch_event")
label(0xFD45, "tube_r4_wait_error")
label(0xFD59, "tube_r4_read_error_loop")
label(0xFD83, "transfer_wait_id")
label(0xFD93, "transfer_read_addr4")
label(0xFD9B, "transfer_read_addr3")
label(0xFDA3, "transfer_read_addr2")
label(0xFDAE, "transfer_read_addr1")
label(0xFDBE, "transfer_wait_sync")
label(0xFDCF, "transfer_write_loop")
label(0xFDDF, "transfer_write_sync")
label(0xFDEE, "transfer_read_loop")
label(0xFDFE, "transfer_read_done")
label(0xFE0F, "nmi0_done")
label(0xFE20, "nmi1_done")
label(0xFE32, "nmi2_second_byte")
label(0xFE3D, "nmi2_done")
label(0xFE51, "nmi3_second_byte")
label(0xFE5C, "nmi3_done")
label(0xFE94, "tube_r1_read_byte")
label(0xFEA0, "print_text_loop")
label(0xFEA6, "print_text_get_char")
label(0xFEB0, "print_text_resume")
label(0xFEB7, "unused_fill_pre_io")
label(0xFEF0, "tube_ula_io_window")
label(0xFEA4, "print_text_inc_high")

# Zero page data references used with indexed addressing
label(0x0000, "zp_data_base")
label(0x0001, "zp_data_base_1")
label(0x0002, "zp_data_base_2")
label(0x0003, "zp_data_base_3")

# Misc auto-generated labels
label(0xF85E, "soft_reset_jmp_lo")
label(0xF85F, "soft_reset_jmp_hi")
label(0xFDFF, "io_page_base")
label(0xFF00, "unused_fill_page_ff")
label(0xFFFB, "nmi_vector_hi")

# Tube I/O register labels (within the ROM address space but mapped to hardware)
label(0xFEF8, "tube_r1_status")
label(0xFEF9, "tube_r1_data")
label(0xFEFA, "tube_r2_status")
label(0xFEFB, "tube_r2_data")
label(0xFEFC, "tube_r3_status")
label(0xFEFD, "tube_r3_data")
label(0xFEFE, "tube_r4_status")
label(0xFEFF, "tube_r4_data")

# Self-modifying code sub labels
label(0xFAF7, "osbyte_lomem_y_value")
label(0xFDD6, "transfer_write_read_byte")
label(0xFDF8, "transfer_read_store_byte")
label(0xFE01, "nmi0_read_byte")
label(0xFFFF, "irq_vector_hi")

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
# Every instruction has an inline comment explaining its purpose.

# --- Reset (&F800) ---
comment(0xF800, "Start copy index at 0", inline=True)
comment(0xF802, "Read byte from page &FF of ROM", inline=True)
comment(0xF805, "Copy to RAM (vectors + MOS entries)", inline=True)
comment(0xF808, "Next byte", inline=True)
comment(0xF809, "Loop until all 256 bytes copied", inline=True)
comment(0xF80B, "54 bytes = 27 default vector entries", inline=True)
comment(0xF80D, "Read default vector value", inline=True)
comment(0xF810, "Write to MOS vector table", inline=True)
comment(0xF813, "Next entry", inline=True)
comment(0xF814, "Loop until all vectors set", inline=True)
comment(0xF816, "Clear the stack (X=&FF from loop)", inline=True)
comment(0xF817, "X=&F0: copy &FE00-&FEEF to RAM", inline=True)
comment(0xF819, "Read ROM byte below Tube I/O window", inline=True)
comment(0xF81C, "Copy to RAM", inline=True)
comment(0xF81F, "Next byte", inline=True)
comment(0xF820, "Loop until &FE00-&FEEF copied", inline=True)
comment(0xF822, "Y=0 for page offset", inline=True)
comment(0xF824, "Point string_ptr low to &00", inline=True)
comment(0xF826, "High byte = &F8 (start of ROM)", inline=True)
comment(0xF828, "Set string_ptr to &F800", inline=True)
comment(0xF82A, "Read byte from ROM page", inline=True)
comment(0xF82C, "Write to RAM (self-copy)", inline=True)
comment(0xF82E, "Next byte in page", inline=True)
comment(0xF82F, "Loop until 256 bytes copied", inline=True)
comment(0xF831, "Move to next page", inline=True)
comment(0xF833, "Get current page number", inline=True)
comment(0xF835, "Reached Tube I/O window at &FE00?", inline=True)
comment(0xF837, "No, copy next page", inline=True)
comment(0xF839, "17 bytes of startup code to copy", inline=True)
comment(0xF83B, "Read startup code byte", inline=True)
comment(0xF83E, "Write to low memory at &0100", inline=True)
comment(0xF841, "Next byte", inline=True)
comment(0xF842, "Loop until all startup code copied", inline=True)
comment(0xF844, "Get current program low byte", inline=True)
comment(0xF846, "Set as transfer address low", inline=True)
comment(0xF848, "Get current program high byte", inline=True)
comment(0xF84A, "Set as transfer address high", inline=True)
comment(0xF84C, "A=0 for clearing", inline=True)
comment(0xF84E, "Clear Escape flag", inline=True)
comment(0xF850, "Set memory top low byte to 0", inline=True)
comment(0xF852, "High byte = &F8 (start of ROM)", inline=True)
comment(0xF854, "Set memory top to &F800", inline=True)
comment(0xF856, "Jump to low memory to page ROM out", inline=True)

# --- Low memory startup code (&F859) ---
comment(0xF859, "Read Tube R1 status to page ROM out", inline=True)
comment(0xF85C, "Enable interrupts for data transfers", inline=True)
comment(0xF85D, "Patched after first boot to skip banner", inline=True)

# --- Startup banner (&F860) ---
comment(0xF860, "Print inline startup banner string", inline=True)
comment(0xF87B, "Padding NOP", inline=True)
comment(0xF87C, "Low byte of command_prompt address", inline=True)
comment(0xF87E, "Patch JMP target low byte", inline=True)
comment(0xF881, "High byte of command_prompt address", inline=True)
comment(0xF883, "Patch JMP target high byte", inline=True)
comment(0xF886, "Wait for host acknowledge byte", inline=True)
comment(0xF889, "Is it &80 (enter code)?", inline=True)
comment(0xF88B, "Yes, enter transferred code", inline=True)

# --- Command prompt (&F88D) ---
comment(0xF88D, "Print '*' prompt character", inline=True)
comment(0xF88F, "Send '*' via OSWRCH", inline=True)
comment(0xF892, "Low byte of rdline control block", inline=True)
comment(0xF894, "High byte of rdline control block", inline=True)
comment(0xF896, "OSWORD 0: read line of input", inline=True)
comment(0xF898, "Call OSWORD", inline=True)
comment(0xF89B, "Carry set: Escape was pressed", inline=True)
comment(0xF89D, "Low byte of input buffer &0236", inline=True)
comment(0xF89F, "High byte of input buffer", inline=True)
comment(0xF8A1, "Execute command via OSCLI", inline=True)
comment(0xF8A4, "Loop back for next command", inline=True)
comment(0xF8A7, "OSBYTE &7E: acknowledge Escape", inline=True)
comment(0xF8A9, "Call OSBYTE", inline=True)
comment(0xF8AC, "Generate error 17: 'Escape'", inline=True)

# --- Enter code (&F8B5) ---
comment(0xF8B5, "Get transfer address low byte", inline=True)
comment(0xF8B7, "Set as current program low", inline=True)
comment(0xF8B9, "Also set memory top low", inline=True)
comment(0xF8BB, "Get transfer address high byte", inline=True)
comment(0xF8BD, "Set as current program high", inline=True)
comment(0xF8BF, "Also set memory top high", inline=True)
comment(0xF8C1, "Offset 7 = copyright string offset", inline=True)
comment(0xF8C3, "Read copyright offset from header", inline=True)
comment(0xF8C5, "Clear decimal mode", inline=True)
comment(0xF8C6, "Clear carry for addition", inline=True)
comment(0xF8C7, "Add base address to offset", inline=True)
comment(0xF8C9, "Store copyright pointer low", inline=True)
comment(0xF8CB, "A=0 for high byte add", inline=True)
comment(0xF8CD, "Add carry to high byte", inline=True)
comment(0xF8CF, "Store copyright pointer high", inline=True)
comment(0xF8D1, "Y=0 to check first byte", inline=True)
comment(0xF8D3, "Read byte at copyright pointer", inline=True)
comment(0xF8D5, "Not zero: no valid header, enter raw", inline=True)
comment(0xF8D7, "Y=1 to check '('", inline=True)
comment(0xF8D8, "Read next byte", inline=True)
comment(0xF8DA, "Is it '('?", inline=True)
comment(0xF8DC, "No: enter as raw code", inline=True)
comment(0xF8DE, "Y=2 to check 'C'", inline=True)
comment(0xF8DF, "Read next byte", inline=True)
comment(0xF8E1, "Is it 'C'?", inline=True)
comment(0xF8E3, "No: enter as raw code", inline=True)
comment(0xF8E5, "Y=3 to check ')'", inline=True)
comment(0xF8E6, "Read next byte", inline=True)
comment(0xF8E8, "Is it ')'?", inline=True)
comment(0xF8EA, "No: enter as raw code", inline=True)
comment(0xF8EC, "Offset 6 = ROM type byte", inline=True)
comment(0xF8EE, "Read ROM type", inline=True)
comment(0xF8F0, "Mask language and CPU type bits", inline=True)
comment(0xF8F2, "Bit 6 clear: not a language ROM", inline=True)
comment(0xF8F4, "Generate 'not a language' error", inline=True)
comment(0xF8F6, "Mask CPU type: 0 or 2 = 6502", inline=True)
comment(0xF8F8, "Non-zero: not 6502 code", inline=True)
comment(0xF8FA, "Enter code with A=1", inline=True)
comment(0xF8FC, "Jump to code via memory top pointer", inline=True)
comment(0xF8FF, "Set BRKV low to error handler", inline=True)
comment(0xF901, "Store BRKV low byte", inline=True)
comment(0xF904, "Set BRKV high to error handler", inline=True)
comment(0xF906, "Store BRKV high byte", inline=True)
comment(0xF909, "Generate 'not a language' error", inline=True)
comment(0xF922, "Set BRKV low to error handler", inline=True)
comment(0xF924, "Store BRKV low byte", inline=True)
comment(0xF927, "Set BRKV high to error handler", inline=True)
comment(0xF929, "Store BRKV high byte", inline=True)
comment(0xF92C, "Generate 'I cannot run this code'", inline=True)

# --- Error handler (&F945) ---
comment(0xF945, "Reset stack pointer to &FF", inline=True)
comment(0xF947, "Clear the stack", inline=True)
comment(0xF948, "Print newline before error message", inline=True)
comment(0xF94B, "Start at offset 1 (skip error number)", inline=True)
comment(0xF94D, "Get next error message character", inline=True)
comment(0xF94F, "Zero: end of error message", inline=True)
comment(0xF951, "Print character via OSWRCH", inline=True)
comment(0xF954, "Next character", inline=True)
comment(0xF955, "Loop until all characters printed", inline=True)
comment(0xF957, "Print trailing newline", inline=True)
comment(0xF95A, "Return to command prompt", inline=True)

# --- OSWORD 0 control block (&F95D) ---
comment(0xF95D, "Buffer at &0236, length &CA", inline=True)

# --- OSWRCH (&F962) ---
comment(0xF962, "Check Tube R1 status", inline=True)
comment(0xF965, "NOP for timing", inline=True)
comment(0xF966, "Wait until R1 ready to accept data", inline=True)
comment(0xF968, "Send character to Tube R1", inline=True)
comment(0xF96B, "Return with A preserved", inline=True)

# --- OSRDCH (&F96C) ---
comment(0xF96C, "Command &00: request character", inline=True)
comment(0xF96E, "Send command to host via Tube R2", inline=True)
comment(0xF971, "Wait for carry byte from host", inline=True)
comment(0xF974, "Shift carry flag into C", inline=True)

# --- Wait for Tube R2 byte (&F975) ---
comment(0xF975, "Poll Tube R2 status", inline=True)
comment(0xF978, "Loop until data available", inline=True)
comment(0xF97A, "Read data byte from Tube R2", inline=True)
comment(0xF97D, "Return", inline=True)

# --- Skip spaces (&F97E-&F985) ---
comment(0xF97E, "Advance past current character", inline=True)
comment(0xF97F, "Get character from string", inline=True)
comment(0xF981, "Is it a space?", inline=True)
comment(0xF983, "Yes: skip and check next", inline=True)
comment(0xF985, "Return with non-space char in A", inline=True)

# --- Scan hex (&F986) ---
comment(0xF986, "X=0: no digits parsed yet", inline=True)
comment(0xF988, "Clear hex accumulator low", inline=True)
comment(0xF98A, "Clear hex accumulator high", inline=True)
comment(0xF98C, "Get current character", inline=True)
comment(0xF98E, "Below '0': not a hex digit", inline=True)
comment(0xF990, "Exit if not a digit", inline=True)
comment(0xF992, "Below ':': it is a decimal digit", inline=True)
comment(0xF994, "Process digit 0-9", inline=True)
comment(0xF996, "Force uppercase", inline=True)
comment(0xF998, "Adjust for hex letter offset", inline=True)
comment(0xF99A, "Below 'A': not a hex digit", inline=True)
comment(0xF99C, "Above 'F': not a hex digit", inline=True)
comment(0xF99E, "Exit if out of range", inline=True)
comment(0xF9A0, "Shift digit into upper nybble", inline=True)
comment(0xF9A1, "Second shift", inline=True)
comment(0xF9A2, "Third shift", inline=True)
comment(0xF9A3, "Fourth shift (digit now in bits 7-4)", inline=True)
comment(0xF9A4, "4 bits to rotate in", inline=True)
comment(0xF9A6, "Shift bit out of digit", inline=True)
comment(0xF9A7, "Rotate into accumulator low", inline=True)
comment(0xF9A9, "Rotate into accumulator high", inline=True)
comment(0xF9AB, "Next bit", inline=True)
comment(0xF9AC, "Loop for 4 bits", inline=True)
comment(0xF9AE, "Move to next input character", inline=True)
comment(0xF9AF, "Loop for more hex digits", inline=True)
comment(0xF9B1, "Return", inline=True)

# --- Send string (&F9B2) ---
comment(0xF9B2, "Set string pointer low byte", inline=True)
comment(0xF9B4, "Set string pointer high byte", inline=True)
comment(0xF9B6, "Start at offset 0", inline=True)
comment(0xF9B8, "Poll Tube R2 status", inline=True)
comment(0xF9BB, "Wait until R2 ready", inline=True)
comment(0xF9BD, "Get character from string", inline=True)
comment(0xF9BF, "Send to Tube R2", inline=True)
comment(0xF9C2, "Next character", inline=True)
comment(0xF9C3, "Was it carriage return?", inline=True)
comment(0xF9C5, "No: send next character", inline=True)
comment(0xF9C7, "Restore Y from string_ptr_hi", inline=True)
comment(0xF9C9, "Return", inline=True)

# --- OSCLI (&F9CA) ---
comment(0xF9CA, "Save A on stack", inline=True)
comment(0xF9CB, "Store command string low byte", inline=True)
comment(0xF9CD, "Store command string high byte", inline=True)
comment(0xF9CF, "Start at offset 0", inline=True)
comment(0xF9D1, "Skip leading spaces", inline=True)
comment(0xF9D4, "Advance past character", inline=True)
comment(0xF9D5, "Is it a '*'?", inline=True)
comment(0xF9D7, "Yes: skip leading stars", inline=True)
comment(0xF9D9, "Force uppercase for matching", inline=True)
comment(0xF9DB, "Save first command letter in X", inline=True)
comment(0xF9DC, "Peek at next character", inline=True)
comment(0xF9DE, "Is first letter 'G'?", inline=True)
comment(0xF9E0, "Yes: check for *GO", inline=True)
comment(0xF9E2, "Is first letter 'H'?", inline=True)
comment(0xF9E4, "No: pass command to host", inline=True)
comment(0xF9E6, "Is next char '.' (abbreviated)?", inline=True)
comment(0xF9E8, "H. matches *HELP", inline=True)
comment(0xF9EA, "Force uppercase", inline=True)
comment(0xF9EC, "Is it 'E'?", inline=True)
comment(0xF9EE, "No: pass to host", inline=True)
comment(0xF9F0, "Advance past 'E'", inline=True)
comment(0xF9F1, "Get next character", inline=True)
comment(0xF9F3, "Is it '.' (abbreviated)?", inline=True)
comment(0xF9F5, "HE. matches *HELP", inline=True)
comment(0xF9F7, "Force uppercase", inline=True)
comment(0xF9F9, "Is it 'L'?", inline=True)
comment(0xF9FB, "No: pass to host", inline=True)
comment(0xF9FD, "Advance past 'L'", inline=True)
comment(0xF9FE, "Get next character", inline=True)
comment(0xFA00, "Is it '.' (abbreviated)?", inline=True)
comment(0xFA02, "HEL. matches *HELP", inline=True)
comment(0xFA04, "Force uppercase", inline=True)
comment(0xFA06, "Is it 'P'?", inline=True)
comment(0xFA08, "No: pass to host", inline=True)
comment(0xFA0A, "Advance past 'P'", inline=True)
comment(0xFA0B, "Get next character", inline=True)
comment(0xFA0D, "Force uppercase", inline=True)
comment(0xFA0F, "Below 'A': end of command, it is HELP", inline=True)
comment(0xFA11, "Non-letter terminates: do *HELP", inline=True)
comment(0xFA13, "Below '[': followed by letter", inline=True)
comment(0xFA15, "Letter follows: pass to host", inline=True)

# --- *HELP (&FA17) ---
comment(0xFA17, "Print inline version string", inline=True)
comment(0xFA2C, "Padding NOP after inline string", inline=True)

# --- OSCLI send to host (&FA2D) ---
comment(0xFA2D, "Command &02: OSCLI", inline=True)
comment(0xFA2F, "Send command code to host", inline=True)
comment(0xFA32, "Send command string via string_ptr", inline=True)
comment(0xFA35, "Wait for host acknowledgement", inline=True)
comment(0xFA38, "&80: host wants code entered", inline=True)
comment(0xFA3A, "Enter transferred code", inline=True)
comment(0xFA3C, "Restore saved A", inline=True)
comment(0xFA3D, "Return to caller", inline=True)

# --- *GO (&FA3E) ---
comment(0xFA3E, "Force uppercase", inline=True)
comment(0xFA40, "Is it 'O' (completing GO)?", inline=True)
comment(0xFA42, "No: pass to host", inline=True)
comment(0xFA44, "Skip past 'O' and spaces", inline=True)
comment(0xFA47, "Parse optional hex address", inline=True)
comment(0xFA4A, "Skip trailing spaces", inline=True)
comment(0xFA4D, "End of line (CR)?", inline=True)
comment(0xFA4F, "No: extra params, pass to host", inline=True)
comment(0xFA51, "X=0 means no address was given", inline=True)
comment(0xFA52, "Use current transfer address", inline=True)
comment(0xFA54, "Get parsed address low byte", inline=True)
comment(0xFA56, "Set transfer address low", inline=True)
comment(0xFA58, "Get parsed address high byte", inline=True)
comment(0xFA5A, "Set transfer address high", inline=True)

# --- Execute code (&FA5C) ---
comment(0xFA5C, "Get current program high byte", inline=True)
comment(0xFA5E, "Save on stack", inline=True)
comment(0xFA5F, "Get current program low byte", inline=True)
comment(0xFA61, "Save on stack", inline=True)
comment(0xFA62, "Enter the code at transfer address", inline=True)
comment(0xFA65, "Restore current program low", inline=True)
comment(0xFA66, "Set current program low", inline=True)
comment(0xFA68, "Also restore memory top low", inline=True)
comment(0xFA6A, "Restore current program high", inline=True)
comment(0xFA6B, "Set current program high", inline=True)
comment(0xFA6D, "Also restore memory top high", inline=True)
comment(0xFA6F, "Restore saved A", inline=True)
comment(0xFA70, "Return to caller", inline=True)

# --- Check OSCLI ack (&FA71) ---
comment(0xFA71, "If &8E matched, wait for OSCLI ack", inline=True)

# --- OSBYTE (&FA73) ---
comment(0xFA73, "Function >= &80?", inline=True)
comment(0xFA75, "Yes: handle high OSBYTE", inline=True)
comment(0xFA77, "Save function on stack", inline=True)
comment(0xFA78, "Command &04: OSBYTE low", inline=True)
comment(0xFA7A, "Poll Tube R2 status", inline=True)
comment(0xFA7D, "Wait until R2 ready", inline=True)
comment(0xFA7F, "Send command &04", inline=True)
comment(0xFA82, "Poll Tube R2 status", inline=True)
comment(0xFA85, "Wait until R2 ready", inline=True)
comment(0xFA87, "Send X parameter", inline=True)
comment(0xFA8A, "Restore function code", inline=True)
comment(0xFA8B, "Poll Tube R2 status", inline=True)
comment(0xFA8E, "Wait until R2 ready", inline=True)
comment(0xFA90, "Send function code", inline=True)
comment(0xFA93, "Poll Tube R2 for response", inline=True)
comment(0xFA96, "Wait until data available", inline=True)
comment(0xFA98, "Read return value into X", inline=True)
comment(0xFA9B, "Return", inline=True)
comment(0xFA9C, "Is it OSBYTE &82 (read high word)?", inline=True)
comment(0xFA9E, "Yes: return &0000", inline=True)
comment(0xFAA0, "Is it OSBYTE &83 (read LOMEM)?", inline=True)
comment(0xFAA2, "Yes: return &0800", inline=True)
comment(0xFAA4, "Is it OSBYTE &84 (read HIMEM)?", inline=True)
comment(0xFAA6, "Yes: return memory_top", inline=True)
comment(0xFAA8, "Save function on stack", inline=True)
comment(0xFAA9, "Command &06: OSBYTE high", inline=True)
comment(0xFAAB, "Poll Tube R2 status", inline=True)
comment(0xFAAE, "Wait until R2 ready", inline=True)
comment(0xFAB0, "Send command &06", inline=True)
comment(0xFAB3, "Poll Tube R2 status", inline=True)
comment(0xFAB6, "Wait until R2 ready", inline=True)
comment(0xFAB8, "Send X parameter", inline=True)
comment(0xFABB, "Poll Tube R2 status", inline=True)
comment(0xFABE, "Wait until R2 ready", inline=True)
comment(0xFAC0, "Send Y parameter", inline=True)
comment(0xFAC3, "Restore function code", inline=True)
comment(0xFAC4, "Poll Tube R2 status", inline=True)
comment(0xFAC7, "Wait until R2 ready", inline=True)
comment(0xFAC9, "Send function code", inline=True)
comment(0xFACC, "Is it &8E (select language)?", inline=True)
comment(0xFACE, "Yes: check for code to enter", inline=True)
comment(0xFAD0, "Is it &9D (fast BPUT)?", inline=True)
comment(0xFAD2, "Yes: return without response", inline=True)
comment(0xFAD4, "Save function for later restore", inline=True)
comment(0xFAD5, "Poll Tube R2 for carry byte", inline=True)
comment(0xFAD8, "Wait until data available", inline=True)
comment(0xFADA, "Read carry byte", inline=True)
comment(0xFADD, "Shift carry into C flag", inline=True)
comment(0xFADE, "Restore saved function", inline=True)
comment(0xFADF, "Poll Tube R2 for Y return value", inline=True)
comment(0xFAE2, "Wait until data available", inline=True)
comment(0xFAE4, "Read Y return value", inline=True)
comment(0xFAE7, "Poll Tube R2 for X return value", inline=True)
comment(0xFAEA, "Wait until data available", inline=True)
comment(0xFAEC, "Read X return value", inline=True)
comment(0xFAEF, "Return", inline=True)
comment(0xFAF0, "X = memory top low byte", inline=True)
comment(0xFAF2, "Y = memory top high byte", inline=True)
comment(0xFAF4, "Return (OSBYTE &84)", inline=True)
comment(0xFAF5, "X = &00 (bottom of user memory)", inline=True)
comment(0xFAF7, "Y = &08 (bottom of memory = &0800)", inline=True)
comment(0xFAF9, "Return (OSBYTE &83)", inline=True)
comment(0xFAFA, "X = &00 (high word low)", inline=True)
comment(0xFAFC, "Y = &00 (high word high)", inline=True)
comment(0xFAFE, "Return (OSBYTE &82)", inline=True)

# --- OSWORD (&FAFF) ---
comment(0xFAFF, "Store control block address low", inline=True)
comment(0xFB01, "Store control block address high", inline=True)
comment(0xFB03, "A=0: OSWORD 0?", inline=True)
comment(0xFB04, "Yes: handle read line specially", inline=True)
comment(0xFB06, "Save function on stack", inline=True)
comment(0xFB07, "Command &08: OSWORD", inline=True)
comment(0xFB09, "Poll Tube R2 status", inline=True)
comment(0xFB0C, "Wait until R2 ready", inline=True)
comment(0xFB0E, "Send command &08", inline=True)
comment(0xFB11, "Poll Tube R2 status", inline=True)
comment(0xFB14, "Wait until R2 ready", inline=True)
comment(0xFB16, "Send function number", inline=True)
comment(0xFB19, "Copy function to X", inline=True)
comment(0xFB1A, "Function >= &80?", inline=True)
comment(0xFB1C, "Y=0 for control block read", inline=True)
comment(0xFB1E, "Get send length from control block", inline=True)
comment(0xFB20, "Transfer to Y", inline=True)
comment(0xFB21, "Jump to send block", inline=True)
comment(0xFB24, "Get send length from table", inline=True)
comment(0xFB27, "Function < &15?", inline=True)
comment(0xFB29, "Yes: use table length", inline=True)
comment(0xFB2B, "Default: send 16 bytes", inline=True)
comment(0xFB2D, "Poll Tube R2 status", inline=True)
comment(0xFB30, "Wait until R2 ready", inline=True)
comment(0xFB32, "Send block length to host", inline=True)
comment(0xFB35, "Decrement index", inline=True)
comment(0xFB36, "Negative: nothing to send", inline=True)
comment(0xFB38, "Poll Tube R2 status", inline=True)
comment(0xFB3B, "Wait until R2 ready", inline=True)
comment(0xFB3D, "Read byte from control block", inline=True)
comment(0xFB3F, "Send to Tube R2", inline=True)
comment(0xFB42, "Next byte (reverse order)", inline=True)
comment(0xFB43, "Loop until all bytes sent", inline=True)
comment(0xFB45, "Get function back in A", inline=True)
comment(0xFB46, "Function >= &80?", inline=True)
comment(0xFB48, "Y=1 for control block read", inline=True)
comment(0xFB4A, "Get receive length from block", inline=True)
comment(0xFB4C, "Transfer to Y", inline=True)
comment(0xFB4D, "Jump to receive block", inline=True)
comment(0xFB50, "Get receive length from table", inline=True)
comment(0xFB53, "Function < &15?", inline=True)
comment(0xFB55, "Yes: use table length", inline=True)
comment(0xFB57, "Default: receive 16 bytes", inline=True)
comment(0xFB59, "Poll Tube R2 status", inline=True)
comment(0xFB5C, "Wait until R2 ready", inline=True)
comment(0xFB5E, "Send receive length to host", inline=True)
comment(0xFB61, "Decrement index", inline=True)
comment(0xFB62, "Negative: nothing to receive", inline=True)
comment(0xFB64, "Poll Tube R2 for data", inline=True)
comment(0xFB67, "Wait until data available", inline=True)
comment(0xFB69, "Read response byte", inline=True)
comment(0xFB6C, "Store in control block", inline=True)
comment(0xFB6E, "Next byte (reverse order)", inline=True)
comment(0xFB6F, "Loop until all received", inline=True)
comment(0xFB71, "Restore Y from string_ptr_hi", inline=True)
comment(0xFB73, "Restore X from string_ptr", inline=True)
comment(0xFB75, "Restore function code", inline=True)
comment(0xFB76, "Return", inline=True)

# --- RDLINE (&FB77) ---
comment(0xFB77, "Command &0A: read line", inline=True)
comment(0xFB79, "Send command to host", inline=True)
comment(0xFB7C, "Start at control block byte 4", inline=True)
comment(0xFB7E, "Poll Tube R2 status", inline=True)
comment(0xFB81, "Wait until R2 ready", inline=True)
comment(0xFB83, "Get control block byte", inline=True)
comment(0xFB85, "Send to host", inline=True)
comment(0xFB88, "Decrement index", inline=True)
comment(0xFB89, "Reached byte 1?", inline=True)
comment(0xFB8B, "No: send next (bytes 4, 3, 2)", inline=True)
comment(0xFB8D, "&07 as high byte of buffer address", inline=True)
comment(0xFB8F, "Send buffer address high byte", inline=True)
comment(0xFB92, "Get actual buffer high byte", inline=True)
comment(0xFB94, "Save on stack for later", inline=True)
comment(0xFB95, "Decrement to byte 0", inline=True)
comment(0xFB96, "Poll Tube R2 status", inline=True)
comment(0xFB99, "Wait until R2 ready", inline=True)
comment(0xFB9B, "Send &00 as buffer address low byte", inline=True)
comment(0xFB9E, "Get actual buffer low byte", inline=True)
comment(0xFBA0, "Save on stack for later", inline=True)
comment(0xFBA1, "X=&FF as Escape indicator", inline=True)
comment(0xFBA3, "Wait for host response", inline=True)
comment(0xFBA6, "Is response >= &80 (Escape)?", inline=True)
comment(0xFBA8, "Yes: handle Escape", inline=True)
comment(0xFBAA, "Recover buffer low byte", inline=True)
comment(0xFBAB, "Set string_ptr low", inline=True)
comment(0xFBAD, "Recover buffer high byte", inline=True)
comment(0xFBAE, "Set string_ptr high", inline=True)
comment(0xFBB0, "Start at offset 0", inline=True)
comment(0xFBB2, "Poll Tube R2 for data", inline=True)
comment(0xFBB5, "Wait until data available", inline=True)
comment(0xFBB7, "Read character from host", inline=True)
comment(0xFBBA, "Store in buffer", inline=True)
comment(0xFBBC, "Advance buffer position", inline=True)
comment(0xFBBD, "Is it carriage return?", inline=True)
comment(0xFBBF, "No: receive next character", inline=True)
comment(0xFBC1, "A=0 on success", inline=True)
comment(0xFBC3, "Y=length (exclude CR)", inline=True)
comment(0xFBC4, "Clear carry: no Escape", inline=True)
comment(0xFBC5, "X=0 on success", inline=True)
comment(0xFBC6, "Return: A=0, Y=len, C=0", inline=True)
comment(0xFBC7, "Discard saved buffer low byte", inline=True)
comment(0xFBC8, "Discard saved buffer high byte", inline=True)
comment(0xFBC9, "A=0, carry set from CMP &80", inline=True)
comment(0xFBCB, "Return: Escape, A=0, C=1", inline=True)

# --- OSARGS (&FBCC) ---
comment(0xFBCC, "Save function on stack", inline=True)
comment(0xFBCD, "Command &0C: OSARGS", inline=True)
comment(0xFBCF, "Send command to host", inline=True)
comment(0xFBD2, "Poll Tube R2 status", inline=True)
comment(0xFBD5, "Wait until R2 ready", inline=True)
comment(0xFBD7, "Send file handle", inline=True)
comment(0xFBDA, "Get data word byte 3", inline=True)
comment(0xFBDC, "Send data byte 3", inline=True)
comment(0xFBDF, "Get data word byte 2", inline=True)
comment(0xFBE1, "Send data byte 2", inline=True)
comment(0xFBE4, "Get data word byte 1", inline=True)
comment(0xFBE6, "Send data byte 1", inline=True)
comment(0xFBE9, "Get data word byte 0", inline=True)
comment(0xFBEB, "Send data byte 0", inline=True)
comment(0xFBEE, "Restore function code", inline=True)
comment(0xFBEF, "Send function code", inline=True)
comment(0xFBF2, "Wait for result byte", inline=True)
comment(0xFBF5, "Save result on stack", inline=True)
comment(0xFBF6, "Wait for data byte 3", inline=True)
comment(0xFBF9, "Store in data word", inline=True)
comment(0xFBFB, "Wait for data byte 2", inline=True)
comment(0xFBFE, "Store in data word", inline=True)
comment(0xFC00, "Wait for data byte 1", inline=True)
comment(0xFC03, "Store in data word", inline=True)
comment(0xFC05, "Wait for data byte 0", inline=True)
comment(0xFC08, "Store in data word", inline=True)
comment(0xFC0A, "Restore result to A", inline=True)
comment(0xFC0B, "Return with result in A", inline=True)

# --- OSFIND (&FC0C) ---
comment(0xFC0C, "Save function on stack", inline=True)
comment(0xFC0D, "Command &12: OSFIND", inline=True)
comment(0xFC0F, "Send command to host", inline=True)
comment(0xFC12, "Restore function code", inline=True)
comment(0xFC13, "Send function code", inline=True)
comment(0xFC16, "Is it close (A=0)?", inline=True)
comment(0xFC18, "No: handle open", inline=True)
comment(0xFC1A, "Save A=0", inline=True)
comment(0xFC1B, "Transfer handle from Y to A", inline=True)
comment(0xFC1C, "Send handle", inline=True)
comment(0xFC1F, "Wait for acknowledge", inline=True)
comment(0xFC22, "Restore A=0", inline=True)
comment(0xFC23, "Return", inline=True)
comment(0xFC24, "Send filename string", inline=True)
comment(0xFC27, "Wait for and return file handle", inline=True)

# --- OSBGET (&FC2A) ---
comment(0xFC2A, "Command &0E: OSBGET", inline=True)
comment(0xFC2C, "Send command to host", inline=True)
comment(0xFC2F, "Transfer handle from Y to A", inline=True)
comment(0xFC30, "Send handle", inline=True)
comment(0xFC33, "Wait for carry and data byte", inline=True)

# --- OSBPUT (&FC36) ---
comment(0xFC36, "Save byte to write", inline=True)
comment(0xFC37, "Command &10: OSBPUT", inline=True)
comment(0xFC39, "Send command to host", inline=True)
comment(0xFC3C, "Transfer handle from Y to A", inline=True)
comment(0xFC3D, "Send handle", inline=True)
comment(0xFC40, "Restore byte to write", inline=True)
comment(0xFC41, "Send data byte", inline=True)
comment(0xFC44, "Save A for restore after ack", inline=True)
comment(0xFC45, "Wait for acknowledge", inline=True)
comment(0xFC48, "Restore A (preserved)", inline=True)
comment(0xFC49, "Return", inline=True)

# --- Send byte to Tube R2 (&FC4A) ---
comment(0xFC4A, "Poll Tube R2 status", inline=True)
comment(0xFC4D, "Wait until R2 ready", inline=True)
comment(0xFC4F, "Write byte to Tube R2 data", inline=True)
comment(0xFC52, "Return with A preserved", inline=True)

# --- OSFILE (&FC53) ---
comment(0xFC53, "Store control block high byte", inline=True)
comment(0xFC55, "Store control block low byte", inline=True)
comment(0xFC57, "Save function on stack", inline=True)
comment(0xFC58, "Command &14: OSFILE", inline=True)
comment(0xFC5A, "Send command to host", inline=True)
comment(0xFC5D, "Start at control block byte &11", inline=True)
comment(0xFC5F, "Get control block byte", inline=True)
comment(0xFC61, "Send to host", inline=True)
comment(0xFC64, "Decrement index", inline=True)
comment(0xFC65, "Reached byte 1?", inline=True)
comment(0xFC67, "No: send next byte", inline=True)
comment(0xFC69, "Decrement to byte 0", inline=True)
comment(0xFC6A, "Get filename pointer low", inline=True)
comment(0xFC6C, "Transfer to X", inline=True)
comment(0xFC6D, "Move to byte 1", inline=True)
comment(0xFC6E, "Get filename pointer high", inline=True)
comment(0xFC70, "Transfer to Y", inline=True)
comment(0xFC71, "Send filename string", inline=True)
comment(0xFC74, "Restore function code", inline=True)
comment(0xFC75, "Send function code", inline=True)
comment(0xFC78, "Wait for result byte", inline=True)
comment(0xFC7B, "Save result on stack", inline=True)
comment(0xFC7C, "Start at control block byte &11", inline=True)
comment(0xFC7E, "Wait for response byte", inline=True)
comment(0xFC81, "Store in control block", inline=True)
comment(0xFC83, "Decrement index", inline=True)
comment(0xFC84, "Reached byte 1?", inline=True)
comment(0xFC86, "No: receive next byte", inline=True)
comment(0xFC88, "Restore Y from control block ptr", inline=True)
comment(0xFC8A, "Restore X from control block ptr", inline=True)
comment(0xFC8C, "Restore result to A", inline=True)
comment(0xFC8D, "Return with result in A", inline=True)

# --- OSGBPB (&FC8E) ---
comment(0xFC8E, "Store control block high byte", inline=True)
comment(0xFC90, "Store control block low byte", inline=True)
comment(0xFC92, "Save function on stack", inline=True)
comment(0xFC93, "Command &16: OSGBPB", inline=True)
comment(0xFC95, "Send command to host", inline=True)
comment(0xFC98, "Start at control block byte &0C", inline=True)
comment(0xFC9A, "Get control block byte", inline=True)
comment(0xFC9C, "Send to host", inline=True)
comment(0xFC9F, "Decrement index", inline=True)
comment(0xFCA0, "Loop for bytes &0C..&00", inline=True)
comment(0xFCA2, "Restore function code", inline=True)
comment(0xFCA3, "Send function code", inline=True)
comment(0xFCA6, "Start at control block byte &0C", inline=True)
comment(0xFCA8, "Wait for response byte", inline=True)
comment(0xFCAB, "Store in control block", inline=True)
comment(0xFCAD, "Decrement index", inline=True)
comment(0xFCAE, "Loop for bytes &0C..&00", inline=True)
comment(0xFCB0, "Restore Y from control block ptr", inline=True)
comment(0xFCB2, "Restore X from control block ptr", inline=True)
comment(0xFCB4, "Get carry and result byte", inline=True)

# --- Unsupported (&FCB7) ---
comment(0xFCB7, "Generate error 255: 'Bad'", inline=True)

# --- Data tables ---
comment(0xFCBC, "OSWORD 1-20 send block lengths", inline=True)
comment(0xFCD0, "OSWORD 1-20 receive block lengths", inline=True)

# --- Interrupt handler (&FCE5) ---
comment(0xFCE5, "Save A in irq_a_store", inline=True)
comment(0xFCE7, "Pull stacked processor status", inline=True)
comment(0xFCE8, "Push it back (non-destructive read)", inline=True)
comment(0xFCE9, "Isolate BRK flag (bit 4)", inline=True)
comment(0xFCEB, "BRK flag set: handle BRK", inline=True)
comment(0xFCED, "Dispatch via IRQ1V", inline=True)

# --- IRQ1 handler (&FCF0) ---
comment(0xFCF0, "Check Tube R4 for data", inline=True)
comment(0xFCF3, "Data present: handle transfer/error", inline=True)
comment(0xFCF5, "Check Tube R1 for data", inline=True)
comment(0xFCF8, "Data present: handle escape/event", inline=True)
comment(0xFCFA, "Neither: dispatch via IRQ2V", inline=True)

# --- BRK handler (&FCFB) ---
comment(0xFCFB, "Merge with BRK entry (ASL is TXA;PHA)", inline=True)
comment(0xFCFD, "Save X on stack", inline=True)
comment(0xFCFE, "Push X", inline=True)
comment(0xFCFF, "Get stack pointer", inline=True)
comment(0xFD00, "Get return address low from stack", inline=True)
comment(0xFD03, "Clear decimal mode", inline=True)
comment(0xFD04, "Set carry for subtract", inline=True)
comment(0xFD05, "Subtract 1 to point at error block", inline=True)
comment(0xFD07, "Store as last_error low", inline=True)
comment(0xFD09, "Get return address high from stack", inline=True)
comment(0xFD0C, "Subtract borrow", inline=True)
comment(0xFD0E, "Store as last_error high", inline=True)
comment(0xFD10, "Restore X from stack", inline=True)
comment(0xFD11, "Transfer back to X", inline=True)
comment(0xFD12, "Get saved A from irq_a_store", inline=True)
comment(0xFD14, "Re-enable interrupts", inline=True)
comment(0xFD15, "Dispatch via BRKV", inline=True)

# --- Tube R1 interrupt (&FD18) ---
comment(0xFD18, "Read data from Tube R1", inline=True)
comment(0xFD1B, "Bit 7 set: Escape state change", inline=True)
comment(0xFD1D, "Save Y", inline=True)
comment(0xFD1E, "Push Y", inline=True)
comment(0xFD1F, "Save X", inline=True)
comment(0xFD20, "Push X", inline=True)
comment(0xFD21, "Read event Y parameter via R1", inline=True)
comment(0xFD24, "Store in Y", inline=True)
comment(0xFD25, "Read event X parameter via R1", inline=True)
comment(0xFD28, "Store in X", inline=True)
comment(0xFD29, "Read event number via R1", inline=True)
comment(0xFD2C, "Dispatch event via EVNTV", inline=True)
comment(0xFD2F, "Restore X from stack", inline=True)
comment(0xFD30, "Transfer to X", inline=True)
comment(0xFD31, "Restore Y from stack", inline=True)
comment(0xFD32, "Transfer to Y", inline=True)
comment(0xFD33, "Get saved A from irq_a_store", inline=True)
comment(0xFD35, "Return from interrupt", inline=True)
comment(0xFD36, "Dispatch event via EVNTV", inline=True)
comment(0xFD39, "Shift bit 6 into bit 7 for Escape", inline=True)
comment(0xFD3A, "Store as Escape flag", inline=True)
comment(0xFD3C, "Get saved A from irq_a_store", inline=True)
comment(0xFD3E, "Return from interrupt", inline=True)

# --- Tube R4 interrupt (&FD3F) ---
comment(0xFD3F, "Read data from Tube R4", inline=True)
comment(0xFD42, "Bit 7 clear: data transfer request", inline=True)
comment(0xFD44, "Re-enable IRQs for error reception", inline=True)
comment(0xFD45, "Poll Tube R2 for error data", inline=True)
comment(0xFD48, "Wait until data available", inline=True)
comment(0xFD4A, "Read and discard R2 sync byte", inline=True)
comment(0xFD4D, "A=0 (BRK opcode)", inline=True)
comment(0xFD4F, "Store BRK at start of error buffer", inline=True)
comment(0xFD52, "Y=0 for buffer index", inline=True)
comment(0xFD53, "Wait for error number byte", inline=True)
comment(0xFD56, "Store error number in buffer", inline=True)
comment(0xFD59, "Advance buffer index", inline=True)
comment(0xFD5A, "Wait for next error string byte", inline=True)
comment(0xFD5D, "Store in error buffer", inline=True)
comment(0xFD60, "Loop until NUL terminator", inline=True)
comment(0xFD62, "Execute BRK in error buffer", inline=True)

# --- Data transfer setup (&FD65) ---
comment(0xFD65, "Save transfer type in NMI vector", inline=True)
comment(0xFD68, "Save Y on stack", inline=True)
comment(0xFD69, "Push Y", inline=True)
comment(0xFD6A, "Get transfer type back", inline=True)
comment(0xFD6D, "Look up NMI routine address low", inline=True)
comment(0xFD70, "Set NMI vector low byte", inline=True)
comment(0xFD73, "Look up NMI routine address high", inline=True)
comment(0xFD76, "Set NMI vector high byte", inline=True)
comment(0xFD79, "Look up address pointer low", inline=True)
comment(0xFD7C, "Set transfer_addr_ptr low", inline=True)
comment(0xFD7E, "Look up address pointer high", inline=True)
comment(0xFD81, "Set transfer_addr_ptr high", inline=True)
comment(0xFD83, "Poll Tube R4 for called ID byte", inline=True)
comment(0xFD86, "Wait until data available", inline=True)
comment(0xFD88, "Read called ID byte", inline=True)
comment(0xFD8B, "Type 5: release, no transfer needed", inline=True)
comment(0xFD8D, "Yes: exit immediately", inline=True)
comment(0xFD8F, "Save transfer type", inline=True)
comment(0xFD90, "Push transfer type", inline=True)
comment(0xFD91, "Y=1 for address byte index", inline=True)
comment(0xFD93, "Poll Tube R4 for address byte 4", inline=True)
comment(0xFD96, "Wait until data available", inline=True)
comment(0xFD98, "Read and discard byte 4 (bits 31-24)", inline=True)
comment(0xFD9B, "Poll Tube R4 for address byte 3", inline=True)
comment(0xFD9E, "Wait until data available", inline=True)
comment(0xFDA0, "Read and discard byte 3 (bits 23-16)", inline=True)
comment(0xFDA3, "Poll Tube R4 for address byte 2", inline=True)
comment(0xFDA6, "Wait until data available", inline=True)
comment(0xFDA8, "Read address byte 2 (high)", inline=True)
comment(0xFDAB, "Store via transfer address pointer", inline=True)
comment(0xFDAD, "Decrement to byte 0", inline=True)
comment(0xFDAE, "Poll Tube R4 for address byte 1", inline=True)
comment(0xFDB1, "Wait until data available", inline=True)
comment(0xFDB3, "Read address byte 1 (low)", inline=True)
comment(0xFDB6, "Store via transfer address pointer", inline=True)
comment(0xFDB8, "Dummy read of Tube R3 to sync", inline=True)
comment(0xFDBB, "Second dummy read of Tube R3", inline=True)
comment(0xFDBE, "Poll Tube R4 for sync byte", inline=True)
comment(0xFDC1, "Wait until data available", inline=True)
comment(0xFDC3, "Read sync byte", inline=True)
comment(0xFDC6, "Restore transfer type", inline=True)
comment(0xFDC7, "Is it type 6 or above?", inline=True)
comment(0xFDC9, "Below 6: exit (single/double/release)", inline=True)
comment(0xFDCB, "Not 6: must be type 7 (read block)", inline=True)
comment(0xFDCD, "Y=0 for 256-byte counter", inline=True)
comment(0xFDCF, "Read Tube R3 status", inline=True)
comment(0xFDD2, "Isolate ready bit", inline=True)
comment(0xFDD4, "Wait until R3 ready", inline=True)
comment(0xFDD6, "Read byte (address patched)", inline=True)
comment(0xFDD9, "Send to Tube R3", inline=True)
comment(0xFDDC, "Next byte", inline=True)
comment(0xFDDD, "Loop for 256 bytes", inline=True)
comment(0xFDDF, "Poll Tube R3 status", inline=True)
comment(0xFDE2, "Wait until R3 ready", inline=True)
comment(0xFDE4, "Send final sync byte to R3", inline=True)
comment(0xFDE7, "Restore Y from stack", inline=True)
comment(0xFDE8, "Transfer to Y", inline=True)
comment(0xFDE9, "Get saved A from irq_a_store", inline=True)
comment(0xFDEB, "Return from interrupt", inline=True)

# --- 256-byte read from Tube (&FDEC) ---
comment(0xFDEC, "Y=0 for 256-byte counter", inline=True)
comment(0xFDEE, "Read Tube R3 status", inline=True)
comment(0xFDF1, "Isolate data ready bit", inline=True)
comment(0xFDF3, "Wait until R3 has data", inline=True)
comment(0xFDF5, "Read byte from Tube R3", inline=True)
comment(0xFDF8, "Store byte (address patched)", inline=True)
comment(0xFDFB, "Next byte", inline=True)
comment(0xFDFC, "Loop for 256 bytes", inline=True)
comment(0xFDFE, "Always branch to exit", inline=True)

# --- NMI single byte to Tube (&FE00) ---
comment(0xFE00, "Save A", inline=True)
comment(0xFE01, "Read byte (address patched by setup)", inline=True)
comment(0xFE04, "Send byte to Tube R3", inline=True)
comment(0xFE07, "Increment address low byte", inline=True)
comment(0xFE0A, "No carry: skip high byte increment", inline=True)
comment(0xFE0C, "Increment address high byte", inline=True)
comment(0xFE0F, "Restore A", inline=True)
comment(0xFE10, "Return from NMI", inline=True)

# --- NMI single byte from Tube (&FE11) ---
comment(0xFE11, "Save A", inline=True)
comment(0xFE12, "Read byte from Tube R3", inline=True)
comment(0xFE15, "Store byte (address patched by setup)", inline=True)
comment(0xFE18, "Increment address low byte", inline=True)
comment(0xFE1B, "No carry: skip high byte increment", inline=True)
comment(0xFE1D, "Increment address high byte", inline=True)
comment(0xFE20, "Restore A", inline=True)
comment(0xFE21, "Return from NMI", inline=True)

# --- NMI two bytes to Tube (&FE22) ---
comment(0xFE22, "Save A", inline=True)
comment(0xFE23, "Save Y", inline=True)
comment(0xFE24, "Push Y", inline=True)
comment(0xFE25, "Y=0 for indirect indexed access", inline=True)
comment(0xFE27, "Read first byte via pointer", inline=True)
comment(0xFE29, "Send to Tube R3", inline=True)
comment(0xFE2C, "Increment transfer address low", inline=True)
comment(0xFE2E, "No carry: skip high increment", inline=True)
comment(0xFE30, "Increment transfer address high", inline=True)
comment(0xFE32, "Read second byte via pointer", inline=True)
comment(0xFE34, "Send to Tube R3", inline=True)
comment(0xFE37, "Increment transfer address low", inline=True)
comment(0xFE39, "No carry: skip high increment", inline=True)
comment(0xFE3B, "Increment transfer address high", inline=True)
comment(0xFE3D, "Restore Y from stack", inline=True)
comment(0xFE3E, "Transfer to Y", inline=True)
comment(0xFE3F, "Restore A", inline=True)
comment(0xFE40, "Return from NMI", inline=True)

# --- NMI two bytes from Tube (&FE41) ---
comment(0xFE41, "Save A", inline=True)
comment(0xFE42, "Save Y", inline=True)
comment(0xFE43, "Push Y", inline=True)
comment(0xFE44, "Y=0 for indirect indexed access", inline=True)
comment(0xFE46, "Read first byte from Tube R3", inline=True)
comment(0xFE49, "Store via transfer address pointer", inline=True)
comment(0xFE4B, "Increment transfer address low", inline=True)
comment(0xFE4D, "No carry: skip high increment", inline=True)
comment(0xFE4F, "Increment transfer address high", inline=True)
comment(0xFE51, "Read second byte from Tube R3", inline=True)
comment(0xFE54, "Store via transfer address pointer", inline=True)
comment(0xFE56, "Increment transfer address low", inline=True)
comment(0xFE58, "No carry: skip high increment", inline=True)
comment(0xFE5A, "Increment transfer address high", inline=True)
comment(0xFE5C, "Restore Y from stack", inline=True)
comment(0xFE5D, "Transfer to Y", inline=True)
comment(0xFE5E, "Restore A", inline=True)
comment(0xFE5F, "Return from NMI", inline=True)

# --- Data tables ---
comment(0xFE60, "Low bytes of transfer addr pointers", inline=True)
comment(0xFE68, "High bytes of transfer addr pointers", inline=True)
comment(0xFE70, "Low bytes of NMI handler addresses", inline=True)
comment(0xFE78, "High bytes of NMI handler addresses", inline=True)

# --- Wait for Tube R1 byte (&FE80) ---
comment(0xFE80, "Check Tube R1 for data", inline=True)
comment(0xFE83, "Data available: go read it", inline=True)
comment(0xFE85, "Check Tube R4 for pending transfers", inline=True)
comment(0xFE88, "Nothing pending: keep polling R1", inline=True)
comment(0xFE8A, "Save irq_a_store before IRQ", inline=True)
comment(0xFE8C, "Save processor status", inline=True)
comment(0xFE8D, "Allow one IRQ to service R4", inline=True)
comment(0xFE8E, "Restore processor status", inline=True)
comment(0xFE8F, "Restore irq_a_store after IRQ", inline=True)
comment(0xFE91, "Continue polling R1", inline=True)
comment(0xFE94, "Read byte from Tube R1", inline=True)
comment(0xFE97, "Return with byte in A", inline=True)

# --- Print embedded text (&FE98) ---
comment(0xFE98, "Pull return address low", inline=True)
comment(0xFE99, "Store in control_block_ptr low", inline=True)
comment(0xFE9B, "Pull return address high", inline=True)
comment(0xFE9C, "Store in control_block_ptr high", inline=True)
comment(0xFE9E, "Y=0 for indirect access", inline=True)
comment(0xFEA0, "Increment string pointer low", inline=True)
comment(0xFEA2, "No carry: skip high byte", inline=True)
comment(0xFEA4, "Increment string pointer high", inline=True)
comment(0xFEA6, "Read character from inline string", inline=True)
comment(0xFEA8, "Bit 7 set: end of string", inline=True)
comment(0xFEAA, "Print character via OSWRCH", inline=True)
comment(0xFEAD, "Loop for next character", inline=True)
comment(0xFEB0, "Resume execution after string", inline=True)

# --- NMI acknowledge (&FEB3) ---
comment(0xFEB3, "Write to Tube R3 to acknowledge NMI", inline=True)

# --- Spare/unused regions ---
comment(0xFEB7, "Unused fill between code and I/O window")
comment(0xFEF0, "Tube ULA I/O window: hardware registers")
comment(0xFEF0, "overlay these ROM addresses. The ROM")
comment(0xFEF0, "bytes here are never read by the CPU.")
comment(0xFF00, "Unused fill in lower page &FF. The reset")
comment(0xFF00, "code copies all of page &FF to RAM with")
comment(0xFF00, "LDA/STA &FF00,X but only &FF80 onwards")
comment(0xFF00, "contains the default vector table and")
comment(0xFF00, "MOS entry points.")

# --- Default vector table ---
comment(0xFF80, "Default MOS vector table (27 entries)", inline=True)

# --- MOS entry point stubs ---
comment(0xFFB6, "Vector table: length &36 at &FF80", inline=True)
comment(0xFFB9, "Unsupported: generates 'Bad' error", inline=True)
comment(0xFFC8, "Non-vectored RDCH", inline=True)
comment(0xFFCB, "Non-vectored WRCH", inline=True)
comment(0xFFCE, "Dispatch via FINDV", inline=True)
comment(0xFFD1, "Dispatch via GBPBV", inline=True)
comment(0xFFD4, "Dispatch via BPUTV", inline=True)
comment(0xFFD7, "Dispatch via BGETV", inline=True)
comment(0xFFDA, "Dispatch via ARGSV", inline=True)
comment(0xFFDD, "Dispatch via FILEV", inline=True)
comment(0xFFE0, "Dispatch via RDCHV", inline=True)
comment(0xFFE3, "Is it carriage return?", inline=True)
comment(0xFFE5, "No: skip newline, go to OSWRCH", inline=True)
comment(0xFFE7, "Send linefeed first", inline=True)
comment(0xFFE9, "Send linefeed via OSWRCH", inline=True)
comment(0xFFEC, "Load carriage return", inline=True)
comment(0xFFEE, "Dispatch via WRCHV", inline=True)
comment(0xFFF1, "Dispatch via WORDV", inline=True)
comment(0xFFF4, "Dispatch via BYTEV", inline=True)
comment(0xFFF7, "Dispatch via CLIV", inline=True)

# --- Hardware vectors ---
comment(0xFFFA, "NMI vector", inline=True)
comment(0xFFFC, "RESET vector", inline=True)
comment(0xFFFE, "IRQ/BRK vector", inline=True)

# =====================================================================
# Data declarations
# =====================================================================

# OSWORD 0 control block at &F95D
for addr in [0xF95D, 0xF95E, 0xF95F, 0xF960, 0xF961]:
    byte(addr)

# Spare space filled with &FF
# &FEB7-&FEEF: unused ROM fill between code and I/O window
for addr in range(0xFEB7, 0xFEF0):
    byte(addr)
# &FEF0-&FEF7: Tube ULA I/O window (hardware overlays these ROM addresses;
# the 8 bytes here precede the Tube register pairs at &FEF8-&FEFF)
for addr in range(0xFEF0, 0xFEF8):
    byte(addr)
# &FEF8-&FEFF: Tube register addresses (labelled individually above)
for addr in range(0xFEF8, 0xFF00):
    byte(addr)
# &FF00-&FF7F: unused fill in lower half of page &FF
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
# Each entry points to the address field to update for a given transfer type.
# Types 0-1 use self-modifying code; types 2-5 use zero-page data_transfer_addr;
# types 6-7 use self-modifying code in the 256-byte transfer routines.
_transfer_addr_ptrs = [
    "nmi0_transfer_addr",       # type 0: single byte to Tube
    "nmi1_transfer_addr",       # type 1: single byte from Tube
    "data_transfer_addr",       # type 2: two bytes to Tube
    "data_transfer_addr",       # type 3: two bytes from Tube
    "data_transfer_addr",       # type 4: (release)
    "data_transfer_addr",       # type 5: (release)
    "nmi6_transfer_addr",       # type 6: 256-byte write
    "nmi7_transfer_addr",       # type 7: 256-byte read
]
for i, name in enumerate(_transfer_addr_ptrs):
    byte(0xFE60 + i)
    expr(0xFE60 + i, f"<({name})")
    byte(0xFE68 + i)
    expr(0xFE68 + i, f">({name})")

# NMI routine address tables
# Each entry is the address of the NMI handler for a given transfer type.
_nmi_routines = [
    "nmi_single_byte_to_tube",    # type 0
    "nmi_single_byte_from_tube",  # type 1
    "nmi_two_bytes_to_tube",      # type 2
    "nmi_two_bytes_from_tube",    # type 3
    "nmi_acknowledge",            # type 4
    "nmi_acknowledge",            # type 5
    "nmi_acknowledge",            # type 6
    "nmi_acknowledge",            # type 7
]
for i, name in enumerate(_nmi_routines):
    byte(0xFE70 + i)
    expr(0xFE70 + i, f"<({name})")
    byte(0xFE78 + i)
    expr(0xFE78 + i, f">({name})")

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
