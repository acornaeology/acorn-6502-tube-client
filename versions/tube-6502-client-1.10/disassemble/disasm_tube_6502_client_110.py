"""Disassembly driver for Acorn 6502 Tube Client 1.10.

Configures dasmos to produce an annotated disassembly of the Tube Client ROM.
Run via:
  uv run python versions/tube-6502-client-1.10/disassemble/disasm_tube_6502_client_110.py

The physical ROM is 4 kB but only the upper 2 kB is mapped into the
65C02 address space at &F800-&FFFF. The lower 2 kB is not used.

This is the external 6502 second processor variant.
"""
import os
import tempfile
from pathlib import Path
import dasmos
from dasmos import Align
from dasmos.hooks import stringhi_hook
_script_dirpath = Path(__file__).resolve().parent
_version_dirpath = _script_dirpath.parent
_rom_filepath = os.environ.get('FANTASM_ROM', str(_version_dirpath / 'rom' / 'tube-6502-client-1.10.rom'))
_output_dirpath = Path(os.environ.get('FANTASM_OUTPUT_DIR', str(_version_dirpath / 'output')))
_full_rom = open(_rom_filepath, 'rb').read()
_upper_rom = _full_rom[2048:]
_tmp = tempfile.NamedTemporaryFile(suffix='.rom', delete=False)
_tmp.write(_upper_rom)
_tmp.close()
d = dasmos.Disassembler.create(cpu='65C02', auto_label_data_prefix='l', auto_label_code_prefix='c', auto_label_subroutine_prefix='sub_c', auto_label_loop_prefix='loop_c')
d.load(_tmp.name, 0xF800)
os.unlink(_tmp.name)
d.add_move(0x0100, 0xF859, 0x07)

d.label(0xF859, 'reloc_low_memory_src')

d.label(0x00EE, 'current_program')

d.label(0x00EF, 'current_program_hi')

d.label(0x00F0, 'hex_accumulator')

d.label(0x00F1, 'hex_accumulator_hi')

d.label(0x00F2, 'memory_top')

d.label(0x00F3, 'memory_top_hi')

d.label(0x00F4, 'transfer_addr_ptr')

d.label(0x00F5, 'transfer_addr_ptr_hi')

d.label(0x00F6, 'data_transfer_addr')

d.label(0x00F7, 'data_transfer_addr_hi')

d.label(0x00F8, 'string_ptr')

d.label(0x00F9, 'string_ptr_hi')

d.label(0x00FA, 'control_block_ptr')

d.label(0x00FB, 'control_block_ptr_hi')

d.label(0x00FC, 'irq_a_store')

d.label(0x00FD, 'last_error')

d.label(0x00FE, 'last_error_hi')

d.label(0x00FF, 'escape_flag')

d.label(0x0100, 'low_memory_code')

d.label(0x0103, 'irq_return_addr_lo')

d.label(0x0104, 'irq_return_addr_hi')

d.label(0x0200, 'userv')

d.label(0x0202, 'brkv')

d.label(0x0203, 'brkv_hi')

d.label(0x0204, 'irq1v')

d.label(0x0206, 'irq2v')

d.label(0x0208, 'cliv')

d.label(0x020A, 'bytev')

d.label(0x020C, 'wordv')

d.label(0x020E, 'wrchv')

d.label(0x0210, 'rdchv')

d.label(0x0212, 'filev')

d.label(0x0214, 'argsv')

d.label(0x0216, 'bgetv')

d.label(0x0218, 'bputv')

d.label(0x021A, 'gbpbv')

d.label(0x021C, 'findv')

d.label(0x0220, 'evntv')

d.label(0x0236, 'error_buffer')

d.label(0x0237, 'error_buffer_errnum')
d.hook_subroutine(0xFE98, 'print_embedded_text', stringhi_hook)
d.entry(0xF800)
d.entry(0x0100)
d.entry(0xF860)
d.entry(0xF88D)
d.entry(0xF8B5)
d.entry(0xF945)
d.entry(0xF962)
d.entry(0xF96C)
d.entry(0xF97D)
d.entry(0xF986)
d.entry(0xF9B2)
d.entry(0xF9CA)
d.entry(0xFA17)
d.entry(0xFA2E)
d.entry(0xFA5C)
d.entry(0xFA73)
d.entry(0xFAFF)
d.entry(0xFB77)
d.entry(0xFBCC)
d.entry(0xFC0C)
d.entry(0xFC2A)
d.entry(0xFC36)
d.entry(0xFC4A)
d.entry(0xFC53)
d.entry(0xFC8E)
d.entry(0xFCB7)
d.entry(0xFCE5)
d.entry(0xFCF0)
d.entry(0xFD18)
d.entry(0xFD3F)
d.entry(0xFD65)
d.entry(0xFE00)
d.entry(0xFE11)
d.entry(0xFE22)
d.entry(0xFE41)
d.entry(0xFE80)
d.entry(0xFEB3)
d.entry(0xFFB9)
d.entry(0xFFBC)
d.entry(0xFFBF)
d.entry(0xFFC2)
d.entry(0xFFC5)
d.entry(0xFFC8)
d.entry(0xFFCB)
d.entry(0xFFCE)
d.entry(0xFFD1)
d.entry(0xFFD4)
d.entry(0xFFD7)
d.entry(0xFFDA)
d.entry(0xFFDD)
d.entry(0xFFE0)
d.entry(0xFFE3)
d.entry(0xFFE7)
d.entry(0xFFEC)
d.entry(0xFFEE)
d.entry(0xFFF1)
d.entry(0xFFF4)
d.entry(0xFFF7)

d.label(0xF800, 'reset')

d.label(0xF860, 'startup_banner')

d.label(0xF88D, 'command_prompt')

d.label(0xF8A7, 'command_prompt_escape')

d.label(0xF8B5, 'enter_code')

d.label(0xF8FA, 'enter_raw_code')

d.label(0xF8FF, 'error_not_a_language')

d.label(0xF922, 'error_not_6502_code')

d.label(0xF945, 'error_handler')

d.label(0xF95D, 'rdline_control_block')

d.label(0xF962, 'oswrch_impl')

d.label(0xF96C, 'osrdch_impl')

d.label(0xF971, 'wait_carry_and_byte')

d.label(0xF975, 'wait_for_tube_r2_byte')

d.label(0xF97D, 'null_return')

d.label(0xF97F, 'skip_spaces')

d.label(0xF986, 'scan_hex')

d.label(0xF9B2, 'send_string')

d.label(0xF9B6, 'send_string_via_ptr')

d.label(0xF9CA, 'oscli_impl')

d.label(0xFA17, 'command_help')

d.label(0xFA2D, 'oscli_send_to_host')

d.label(0xFA35, 'oscli_wait_ack')

d.label(0xFA3E, 'command_go')

d.label(0xFA5C, 'execute_code')

d.label(0xFA71, 'check_oscli_ack')

d.label(0xFA73, 'osbyte_impl')

d.label(0xFA9C, 'osbyte_high')

d.label(0xFAF0, 'osbyte_read_himem')

d.label(0xFAFF, 'osword_impl')

d.label(0xFB77, 'rdline')

d.label(0xFBCC, 'osargs_impl')

d.label(0xFC0C, 'osfind_impl')

d.label(0xFC2A, 'osbget_impl')

d.label(0xFC36, 'osbput_impl')

d.label(0xFC4A, 'send_command')

d.label(0xFC4A, 'send_byte_to_tube_r2')

d.label(0xFC53, 'osfile_impl')

d.label(0xFC8E, 'osgbpb_impl')

d.label(0xFCB7, 'unsupported')

d.label(0xFCBC, 'osword_send_lengths')

d.label(0xFCD0, 'osword_recv_lengths')

d.label(0xFCE5, 'interrupt_handler')

d.label(0xFCF0, 'irq1_handler')

d.label(0xFD18, 'tube_r1_interrupt')

d.label(0xFD39, 'set_escape_flag')

d.label(0xFD3F, 'tube_r4_interrupt')

d.label(0xFD65, 'data_transfer_setup')

d.label(0xFDE7, 'restore_regs_and_rti')

d.label(0xFDEC, 'transfer_256_bytes_from_tube')

d.label(0xFE00, 'nmi_single_byte_to_tube')

d.label(0xFE11, 'nmi_single_byte_from_tube')

d.label(0xFE22, 'nmi_two_bytes_to_tube')

d.label(0xFE41, 'nmi_two_bytes_from_tube')

d.label(0xFE60, 'transfer_addr_ptr_table')

d.label(0xFE68, 'transfer_addr_ptr_hi_table')

d.label(0xFE70, 'nmi_routine_addr_table')

d.label(0xFE78, 'nmi_routine_addr_hi_table')

d.label(0xFE80, 'wait_for_tube_r1_byte')

d.label(0xFE98, 'print_embedded_text')

d.label(0xFEB3, 'nmi_acknowledge')

d.label(0xFFB6, 'vector_table_info')

d.label(0xFFB9, 'mos_stub_unsupported_1')

d.label(0xFFBC, 'mos_stub_unsupported_2')

d.label(0xFFBF, 'mos_stub_unsupported_3')

d.label(0xFFC2, 'mos_stub_unsupported_4')

d.label(0xFFC5, 'mos_stub_unsupported_5')

d.label(0xFFC8, 'nvrdch')

d.label(0xFFCB, 'nvwrch')

d.label(0xFFCE, 'osfind_entry')

d.label(0xFFD1, 'osgbpb_entry')

d.label(0xFFD4, 'osbput_entry')

d.label(0xFFD7, 'osbget_entry')

d.label(0xFFDA, 'osargs_entry')

d.label(0xFFDD, 'osfile_entry')

d.label(0xFFE0, 'osrdch_entry')

d.label(0xFFE3, 'osasci_entry')

d.label(0xFFE7, 'osnewl_entry')

d.label(0xFFEC, 'oswrcr_entry')

d.label(0xFFEE, 'oswrch_entry')

d.label(0xFFF1, 'osword_entry')

d.label(0xFFF4, 'osbyte_entry')

d.label(0xFFF7, 'oscli_entry')

d.label(0xFFFA, 'nmi_vector')

d.label(0xFFFC, 'reset_vector')

d.label(0xFFFE, 'irq_vector')

d.label(0xFF80, 'default_vector_table')

d.label(0xFE02, 'nmi0_transfer_addr')

d.label(0xFE16, 'nmi1_transfer_addr')

d.label(0xFDD7, 'nmi6_transfer_addr')

d.label(0xFDF9, 'nmi7_transfer_addr')

d.label(0xF802, 'copy_page_ff_loop')

d.label(0xF80D, 'copy_vectors_loop')

d.label(0xF819, 'copy_io_page_loop')

d.label(0xF82A, 'copy_rom_page')

d.label(0xF83B, 'copy_startup_code_loop')

d.label(0xF85D, 'soft_reset_jmp')

d.label(0xF94D, 'print_error_loop')

d.label(0xF957, 'print_error_done')

d.label(0xF98C, 'scan_hex_next_char')

d.label(0xF9A0, 'scan_hex_got_digit')

d.label(0xF9A6, 'scan_hex_shift_loop')

d.label(0xF9B1, 'scan_hex_return')

d.label(0xF9B8, 'send_string_loop')

d.label(0xF9D1, 'oscli_skip_stars_loop')

d.label(0xFA71, 'osbyte_check_ack')

d.label(0xFA7A, 'osbyte_low_wait_r2_1')

d.label(0xFA82, 'osbyte_low_wait_r2_2')

d.label(0xFA8B, 'osbyte_low_wait_r2_3')

d.label(0xFA93, 'osbyte_low_wait_result')

d.label(0xFAAB, 'osbyte_high_wait_r2_1')

d.label(0xFAB3, 'osbyte_high_wait_r2_2')

d.label(0xFABB, 'osbyte_high_wait_r2_3')

d.label(0xFAC4, 'osbyte_high_wait_r2_4')

d.label(0xFAD5, 'osbyte_high_wait_carry')

d.label(0xFADF, 'osbyte_high_wait_y')

d.label(0xFAE7, 'osbyte_high_wait_x')

d.label(0xFAEF, 'osbyte_high_return')

d.label(0xFAF4, 'osbyte_himem_rts')

d.label(0xFB09, 'osword_wait_r2_cmd')

d.label(0xFB11, 'osword_wait_r2_func')

d.label(0xFB24, 'osword_send_low_lookup')

d.label(0xFB2D, 'osword_send_block')

d.label(0xFB38, 'osword_send_bytes_loop')

d.label(0xFB45, 'osword_recv_get_length')

d.label(0xFB50, 'osword_recv_low_lookup')

d.label(0xFB59, 'osword_recv_block')

d.label(0xFB64, 'osword_recv_bytes_loop')

d.label(0xFB71, 'osword_restore_regs')

d.label(0xFB7E, 'rdline_send_block_loop')

d.label(0xFB96, 'rdline_send_addr_low')

d.label(0xFBB2, 'rdline_recv_loop')

d.label(0xFBC7, 'rdline_escape')

d.label(0xFBD2, 'osargs_wait_r2_handle')

d.label(0xFC24, 'osfind_open')

d.label(0xFC5F, 'osfile_send_block_loop')

d.label(0xFC7E, 'osfile_recv_block_loop')

d.label(0xFC9A, 'osgbpb_send_block_loop')

d.label(0xFCA8, 'osgbpb_recv_block_loop')

d.label(0xFCFD, 'brk_handler_entry')

d.label(0xFD36, 'dispatch_event')

d.label(0xFD45, 'tube_r4_wait_error')

d.label(0xFD59, 'tube_r4_read_error_loop')

d.label(0xFD83, 'transfer_wait_id')

d.label(0xFD93, 'transfer_read_addr4')

d.label(0xFD9B, 'transfer_read_addr3')

d.label(0xFDA3, 'transfer_read_addr2')

d.label(0xFDAE, 'transfer_read_addr1')

d.label(0xFDBE, 'transfer_wait_sync')

d.label(0xFDCF, 'transfer_write_loop')

d.label(0xFDDF, 'transfer_write_sync')

d.label(0xFDEE, 'transfer_read_loop')

d.label(0xFDFE, 'transfer_read_done')

d.label(0xFE0F, 'nmi0_done')

d.label(0xFE20, 'nmi1_done')

d.label(0xFE32, 'nmi2_second_byte')

d.label(0xFE3D, 'nmi2_done')

d.label(0xFE51, 'nmi3_second_byte')

d.label(0xFE5C, 'nmi3_done')

d.label(0xFE94, 'tube_r1_read_byte')

d.label(0xFEA0, 'print_text_loop')

d.label(0xFEA6, 'print_text_get_char')

d.label(0xFEB0, 'print_text_resume')

d.label(0xFEA4, 'print_text_inc_high')

d.label(0x0000, 'zp_data_base')

d.label(0x0001, 'zp_data_base_1')

d.label(0x0002, 'zp_data_base_2')

d.label(0x0003, 'zp_data_base_3')

d.label(0xF85E, 'soft_reset_jmp_lo')

d.label(0xF85F, 'soft_reset_jmp_hi')

d.label(0xFDFF, 'io_page_base')

d.label(0xFFFB, 'nmi_vector_hi')

d.label(0xFEF8, 'tube_r1_status')

d.label(0xFEF9, 'tube_r1_data')

d.label(0xFEFA, 'tube_r2_status')

d.label(0xFEFB, 'tube_r2_data')

d.label(0xFEFC, 'tube_r3_status')

d.label(0xFEFD, 'tube_r3_data')

d.label(0xFEFE, 'tube_r4_status')

d.label(0xFEFF, 'tube_r4_data')

d.label(0xFAF9, 'osbyte_lomem_rts')

d.label(0xFDD6, 'transfer_write_read_byte')

d.label(0xFDF8, 'transfer_read_store_byte')

d.label(0xFE01, 'nmi0_read_byte')

d.label(0xFFFF, 'irq_vector_hi')


d.subroutine(0xF800, 'reset', title='Power-on reset', description="""Initialise the 65C02 parasite processor.

Copies the ROM contents to RAM, sets up the default MOS
vectors, clears the escape flag, and jumps via low memory
to page out the ROM and start the operating system.""")


d.subroutine(0x0100, 'low_memory_startup_code', title='Low memory startup code (relocated from ROM at reloc_low_memory_src)', description="""Copied from ROM to &0100 by the reset routine.

Reads Tube R1 status to page out the ROM, enables
interrupts, then jumps to display the startup banner.
On subsequent soft resets, the JMP target at &F85E is
patched to skip the banner and enter the command prompt
directly.""")


d.subroutine(0xF860, 'startup_banner', title='Display startup banner and initialise', description="""Print the startup banner, patch the soft reset entry
to skip the banner on future resets, then wait for the
host's acknowledge byte.

If the acknowledge has bit 7 set, the host is requesting
code execution; otherwise enters the command prompt.""")


d.subroutine(0xF88D, 'command_prompt', title='Command prompt loop', description="""The main supervisor command prompt.

Prints a '*' prompt, reads a line of input using
OSWORD 0, and passes it to OSCLI for execution.
Handles Escape by acknowledging it and reporting
the error.""")


d.subroutine(0xF8B5, 'enter_code', title='Enter code at transfer address', description="""Check whether the code at the data transfer address
has a valid ROM header with a (C) string, and if so
verify it is a 6502 language ROM.

Sets the current program and memory top to the
transfer address, then enters the code with A=1.
If the header is missing or invalid, enters with A=1
anyway (raw code entry). Generates an error if the
ROM type indicates it is not a language or not 6502
code.

Note: the v1.10 ROM always enters with A=1 regardless
of whether it is a RESET or OSCLI entry, and does not
pass the carry flag. J.G. Harston identifies this as a bug.""")


d.subroutine(0xF8FA, 'enter_raw_code', title='Enter raw code', description="""Enter code at the transfer address without a valid
ROM header. Loads A=1 and jumps via the memory top
pointer (which has been set to the transfer address).

Note: J.G. Harston identifies a bug where raw code should be
entered with A=0, and the carry should indicate
whether the entry is from RESET or OSCLI.""")


d.subroutine(0xF8FF, 'error_not_a_language', title="Generate 'not a language' error", description="""Set up the BRK vector to point to the default error
handler, then generate error 0: 'This is not a
language'. The error handler must be re-established
here because the previous language's handler will
have been overwritten.""")


d.subroutine(0xF922, 'error_not_6502_code', title="Generate 'not 6502 code' error", description="""Set up the BRK vector to point to the default error
handler, then generate error 0: 'I cannot run this
code'. Called when the ROM type indicates the code is
not suitable for a 6502 processor.""")


d.subroutine(0xF945, 'error_handler', title='Error handler', description="""Default BRK handler. Clears the stack, prints the
error message from the BRK instruction, and returns
to the command prompt.""")


d.subroutine(0xF95D, 'rdline_control_block', title='OSWORD 0 control block', description="""Parameter block passed to OSWORD 0 (read line) when reading
input at the supervisor command prompt. Specifies where to
store the input text, the buffer size, and the range of
acceptable character codes.""")


d.subroutine(0xF962, 'oswrch_impl', title='OSWRCH implementation', description='Send character in A to the host via Tube R1.', on_entry={'A': 'character to send'}, on_exit={'A': 'preserved'})


d.subroutine(0xF96C, 'osrdch_impl', title='OSRDCH implementation', description="""Read a character from the host via the Tube.

Sends command &00 to the host, then waits for
a carry byte and the character.""", on_exit={'A': 'character received', 'C': 'Escape flag'})


d.subroutine(0xF971, 'wait_carry_and_byte', title='Wait for carry byte and data byte', description="""Wait for two bytes from Tube R2: first a carry
indicator, then the data byte.

The carry byte is shifted left so bit 7 moves into
the carry flag, then falls through to read the
actual data byte.""", on_exit={'A': 'data byte from Tube R2', 'C': 'carry indicator from host'})


d.subroutine(0xF975, 'wait_for_tube_r2_byte', title='Wait for byte from Tube R2', description="""Poll Tube R2 status until data is available, then
read and return the byte.""", on_exit={'A': 'byte read from Tube R2'})


d.subroutine(0xF97D, 'null_return', title='Null return', description="""An RTS used as a no-op handler for vectors that have
no action (EVNTV, IND1V-IND3V in the default table).""")


d.subroutine(0xF97E, 'skip_spaces_step', title='Advance and skip spaces in command string', description="""Increment Y then fall through to skip_spaces. Called
when the current character has been consumed and any
following spaces should be skipped.""", on_entry={'Y': 'offset of the character just consumed'}, on_exit={'A': 'first non-space character after skipped spaces', 'Y': 'offset of that character'})


d.subroutine(0xF97F, 'skip_spaces', title='Skip spaces in command string', description='Advance past space characters in the string at (string_ptr),Y.', on_entry={'Y': 'current offset into string'}, on_exit={'A': 'first non-space character', 'Y': 'offset of that character'})


d.subroutine(0xF986, 'scan_hex', title='Parse hexadecimal number', description="""Read a hexadecimal number from the string at
(string_ptr),Y into the hex accumulator at &F0/F1.""", on_entry={'Y': 'offset into string'}, on_exit={'hex_accumulator': 'parsed value (low byte)', 'hex_accumulator_hi': 'parsed value (high byte)', 'X': 'non-zero if any digits were parsed', 'Y': 'offset past last hex digit', 'A': 'first non-hex character'})


d.subroutine(0xF9B2, 'send_string', title='Send string to Tube R2', description='Send a CR-terminated string to the host via Tube R2.', on_entry={'X': 'string address low byte', 'Y': 'string address high byte'}, on_exit={'Y': 'restored from string_ptr_hi'})


d.subroutine(0xF9CA, 'oscli_impl', title='OSCLI implementation', description="""Execute a * command. Parses the command to check for
*GO and *HELP which are handled locally; all other
commands are forwarded to the host via the Tube.""", on_entry={'X': 'command string address low byte', 'Y': 'command string address high byte'})


d.subroutine(0xFA17, 'command_help', title='Handle *HELP command', description="""Print local help text showing the Tube Client
version, then fall through to forward the *HELP
command to the host.""")


d.subroutine(0xFA2D, 'oscli_send_to_host', title='Send OSCLI command to host', description="""Forward the command string at (string_ptr) to the
host via Tube R2 with command code &02.

Tube protocol: &02 string &0D -- &7F or &80

If the response has bit 7 set, code needs to be
entered (a language was selected).""")


d.subroutine(0xFA35, 'oscli_wait_ack', title='Wait for OSCLI acknowledgement', description="""Wait for the host's response byte after sending an
OSCLI command. If the response has bit 7 set (&80),
the host has selected a language and code needs to be
entered at the transfer address. Otherwise restore A
and return to the caller.

Also used by OSBYTE &8E (select language) via the
check at osbyte_check_ack.""")


d.subroutine(0xFA3E, 'command_go', title='Handle *GO command', description="""Parse *GO [address]. If an address is given, set the
transfer address to it. If no address given, use the
current transfer address. Falls through to execute
the code.

Note: does not check for a separator after 'GO', so
commands like *GOAD would be incorrectly matched.
J.G. Harston identifies this as a bug.""")


d.subroutine(0xFA5C, 'execute_code', title='Execute code and restore state', description="""Save the current program pointer, call enter_code,
then restore the current program and memory top
on return.

Note: in v1.10, the carry flag is not explicitly set
before calling enter_code, so entered code cannot
reliably distinguish RESET from OSCLI entry. J.G. Harston
identifies this as a bug.""")


d.subroutine(0xFA71, 'check_oscli_ack', title='Check OSCLI acknowledgement (OSBYTE &8E path)', description="""Entry point used by OSBYTE &8E (select language).
If the function matched &8E, branches to wait for
the OSCLI acknowledgement byte from the host, which
may trigger code entry.""")


d.subroutine(0xFA73, 'osbyte_impl', title='OSBYTE implementation', description="""Handle OSBYTE calls. Functions &82-&84 are handled
locally (memory high word, bottom/top of memory).
Low functions (A < &80) send command &04 with X and A.
High functions send command &06 with X, Y, and A.

Special handling for OSBYTE &8E (select language) which
checks for code to enter, and &9D (fast BPUT) which
returns immediately without waiting for a response.""", on_entry={'A': 'function', 'X': 'parameter 1', 'Y': 'parameter 2'}, on_exit={'A': 'preserved', 'X': 'returned value (for A >= &80)', 'Y': 'returned value (for A >= &80)', 'C': 'returned value (for A >= &80)'})


d.subroutine(0xFAF0, 'osbyte_read_himem', title='OSBYTE &84: read top of memory', description="""Return the current top of user memory from &F2/F3.
Falls through to the RTS at osbyte_himem_rts.""", on_exit={'X': 'memory_top low byte', 'Y': 'memory_top high byte'})


d.subroutine(0xFAF5, 'osbyte_read_lomem', title='OSBYTE &83: read bottom of memory', description="""Return the bottom of user memory, fixed at &0800.
Shares its RTS with osbyte_read_high_word.""", on_exit={'X': '&00', 'Y': '&08'})


d.subroutine(0xFAFA, 'osbyte_read_high_word', title='OSBYTE &82: read machine high order address', description="""Return &0000 as the high word of the address space.
This indicates the 6502 has a 16-bit address space
with no bank switching.""", on_exit={'X': '&00', 'Y': '&00'})


d.subroutine(0xFAFF, 'osword_impl', title='OSWORD implementation', description="""Handle OSWORD calls. OSWORD 0 (read line) is handled
specially via rdline. All other functions send the
control block to the host and receive the response,
with block sizes determined by lookup tables.""", on_entry={'A': 'function', 'XY': 'control block address'})


d.subroutine(0xFB77, 'rdline', title='Read line of input (OSWORD 0)', description="""Read a line of text from the host.

Sends command &0A with the control block parameters,
then receives the input string character by character.

Tube protocol: &0A block -- &FF or &7F string &0D""", on_exit={'Y': 'length of string (excluding CR)', 'C': '0 if OK, 1 if Escape'})


d.subroutine(0xFBCC, 'osargs_impl', title='OSARGS implementation', description="""Read or write information about an open file.

Sends command &0C with handle, 4-byte data word,
and function code. Receives result and updated data.""", on_entry={'A': 'function', 'X': 'zero-page data word address', 'Y': 'handle'}, on_exit={'A': 'result', 'data word at X': 'updated'})


d.subroutine(0xFC0C, 'osfind_impl', title='OSFIND implementation', description="""Open or close a file.

For close (A=0): sends command &12, function, handle.
For open (A<>0): sends command &12, function, filename.""", on_entry={'A': 'function', 'XY': 'filename address (open) or Y = handle (close)'}, on_exit={'A': 'handle (open) or preserved (close)'})


d.subroutine(0xFC2A, 'osbget_impl', title='OSBGET implementation', description="""Read a byte from an open file.

Sends command &0E with handle, waits for carry and byte.""", on_entry={'Y': 'handle'}, on_exit={'A': 'byte read', 'C': 'set if EOF'})


d.subroutine(0xFC36, 'osbput_impl', title='OSBPUT implementation', description="""Write a byte to an open file.

Sends command &10 with handle and byte.""", on_entry={'A': 'byte', 'Y': 'handle'}, on_exit={'A': 'preserved'})


d.subroutine(0xFC4A, 'send_command', title='Send byte to Tube R2', description='Wait for Tube R2 to be free, then send byte.', on_entry={'A': 'byte to send'}, on_exit={'A': 'preserved'})


d.subroutine(0xFC53, 'osfile_impl', title='OSFILE implementation', description="""Operate on whole files (load, save, read/write attributes).

Sends command &14 with 16-byte control block, filename,
and function code. Receives result and updated control block.""", on_entry={'A': 'function', 'XY': 'control block address'})


d.subroutine(0xFC8E, 'osgbpb_impl', title='OSGBPB implementation', description="""Multiple byte read and write.

Sends command &16 with 13-byte control block and function.
Receives updated control block, carry, and result.""", on_entry={'A': 'function', 'XY': 'control block address'})


d.subroutine(0xFCB7, 'unsupported', title='Unsupported MOS call', description="""Generate a 'Bad' error for unsupported MOS calls.
Used as the default handler for USERV, IRQ2V, FSCV,
and several other vectors that have no parasite-side
implementation.""")


d.subroutine(0xFCBC, 'osword_send_lengths', title='OSWORD send block length table', description="""Indexed by OSWORD number via LDY table,X where X is
the OSWORD function. Entry 0 is never used because
OSWORD 0 (RDLINE) is handled separately. Entries
1-20 give the number of bytes to send from the
control block to the host for each OSWORD function.
Functions above &14 (20) default to sending 16 bytes.

For functions >= &80, the send length is taken from
byte 0 of the control block instead of this table.""")


d.subroutine(0xFCD0, 'osword_recv_lengths', title='OSWORD receive block length table', description="""Indexed by OSWORD number via LDY table,X. Gives the
number of bytes to receive back from the host into
the control block. Entries 1-20 correspond to OSWORD
functions &01-&14. Functions above &14 default to
receiving 16 bytes.

The first byte (&80) is shared: it serves as both
the OSWORD &14 send length (meaning the length is in
the control block) and the unused recv slot 0.

For functions >= &80, the receive length is taken from
byte 1 of the control block instead of this table.""")


d.subroutine(0xFCE5, 'interrupt_handler', title='Interrupt handler entry', description="""Hardware interrupt entry point. Saves A, checks the
break flag in the stacked processor status to distinguish
BRK from IRQ, and dispatches accordingly.""")


d.subroutine(0xFCF0, 'irq1_handler', title='IRQ1 handler', description="""First-level IRQ handler. Checks Tube R4 for data
transfer requests, then Tube R1 for escape/event
notifications. Falls through to IRQ2V if neither.""")


d.subroutine(0xFCFD, 'brk_handler_entry', title='BRK handler dispatch', description="""Extract the return address from the stack, subtract 1
to point to the byte after the BRK opcode (the error
block), store the pointer in last_error (&FD/FE),
then re-enable interrupts and dispatch via BRKV.""")


d.subroutine(0xFD18, 'tube_r1_interrupt', title='Handle Tube R1 interrupt (escape and events)', description="""Process data received via Tube R1. If bit 7 is set,
it is an Escape state change (stored in escape_flag).
Otherwise, it is an event notification: reads the
event parameters (Y, X, event number) from R1 and
dispatches via EVNTV.""")


d.subroutine(0xFD39, 'set_escape_flag', title='Set escape flag from Tube R1 data', description="""Called when Tube R1 data has bit 7 set, indicating
an Escape state change. Shifts bit 6 of the received
byte into bit 7 via ASL and stores the result in
escape_flag (&FF). Bit 7 set = Escape active.""")


d.subroutine(0xFD3F, 'tube_r4_interrupt', title='Handle Tube R4 interrupt', description="""Process data received via Tube R4. If bit 7 is set,
it is an error from the host: reads the error number
and message via R2 into the error buffer, then
executes the error via a JMP to the buffer (which
starts with a BRK opcode).

If bit 7 is clear, it is a data transfer request:
falls through to data_transfer_setup.""")


d.subroutine(0xFD65, 'data_transfer_setup', title='Set up data transfer via NMI', description="""Configure the NMI handler for a data transfer.

The transfer type (0-7) from R4 selects the NMI
routine and the address pointer. Types 0-3 are
single/double byte transfers. Types 4-5 are release.
Types 6-7 are 256-byte block transfers.

The setup phase consumes 7 bytes on R4 in this order:
transfer type, called ID, address bytes 4/3/2/1 (only
the low two are stored, via transfer_addr_ptr), then a
sync byte. The transfer type byte has already been read
by tube_r4_interrupt before falling through here; the
other 6 are read below. Between the last address byte
and the sync wait, two bytes are drained from R3 in the
H-to-P direction via BIT tube_r3_data.

No bytes are written to R3 during setup: any P-to-H R3
write happens later, from the NMI handler selected by
the transfer type. For transfer types 0-5 the routine
exits via RTI after the sync byte; for type 6 it runs
transfer_write_loop to send 256 bytes to R3, and for
type 7 it runs transfer_256_bytes_from_tube to read 256
bytes from R3.

The sync byte is the final step of the host-side Tube
handshake: the host writes it only once it is ready to
begin the data phase. The parasite blocks in the BIT/BPL
loop at transfer_wait_sync until bit 7 of R4 status is
set, so if the sync byte is never written the parasite
spins here indefinitely.""")


d.subroutine(0xFDE7, 'restore_regs_and_rti', title='Restore registers and return from interrupt', description="""Common exit path for data transfer setup. Restores Y
from the stack, retrieves saved A from irq_a_store,
and executes RTI.""")


d.subroutine(0xFDEC, 'transfer_256_bytes_from_tube', title='Transfer 256 bytes from Tube via R3', description="""Read 256 bytes from Tube R3 into memory at the
address patched into the STA instruction. Used for
transfer type 7 (256-byte read from host).

The target address is set up by data_transfer_setup
via the transfer address pointer table.""")


d.subroutine(0xFE00, 'nmi_single_byte_to_tube', title='NMI: single byte to Tube', description="""Transfer type 0. Sends one byte from the transfer
address to Tube R3, then increments the address.""")


d.subroutine(0xFE11, 'nmi_single_byte_from_tube', title='NMI: single byte from Tube', description="""Transfer type 1. Reads one byte from Tube R3 and
stores it at the transfer address, then increments
the address.""")


d.subroutine(0xFE22, 'nmi_two_bytes_to_tube', title='NMI: two bytes to Tube', description="""Transfer type 2. Sends two consecutive bytes from
(data_transfer_addr) to Tube R3, incrementing the
pointer after each byte.""")


d.subroutine(0xFE41, 'nmi_two_bytes_from_tube', title='NMI: two bytes from Tube', description="""Transfer type 3. Reads two bytes from Tube R3 and
stores them at (data_transfer_addr), incrementing
the pointer after each byte.""")


d.subroutine(0xFE60, 'transfer_addr_ptr_table', title='Transfer address pointer table (low bytes)', description="""Eight entries indexed by transfer type (0-7). Each
entry is the low byte of the address of the two-byte
field that holds the current transfer address for
that type. Types 0-1 and 6-7 point to self-modifying
code address operands; types 2-5 point to the
data_transfer_addr zero page location (&F6).""")


d.subroutine(0xFE68, 'transfer_addr_ptr_hi_table', title='Transfer address pointer table (high bytes)', description="""High bytes corresponding to the low byte table at
&FE60. Together they form 8 pointers to the address
fields used by each transfer type.""")


d.subroutine(0xFE70, 'nmi_routine_addr_table', title='NMI routine address table (low bytes)', description="""Eight entries indexed by transfer type (0-7). Each
entry is the low byte of the NMI handler routine
for that type. Types 0-3 have dedicated handlers;
types 4-7 all use the NMI acknowledge routine.""")


d.subroutine(0xFE78, 'nmi_routine_addr_hi_table', title='NMI routine address table (high bytes)', description="""High bytes corresponding to the low byte table at
&FE70. Together they form 8 NMI handler addresses.""")


d.subroutine(0xFE80, 'wait_for_tube_r1_byte', title='Wait for byte in Tube R1', description="""Wait for data in Tube R1, allowing Tube R4 transfer
requests to be serviced via IRQ while waiting.

Polls R1 status; if R4 has data instead, briefly
enables interrupts to let the R4 handler run, then
resumes polling R1.""", on_exit={'A': 'byte from Tube R1'})


d.subroutine(0xFE98, 'print_embedded_text', title='Print inline text', description="""Print the text string embedded immediately after the
JSR to this routine. Characters are sent to OSWRCH
until a byte with bit 7 set is encountered, which
terminates the string.

Execution resumes by jumping directly to the address
of the terminator byte, so the terminator is executed
as a 6502 instruction. This is why NOP (&EA) is used:
bit 7 is set (ending the string loop), it is a single-
byte opcode (no operand to skip), and it has no effect
when executed. This saves the bytes and cycles that
would otherwise be needed to increment the pointer
past the terminator before returning.""", on_exit={'A': 'terminator byte (bit 7 set)'})


d.subroutine(0xFEB3, 'nmi_acknowledge', title='NMI acknowledge', description="""Acknowledge an NMI by writing A to Tube R3, then
return from interrupt. Used as the NMI handler for
transfer types 4-7 (release and 256-byte block
transfers, which do not use NMI for individual
bytes). Also the initial value of the NMI vector
at reset.""")


d.subroutine(0xFEB7, 'unused_fill_pre_io', title='Unused fill between code and I/O window', description="""39 bytes of &FF fill between the end of the NMI
acknowledge routine and the start of the Tube ULA
I/O register window at &FEF0.""")


d.subroutine(0xFEF0, 'tube_ula_io_window', title='Tube ULA I/O window', description="""Hardware registers overlay these ROM addresses.
The ROM bytes here are never read by the CPU.
The registers at &FEF0-&FEF7 mirror &FEF8-&FEFF
but are not used by the Tube Client software.""")


d.subroutine(0xFF00, 'unused_fill_page_ff', title='Unused fill in lower page &FF', description="""The reset code copies all of page &FF to RAM with
LDA/STA &FF00,X but only &FF80 onwards contains the
default vector table and MOS entry points.""")


d.subroutine(0xFF80, 'default_vector_table', title='Default MOS vector table', description="""27 two-byte entries (54 bytes) copied to &0200-&0235
at reset. Each entry is the initial value for the
corresponding MOS vector. Vectors for unimplemented
functions point to the 'unsupported' error handler;
unused event and indirect vectors point to
null_return (RTS).""")


d.subroutine(0xFFB6, 'vector_table_info', title='Vector table descriptor', description="""Three-byte block at &FFB6 used by OSBYTE &FD
(read vector table info). Byte 0 = length of the
vector table in bytes (&36 = 54 = 27 vectors).
Bytes 1-2 = address of the default vector table
(&FF80).""")


d.subroutine(0xFFB9, 'mos_stub_unsupported_1', title='MOS entry: unsupported (5 stubs at &FFB9-&FFC7)', description="""Five consecutive JMP unsupported stubs at &FFB9,
&FFBC, &FFBF, &FFC2, &FFC5. In the v1.10 external
ROM, all five generate a 'Bad' error. These
addresses are reserved for MOS compatibility but
have no function in this Tube Client.""")


d.subroutine(0xFFC8, 'nvrdch', title='MOS entry: NVRDCH (non-vectored RDCH)', description="""Jump directly to the OSRDCH implementation,
bypassing RDCHV. Used when the caller needs to
ensure the real RDCH handler runs regardless of
any vector interception.""")


d.subroutine(0xFFCB, 'nvwrch', title='MOS entry: NVWRCH (non-vectored WRCH)', description="""Jump directly to the OSWRCH implementation,
bypassing WRCHV. Used when the caller needs to
ensure the real WRCH handler runs regardless of
any vector interception.""")


d.subroutine(0xFFCE, 'osfind_entry', title='MOS entry: OSFIND', description='Open or close a file. Dispatches via FINDV (&021C).', on_entry={'A': '0 to close, non-zero to open', 'Y': 'handle (close) or XY => filename (open)'}, on_exit={'A': 'file handle (open) or preserved (close)'})


d.subroutine(0xFFD1, 'osgbpb_entry', title='MOS entry: OSGBPB', description='Multiple-byte get or put. Dispatches via GBPBV (&021A).', on_entry={'A': 'function', 'XY': '13-byte control block address'})


d.subroutine(0xFFD4, 'osbput_entry', title='MOS entry: OSBPUT', description='Write a byte to an open file. Dispatches via BPUTV (&0218).', on_entry={'A': 'byte to write', 'Y': 'file handle'})


d.subroutine(0xFFD7, 'osbget_entry', title='MOS entry: OSBGET', description='Read a byte from an open file. Dispatches via BGETV (&0216).', on_entry={'Y': 'file handle'}, on_exit={'A': 'byte read', 'C': 'set if EOF'})


d.subroutine(0xFFDA, 'osargs_entry', title='MOS entry: OSARGS', description='Read or write open file arguments. Dispatches via ARGSV (&0214).', on_entry={'A': 'function', 'X': 'zero-page data word address', 'Y': 'handle'})


d.subroutine(0xFFDD, 'osfile_entry', title='MOS entry: OSFILE', description='Whole-file operations. Dispatches via FILEV (&0212).', on_entry={'A': 'function', 'XY': '18-byte control block address'})


d.subroutine(0xFFE0, 'osrdch_entry', title='MOS entry: OSRDCH', description='Read a character from the input stream. Dispatches via RDCHV (&0210).', on_exit={'A': 'character', 'C': 'set if Escape'})


d.subroutine(0xFFE3, 'osasci_entry', title='MOS entry: OSASCI', description="""Write a character, converting CR to CR+LF. If the
character is &0D, falls through to OSNEWL to send
LF then CR. Otherwise jumps directly to OSWRCH.""", on_entry={'A': 'character to write'})


d.subroutine(0xFFE7, 'osnewl_entry', title='MOS entry: OSNEWL', description="""Send a newline sequence (LF followed by CR) via OSWRCH.
Loads A=&0A, calls OSWRCH, then falls through to
OSWRCR which loads A=&0D and calls OSWRCH.""")


d.subroutine(0xFFEC, 'oswrcr_entry', title='MOS entry: OSWRCR', description="""Send a carriage return via OSWRCH. Loads A=&0D and
falls through to OSWRCH.""")


d.subroutine(0xFFEE, 'oswrch_entry', title='MOS entry: OSWRCH', description='Write a character to the output stream. Dispatches via WRCHV (&020E).', on_entry={'A': 'character to write'}, on_exit={'A': 'preserved'})


d.subroutine(0xFFF1, 'osword_entry', title='MOS entry: OSWORD', description='Perform a word-based MOS operation. Dispatches via WORDV (&020C).', on_entry={'A': 'function', 'XY': 'control block address'})


d.subroutine(0xFFF4, 'osbyte_entry', title='MOS entry: OSBYTE', description='Perform a byte-based MOS operation. Dispatches via BYTEV (&020A).', on_entry={'A': 'function', 'X': 'parameter 1', 'Y': 'parameter 2'})


d.subroutine(0xFFF7, 'oscli_entry', title='MOS entry: OSCLI', description='Execute a star command. Dispatches via CLIV (&0208).', on_entry={'XY': 'command string address (CR-terminated)'})
d.comment(0xF800, 'Start copy index at 0', align=Align.INLINE)
d.comment(0xF802, 'Read byte from page &FF of ROM', align=Align.INLINE)
d.comment(0xF805, 'Copy to RAM (vectors + MOS entries)', align=Align.INLINE)
d.comment(0xF808, 'Next byte', align=Align.INLINE)
d.comment(0xF809, 'Loop until all 256 bytes copied', align=Align.INLINE)
d.comment(0xF80B, '54 bytes = 27 default vector entries', align=Align.INLINE)
d.comment(0xF80D, 'Read default vector value', align=Align.INLINE)
d.comment(0xF810, 'Write to MOS vector table', align=Align.INLINE)
d.comment(0xF813, 'Next entry', align=Align.INLINE)
d.comment(0xF814, 'Loop until all vectors set', align=Align.INLINE)
d.comment(0xF816, 'Clear the stack (X=&FF from loop)', align=Align.INLINE)
d.comment(0xF817, 'X=&F0: copy &FE00-&FEEF to RAM', align=Align.INLINE)
d.comment(0xF819, 'Read ROM byte below Tube I/O window', align=Align.INLINE)
d.comment(0xF81C, 'Copy to RAM', align=Align.INLINE)
d.comment(0xF81F, 'Next byte', align=Align.INLINE)
d.comment(0xF820, 'Loop until &FE00-&FEEF copied', align=Align.INLINE)
d.comment(0xF822, 'Y=0 for page offset', align=Align.INLINE)
d.comment(0xF824, 'Point string_ptr low to &00', align=Align.INLINE)
d.comment(0xF826, 'High byte = &F8 (start of ROM)', align=Align.INLINE)
d.comment(0xF828, 'Set string_ptr to &F800', align=Align.INLINE)
d.comment(0xF82A, 'Read byte from ROM page', align=Align.INLINE)
d.comment(0xF82C, 'Write to RAM (self-copy)', align=Align.INLINE)
d.comment(0xF82E, 'Next byte in page', align=Align.INLINE)
d.comment(0xF82F, 'Loop until 256 bytes copied', align=Align.INLINE)
d.comment(0xF831, 'Move to next page', align=Align.INLINE)
d.comment(0xF833, 'Get current page number', align=Align.INLINE)
d.comment(0xF835, 'Reached Tube I/O window at &FE00?', align=Align.INLINE)
d.comment(0xF837, 'No, copy next page', align=Align.INLINE)
d.comment(0xF839, '17 bytes of startup code to copy', align=Align.INLINE)
d.comment(0xF83B, 'Read startup code byte', align=Align.INLINE)
d.comment(0xF83E, 'Write to low memory at &0100', align=Align.INLINE)
d.comment(0xF841, 'Next byte', align=Align.INLINE)
d.comment(0xF842, 'Loop until all startup code copied', align=Align.INLINE)
d.comment(0xF844, 'Get current program low byte', align=Align.INLINE)
d.comment(0xF846, 'Set as transfer address low', align=Align.INLINE)
d.comment(0xF848, 'Get current program high byte', align=Align.INLINE)
d.comment(0xF84A, 'Set as transfer address high', align=Align.INLINE)
d.comment(0xF84C, 'A=0 for clearing', align=Align.INLINE)
d.comment(0xF84E, 'Clear Escape flag', align=Align.INLINE)
d.comment(0xF850, 'Set memory top low byte to 0', align=Align.INLINE)
d.comment(0xF852, 'High byte = &F8 (start of ROM)', align=Align.INLINE)
d.comment(0xF854, 'Set memory top to &F800', align=Align.INLINE)
d.comment(0xF856, 'Jump to low memory to page ROM out', align=Align.INLINE)
d.comment(0x0100, 'Read Tube R1 status to page ROM out', align=Align.INLINE)
d.comment(0x0103, 'Enable interrupts for data transfers', align=Align.INLINE)
d.comment(0x0104, 'Patched after first boot to skip banner', align=Align.INLINE)
# The instructions rendered at &0103/&0104 are the relocated low-memory
# startup code. The irq_return_addr_lo/hi labels name these addresses
# for a second, unrelated use as stack-frame bases (see brk_handler_entry),
# so flag that here to avoid confusing the two.
d.comment(0x0103,
          'irq_return_addr_lo also names &0103 as a stack-frame base:\n'
          'brk_handler_entry reads &0103,X (X = SP) to fetch the pushed\n'
          'BRK return address low byte.',
          word_wrap=False)
d.comment(0x0104,
          'irq_return_addr_hi also names &0104 as a stack-frame base:\n'
          'brk_handler_entry reads &0104,X (X = SP) to fetch the pushed\n'
          'BRK return address high byte.',
          word_wrap=False)
d.comment(0xF860, 'Print inline startup banner string', align=Align.INLINE)
d.comment(0xF87B, 'NOP (&EA) terminates string and is executed', align=Align.INLINE)
d.comment(0xF87C, 'Low byte of command_prompt address', align=Align.INLINE)
d.comment(0xF87E, 'Patch JMP target low byte', align=Align.INLINE)
d.comment(0xF881, 'High byte of command_prompt address', align=Align.INLINE)
d.comment(0xF883, 'Patch JMP target high byte', align=Align.INLINE)
d.comment(0xF886, 'Wait for host acknowledge byte', align=Align.INLINE)
d.comment(0xF889, 'Is it &80 (enter code)?', align=Align.INLINE)
d.comment(0xF88B, 'Yes, enter transferred code', align=Align.INLINE)
d.comment(0xF88D, "Print '*' prompt character", align=Align.INLINE)
d.comment(0xF88F, "Send '*' via OSWRCH", align=Align.INLINE)
d.comment(0xF892, 'Low byte of rdline control block', align=Align.INLINE)
d.comment(0xF894, 'High byte of rdline control block', align=Align.INLINE)
d.comment(0xF896, 'OSWORD 0: read line of input', align=Align.INLINE)
d.comment(0xF898, 'Call OSWORD', align=Align.INLINE)
d.comment(0xF89B, 'Carry set: Escape was pressed', align=Align.INLINE)
d.comment(0xF89D, 'Low byte of input buffer &0236', align=Align.INLINE)
d.comment(0xF89F, 'High byte of input buffer', align=Align.INLINE)
d.comment(0xF8A1, 'Execute command via OSCLI', align=Align.INLINE)
d.comment(0xF8A4, 'Loop back for next command', align=Align.INLINE)
d.comment(0xF8A7, 'OSBYTE &7E: acknowledge Escape', align=Align.INLINE)
d.comment(0xF8A9, 'Call OSBYTE', align=Align.INLINE)
d.comment(0xF8AC, "Generate error 17: 'Escape'", align=Align.INLINE)
d.comment(0xF8B5, 'Get transfer address low byte', align=Align.INLINE)
d.comment(0xF8B7, 'Set as current program low', align=Align.INLINE)
d.comment(0xF8B9, 'Also set memory top low', align=Align.INLINE)
d.comment(0xF8BB, 'Get transfer address high byte', align=Align.INLINE)
d.comment(0xF8BD, 'Set as current program high', align=Align.INLINE)
d.comment(0xF8BF, 'Also set memory top high', align=Align.INLINE)
d.comment(0xF8C1, 'Offset 7 = copyright string offset', align=Align.INLINE)
d.comment(0xF8C3, 'Read copyright offset from header', align=Align.INLINE)
d.comment(0xF8C5, 'Clear decimal mode', align=Align.INLINE)
d.comment(0xF8C6, 'Clear carry for addition', align=Align.INLINE)
d.comment(0xF8C7, 'Add base address to offset', align=Align.INLINE)
d.comment(0xF8C9, 'Store copyright pointer low', align=Align.INLINE)
d.comment(0xF8CB, 'A=0 for high byte add', align=Align.INLINE)
d.comment(0xF8CD, 'Add carry to high byte', align=Align.INLINE)
d.comment(0xF8CF, 'Store copyright pointer high', align=Align.INLINE)
d.comment(0xF8D1, 'Y=0 to check first byte', align=Align.INLINE)
d.comment(0xF8D3, 'Read byte at copyright pointer', align=Align.INLINE)
d.comment(0xF8D5, 'Not zero: no valid header, enter raw', align=Align.INLINE)
d.comment(0xF8D7, "Y=1 to check '('", align=Align.INLINE)
d.comment(0xF8D8, 'Read next byte', align=Align.INLINE)
d.comment(0xF8DA, "Is it '('?", align=Align.INLINE)
d.comment(0xF8DC, 'No: enter as raw code', align=Align.INLINE)
d.comment(0xF8DE, "Y=2 to check 'C'", align=Align.INLINE)
d.comment(0xF8DF, 'Read next byte', align=Align.INLINE)
d.comment(0xF8E1, "Is it 'C'?", align=Align.INLINE)
d.comment(0xF8E3, 'No: enter as raw code', align=Align.INLINE)
d.comment(0xF8E5, "Y=3 to check ')'", align=Align.INLINE)
d.comment(0xF8E6, 'Read next byte', align=Align.INLINE)
d.comment(0xF8E8, "Is it ')'?", align=Align.INLINE)
d.comment(0xF8EA, 'No: enter as raw code', align=Align.INLINE)
d.comment(0xF8EC, 'Offset 6 = ROM type byte', align=Align.INLINE)
d.comment(0xF8EE, 'Read ROM type', align=Align.INLINE)
d.comment(0xF8F0, 'Mask language and CPU type bits', align=Align.INLINE)
d.comment(0xF8F2, 'Bit 6 clear: not a language ROM', align=Align.INLINE)
d.comment(0xF8F4, "Generate 'not a language' error", align=Align.INLINE)
d.comment(0xF8F6, 'Mask CPU type: 0 or 2 = 6502', align=Align.INLINE)
d.comment(0xF8F8, 'Non-zero: not 6502 code', align=Align.INLINE)
d.comment(0xF8FA, 'Enter code with A=1', align=Align.INLINE)
d.comment(0xF8FC, 'Jump to code via memory top pointer', align=Align.INLINE)
d.comment(0xF8FF, 'Set BRKV low to error handler', align=Align.INLINE)
d.comment(0xF901, 'Store BRKV low byte', align=Align.INLINE)
d.comment(0xF904, 'Set BRKV high to error handler', align=Align.INLINE)
d.comment(0xF906, 'Store BRKV high byte', align=Align.INLINE)
d.comment(0xF909, "Generate 'not a language' error", align=Align.INLINE)
d.comment(0xF922, 'Set BRKV low to error handler', align=Align.INLINE)
d.comment(0xF924, 'Store BRKV low byte', align=Align.INLINE)
d.comment(0xF927, 'Set BRKV high to error handler', align=Align.INLINE)
d.comment(0xF929, 'Store BRKV high byte', align=Align.INLINE)
d.comment(0xF92C, "Generate 'I cannot run this code'", align=Align.INLINE)
d.comment(0xF945, 'Reset stack pointer to &FF', align=Align.INLINE)
d.comment(0xF947, 'Clear the stack', align=Align.INLINE)
d.comment(0xF948, 'Print newline before error message', align=Align.INLINE)
d.comment(0xF94B, 'Start at offset 1 (skip error number)', align=Align.INLINE)
d.comment(0xF94D, 'Get next error message character', align=Align.INLINE)
d.comment(0xF94F, 'Zero: end of error message', align=Align.INLINE)
d.comment(0xF951, 'Print character via OSWRCH', align=Align.INLINE)
d.comment(0xF954, 'Next character', align=Align.INLINE)
d.comment(0xF955, 'Loop until all characters printed', align=Align.INLINE)
d.comment(0xF957, 'Print trailing newline', align=Align.INLINE)
d.comment(0xF95A, 'Return to command prompt', align=Align.INLINE)
d.comment(0xF95D, 'Buffer address low (&0236)', align=Align.INLINE)
d.comment(0xF95E, 'Buffer address high', align=Align.INLINE)
d.comment(0xF95F, 'Buffer length (&CA = 202 bytes)', align=Align.INLINE)
d.comment(0xF960, 'Minimum ASCII value (&20 = space)', align=Align.INLINE)
d.comment(0xF961, 'Maximum ASCII value (&FF = all)', align=Align.INLINE)
d.comment(0xF962, 'Check Tube R1 status', align=Align.INLINE)
d.comment(0xF965, 'NOP for timing', align=Align.INLINE)
d.comment(0xF966, 'Wait until R1 ready to accept data', align=Align.INLINE)
d.comment(0xF968, 'Send character to Tube R1', align=Align.INLINE)
d.comment(0xF96B, 'Return with A preserved', align=Align.INLINE)
d.comment(0xF96C, 'Command &00: request character', align=Align.INLINE)
d.comment(0xF96E, 'Send command to host via Tube R2', align=Align.INLINE)
d.comment(0xF971, 'Wait for carry byte from host', align=Align.INLINE)
d.comment(0xF974, 'Shift carry flag into C', align=Align.INLINE)
d.comment(0xF975, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xF978, 'Loop until data available', align=Align.INLINE)
d.comment(0xF97A, 'Read data byte from Tube R2', align=Align.INLINE)
d.comment(0xF97D, 'Return', align=Align.INLINE)
d.comment(0xF97E, 'Advance past current character', align=Align.INLINE)
d.comment(0xF97F, 'Get character from string', align=Align.INLINE)
d.comment(0xF981, 'Is it a space?', align=Align.INLINE)
d.comment(0xF983, 'Yes: skip and check next', align=Align.INLINE)
d.comment(0xF985, 'Return with non-space char in A', align=Align.INLINE)
d.comment(0xF986, 'X=0: no digits parsed yet', align=Align.INLINE)
d.comment(0xF988, 'Clear hex accumulator low', align=Align.INLINE)
d.comment(0xF98A, 'Clear hex accumulator high', align=Align.INLINE)
d.comment(0xF98C, 'Get current character', align=Align.INLINE)
d.comment(0xF98E, "Below '0': not a hex digit", align=Align.INLINE)
d.comment(0xF990, 'Exit if not a digit', align=Align.INLINE)
d.comment(0xF992, "Below ':': it is a decimal digit", align=Align.INLINE)
d.comment(0xF994, 'Process digit 0-9', align=Align.INLINE)
d.comment(0xF996, 'Force uppercase', align=Align.INLINE)
d.comment(0xF998, 'Adjust for hex letter offset', align=Align.INLINE)
d.comment(0xF99A, "Below 'A': not a hex digit", align=Align.INLINE)
d.comment(0xF99C, "Above 'F': not a hex digit", align=Align.INLINE)
d.comment(0xF99E, 'Exit if out of range', align=Align.INLINE)
d.comment(0xF9A0, 'Shift digit into upper nybble', align=Align.INLINE)
d.comment(0xF9A1, 'Second shift', align=Align.INLINE)
d.comment(0xF9A2, 'Third shift', align=Align.INLINE)
d.comment(0xF9A3, 'Fourth shift (digit now in bits 7-4)', align=Align.INLINE)
d.comment(0xF9A4, '4 bits to rotate in', align=Align.INLINE)
d.comment(0xF9A6, 'Shift bit out of digit', align=Align.INLINE)
d.comment(0xF9A7, 'Rotate into accumulator low', align=Align.INLINE)
d.comment(0xF9A9, 'Rotate into accumulator high', align=Align.INLINE)
d.comment(0xF9AB, 'Next bit', align=Align.INLINE)
d.comment(0xF9AC, 'Loop for 4 bits', align=Align.INLINE)
d.comment(0xF9AE, 'Move to next input character', align=Align.INLINE)
d.comment(0xF9AF, 'Loop for more hex digits', align=Align.INLINE)
d.comment(0xF9B1, 'Return', align=Align.INLINE)
d.comment(0xF9B2, 'Set string pointer low byte', align=Align.INLINE)
d.comment(0xF9B4, 'Set string pointer high byte', align=Align.INLINE)
d.comment(0xF9B6, 'Start at offset 0', align=Align.INLINE)
d.comment(0xF9B8, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xF9BB, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xF9BD, 'Get character from string', align=Align.INLINE)
d.comment(0xF9BF, 'Send to Tube R2', align=Align.INLINE)
d.comment(0xF9C2, 'Next character', align=Align.INLINE)
d.comment(0xF9C3, 'Was it carriage return?', align=Align.INLINE)
d.comment(0xF9C5, 'No: send next character', align=Align.INLINE)
d.comment(0xF9C7, 'Restore Y from string_ptr_hi', align=Align.INLINE)
d.comment(0xF9C9, 'Return', align=Align.INLINE)
d.comment(0xF9CA, 'Save A on stack', align=Align.INLINE)
d.comment(0xF9CB, 'Store command string low byte', align=Align.INLINE)
d.comment(0xF9CD, 'Store command string high byte', align=Align.INLINE)
d.comment(0xF9CF, 'Start at offset 0', align=Align.INLINE)
d.comment(0xF9D1, 'Skip leading spaces', align=Align.INLINE)
d.comment(0xF9D4, 'Advance past character', align=Align.INLINE)
d.comment(0xF9D5, "Is it a '*'?", align=Align.INLINE)
d.comment(0xF9D7, 'Yes: skip leading stars', align=Align.INLINE)
d.comment(0xF9D9, 'Force uppercase for matching', align=Align.INLINE)
d.comment(0xF9DB, 'Save first command letter in X', align=Align.INLINE)
d.comment(0xF9DC, 'Peek at next character', align=Align.INLINE)
d.comment(0xF9DE, "Is first letter 'G'?", align=Align.INLINE)
d.comment(0xF9E0, 'Yes: check for *GO', align=Align.INLINE)
d.comment(0xF9E2, "Is first letter 'H'?", align=Align.INLINE)
d.comment(0xF9E4, 'No: pass command to host', align=Align.INLINE)
d.comment(0xF9E6, "Is next char '.' (abbreviated)?", align=Align.INLINE)
d.comment(0xF9E8, 'H. matches *HELP', align=Align.INLINE)
d.comment(0xF9EA, 'Force uppercase', align=Align.INLINE)
d.comment(0xF9EC, "Is it 'E'?", align=Align.INLINE)
d.comment(0xF9EE, 'No: pass to host', align=Align.INLINE)
d.comment(0xF9F0, "Advance past 'E'", align=Align.INLINE)
d.comment(0xF9F1, 'Get next character', align=Align.INLINE)
d.comment(0xF9F3, "Is it '.' (abbreviated)?", align=Align.INLINE)
d.comment(0xF9F5, 'HE. matches *HELP', align=Align.INLINE)
d.comment(0xF9F7, 'Force uppercase', align=Align.INLINE)
d.comment(0xF9F9, "Is it 'L'?", align=Align.INLINE)
d.comment(0xF9FB, 'No: pass to host', align=Align.INLINE)
d.comment(0xF9FD, "Advance past 'L'", align=Align.INLINE)
d.comment(0xF9FE, 'Get next character', align=Align.INLINE)
d.comment(0xFA00, "Is it '.' (abbreviated)?", align=Align.INLINE)
d.comment(0xFA02, 'HEL. matches *HELP', align=Align.INLINE)
d.comment(0xFA04, 'Force uppercase', align=Align.INLINE)
d.comment(0xFA06, "Is it 'P'?", align=Align.INLINE)
d.comment(0xFA08, 'No: pass to host', align=Align.INLINE)
d.comment(0xFA0A, "Advance past 'P'", align=Align.INLINE)
d.comment(0xFA0B, 'Get next character', align=Align.INLINE)
d.comment(0xFA0D, 'Force uppercase', align=Align.INLINE)
d.comment(0xFA0F, "Below 'A': end of command, it is HELP", align=Align.INLINE)
d.comment(0xFA11, 'Non-letter terminates: do *HELP', align=Align.INLINE)
d.comment(0xFA13, "Below '[': followed by letter", align=Align.INLINE)
d.comment(0xFA15, 'Letter follows: pass to host', align=Align.INLINE)
d.comment(0xFA17, 'Print inline version string', align=Align.INLINE)
d.comment(0xFA2C, 'NOP (&EA) terminates string and is executed', align=Align.INLINE)
d.comment(0xFA2D, 'Command &02: OSCLI', align=Align.INLINE)
d.comment(0xFA2F, 'Send command code to host', align=Align.INLINE)
d.comment(0xFA32, 'Send command string via string_ptr', align=Align.INLINE)
d.comment(0xFA35, 'Wait for host acknowledgement', align=Align.INLINE)
d.comment(0xFA38, '&80: host wants code entered', align=Align.INLINE)
d.comment(0xFA3A, 'Enter transferred code', align=Align.INLINE)
d.comment(0xFA3C, 'Restore saved A', align=Align.INLINE)
d.comment(0xFA3D, 'Return to caller', align=Align.INLINE)
d.comment(0xFA3E, 'Force uppercase', align=Align.INLINE)
d.comment(0xFA40, "Is it 'O' (completing GO)?", align=Align.INLINE)
d.comment(0xFA42, 'No: pass to host', align=Align.INLINE)
d.comment(0xFA44, "Skip past 'O' and spaces", align=Align.INLINE)
d.comment(0xFA47, 'Parse optional hex address', align=Align.INLINE)
d.comment(0xFA4A, 'Skip trailing spaces', align=Align.INLINE)
d.comment(0xFA4D, 'End of line (CR)?', align=Align.INLINE)
d.comment(0xFA4F, 'No: extra params, pass to host', align=Align.INLINE)
d.comment(0xFA51, 'X=0 means no address was given', align=Align.INLINE)
d.comment(0xFA52, 'Use current transfer address', align=Align.INLINE)
d.comment(0xFA54, 'Get parsed address low byte', align=Align.INLINE)
d.comment(0xFA56, 'Set transfer address low', align=Align.INLINE)
d.comment(0xFA58, 'Get parsed address high byte', align=Align.INLINE)
d.comment(0xFA5A, 'Set transfer address high', align=Align.INLINE)
d.comment(0xFA5C, 'Get current program high byte', align=Align.INLINE)
d.comment(0xFA5E, 'Save on stack', align=Align.INLINE)
d.comment(0xFA5F, 'Get current program low byte', align=Align.INLINE)
d.comment(0xFA61, 'Save on stack', align=Align.INLINE)
d.comment(0xFA62, 'Enter the code at transfer address', align=Align.INLINE)
d.comment(0xFA65, 'Restore current program low', align=Align.INLINE)
d.comment(0xFA66, 'Set current program low', align=Align.INLINE)
d.comment(0xFA68, 'Also restore memory top low', align=Align.INLINE)
d.comment(0xFA6A, 'Restore current program high', align=Align.INLINE)
d.comment(0xFA6B, 'Set current program high', align=Align.INLINE)
d.comment(0xFA6D, 'Also restore memory top high', align=Align.INLINE)
d.comment(0xFA6F, 'Restore saved A', align=Align.INLINE)
d.comment(0xFA70, 'Return to caller', align=Align.INLINE)
d.comment(0xFA71, 'If &8E matched, wait for OSCLI ack', align=Align.INLINE)
d.comment(0xFA73, 'Function >= &80?', align=Align.INLINE)
d.comment(0xFA75, 'Yes: handle high OSBYTE', align=Align.INLINE)
d.comment(0xFA77, 'Save function on stack', align=Align.INLINE)
d.comment(0xFA78, 'Command &04: OSBYTE low', align=Align.INLINE)
d.comment(0xFA7A, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFA7D, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFA7F, 'Send command &04', align=Align.INLINE)
d.comment(0xFA82, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFA85, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFA87, 'Send X parameter', align=Align.INLINE)
d.comment(0xFA8A, 'Restore function code', align=Align.INLINE)
d.comment(0xFA8B, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFA8E, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFA90, 'Send function code', align=Align.INLINE)
d.comment(0xFA93, 'Poll Tube R2 for response', align=Align.INLINE)
d.comment(0xFA96, 'Wait until data available', align=Align.INLINE)
d.comment(0xFA98, 'Read return value into X', align=Align.INLINE)
d.comment(0xFA9B, 'Return', align=Align.INLINE)
d.comment(0xFA9C, 'Is it OSBYTE &82 (read high word)?', align=Align.INLINE)
d.comment(0xFA9E, 'Yes: return &0000', align=Align.INLINE)
d.comment(0xFAA0, 'Is it OSBYTE &83 (read LOMEM)?', align=Align.INLINE)
d.comment(0xFAA2, 'Yes: return &0800', align=Align.INLINE)
d.comment(0xFAA4, 'Is it OSBYTE &84 (read HIMEM)?', align=Align.INLINE)
d.comment(0xFAA6, 'Yes: return memory_top', align=Align.INLINE)
d.comment(0xFAA8, 'Save function on stack', align=Align.INLINE)
d.comment(0xFAA9, 'Command &06: OSBYTE high', align=Align.INLINE)
d.comment(0xFAAB, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFAAE, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFAB0, 'Send command &06', align=Align.INLINE)
d.comment(0xFAB3, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFAB6, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFAB8, 'Send X parameter', align=Align.INLINE)
d.comment(0xFABB, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFABE, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFAC0, 'Send Y parameter', align=Align.INLINE)
d.comment(0xFAC3, 'Restore function code', align=Align.INLINE)
d.comment(0xFAC4, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFAC7, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFAC9, 'Send function code', align=Align.INLINE)
d.comment(0xFACC, 'Is it &8E (select language)?', align=Align.INLINE)
d.comment(0xFACE, 'Yes: check for code to enter', align=Align.INLINE)
d.comment(0xFAD0, 'Is it &9D (fast BPUT)?', align=Align.INLINE)
d.comment(0xFAD2, 'Yes: return without response', align=Align.INLINE)
d.comment(0xFAD4, 'Save function for later restore', align=Align.INLINE)
d.comment(0xFAD5, 'Poll Tube R2 for carry byte', align=Align.INLINE)
d.comment(0xFAD8, 'Wait until data available', align=Align.INLINE)
d.comment(0xFADA, 'Read carry byte', align=Align.INLINE)
d.comment(0xFADD, 'Shift carry into C flag', align=Align.INLINE)
d.comment(0xFADE, 'Restore saved function', align=Align.INLINE)
d.comment(0xFADF, 'Poll Tube R2 for Y return value', align=Align.INLINE)
d.comment(0xFAE2, 'Wait until data available', align=Align.INLINE)
d.comment(0xFAE4, 'Read Y return value', align=Align.INLINE)
d.comment(0xFAE7, 'Poll Tube R2 for X return value', align=Align.INLINE)
d.comment(0xFAEA, 'Wait until data available', align=Align.INLINE)
d.comment(0xFAEC, 'Read X return value', align=Align.INLINE)
d.comment(0xFAEF, 'Return', align=Align.INLINE)
d.comment(0xFAF0, 'X = memory top low byte', align=Align.INLINE)
d.comment(0xFAF2, 'Y = memory top high byte', align=Align.INLINE)
d.comment(0xFAF4, 'Return (OSBYTE &84)', align=Align.INLINE)
d.comment(0xFAF5, 'X = &00 (bottom of user memory)', align=Align.INLINE)
d.comment(0xFAF7, 'Y = &08 (bottom of memory high byte)', align=Align.INLINE)
d.comment(0xFAF9, 'Return (OSBYTE &83)', align=Align.INLINE)
d.comment(0xFAFA, 'X = &00 (high word low)', align=Align.INLINE)
d.comment(0xFAFC, 'Y = &00 (high word high)', align=Align.INLINE)
d.comment(0xFAFE, 'Return (OSBYTE &82)', align=Align.INLINE)
d.comment(0xFAFF, 'Store control block address low', align=Align.INLINE)
d.comment(0xFB01, 'Store control block address high', align=Align.INLINE)
d.comment(0xFB03, 'A=0: OSWORD 0?', align=Align.INLINE)
d.comment(0xFB04, 'Yes: handle read line specially', align=Align.INLINE)
d.comment(0xFB06, 'Save function on stack', align=Align.INLINE)
d.comment(0xFB07, 'Command &08: OSWORD', align=Align.INLINE)
d.comment(0xFB09, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFB0C, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFB0E, 'Send command &08', align=Align.INLINE)
d.comment(0xFB11, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFB14, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFB16, 'Send function number', align=Align.INLINE)
d.comment(0xFB19, 'Copy function to X', align=Align.INLINE)
d.comment(0xFB1A, 'Function >= &80?', align=Align.INLINE)
d.comment(0xFB1C, 'Y=0 for control block read', align=Align.INLINE)
d.comment(0xFB1E, 'Get send length from control block', align=Align.INLINE)
d.comment(0xFB20, 'Transfer to Y', align=Align.INLINE)
d.comment(0xFB21, 'Jump to send block', align=Align.INLINE)
d.comment(0xFB24, 'Get send length from table', align=Align.INLINE)
d.comment(0xFB27, 'Function < &15?', align=Align.INLINE)
d.comment(0xFB29, 'Yes: use table length', align=Align.INLINE)
d.comment(0xFB2B, 'Default: send 16 bytes', align=Align.INLINE)
d.comment(0xFB2D, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFB30, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFB32, 'Send block length to host', align=Align.INLINE)
d.comment(0xFB35, 'Decrement index', align=Align.INLINE)
d.comment(0xFB36, 'Negative: nothing to send', align=Align.INLINE)
d.comment(0xFB38, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFB3B, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFB3D, 'Read byte from control block', align=Align.INLINE)
d.comment(0xFB3F, 'Send to Tube R2', align=Align.INLINE)
d.comment(0xFB42, 'Next byte (reverse order)', align=Align.INLINE)
d.comment(0xFB43, 'Loop until all bytes sent', align=Align.INLINE)
d.comment(0xFB45, 'Get function back in A', align=Align.INLINE)
d.comment(0xFB46, 'Function >= &80?', align=Align.INLINE)
d.comment(0xFB48, 'Y=1 for control block read', align=Align.INLINE)
d.comment(0xFB4A, 'Get receive length from block', align=Align.INLINE)
d.comment(0xFB4C, 'Transfer to Y', align=Align.INLINE)
d.comment(0xFB4D, 'Jump to receive block', align=Align.INLINE)
d.comment(0xFB50, 'Get receive length from table', align=Align.INLINE)
d.comment(0xFB53, 'Function < &15?', align=Align.INLINE)
d.comment(0xFB55, 'Yes: use table length', align=Align.INLINE)
d.comment(0xFB57, 'Default: receive 16 bytes', align=Align.INLINE)
d.comment(0xFB59, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFB5C, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFB5E, 'Send receive length to host', align=Align.INLINE)
d.comment(0xFB61, 'Decrement index', align=Align.INLINE)
d.comment(0xFB62, 'Negative: nothing to receive', align=Align.INLINE)
d.comment(0xFB64, 'Poll Tube R2 for data', align=Align.INLINE)
d.comment(0xFB67, 'Wait until data available', align=Align.INLINE)
d.comment(0xFB69, 'Read response byte', align=Align.INLINE)
d.comment(0xFB6C, 'Store in control block', align=Align.INLINE)
d.comment(0xFB6E, 'Next byte (reverse order)', align=Align.INLINE)
d.comment(0xFB6F, 'Loop until all received', align=Align.INLINE)
d.comment(0xFB71, 'Restore Y from string_ptr_hi', align=Align.INLINE)
d.comment(0xFB73, 'Restore X from string_ptr', align=Align.INLINE)
d.comment(0xFB75, 'Restore function code', align=Align.INLINE)
d.comment(0xFB76, 'Return', align=Align.INLINE)
d.comment(0xFB77, 'Command &0A: read line', align=Align.INLINE)
d.comment(0xFB79, 'Send command to host', align=Align.INLINE)
d.comment(0xFB7C, 'Start at control block byte 4', align=Align.INLINE)
d.comment(0xFB7E, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFB81, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFB83, 'Get control block byte', align=Align.INLINE)
d.comment(0xFB85, 'Send to host', align=Align.INLINE)
d.comment(0xFB88, 'Decrement index', align=Align.INLINE)
d.comment(0xFB89, 'Reached byte 1?', align=Align.INLINE)
d.comment(0xFB8B, 'No: send next (bytes 4, 3, 2)', align=Align.INLINE)
d.comment(0xFB8D, '&07 as high byte of buffer address', align=Align.INLINE)
d.comment(0xFB8F, 'Send buffer address high byte', align=Align.INLINE)
d.comment(0xFB92, 'Get actual buffer high byte', align=Align.INLINE)
d.comment(0xFB94, 'Save on stack for later', align=Align.INLINE)
d.comment(0xFB95, 'Decrement to byte 0', align=Align.INLINE)
d.comment(0xFB96, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFB99, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFB9B, 'Send &00 as buffer address low byte', align=Align.INLINE)
d.comment(0xFB9E, 'Get actual buffer low byte', align=Align.INLINE)
d.comment(0xFBA0, 'Save on stack for later', align=Align.INLINE)
d.comment(0xFBA1, 'X=&FF as Escape indicator', align=Align.INLINE)
d.comment(0xFBA3, 'Wait for host response', align=Align.INLINE)
d.comment(0xFBA6, 'Is response >= &80 (Escape)?', align=Align.INLINE)
d.comment(0xFBA8, 'Yes: handle Escape', align=Align.INLINE)
d.comment(0xFBAA, 'Recover buffer low byte', align=Align.INLINE)
d.comment(0xFBAB, 'Set string_ptr low', align=Align.INLINE)
d.comment(0xFBAD, 'Recover buffer high byte', align=Align.INLINE)
d.comment(0xFBAE, 'Set string_ptr high', align=Align.INLINE)
d.comment(0xFBB0, 'Start at offset 0', align=Align.INLINE)
d.comment(0xFBB2, 'Poll Tube R2 for data', align=Align.INLINE)
d.comment(0xFBB5, 'Wait until data available', align=Align.INLINE)
d.comment(0xFBB7, 'Read character from host', align=Align.INLINE)
d.comment(0xFBBA, 'Store in buffer', align=Align.INLINE)
d.comment(0xFBBC, 'Advance buffer position', align=Align.INLINE)
d.comment(0xFBBD, 'Is it carriage return?', align=Align.INLINE)
d.comment(0xFBBF, 'No: receive next character', align=Align.INLINE)
d.comment(0xFBC1, 'A=0 on success', align=Align.INLINE)
d.comment(0xFBC3, 'Y=length (exclude CR)', align=Align.INLINE)
d.comment(0xFBC4, 'Clear carry: no Escape', align=Align.INLINE)
d.comment(0xFBC5, 'X=0 on success', align=Align.INLINE)
d.comment(0xFBC6, 'Return: A=0, Y=len, C=0', align=Align.INLINE)
d.comment(0xFBC7, 'Discard saved buffer low byte', align=Align.INLINE)
d.comment(0xFBC8, 'Discard saved buffer high byte', align=Align.INLINE)
d.comment(0xFBC9, 'A=0, carry set from CMP &80', align=Align.INLINE)
d.comment(0xFBCB, 'Return: Escape, A=0, C=1', align=Align.INLINE)
d.comment(0xFBCC, 'Save function on stack', align=Align.INLINE)
d.comment(0xFBCD, 'Command &0C: OSARGS', align=Align.INLINE)
d.comment(0xFBCF, 'Send command to host', align=Align.INLINE)
d.comment(0xFBD2, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFBD5, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFBD7, 'Send file handle', align=Align.INLINE)
d.comment(0xFBDA, 'Get data word byte 3', align=Align.INLINE)
d.comment(0xFBDC, 'Send data byte 3', align=Align.INLINE)
d.comment(0xFBDF, 'Get data word byte 2', align=Align.INLINE)
d.comment(0xFBE1, 'Send data byte 2', align=Align.INLINE)
d.comment(0xFBE4, 'Get data word byte 1', align=Align.INLINE)
d.comment(0xFBE6, 'Send data byte 1', align=Align.INLINE)
d.comment(0xFBE9, 'Get data word byte 0', align=Align.INLINE)
d.comment(0xFBEB, 'Send data byte 0', align=Align.INLINE)
d.comment(0xFBEE, 'Restore function code', align=Align.INLINE)
d.comment(0xFBEF, 'Send function code', align=Align.INLINE)
d.comment(0xFBF2, 'Wait for result byte', align=Align.INLINE)
d.comment(0xFBF5, 'Save result on stack', align=Align.INLINE)
d.comment(0xFBF6, 'Wait for data byte 3', align=Align.INLINE)
d.comment(0xFBF9, 'Store in data word', align=Align.INLINE)
d.comment(0xFBFB, 'Wait for data byte 2', align=Align.INLINE)
d.comment(0xFBFE, 'Store in data word', align=Align.INLINE)
d.comment(0xFC00, 'Wait for data byte 1', align=Align.INLINE)
d.comment(0xFC03, 'Store in data word', align=Align.INLINE)
d.comment(0xFC05, 'Wait for data byte 0', align=Align.INLINE)
d.comment(0xFC08, 'Store in data word', align=Align.INLINE)
d.comment(0xFC0A, 'Restore result to A', align=Align.INLINE)
d.comment(0xFC0B, 'Return with result in A', align=Align.INLINE)
d.comment(0xFC0C, 'Save function on stack', align=Align.INLINE)
d.comment(0xFC0D, 'Command &12: OSFIND', align=Align.INLINE)
d.comment(0xFC0F, 'Send command to host', align=Align.INLINE)
d.comment(0xFC12, 'Restore function code', align=Align.INLINE)
d.comment(0xFC13, 'Send function code', align=Align.INLINE)
d.comment(0xFC16, 'Is it close (A=0)?', align=Align.INLINE)
d.comment(0xFC18, 'No: handle open', align=Align.INLINE)
d.comment(0xFC1A, 'Save A=0', align=Align.INLINE)
d.comment(0xFC1B, 'Transfer handle from Y to A', align=Align.INLINE)
d.comment(0xFC1C, 'Send handle', align=Align.INLINE)
d.comment(0xFC1F, 'Wait for acknowledge', align=Align.INLINE)
d.comment(0xFC22, 'Restore A=0', align=Align.INLINE)
d.comment(0xFC23, 'Return', align=Align.INLINE)
d.comment(0xFC24, 'Send filename string', align=Align.INLINE)
d.comment(0xFC27, 'Wait for and return file handle', align=Align.INLINE)
d.comment(0xFC2A, 'Command &0E: OSBGET', align=Align.INLINE)
d.comment(0xFC2C, 'Send command to host', align=Align.INLINE)
d.comment(0xFC2F, 'Transfer handle from Y to A', align=Align.INLINE)
d.comment(0xFC30, 'Send handle', align=Align.INLINE)
d.comment(0xFC33, 'Wait for carry and data byte', align=Align.INLINE)
d.comment(0xFC36, 'Save byte to write', align=Align.INLINE)
d.comment(0xFC37, 'Command &10: OSBPUT', align=Align.INLINE)
d.comment(0xFC39, 'Send command to host', align=Align.INLINE)
d.comment(0xFC3C, 'Transfer handle from Y to A', align=Align.INLINE)
d.comment(0xFC3D, 'Send handle', align=Align.INLINE)
d.comment(0xFC40, 'Restore byte to write', align=Align.INLINE)
d.comment(0xFC41, 'Send data byte', align=Align.INLINE)
d.comment(0xFC44, 'Save A for restore after ack', align=Align.INLINE)
d.comment(0xFC45, 'Wait for acknowledge', align=Align.INLINE)
d.comment(0xFC48, 'Restore A (preserved)', align=Align.INLINE)
d.comment(0xFC49, 'Return', align=Align.INLINE)
d.comment(0xFC4A, 'Poll Tube R2 status', align=Align.INLINE)
d.comment(0xFC4D, 'Wait until R2 ready', align=Align.INLINE)
d.comment(0xFC4F, 'Write byte to Tube R2 data', align=Align.INLINE)
d.comment(0xFC52, 'Return with A preserved', align=Align.INLINE)
d.comment(0xFC53, 'Store control block high byte', align=Align.INLINE)
d.comment(0xFC55, 'Store control block low byte', align=Align.INLINE)
d.comment(0xFC57, 'Save function on stack', align=Align.INLINE)
d.comment(0xFC58, 'Command &14: OSFILE', align=Align.INLINE)
d.comment(0xFC5A, 'Send command to host', align=Align.INLINE)
d.comment(0xFC5D, 'Start at control block byte &11', align=Align.INLINE)
d.comment(0xFC5F, 'Get control block byte', align=Align.INLINE)
d.comment(0xFC61, 'Send to host', align=Align.INLINE)
d.comment(0xFC64, 'Decrement index', align=Align.INLINE)
d.comment(0xFC65, 'Reached byte 1?', align=Align.INLINE)
d.comment(0xFC67, 'No: send next byte', align=Align.INLINE)
d.comment(0xFC69, 'Decrement to byte 0', align=Align.INLINE)
d.comment(0xFC6A, 'Get filename pointer low', align=Align.INLINE)
d.comment(0xFC6C, 'Transfer to X', align=Align.INLINE)
d.comment(0xFC6D, 'Move to byte 1', align=Align.INLINE)
d.comment(0xFC6E, 'Get filename pointer high', align=Align.INLINE)
d.comment(0xFC70, 'Transfer to Y', align=Align.INLINE)
d.comment(0xFC71, 'Send filename string', align=Align.INLINE)
d.comment(0xFC74, 'Restore function code', align=Align.INLINE)
d.comment(0xFC75, 'Send function code', align=Align.INLINE)
d.comment(0xFC78, 'Wait for result byte', align=Align.INLINE)
d.comment(0xFC7B, 'Save result on stack', align=Align.INLINE)
d.comment(0xFC7C, 'Start at control block byte &11', align=Align.INLINE)
d.comment(0xFC7E, 'Wait for response byte', align=Align.INLINE)
d.comment(0xFC81, 'Store in control block', align=Align.INLINE)
d.comment(0xFC83, 'Decrement index', align=Align.INLINE)
d.comment(0xFC84, 'Reached byte 1?', align=Align.INLINE)
d.comment(0xFC86, 'No: receive next byte', align=Align.INLINE)
d.comment(0xFC88, 'Restore Y from control block ptr', align=Align.INLINE)
d.comment(0xFC8A, 'Restore X from control block ptr', align=Align.INLINE)
d.comment(0xFC8C, 'Restore result to A', align=Align.INLINE)
d.comment(0xFC8D, 'Return with result in A', align=Align.INLINE)
d.comment(0xFC8E, 'Store control block high byte', align=Align.INLINE)
d.comment(0xFC90, 'Store control block low byte', align=Align.INLINE)
d.comment(0xFC92, 'Save function on stack', align=Align.INLINE)
d.comment(0xFC93, 'Command &16: OSGBPB', align=Align.INLINE)
d.comment(0xFC95, 'Send command to host', align=Align.INLINE)
d.comment(0xFC98, 'Start at control block byte &0C', align=Align.INLINE)
d.comment(0xFC9A, 'Get control block byte', align=Align.INLINE)
d.comment(0xFC9C, 'Send to host', align=Align.INLINE)
d.comment(0xFC9F, 'Decrement index', align=Align.INLINE)
d.comment(0xFCA0, 'Loop for bytes &0C..&00', align=Align.INLINE)
d.comment(0xFCA2, 'Restore function code', align=Align.INLINE)
d.comment(0xFCA3, 'Send function code', align=Align.INLINE)
d.comment(0xFCA6, 'Start at control block byte &0C', align=Align.INLINE)
d.comment(0xFCA8, 'Wait for response byte', align=Align.INLINE)
d.comment(0xFCAB, 'Store in control block', align=Align.INLINE)
d.comment(0xFCAD, 'Decrement index', align=Align.INLINE)
d.comment(0xFCAE, 'Loop for bytes &0C..&00', align=Align.INLINE)
d.comment(0xFCB0, 'Restore Y from control block ptr', align=Align.INLINE)
d.comment(0xFCB2, 'Restore X from control block ptr', align=Align.INLINE)
d.comment(0xFCB4, 'Get carry and result byte', align=Align.INLINE)
d.comment(0xFCB7, "Generate error 255: 'Bad'", align=Align.INLINE)
d.comment(0xFCBC, '(unused: OSWORD 0 handled separately)', align=Align.INLINE)
d.comment(0xFCBD, '&01 Read system clock', align=Align.INLINE)
d.comment(0xFCBE, '&02 Write system clock', align=Align.INLINE)
d.comment(0xFCBF, '&03 Read interval timer', align=Align.INLINE)
d.comment(0xFCC0, '&04 Write interval timer', align=Align.INLINE)
d.comment(0xFCC1, '&05 Read I/O memory (2-byte addr)', align=Align.INLINE)
d.comment(0xFCC2, '&06 Read real-time clock', align=Align.INLINE)
d.comment(0xFCC3, '&07 Write real-time clock / sound', align=Align.INLINE)
d.comment(0xFCC4, '&08 Define envelope', align=Align.INLINE)
d.comment(0xFCC5, '&09 Read pixel colour', align=Align.INLINE)
d.comment(0xFCC6, '&0A Read character definition', align=Align.INLINE)
d.comment(0xFCC7, '&0B Read palette', align=Align.INLINE)
d.comment(0xFCC8, '&0C Write palette', align=Align.INLINE)
d.comment(0xFCC9, '&0D Read last two graphics cursor posns', align=Align.INLINE)
d.comment(0xFCCA, '&0E Read clock as string', align=Align.INLINE)
d.comment(0xFCCB, '&0F Write clock as string', align=Align.INLINE)
d.comment(0xFCCC, '&10 Net transmit', align=Align.INLINE)
d.comment(0xFCCD, '&11 Net receive', align=Align.INLINE)
d.comment(0xFCCE, '&12 Net read arguments', align=Align.INLINE)
d.comment(0xFCCF, '&13 Net FS operation', align=Align.INLINE)
d.comment(0xFCD0, '&14 send / (recv slot 0 unused)', align=Align.INLINE)
d.comment(0xFCD1, '&01 Read system clock', align=Align.INLINE)
d.comment(0xFCD2, '&02 Write system clock', align=Align.INLINE)
d.comment(0xFCD3, '&03 Read interval timer', align=Align.INLINE)
d.comment(0xFCD4, '&04 Write interval timer', align=Align.INLINE)
d.comment(0xFCD5, '&05 Read I/O memory', align=Align.INLINE)
d.comment(0xFCD6, '&06 Read real-time clock', align=Align.INLINE)
d.comment(0xFCD7, '&07 Write real-time clock / sound', align=Align.INLINE)
d.comment(0xFCD8, '&08 Define envelope', align=Align.INLINE)
d.comment(0xFCD9, '&09 Read pixel colour', align=Align.INLINE)
d.comment(0xFCDA, '&0A Read character definition', align=Align.INLINE)
d.comment(0xFCDB, '&0B Read palette', align=Align.INLINE)
d.comment(0xFCDC, '&0C Write palette', align=Align.INLINE)
d.comment(0xFCDD, '&0D Read last two graphics cursor posns', align=Align.INLINE)
d.comment(0xFCDE, '&0E Read clock as string', align=Align.INLINE)
d.comment(0xFCDF, '&0F Write clock as string', align=Align.INLINE)
d.comment(0xFCE0, '&10 Net transmit', align=Align.INLINE)
d.comment(0xFCE1, '&11 Net receive', align=Align.INLINE)
d.comment(0xFCE2, '&12 Net read arguments', align=Align.INLINE)
d.comment(0xFCE3, '&13 Net FS operation', align=Align.INLINE)
d.comment(0xFCE4, '&14 Net FS operation', align=Align.INLINE)
d.comment(0xFCE5, 'Save A in irq_a_store', align=Align.INLINE)
d.comment(0xFCE7, 'Pull stacked processor status', align=Align.INLINE)
d.comment(0xFCE8, 'Push it back (non-destructive read)', align=Align.INLINE)
d.comment(0xFCE9, 'Isolate BRK flag (bit 4)', align=Align.INLINE)
d.comment(0xFCEB, 'BRK flag set: handle BRK', align=Align.INLINE)
d.comment(0xFCED, 'Dispatch via IRQ1V', align=Align.INLINE)
d.comment(0xFCF0, 'Check Tube R4 for data', align=Align.INLINE)
d.comment(0xFCF3, 'Data present: handle transfer/error', align=Align.INLINE)
d.comment(0xFCF5, 'Check Tube R1 for data', align=Align.INLINE)
d.comment(0xFCF8, 'Data present: handle escape/event', align=Align.INLINE)
d.comment(0xFCFA, 'Neither: dispatch via IRQ2V', align=Align.INLINE)
d.comment(0xFCFD, 'Save X on stack', align=Align.INLINE)
d.comment(0xFCFE, 'Push X', align=Align.INLINE)
d.comment(0xFCFF, 'Get stack pointer', align=Align.INLINE)
d.comment(0xFD00, 'Get return address low from stack', align=Align.INLINE)
d.comment(0xFD03, 'Clear decimal mode', align=Align.INLINE)
d.comment(0xFD04, 'Set carry for subtract', align=Align.INLINE)
d.comment(0xFD05, 'Subtract 1 to point at error block', align=Align.INLINE)
d.comment(0xFD07, 'Store as last_error low', align=Align.INLINE)
d.comment(0xFD09, 'Get return address high from stack', align=Align.INLINE)
d.comment(0xFD0C, 'Subtract borrow', align=Align.INLINE)
d.comment(0xFD0E, 'Store as last_error high', align=Align.INLINE)
d.comment(0xFD10, 'Restore X from stack', align=Align.INLINE)
d.comment(0xFD11, 'Transfer back to X', align=Align.INLINE)
d.comment(0xFD12, 'Get saved A from irq_a_store', align=Align.INLINE)
d.comment(0xFD14, 'Re-enable interrupts', align=Align.INLINE)
d.comment(0xFD15, 'Dispatch via BRKV', align=Align.INLINE)
d.comment(0xFD18, 'Read data from Tube R1', align=Align.INLINE)
d.comment(0xFD1B, 'Bit 7 set: Escape state change', align=Align.INLINE)
d.comment(0xFD1D, 'Save Y', align=Align.INLINE)
d.comment(0xFD1E, 'Push Y', align=Align.INLINE)
d.comment(0xFD1F, 'Save X', align=Align.INLINE)
d.comment(0xFD20, 'Push X', align=Align.INLINE)
d.comment(0xFD21, 'Read event Y parameter via R1', align=Align.INLINE)
d.comment(0xFD24, 'Store in Y', align=Align.INLINE)
d.comment(0xFD25, 'Read event X parameter via R1', align=Align.INLINE)
d.comment(0xFD28, 'Store in X', align=Align.INLINE)
d.comment(0xFD29, 'Read event number via R1', align=Align.INLINE)
d.comment(0xFD2C, 'Dispatch event via EVNTV', align=Align.INLINE)
d.comment(0xFD2F, 'Restore X from stack', align=Align.INLINE)
d.comment(0xFD30, 'Transfer to X', align=Align.INLINE)
d.comment(0xFD31, 'Restore Y from stack', align=Align.INLINE)
d.comment(0xFD32, 'Transfer to Y', align=Align.INLINE)
d.comment(0xFD33, 'Get saved A from irq_a_store', align=Align.INLINE)
d.comment(0xFD35, 'Return from interrupt', align=Align.INLINE)
d.comment(0xFD36, 'Dispatch event via EVNTV', align=Align.INLINE)
d.comment(0xFD39, 'Shift bit 6 into bit 7 for Escape', align=Align.INLINE)
d.comment(0xFD3A, 'Store as Escape flag', align=Align.INLINE)
d.comment(0xFD3C, 'Get saved A from irq_a_store', align=Align.INLINE)
d.comment(0xFD3E, 'Return from interrupt', align=Align.INLINE)
d.comment(0xFD3F, 'Read data from Tube R4', align=Align.INLINE)
d.comment(0xFD42, 'Bit 7 clear: data transfer request', align=Align.INLINE)
d.comment(0xFD44, 'Re-enable IRQs for error reception', align=Align.INLINE)
d.comment(0xFD45, 'Poll Tube R2 for error data', align=Align.INLINE)
d.comment(0xFD48, 'Wait until data available', align=Align.INLINE)
d.comment(0xFD4A, 'Read and discard R2 sync byte', align=Align.INLINE)
d.comment(0xFD4D, 'A=0 (BRK opcode)', align=Align.INLINE)
d.comment(0xFD4F, 'Store BRK at start of error buffer', align=Align.INLINE)
d.comment(0xFD52, 'Y=0 for buffer index', align=Align.INLINE)
d.comment(0xFD53, 'Wait for error number byte', align=Align.INLINE)
d.comment(0xFD56, 'Store error number in buffer', align=Align.INLINE)
d.comment(0xFD59, 'Advance buffer index', align=Align.INLINE)
d.comment(0xFD5A, 'Wait for next error string byte', align=Align.INLINE)
d.comment(0xFD5D, 'Store in error buffer', align=Align.INLINE)
d.comment(0xFD60, 'Loop until NUL terminator', align=Align.INLINE)
d.comment(0xFD62, 'Execute BRK in error buffer', align=Align.INLINE)
d.comment(0xFD65, 'Save transfer type in NMI vector', align=Align.INLINE)
d.comment(0xFD68, 'Save Y on stack', align=Align.INLINE)
d.comment(0xFD69, 'Push Y', align=Align.INLINE)
d.comment(0xFD6A, 'Get transfer type back', align=Align.INLINE)
d.comment(0xFD6D, 'Look up NMI routine address low', align=Align.INLINE)
d.comment(0xFD70, 'Set NMI vector low byte', align=Align.INLINE)
d.comment(0xFD73, 'Look up NMI routine address high', align=Align.INLINE)
d.comment(0xFD76, 'Set NMI vector high byte', align=Align.INLINE)
d.comment(0xFD79, 'Look up address pointer low', align=Align.INLINE)
d.comment(0xFD7C, 'Set transfer_addr_ptr low', align=Align.INLINE)
d.comment(0xFD7E, 'Look up address pointer high', align=Align.INLINE)
d.comment(0xFD81, 'Set transfer_addr_ptr high', align=Align.INLINE)
d.comment(0xFD83, 'Poll Tube R4 for called ID byte', align=Align.INLINE)
d.comment(0xFD86, 'Wait until data available', align=Align.INLINE)
d.comment(0xFD88, 'Consume called ID byte (value discarded)', align=Align.INLINE)
d.comment(0xFD8B, 'Type 5: release, no transfer needed', align=Align.INLINE)
d.comment(0xFD8D, 'Yes: exit immediately', align=Align.INLINE)
d.comment(0xFD8F, 'Save transfer type', align=Align.INLINE)
d.comment(0xFD90, 'Push transfer type', align=Align.INLINE)
d.comment(0xFD91, 'Y=1 for address byte index', align=Align.INLINE)
d.comment(0xFD93, 'Poll Tube R4 for address byte 4', align=Align.INLINE)
d.comment(0xFD96, 'Wait until data available', align=Align.INLINE)
d.comment(0xFD98, 'Read and discard byte 4 (bits 31-24)', align=Align.INLINE)
d.comment(0xFD9B, 'Poll Tube R4 for address byte 3', align=Align.INLINE)
d.comment(0xFD9E, 'Wait until data available', align=Align.INLINE)
d.comment(0xFDA0, 'Read and discard byte 3 (bits 23-16)', align=Align.INLINE)
d.comment(0xFDA3, 'Poll Tube R4 for address byte 2', align=Align.INLINE)
d.comment(0xFDA6, 'Wait until data available', align=Align.INLINE)
d.comment(0xFDA8, 'Read address byte 2 (high)', align=Align.INLINE)
d.comment(0xFDAB, 'Store via transfer address pointer', align=Align.INLINE)
d.comment(0xFDAD, 'Decrement to byte 0', align=Align.INLINE)
d.comment(0xFDAE, 'Poll Tube R4 for address byte 1', align=Align.INLINE)
d.comment(0xFDB1, 'Wait until data available', align=Align.INLINE)
d.comment(0xFDB3, 'Read address byte 1 (low)', align=Align.INLINE)
d.comment(0xFDB6, 'Store via transfer address pointer', align=Align.INLINE)
d.comment(0xFDB8, 'Drain 1st byte from R3 H-to-P FIFO (BIT reads R3 data)', align=Align.INLINE)
d.comment(0xFDBB, 'Drain 2nd byte from R3 H-to-P FIFO', align=Align.INLINE)
d.comment(0xFDBE, 'Poll Tube R4 status for host sync byte', align=Align.INLINE)
d.comment(0xFDC1, 'Spin until host writes sync byte (gates data phase)', align=Align.INLINE)
d.comment(0xFDC3, 'Read sync byte', align=Align.INLINE)
d.comment(0xFDC6, 'Restore transfer type', align=Align.INLINE)
d.comment(0xFDC7, 'Is it type 6 or above?', align=Align.INLINE)
d.comment(0xFDC9, 'Below 6: exit (single/double/release)', align=Align.INLINE)
d.comment(0xFDCB, 'Not 6: must be type 7 (read block)', align=Align.INLINE)
d.comment(0xFDCD, 'Y=0 for 256-byte counter', align=Align.INLINE)
d.comment(0xFDCF, 'Read Tube R3 status', align=Align.INLINE)
d.comment(0xFDD2, 'Isolate ready bit', align=Align.INLINE)
d.comment(0xFDD4, 'Wait until R3 ready', align=Align.INLINE)
d.comment(0xFDD6, 'Read byte (address patched)', align=Align.INLINE)
d.comment(0xFDD9, 'Send to Tube R3', align=Align.INLINE)
d.comment(0xFDDC, 'Next byte', align=Align.INLINE)
d.comment(0xFDDD, 'Loop for 256 bytes', align=Align.INLINE)
d.comment(0xFDDF, 'Poll Tube R3 status', align=Align.INLINE)
d.comment(0xFDE2, 'Wait until R3 ready', align=Align.INLINE)
d.comment(0xFDE4, 'Send final sync byte to R3', align=Align.INLINE)
d.comment(0xFDE7, 'Restore Y from stack', align=Align.INLINE)
d.comment(0xFDE8, 'Transfer to Y', align=Align.INLINE)
d.comment(0xFDE9, 'Get saved A from irq_a_store', align=Align.INLINE)
d.comment(0xFDEB, 'Return from interrupt', align=Align.INLINE)
d.comment(0xFDEC, 'Y=0 for 256-byte counter', align=Align.INLINE)
d.comment(0xFDEE, 'Read Tube R3 status', align=Align.INLINE)
d.comment(0xFDF1, 'Isolate data ready bit', align=Align.INLINE)
d.comment(0xFDF3, 'Wait until R3 has data', align=Align.INLINE)
d.comment(0xFDF5, 'Read byte from Tube R3', align=Align.INLINE)
d.comment(0xFDF8, 'Store byte (address patched)', align=Align.INLINE)
d.comment(0xFDFB, 'Next byte', align=Align.INLINE)
d.comment(0xFDFC, 'Loop for 256 bytes', align=Align.INLINE)
d.comment(0xFDFE, 'Always branch to exit', align=Align.INLINE)
d.comment(0xFE00, 'Save A', align=Align.INLINE)
d.comment(0xFE01, 'Read byte (address patched by setup)', align=Align.INLINE)
d.comment(0xFE04, 'Send byte to Tube R3', align=Align.INLINE)
d.comment(0xFE07, 'Increment address low byte', align=Align.INLINE)
d.comment(0xFE0A, 'No carry: skip high byte increment', align=Align.INLINE)
d.comment(0xFE0C, 'Increment address high byte', align=Align.INLINE)
d.comment(0xFE0F, 'Restore A', align=Align.INLINE)
d.comment(0xFE10, 'Return from NMI', align=Align.INLINE)
d.comment(0xFE11, 'Save A', align=Align.INLINE)
d.comment(0xFE12, 'Read byte from Tube R3', align=Align.INLINE)
d.comment(0xFE15, 'Store byte (address patched by setup)', align=Align.INLINE)
d.comment(0xFE18, 'Increment address low byte', align=Align.INLINE)
d.comment(0xFE1B, 'No carry: skip high byte increment', align=Align.INLINE)
d.comment(0xFE1D, 'Increment address high byte', align=Align.INLINE)
d.comment(0xFE20, 'Restore A', align=Align.INLINE)
d.comment(0xFE21, 'Return from NMI', align=Align.INLINE)
d.comment(0xFE22, 'Save A', align=Align.INLINE)
d.comment(0xFE23, 'Save Y', align=Align.INLINE)
d.comment(0xFE24, 'Push Y', align=Align.INLINE)
d.comment(0xFE25, 'Y=0 for indirect indexed access', align=Align.INLINE)
d.comment(0xFE27, 'Read first byte via pointer', align=Align.INLINE)
d.comment(0xFE29, 'Send to Tube R3', align=Align.INLINE)
d.comment(0xFE2C, 'Increment transfer address low', align=Align.INLINE)
d.comment(0xFE2E, 'No carry: skip high increment', align=Align.INLINE)
d.comment(0xFE30, 'Increment transfer address high', align=Align.INLINE)
d.comment(0xFE32, 'Read second byte via pointer', align=Align.INLINE)
d.comment(0xFE34, 'Send to Tube R3', align=Align.INLINE)
d.comment(0xFE37, 'Increment transfer address low', align=Align.INLINE)
d.comment(0xFE39, 'No carry: skip high increment', align=Align.INLINE)
d.comment(0xFE3B, 'Increment transfer address high', align=Align.INLINE)
d.comment(0xFE3D, 'Restore Y from stack', align=Align.INLINE)
d.comment(0xFE3E, 'Transfer to Y', align=Align.INLINE)
d.comment(0xFE3F, 'Restore A', align=Align.INLINE)
d.comment(0xFE40, 'Return from NMI', align=Align.INLINE)
d.comment(0xFE41, 'Save A', align=Align.INLINE)
d.comment(0xFE42, 'Save Y', align=Align.INLINE)
d.comment(0xFE43, 'Push Y', align=Align.INLINE)
d.comment(0xFE44, 'Y=0 for indirect indexed access', align=Align.INLINE)
d.comment(0xFE46, 'Read first byte from Tube R3', align=Align.INLINE)
d.comment(0xFE49, 'Store via transfer address pointer', align=Align.INLINE)
d.comment(0xFE4B, 'Increment transfer address low', align=Align.INLINE)
d.comment(0xFE4D, 'No carry: skip high increment', align=Align.INLINE)
d.comment(0xFE4F, 'Increment transfer address high', align=Align.INLINE)
d.comment(0xFE51, 'Read second byte from Tube R3', align=Align.INLINE)
d.comment(0xFE54, 'Store via transfer address pointer', align=Align.INLINE)
d.comment(0xFE56, 'Increment transfer address low', align=Align.INLINE)
d.comment(0xFE58, 'No carry: skip high increment', align=Align.INLINE)
d.comment(0xFE5A, 'Increment transfer address high', align=Align.INLINE)
d.comment(0xFE5C, 'Restore Y from stack', align=Align.INLINE)
d.comment(0xFE5D, 'Transfer to Y', align=Align.INLINE)
d.comment(0xFE5E, 'Restore A', align=Align.INLINE)
d.comment(0xFE5F, 'Return from NMI', align=Align.INLINE)
d.comment(0xFE60, 'Low bytes of transfer addr pointers', align=Align.INLINE)
d.comment(0xFE68, 'High bytes of transfer addr pointers', align=Align.INLINE)
d.comment(0xFE70, 'Low bytes of NMI handler addresses', align=Align.INLINE)
d.comment(0xFE78, 'High bytes of NMI handler addresses', align=Align.INLINE)
d.comment(0xFE80, 'Check Tube R1 for data', align=Align.INLINE)
d.comment(0xFE83, 'Data available: go read it', align=Align.INLINE)
d.comment(0xFE85, 'Check Tube R4 for pending transfers', align=Align.INLINE)
d.comment(0xFE88, 'Nothing pending: keep polling R1', align=Align.INLINE)
d.comment(0xFE8A, 'Save irq_a_store before IRQ', align=Align.INLINE)
d.comment(0xFE8C, 'Save processor status', align=Align.INLINE)
d.comment(0xFE8D, 'Allow one IRQ to service R4', align=Align.INLINE)
d.comment(0xFE8E, 'Restore processor status', align=Align.INLINE)
d.comment(0xFE8F, 'Restore irq_a_store after IRQ', align=Align.INLINE)
d.comment(0xFE91, 'Continue polling R1', align=Align.INLINE)
d.comment(0xFE94, 'Read byte from Tube R1', align=Align.INLINE)
d.comment(0xFE97, 'Return with byte in A', align=Align.INLINE)
d.comment(0xFE98, 'Pull return address low', align=Align.INLINE)
d.comment(0xFE99, 'Store in control_block_ptr low', align=Align.INLINE)
d.comment(0xFE9B, 'Pull return address high', align=Align.INLINE)
d.comment(0xFE9C, 'Store in control_block_ptr high', align=Align.INLINE)
d.comment(0xFE9E, 'Y=0 for indirect access', align=Align.INLINE)
d.comment(0xFEA0, 'Increment string pointer low', align=Align.INLINE)
d.comment(0xFEA2, 'No carry: skip high byte', align=Align.INLINE)
d.comment(0xFEA4, 'Increment string pointer high', align=Align.INLINE)
d.comment(0xFEA6, 'Read character from inline string', align=Align.INLINE)
d.comment(0xFEA8, 'Bit 7 set: end of string', align=Align.INLINE)
d.comment(0xFEAA, 'Print character via OSWRCH', align=Align.INLINE)
d.comment(0xFEAD, 'Loop for next character', align=Align.INLINE)
d.comment(0xFEB0, 'Jump to terminator byte and execute it', align=Align.INLINE)
d.comment(0xFEB3, 'Write to Tube R3 to acknowledge NMI', align=Align.INLINE)
d.comment(0xFEF0, 'Tube R1 status (mirror, not used)', align=Align.INLINE)
d.comment(0xFEF1, 'Tube R1 data (mirror, not used)', align=Align.INLINE)
d.comment(0xFEF2, 'Tube R2 status (mirror, not used)', align=Align.INLINE)
d.comment(0xFEF3, 'Tube R2 data (mirror, not used)', align=Align.INLINE)
d.comment(0xFEF4, 'Tube R3 status (mirror, not used)', align=Align.INLINE)
d.comment(0xFEF5, 'Tube R3 data (mirror, not used)', align=Align.INLINE)
d.comment(0xFEF6, 'Tube R4 status (mirror, not used)', align=Align.INLINE)
d.comment(0xFEF7, 'Tube R4 data (mirror, not used)', align=Align.INLINE)
d.comment(0xFEF8, 'Tube register 1 status', align=Align.INLINE)
d.comment(0xFEF9, 'Tube register 1 data', align=Align.INLINE)
d.comment(0xFEFA, 'Tube register 2 status', align=Align.INLINE)
d.comment(0xFEFB, 'Tube register 2 data', align=Align.INLINE)
d.comment(0xFEFC, 'Tube register 3 status', align=Align.INLINE)
d.comment(0xFEFD, 'Tube register 3 data', align=Align.INLINE)
d.comment(0xFEFE, 'Tube register 4 status', align=Align.INLINE)
d.comment(0xFEFF, 'Tube register 4 data', align=Align.INLINE)
d.comment(0xFFB9, "Unsupported: generates 'Bad' error", align=Align.INLINE)
d.comment(0xFFC8, 'Non-vectored RDCH', align=Align.INLINE)
d.comment(0xFFCB, 'Non-vectored WRCH', align=Align.INLINE)
d.comment(0xFFCE, 'Dispatch via FINDV', align=Align.INLINE)
d.comment(0xFFD1, 'Dispatch via GBPBV', align=Align.INLINE)
d.comment(0xFFD4, 'Dispatch via BPUTV', align=Align.INLINE)
d.comment(0xFFD7, 'Dispatch via BGETV', align=Align.INLINE)
d.comment(0xFFDA, 'Dispatch via ARGSV', align=Align.INLINE)
d.comment(0xFFDD, 'Dispatch via FILEV', align=Align.INLINE)
d.comment(0xFFE0, 'Dispatch via RDCHV', align=Align.INLINE)
d.comment(0xFFE3, 'Is it carriage return?', align=Align.INLINE)
d.comment(0xFFE5, 'No: skip newline, go to OSWRCH', align=Align.INLINE)
d.comment(0xFFE7, 'Send linefeed first', align=Align.INLINE)
d.comment(0xFFE9, 'Send linefeed via OSWRCH', align=Align.INLINE)
d.comment(0xFFEC, 'Load carriage return', align=Align.INLINE)
d.comment(0xFFEE, 'Dispatch via WRCHV', align=Align.INLINE)
d.comment(0xFFF1, 'Dispatch via WORDV', align=Align.INLINE)
d.comment(0xFFF4, 'Dispatch via BYTEV', align=Align.INLINE)
d.comment(0xFFF7, 'Dispatch via CLIV', align=Align.INLINE)
for addr in [0xF95D, 0xF95E, 0xF95F, 0xF960, 0xF961]:
    d.byte(addr)
d.byte(0xFEB7, 0xFEF0 - 0xFEB7)
for addr in range(0xFEF0, 0xFEF8):
    d.byte(addr)
for addr in range(0xFEF8, 0xFF00):
    d.byte(addr)
d.byte(0xFF00, 0xFF80 - 0xFF00)
_default_vectors = [(0xFF80, 'unsupported', 'USERV  - User vector'), (0xFF82, 'error_handler', 'BRKV   - BRK vector'), (0xFF84, 'irq1_handler', 'IRQ1V  - Primary IRQ handler'), (0xFF86, 'unsupported', 'IRQ2V  - Secondary IRQ handler'), (0xFF88, 'oscli_impl', 'CLIV   - OSCLI vector'), (0xFF8A, 'osbyte_impl', 'BYTEV  - OSBYTE vector'), (0xFF8C, 'osword_impl', 'WORDV  - OSWORD vector'), (0xFF8E, 'oswrch_impl', 'WRCHV  - OSWRCH vector'), (0xFF90, 'osrdch_impl', 'RDCHV  - OSRDCH vector'), (0xFF92, 'osfile_impl', 'FILEV  - OSFILE vector'), (0xFF94, 'osargs_impl', 'ARGSV  - OSARGS vector'), (0xFF96, 'osbget_impl', 'BGetV  - OSBGET vector'), (0xFF98, 'osbput_impl', 'BPutV  - OSBPUT vector'), (0xFF9A, 'osgbpb_impl', 'GBPBV  - OSGBPB vector'), (0xFF9C, 'osfind_impl', 'FINDV  - OSFIND vector'), (0xFF9E, 'unsupported', 'FSCV   - FS control vector'), (0xFFA0, 'null_return', 'EVNTV  - Event vector'), (0xFFA2, 'unsupported', 'UPTV   - User print vector'), (0xFFA4, 'unsupported', 'NETV   - Network vector'), (0xFFA6, 'unsupported', 'VduV   - Unrecognised VDU vector'), (0xFFA8, 'unsupported', 'KEYV   - Keyboard vector'), (0xFFAA, 'unsupported', 'INSV   - Insert buffer vector'), (0xFFAC, 'unsupported', 'RemV   - Remove buffer vector'), (0xFFAE, 'unsupported', 'CNPV   - Count/purge buffer vector'), (0xFFB0, 'null_return', 'IND1V  - Spare indirect vector 1'), (0xFFB2, 'null_return', 'IND2V  - Spare indirect vector 2'), (0xFFB4, 'null_return', 'IND3V  - Spare indirect vector 3')]
for addr, target, desc in _default_vectors:
    d.word(addr)
    d.expr(addr, target)
    d.comment(addr, desc, align=Align.INLINE)
d.byte(0xFFB6)
d.comment(0xFFB6, 'Vector table length: &36 bytes (27 words at &FF80)', align=Align.INLINE)
d.word(0xFFB7)
d.expr(0xFFB7, 'default_vector_table')
d.comment(0xFFB7, 'Address of default vector table', align=Align.INLINE)
d.word(0xFFFA)
d.expr(0xFFFA, 'nmi_acknowledge')
d.comment(0xFFFA, 'NMI vector (patched at runtime)', align=Align.INLINE)
d.word(0xFFFC)
d.expr(0xFFFC, 'reset')
d.comment(0xFFFC, 'RESET vector', align=Align.INLINE)
d.word(0xFFFE)
d.expr(0xFFFE, 'interrupt_handler')
d.comment(0xFFFE, 'IRQ/BRK vector', align=Align.INLINE)
for addr in range(0xFCBC, 0xFCD0):
    d.byte(addr)
for addr in range(0xFCD0, 0xFCE5):
    d.byte(addr)
_transfer_addr_ptrs = ['nmi0_transfer_addr', 'nmi1_transfer_addr', 'data_transfer_addr', 'data_transfer_addr', 'data_transfer_addr', 'data_transfer_addr', 'nmi6_transfer_addr', 'nmi7_transfer_addr']
for i, name in enumerate(_transfer_addr_ptrs):
    d.byte(0xFE60 + i)
    d.expr(0xFE60 + i, f'<({name})')
    d.byte(0xFE68 + i)
    d.expr(0xFE68 + i, f'>({name})')
_nmi_routines = ['nmi_single_byte_to_tube', 'nmi_single_byte_from_tube', 'nmi_two_bytes_to_tube', 'nmi_two_bytes_from_tube', 'nmi_acknowledge', 'nmi_acknowledge', 'nmi_acknowledge', 'nmi_acknowledge']
for i, name in enumerate(_nmi_routines):
    d.byte(0xFE70 + i)
    d.expr(0xFE70 + i, f'<({name})')
    d.byte(0xFE78 + i)
    d.expr(0xFE78 + i, f'>({name})')
import sys
ir = d.disassemble()
output = str(ir.render('beebasm', boundary_label_prefix='pydis_', byte_column=True, byte_column_format='py8dis', default_byte_cols=12, default_word_cols=6))
_output_dirpath.mkdir(parents=True, exist_ok=True)
output_filepath = _output_dirpath / 'tube-6502-client-1.10.asm'
output_filepath.write_text(output, encoding='utf-8')
print(f'Wrote {output_filepath}', file=sys.stderr)
json_filepath = _output_dirpath / 'tube-6502-client-1.10.json'
json_filepath.write_text(str(ir.render('json')), encoding='utf-8')
print(f'Wrote {json_filepath}', file=sys.stderr)
