    cpu 1

; Constants
tube_r1_data    = 65273
tube_r1_status  = 65272
tube_r2_data    = 65275
tube_r2_status  = 65274
tube_r3_data    = 65277
tube_r3_status  = 65276
tube_r4_data    = 65279
tube_r4_status  = 65278

; Memory locations
l0000                   = &0000
l0001                   = &0001
l0002                   = &0002
l0003                   = &0003
current_program         = &00ee
current_program_hi      = &00ef
hex_accumulator         = &00f0
hex_accumulator_hi      = &00f1
memory_top              = &00f2
memory_top_hi           = &00f3
transfer_addr_ptr       = &00f4
transfer_addr_ptr_hi    = &00f5
data_transfer_addr      = &00f6
data_transfer_addr_hi   = &00f7
string_ptr              = &00f8
string_ptr_hi           = &00f9
control_block_ptr       = &00fa
control_block_ptr_hi    = &00fb
irq_a_store             = &00fc
last_error              = &00fd
last_error_hi           = &00fe
escape_flag             = &00ff
low_memory_code         = &0100
irq_return_addr_lo      = &0103
irq_return_addr_hi      = &0104
userv                   = &0200
brkv                    = &0202
brkv_hi                 = &0203
irq1v                   = &0204
irq2v                   = &0206
cliv                    = &0208
bytev                   = &020a
wordv                   = &020c
wrchv                   = &020e
rdchv                   = &0210
filev                   = &0212
argsv                   = &0214
bgetv                   = &0216
bputv                   = &0218
gbpbv                   = &021a
findv                   = &021c
evntv                   = &0220
error_buffer            = &0236
error_buffer_errnum     = &0237

    org &f800

; ***************************************************************************************
; Initialise the 65C02 parasite processor.
; 
;     Copies the ROM contents to RAM, sets up the default MOS
;     vectors, clears the escape flag, and jumps via low memory
;     to page out the ROM and start the operating system.
; ***************************************************************************************
.pydis_start
.reset
    ldx #0                                                            ; f800: a2 00       ..
; Copy &FF00-&FFFF to RAM (self-copy)
; &f802 referenced 1 time by &f809
.loop_cf802
    lda lff00,x                                                       ; f802: bd 00 ff    ...
    sta lff00,x                                                       ; f805: 9d 00 ff    ...
    dex                                                               ; f808: ca          .
    bne loop_cf802                                                    ; f809: d0 f7       ..
; 54 bytes = 27 default vector entries
    ldx #&36 ; '6'                                                    ; f80b: a2 36       .6
; Copy default vector table to &0200-&0236
; &f80d referenced 1 time by &f814
.loop_cf80d
    lda default_vector_table,x                                        ; f80d: bd 80 ff    ...
    sta userv,x                                                       ; f810: 9d 00 02    ...
    dex                                                               ; f813: ca          .
    bpl loop_cf80d                                                    ; f814: 10 f7       ..
; Clear the stack
    txs                                                               ; f816: 9a          .
; X=&F0: copy &FE00-&FEEF, avoiding Tube I/O
    ldx #&f0                                                          ; f817: a2 f0       ..
; Copy pages &FE-&FD to RAM, skipping Tube registers
; &f819 referenced 1 time by &f820
.loop_cf819
    lda lfdff,x                                                       ; f819: bd ff fd    ...
    sta lfdff,x                                                       ; f81c: 9d ff fd    ...
    dex                                                               ; f81f: ca          .
    bne loop_cf819                                                    ; f820: d0 f7       ..
; Point string_ptr to start of ROM (&F800)
    ldy #0                                                            ; f822: a0 00       ..
    sty string_ptr                                                    ; f824: 84 f8       ..
    lda #&f8                                                          ; f826: a9 f8       ..
    sta string_ptr_hi                                                 ; f828: 85 f9       ..
; Copy a page of ROM to RAM
; &f82a referenced 2 times by &f82f, &f837
.cf82a
    lda (string_ptr),y                                                ; f82a: b1 f8       ..
    sta (string_ptr),y                                                ; f82c: 91 f8       ..
    iny                                                               ; f82e: c8          .
    bne cf82a                                                         ; f82f: d0 f9       ..
; Next page
    inc string_ptr_hi                                                 ; f831: e6 f9       ..
    lda string_ptr_hi                                                 ; f833: a5 f9       ..
; Stop before I/O space at &FE00
    cmp #&fe                                                          ; f835: c9 fe       ..
    bne cf82a                                                         ; f837: d0 f1       ..
; 17 bytes of low memory startup code
    ldx #&10                                                          ; f839: a2 10       ..
; Copy startup code to &0100
; &f83b referenced 1 time by &f842
.loop_cf83b
    lda low_memory_startup_code,x                                     ; f83b: bd 59 f8    .Y.
    sta low_memory_code,x                                             ; f83e: 9d 00 01    ...
    dex                                                               ; f841: ca          .
    bpl loop_cf83b                                                    ; f842: 10 f7       ..
; Copy current program address to transfer address
    lda current_program                                               ; f844: a5 ee       ..
    sta data_transfer_addr                                            ; f846: 85 f6       ..
    lda current_program_hi                                            ; f848: a5 ef       ..
    sta data_transfer_addr_hi                                         ; f84a: 85 f7       ..
; Clear escape flag
    lda #0                                                            ; f84c: a9 00       ..
    sta escape_flag                                                   ; f84e: 85 ff       ..
; Set low byte of memory top
    sta memory_top                                                    ; f850: 85 f2       ..
; Memory top = start of ROM code
    lda #&f8                                                          ; f852: a9 f8       ..
    sta memory_top_hi                                                 ; f854: 85 f3       ..
; Jump to low memory to page ROM out
    jmp low_memory_code                                               ; f856: 4c 00 01    L..

; ***************************************************************************************
; Executed from &0100 after being copied from ROM.
; 
;     Reads Tube R1 status to page out the ROM, enables
;     interrupts, then jumps to display the startup banner.
;     On subsequent soft resets, the JMP target at &F85E is
;     patched to skip the banner and enter the command prompt
;     directly.
; ***************************************************************************************
; Read Tube R1 status to page ROM out
; &f859 referenced 1 time by &f83b
.low_memory_startup_code
    lda lfef8                                                         ; f859: ad f8 fe    ...
; Enable IRQs for data transfers
    cli                                                               ; f85c: 58          X
; Target patched after first boot to skip banner
.sub_cf85d
lf85e = sub_cf85d+1
lf85f = sub_cf85d+2
    jmp startup_banner                                                ; f85d: 4c 60 f8    L`.            ; Print the startup banner, patch the soft reset entry
;     to skip the banner on future resets, then wait for the
;     host's acknowledge byte.
; 
;     If the acknowledge has bit 7 set, the host is requesting
;     code execution; otherwise enters the command prompt.

; &f85e referenced 1 time by &f87e
; &f85f referenced 1 time by &f883
; ***************************************************************************************
; Print the startup banner, patch the soft reset entry
;     to skip the banner on future resets, then wait for the
;     host's acknowledge byte.
; 
;     If the acknowledge has bit 7 set, the host is requesting
;     code execution; otherwise enters the command prompt.
; ***************************************************************************************
; &f860 referenced 1 time by &f85d
.startup_banner
    jsr print_embedded_text                                           ; f860: 20 98 fe     ..            ; Print the text string embedded immediately after the
;     JSR to this routine. Characters are sent to OSWRCH
;     until a byte with bit 7 set is encountered, which
;     terminates the string. Execution resumes after the
;     terminator byte.
; 
;     On exit:
;       A = terminator byte (bit 7 set)
    equs &0a, "Acorn TUBE 6502 64K", &0a, &0a, &0d, 0                 ; f863: 0a 41 63... .Ac
; Patch the low memory JMP target to command_prompt

    nop                                                               ; f87b: ea          .
    lda #&8d                                                          ; f87c: a9 8d       ..
    sta lf85e                                                         ; f87e: 8d 5e f8    .^.
; Wait for host's acknowledge byte
    lda #&f8                                                          ; f881: a9 f8       ..
; Bit 7 set means host wants code entered
    sta lf85f                                                         ; f883: 8d 5f f8    ._.
; Otherwise enter the command prompt
    jsr wait_for_tube_r2_byte                                         ; f886: 20 75 f9     u.
    cmp #&80                                                          ; f889: c9 80       ..
    beq enter_code                                                    ; f88b: f0 28       .(             ; Check whether the code at the data transfer address
;     has a valid ROM header with a (C) string, and if so
;     verify it is a 6502 language ROM.
; 
;     Sets the current program and memory top to the
;     transfer address, then enters the code with A=1.
;     If the header is missing or invalid, enters with A=1
;     anyway (raw code entry). Generates an error if the
;     ROM type indicates it is not a language or not 6502
;     code.
; ***************************************************************************************
; The main supervisor command prompt.
; 
;     Prints a '*' prompt, reads a line of input using
;     OSWORD 0, and passes it to OSCLI for execution.
;     Handles Escape by acknowledging it and reporting
;     the error.
; ***************************************************************************************
; Print '*' prompt
; &f88d referenced 2 times by &f8a4, &f95a
.command_prompt
    lda #&2a ; '*'                                                    ; f88d: a9 2a       .*
    jsr oswrch_entry                                                  ; f88f: 20 ee ff     ..
; Point to rdline control block
    ldx #&5d ; ']'                                                    ; f892: a2 5d       .]
    ldy #&f9                                                          ; f894: a0 f9       ..
; OSWORD 0: read line
    lda #0                                                            ; f896: a9 00       ..
    jsr osword_entry                                                  ; f898: 20 f1 ff     ..
; Escape pressed during input
    bcs command_prompt_escape                                         ; f89b: b0 0a       ..
; Point XY to input buffer at &0236
    ldx #&36 ; '6'                                                    ; f89d: a2 36       .6
    ldy #2                                                            ; f89f: a0 02       ..
; Execute the command via OSCLI
    jsr oscli_entry                                                   ; f8a1: 20 f7 ff     ..
    jmp command_prompt                                                ; f8a4: 4c 8d f8    L..            ; The main supervisor command prompt.
; 
;     Prints a '*' prompt, reads a line of input using
;     OSWORD 0, and passes it to OSCLI for execution.
;     Handles Escape by acknowledging it and reporting
;     the error.

; OSBYTE &7E: acknowledge Escape
; &f8a7 referenced 1 time by &f89b
.command_prompt_escape
    lda #&7e ; '~'                                                    ; f8a7: a9 7e       .~
    jsr osbyte_entry                                                  ; f8a9: 20 f4 ff     ..
; BRK with error 17: 'Escape'
    brk                                                               ; f8ac: 00          .

    equb &11                                                          ; f8ad: 11          .
    equs "Escape"                                                     ; f8ae: 45 73 63... Esc
    equb 0                                                            ; f8b4: 00          .

; ***************************************************************************************
; Check whether the code at the data transfer address
;     has a valid ROM header with a (C) string, and if so
;     verify it is a 6502 language ROM.
; 
;     Sets the current program and memory top to the
;     transfer address, then enters the code with A=1.
;     If the header is missing or invalid, enters with A=1
;     anyway (raw code entry). Generates an error if the
;     ROM type indicates it is not a language or not 6502
;     code.
; ***************************************************************************************
; Set current program from transfer address
; &f8b5 referenced 2 times by &f88b, &fa62
.enter_code
    lda data_transfer_addr                                            ; f8b5: a5 f6       ..
    sta current_program                                               ; f8b7: 85 ee       ..
; Also set memory top
    sta memory_top                                                    ; f8b9: 85 f2       ..
    lda data_transfer_addr_hi                                         ; f8bb: a5 f7       ..
    sta current_program_hi                                            ; f8bd: 85 ef       ..
    sta memory_top_hi                                                 ; f8bf: 85 f3       ..
; Offset 7 in ROM header = copyright offset
    ldy #7                                                            ; f8c1: a0 07       ..
    lda (current_program),y                                           ; f8c3: b1 ee       ..
; Clear decimal mode, compute copyright pointer
    cld                                                               ; f8c5: d8          .
    clc                                                               ; f8c6: 18          .
    adc current_program                                               ; f8c7: 65 ee       e.
; last_error now points to copyright string
    sta last_error                                                    ; f8c9: 85 fd       ..
    lda #0                                                            ; f8cb: a9 00       ..
    adc current_program_hi                                            ; f8cd: 65 ef       e.
    sta last_error_hi                                                 ; f8cf: 85 fe       ..
    ldy #0                                                            ; f8d1: a0 00       ..
; Check for &00 before '(C)'
    lda (last_error),y                                                ; f8d3: b1 fd       ..
    bne enter_raw_code                                                ; f8d5: d0 23       .#
; Check for '('
    iny                                                               ; f8d7: c8          .              ; Y=&01
    lda (last_error),y                                                ; f8d8: b1 fd       ..
    cmp #&28 ; '('                                                    ; f8da: c9 28       .(
    bne enter_raw_code                                                ; f8dc: d0 1c       ..
; Check for 'C'
    iny                                                               ; f8de: c8          .              ; Y=&02
    lda (last_error),y                                                ; f8df: b1 fd       ..
    cmp #&43 ; 'C'                                                    ; f8e1: c9 43       .C
    bne enter_raw_code                                                ; f8e3: d0 15       ..
; Check for ')'
    iny                                                               ; f8e5: c8          .              ; Y=&03
    lda (last_error),y                                                ; f8e6: b1 fd       ..
    cmp #&29 ; ')'                                                    ; f8e8: c9 29       .)
    bne enter_raw_code                                                ; f8ea: d0 0e       ..
; Offset 6 = ROM type byte
    ldy #6                                                            ; f8ec: a0 06       ..
    lda (current_program),y                                           ; f8ee: b1 ee       ..
; Mask to check language and 6502 bits
    and #&4f ; 'O'                                                    ; f8f0: 29 4f       )O
; Bit 6 clear means not a language
    cmp #&40 ; '@'                                                    ; f8f2: c9 40       .@
    bcc error_not_a_language                                          ; f8f4: 90 09       ..
; Type 0 or 2 = 6502 code
    and #&0d                                                          ; f8f6: 29 0d       ).
    bne error_not_6502_code                                           ; f8f8: d0 28       .(
; Enter code with A=1
; &f8fa referenced 4 times by &f8d5, &f8dc, &f8e3, &f8ea
.enter_raw_code
    lda #1                                                            ; f8fa: a9 01       ..
    jmp (memory_top)                                                  ; f8fc: 6c f2 00    l..

; Set up error handler before reporting error
; &f8ff referenced 1 time by &f8f4
.error_not_a_language
    lda #&45 ; 'E'                                                    ; f8ff: a9 45       .E
    sta brkv                                                          ; f901: 8d 02 02    ...
    lda #&f9                                                          ; f904: a9 f9       ..
    sta brkv_hi                                                       ; f906: 8d 03 02    ...
; BRK: 'This is not a language'
    brk                                                               ; f909: 00          .

    equb 0                                                            ; f90a: 00          .
    equs "This is not a language"                                     ; f90b: 54 68 69... Thi
    equb 0                                                            ; f921: 00          .

; Set up error handler before reporting error
; &f922 referenced 1 time by &f8f8
.error_not_6502_code
    lda #&45 ; 'E'                                                    ; f922: a9 45       .E
    sta brkv                                                          ; f924: 8d 02 02    ...
    lda #&f9                                                          ; f927: a9 f9       ..
    sta brkv_hi                                                       ; f929: 8d 03 02    ...
; BRK: error 0, 'I cannot run this code'
    brk                                                               ; f92c: 00          .

    equb 0                                                            ; f92d: 00          .
    equs "I cannot run this code"                                     ; f92e: 49 20 63... I c
    equb 0                                                            ; f944: 00          .

; ***************************************************************************************
; Default BRK handler. Clears the stack, prints the
;     error message from the BRK instruction, and returns
;     to the command prompt.
; ***************************************************************************************
; Reset the stack
.error_handler
    ldx #&ff                                                          ; f945: a2 ff       ..
    txs                                                               ; f947: 9a          .
; Print newline
    jsr osnewl_entry                                                  ; f948: 20 e7 ff     ..
    ldy #1                                                            ; f94b: a0 01       ..
; Print error message characters
; &f94d referenced 1 time by &f955
.loop_cf94d
    lda (last_error),y                                                ; f94d: b1 fd       ..
    beq cf957                                                         ; f94f: f0 06       ..
    jsr oswrch_entry                                                  ; f951: 20 ee ff     ..
    iny                                                               ; f954: c8          .
    bne loop_cf94d                                                    ; f955: d0 f6       ..
; Print newline and return to command prompt
; &f957 referenced 1 time by &f94f
.cf957
    jsr osnewl_entry                                                  ; f957: 20 e7 ff     ..
    jmp command_prompt                                                ; f95a: 4c 8d f8    L..            ; The main supervisor command prompt.
; 
;     Prints a '*' prompt, reads a line of input using
;     OSWORD 0, and passes it to OSCLI for execution.
;     Handles Escape by acknowledging it and reporting
;     the error.

; Buffer at &0236, length &CA, min &20, max &FF
.rdline_control_block
    equb &36                                                          ; f95d: 36          6
    equb 2                                                            ; f95e: 02          .
    equb &ca                                                          ; f95f: ca          .
    equb &20                                                          ; f960: 20
    equb &ff                                                          ; f961: ff          .

; ***************************************************************************************
; Send character in A to the host via Tube R1.
; 
;     On entry:
;       A = character to send
;     On exit:
;       A preserved
; ***************************************************************************************
; Check Tube R1 status
; &f962 referenced 2 times by &f966, &ffcb
.oswrch_impl
    bit lfef8                                                         ; f962: 2c f8 fe    ,..
; NOP for timing
    nop                                                               ; f965: ea          .
; Wait until Tube R1 is ready for data
    bvc oswrch_impl                                                   ; f966: 50 fa       P.             ; Send character in A to the host via Tube R1.
; 
;     On entry:
;       A = character to send
;     On exit:
;       A preserved
; Send character to Tube R1 data register
    sta lfef9                                                         ; f968: 8d f9 fe    ...
    rts                                                               ; f96b: 60          `

; ***************************************************************************************
; Read a character from the host via the Tube.
; 
;     Sends command &00 to the host, then waits for
;     a carry byte and the character.
; 
;     On exit:
;       A = character received
;       C = Escape flag
; ***************************************************************************************
; Send command &00 to host via R2: OSRDCH
; &f96c referenced 1 time by &ffc8
.osrdch_impl
    lda #0                                                            ; f96c: a9 00       ..
    jsr send_command                                                  ; f96e: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Wait for carry byte from R2
; &f971 referenced 2 times by &fc33, &fcb4
.wait_carry_and_byte
    jsr wait_for_tube_r2_byte                                         ; f971: 20 75 f9     u.
; Shift carry into C flag via ASL
    asl a                                                             ; f974: 0a          .
; Poll Tube R2 status for data available
; &f975 referenced 18 times by &f886, &f971, &f978, &fa35, &fba3, &fbf2, &fbf6, &fbfb, &fc00, &fc05, &fc1f, &fc27, &fc45, &fc78, &fc7e, &fca8, &fd53, &fd5a
.wait_for_tube_r2_byte
    bit lfefa                                                         ; f975: 2c fa fe    ,..
    bpl wait_for_tube_r2_byte                                         ; f978: 10 fb       ..
; Read byte from Tube R2
    lda lfefb                                                         ; f97a: ad fb fe    ...
.null_return
    rts                                                               ; f97d: 60          `

; &f97e referenced 2 times by &f983, &fa44
.skip_spaces_step
    iny                                                               ; f97e: c8          .
; ***************************************************************************************
; Advance past space characters in the string at
;     (string_ptr),Y.
; 
;     On entry:
;       Y = current offset into string
;     On exit:
;       A = first non-space character
;       Y = offset of that character
; ***************************************************************************************
; Load character from (string_ptr),Y
; &f97f referenced 2 times by &f9d1, &fa4a
.skip_spaces
    lda (string_ptr),y                                                ; f97f: b1 f8       ..
; Is it a space?
    cmp #&20 ; ' '                                                    ; f981: c9 20       .
    beq skip_spaces_step                                              ; f983: f0 f9       ..
    rts                                                               ; f985: 60          `

; ***************************************************************************************
; Read a hexadecimal number from the string at
;     (string_ptr),Y into the hex accumulator at &F0/F1.
; 
;     On entry:
;       Y = offset into string
;     On exit:
;       hex_accumulator/hex_accumulator_hi = parsed value
;       X = non-zero if any digits were parsed
;       Y = offset past last hex digit
;       A = first non-hex character
; ***************************************************************************************
; Clear hex accumulator
; &f986 referenced 1 time by &fa47
.scan_hex
    ldx #0                                                            ; f986: a2 00       ..
    stx hex_accumulator                                               ; f988: 86 f0       ..
    stx hex_accumulator_hi                                            ; f98a: 86 f1       ..
; Get next character
; &f98c referenced 1 time by &f9af
.cf98c
    lda (string_ptr),y                                                ; f98c: b1 f8       ..
; Below '0': not a hex digit
    cmp #&30 ; '0'                                                    ; f98e: c9 30       .0
    bcc return_1                                                      ; f990: 90 1f       ..
; Below ':': it's '0'-'9'
    cmp #&3a ; ':'                                                    ; f992: c9 3a       .:
    bcc cf9a0                                                         ; f994: 90 0a       ..
; Force uppercase and adjust for A-F
    and #&df                                                          ; f996: 29 df       ).
    sbc #7                                                            ; f998: e9 07       ..
    bcc return_1                                                      ; f99a: 90 15       ..
; Above 'F': not a hex digit
    cmp #&40 ; '@'                                                    ; f99c: c9 40       .@
    bcs return_1                                                      ; f99e: b0 11       ..
; Shift digit into upper nybble
; &f9a0 referenced 1 time by &f994
.cf9a0
    asl a                                                             ; f9a0: 0a          .
    asl a                                                             ; f9a1: 0a          .
    asl a                                                             ; f9a2: 0a          .
    asl a                                                             ; f9a3: 0a          .
; Rotate 4 bits into accumulator
    ldx #3                                                            ; f9a4: a2 03       ..
; &f9a6 referenced 1 time by &f9ac
.loop_cf9a6
    asl a                                                             ; f9a6: 0a          .
    rol hex_accumulator                                               ; f9a7: 26 f0       &.
    rol hex_accumulator_hi                                            ; f9a9: 26 f1       &.
    dex                                                               ; f9ab: ca          .
    bpl loop_cf9a6                                                    ; f9ac: 10 f8       ..
    iny                                                               ; f9ae: c8          .
    bne cf98c                                                         ; f9af: d0 db       ..
; &f9b1 referenced 3 times by &f990, &f99a, &f99e
.return_1
    rts                                                               ; f9b1: 60          `

; ***************************************************************************************
; Send a CR-terminated string to the host via Tube R2.
; 
;     On entry:
;       X = string address low byte
;       Y = string address high byte
;     On exit:
;       Y restored from string_ptr_hi
; ***************************************************************************************
; Store string address in string_ptr
; &f9b2 referenced 2 times by &fc24, &fc71
.send_string
    stx string_ptr                                                    ; f9b2: 86 f8       ..
    sty string_ptr_hi                                                 ; f9b4: 84 f9       ..
; &f9b6 referenced 1 time by &fa32
.send_string_via_ptr
    ldy #0                                                            ; f9b6: a0 00       ..
; Wait for Tube R2 free
; &f9b8 referenced 2 times by &f9bb, &f9c5
.cf9b8
    bit lfefa                                                         ; f9b8: 2c fa fe    ,..
    bvc cf9b8                                                         ; f9bb: 50 fb       P.
; Send character from (string_ptr),Y
    lda (string_ptr),y                                                ; f9bd: b1 f8       ..
    sta lfefb                                                         ; f9bf: 8d fb fe    ...
    iny                                                               ; f9c2: c8          .
; Loop until CR sent
    cmp #&0d                                                          ; f9c3: c9 0d       ..
    bne cf9b8                                                         ; f9c5: d0 f1       ..
; Restore Y from string_ptr_hi
    ldy string_ptr_hi                                                 ; f9c7: a4 f9       ..
    rts                                                               ; f9c9: 60          `

; ***************************************************************************************
; Execute a * command. Parses the command to check for
;     *GO and *HELP which are handled locally; all other
;     commands are forwarded to the host via the Tube.
; 
;     On entry:
;       X = command string address low byte
;       Y = command string address high byte
; ***************************************************************************************
; Save A, store command string address
.oscli_impl
    pha                                                               ; f9ca: 48          H
    stx string_ptr                                                    ; f9cb: 86 f8       ..
    sty string_ptr_hi                                                 ; f9cd: 84 f9       ..
    ldy #0                                                            ; f9cf: a0 00       ..
; Skip leading spaces and stars
; &f9d1 referenced 1 time by &f9d7
.loop_cf9d1
    jsr skip_spaces                                                   ; f9d1: 20 7f f9     ..            ; Advance past space characters in the string at
;     (string_ptr),Y.
; 
;     On entry:
;       Y = current offset into string
;     On exit:
;       A = first non-space character
;       Y = offset of that character
    iny                                                               ; f9d4: c8          .
    cmp #&2a ; '*'                                                    ; f9d5: c9 2a       .*
    beq loop_cf9d1                                                    ; f9d7: f0 f8       ..
; Force uppercase for command matching
    and #&df                                                          ; f9d9: 29 df       ).
    tax                                                               ; f9db: aa          .
; Peek at next character
    lda (string_ptr),y                                                ; f9dc: b1 f8       ..
; Check for *GO
    cpx #&47 ; 'G'                                                    ; f9de: e0 47       .G
    beq command_go                                                    ; f9e0: f0 5c       .\             ; Parse *GO [address]. If an address is given, set the
;     transfer address to it. If no address given, use the
;     current transfer address. Falls through to execute
;     the code.
; 
;     Note: does not check for a separator after 'GO', so
;     commands like *GOAD would be incorrectly matched.
; Check for *H...
    cpx #&48 ; 'H'                                                    ; f9e2: e0 48       .H
    bne oscli_send_to_host                                            ; f9e4: d0 47       .G             ; Forward the command string at (string_ptr) to the
;     host via Tube R2 with command code &02.
; 
;     Tube protocol: &02 string &0D -- &7F or &80
; 
;     If the response has bit 7 set, code needs to be
;     entered (a language was selected).
; Abbreviated: H.
    cmp #&2e ; '.'                                                    ; f9e6: c9 2e       ..
    beq command_help                                                  ; f9e8: f0 2d       .-             ; Print local help text showing the Tube Client
;     version, then fall through to forward the *HELP
;     command to the host.
    and #&df                                                          ; f9ea: 29 df       ).
; Check for *HE...
    cmp #&45 ; 'E'                                                    ; f9ec: c9 45       .E
    bne oscli_send_to_host                                            ; f9ee: d0 3d       .=             ; Forward the command string at (string_ptr) to the
;     host via Tube R2 with command code &02.
; 
;     Tube protocol: &02 string &0D -- &7F or &80
; 
;     If the response has bit 7 set, code needs to be
;     entered (a language was selected).
    iny                                                               ; f9f0: c8          .
    lda (string_ptr),y                                                ; f9f1: b1 f8       ..
; Abbreviated: HE.
    cmp #&2e ; '.'                                                    ; f9f3: c9 2e       ..
    beq command_help                                                  ; f9f5: f0 20       .              ; Print local help text showing the Tube Client
;     version, then fall through to forward the *HELP
;     command to the host.
    and #&df                                                          ; f9f7: 29 df       ).
; Check for *HEL...
    cmp #&4c ; 'L'                                                    ; f9f9: c9 4c       .L
    bne oscli_send_to_host                                            ; f9fb: d0 30       .0             ; Forward the command string at (string_ptr) to the
;     host via Tube R2 with command code &02.
; 
;     Tube protocol: &02 string &0D -- &7F or &80
; 
;     If the response has bit 7 set, code needs to be
;     entered (a language was selected).
    iny                                                               ; f9fd: c8          .
    lda (string_ptr),y                                                ; f9fe: b1 f8       ..
; Abbreviated: HEL.
    cmp #&2e ; '.'                                                    ; fa00: c9 2e       ..
    beq command_help                                                  ; fa02: f0 13       ..             ; Print local help text showing the Tube Client
;     version, then fall through to forward the *HELP
;     command to the host.
    and #&df                                                          ; fa04: 29 df       ).
; Check for *HELP...
    cmp #&50 ; 'P'                                                    ; fa06: c9 50       .P
    bne oscli_send_to_host                                            ; fa08: d0 23       .#             ; Forward the command string at (string_ptr) to the
;     host via Tube R2 with command code &02.
; 
;     Tube protocol: &02 string &0D -- &7F or &80
; 
;     If the response has bit 7 set, code needs to be
;     entered (a language was selected).
    iny                                                               ; fa0a: c8          .
    lda (string_ptr),y                                                ; fa0b: b1 f8       ..
; Terminated by non-letter: it's *HELP
    and #&df                                                          ; fa0d: 29 df       ).
    cmp #&41 ; 'A'                                                    ; fa0f: c9 41       .A
    bcc command_help                                                  ; fa11: 90 04       ..             ; Print local help text showing the Tube Client
;     version, then fall through to forward the *HELP
;     command to the host.
; Followed by letter: pass to host
    cmp #&5b ; '['                                                    ; fa13: c9 5b       .[
    bcc oscli_send_to_host                                            ; fa15: 90 16       ..             ; Forward the command string at (string_ptr) to the
;     host via Tube R2 with command code &02.
; 
;     Tube protocol: &02 string &0D -- &7F or &80
; 
;     If the response has bit 7 set, code needs to be
;     entered (a language was selected).
; ***************************************************************************************
; Print local help text showing the Tube Client
;     version, then fall through to forward the *HELP
;     command to the host.
; ***************************************************************************************
; Print help text with version string
; &fa17 referenced 4 times by &f9e8, &f9f5, &fa02, &fa11
.command_help
    equb &20                                                          ; fa17: 20

    tya                                                               ; fa18: 98          .
    equb &fe                                                          ; fa19: fe          .
    equs &0a, &0d, "6502 TUBE 1.10", &0a, &0d                         ; fa1a: 0a 0d 36... ..6

    nop                                                               ; fa2c: ea          .
; ***************************************************************************************
; Forward the command string at (string_ptr) to the
;     host via Tube R2 with command code &02.
; 
;     Tube protocol: &02 string &0D -- &7F or &80
; 
;     If the response has bit 7 set, code needs to be
;     entered (a language was selected).
; ***************************************************************************************
; Send command &02 to host: OSCLI
; &fa2d referenced 7 times by &f9e4, &f9ee, &f9fb, &fa08, &fa15, &fa42, &fa4f
.oscli_send_to_host
    lda #2                                                            ; fa2d: a9 02       ..
    jsr send_command                                                  ; fa2f: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Send the command string via string_ptr
    jsr send_string_via_ptr                                           ; fa32: 20 b6 f9     ..
; Wait for host acknowledgement
; &fa35 referenced 1 time by &fa71
.oscli_wait_ack
    jsr wait_for_tube_r2_byte                                         ; fa35: 20 75 f9     u.
; Bit 7 set: host wants us to enter code
    cmp #&80                                                          ; fa38: c9 80       ..
    beq execute_code                                                  ; fa3a: f0 20       .              ; Save the current program pointer, call enter_code,
;     then restore the current program and memory top
;     on return.
; Restore A and return to caller
    pla                                                               ; fa3c: 68          h
    rts                                                               ; fa3d: 60          `

; ***************************************************************************************
; Parse *GO [address]. If an address is given, set the
;     transfer address to it. If no address given, use the
;     current transfer address. Falls through to execute
;     the code.
; 
;     Note: does not check for a separator after 'GO', so
;     commands like *GOAD would be incorrectly matched.
; ***************************************************************************************
; Check for 'O' after 'G'
; &fa3e referenced 1 time by &f9e0
.command_go
    and #&df                                                          ; fa3e: 29 df       ).
    cmp #&4f ; 'O'                                                    ; fa40: c9 4f       .O
    bne oscli_send_to_host                                            ; fa42: d0 e9       ..             ; Forward the command string at (string_ptr) to the
;     host via Tube R2 with command code &02.
; 
;     Tube protocol: &02 string &0D -- &7F or &80
; 
;     If the response has bit 7 set, code needs to be
;     entered (a language was selected).
; Skip past 'O' and any spaces
    jsr skip_spaces_step                                              ; fa44: 20 7e f9     ~.
; Parse optional hex address
    jsr scan_hex                                                      ; fa47: 20 86 f9     ..            ; Read a hexadecimal number from the string at
;     (string_ptr),Y into the hex accumulator at &F0/F1.
; 
;     On entry:
;       Y = offset into string
;     On exit:
;       hex_accumulator/hex_accumulator_hi = parsed value
;       X = non-zero if any digits were parsed
;       Y = offset past last hex digit
;       A = first non-hex character
; Skip trailing spaces
    jsr skip_spaces                                                   ; fa4a: 20 7f f9     ..            ; Advance past space characters in the string at
;     (string_ptr),Y.
; 
;     On entry:
;       Y = current offset into string
;     On exit:
;       A = first non-space character
;       Y = offset of that character
; More parameters: pass to host instead
    cmp #&0d                                                          ; fa4d: c9 0d       ..
; X=0 means no address given: use default
    bne oscli_send_to_host                                            ; fa4f: d0 dc       ..             ; Forward the command string at (string_ptr) to the
;     host via Tube R2 with command code &02.
; 
;     Tube protocol: &02 string &0D -- &7F or &80
; 
;     If the response has bit 7 set, code needs to be
;     entered (a language was selected).
; Set transfer address from parsed hex value
    txa                                                               ; fa51: 8a          .
    beq execute_code                                                  ; fa52: f0 08       ..             ; Save the current program pointer, call enter_code,
;     then restore the current program and memory top
;     on return.
    lda hex_accumulator                                               ; fa54: a5 f0       ..
    sta data_transfer_addr                                            ; fa56: 85 f6       ..
    lda hex_accumulator_hi                                            ; fa58: a5 f1       ..
    sta data_transfer_addr_hi                                         ; fa5a: 85 f7       ..
; ***************************************************************************************
; Save the current program pointer, call enter_code,
;     then restore the current program and memory top
;     on return.
; ***************************************************************************************
; Save current program on stack
; &fa5c referenced 2 times by &fa3a, &fa52
.execute_code
    lda current_program_hi                                            ; fa5c: a5 ef       ..
    pha                                                               ; fa5e: 48          H
    lda current_program                                               ; fa5f: a5 ee       ..
    pha                                                               ; fa61: 48          H
; Enter the code
    jsr enter_code                                                    ; fa62: 20 b5 f8     ..            ; Check whether the code at the data transfer address
;     has a valid ROM header with a (C) string, and if so
;     verify it is a 6502 language ROM.
; 
;     Sets the current program and memory top to the
;     transfer address, then enters the code with A=1.
;     If the header is missing or invalid, enters with A=1
;     anyway (raw code entry). Generates an error if the
;     ROM type indicates it is not a language or not 6502
;     code.
; Restore current program and memory top
    pla                                                               ; fa65: 68          h
    sta current_program                                               ; fa66: 85 ee       ..
    sta memory_top                                                    ; fa68: 85 f2       ..
; Restore A and return
    pla                                                               ; fa6a: 68          h
    sta current_program_hi                                            ; fa6b: 85 ef       ..
    sta memory_top_hi                                                 ; fa6d: 85 f3       ..
    pla                                                               ; fa6f: 68          h
    rts                                                               ; fa70: 60          `

; If zero, wait for OSCLI ack
; &fa71 referenced 1 time by &face
.check_oscli_ack
    beq oscli_wait_ack                                                ; fa71: f0 c2       ..
; ***************************************************************************************
; Handle OSBYTE calls. Functions &82-&84 are handled
;     locally (memory high word, bottom/top of memory).
;     Low functions (A < &80) send command &04 with X and A.
;     High functions send command &06 with X, Y, and A.
; 
;     Special handling for OSBYTE &8E (select language) which
;     checks for code to enter, and &9D (fast BPUT) which
;     returns immediately without waiting for a response.
; 
;     On entry:
;       A = function, X = parameter 1, Y = parameter 2
;     On exit:
;       A preserved
;       X, Y, Carry = returned values (for A >= &80)
; ***************************************************************************************
; Function >= &80: jump to high handler
.osbyte_impl
    cmp #&80                                                          ; fa73: c9 80       ..
    bcs osbyte_high                                                   ; fa75: b0 25       .%
; Send command &04 to host: OSBYTE low
    pha                                                               ; fa77: 48          H
    lda #4                                                            ; fa78: a9 04       ..
; Wait for Tube R2 free, send command
; &fa7a referenced 1 time by &fa7d
.loop_cfa7a
    bit lfefa                                                         ; fa7a: 2c fa fe    ,..
    bvc loop_cfa7a                                                    ; fa7d: 50 fb       P.
    sta lfefb                                                         ; fa7f: 8d fb fe    ...
; Send X parameter
; &fa82 referenced 1 time by &fa85
.loop_cfa82
    bit lfefa                                                         ; fa82: 2c fa fe    ,..
    bvc loop_cfa82                                                    ; fa85: 50 fb       P.
    stx lfefb                                                         ; fa87: 8e fb fe    ...
    pla                                                               ; fa8a: 68          h
; Send function code from A
; &fa8b referenced 1 time by &fa8e
.loop_cfa8b
    bit lfefa                                                         ; fa8b: 2c fa fe    ,..
    bvc loop_cfa8b                                                    ; fa8e: 50 fb       P.
    sta lfefb                                                         ; fa90: 8d fb fe    ...
; Wait for return value in X
; &fa93 referenced 1 time by &fa96
.loop_cfa93
    bit lfefa                                                         ; fa93: 2c fa fe    ,..
    bpl loop_cfa93                                                    ; fa96: 10 fb       ..
    ldx lfefb                                                         ; fa98: ae fb fe    ...
    rts                                                               ; fa9b: 60          `

; OSBYTE &82: read memory high word
; &fa9c referenced 1 time by &fa75
.osbyte_high
    cmp #&82                                                          ; fa9c: c9 82       ..
; OSBYTE &83: read bottom of memory
    beq cfafa                                                         ; fa9e: f0 5a       .Z
; OSBYTE &84: read top of memory
    cmp #&83                                                          ; faa0: c9 83       ..
    beq cfaf5                                                         ; faa2: f0 51       .Q
; Send command &06 to host: OSBYTE high
    cmp #&84                                                          ; faa4: c9 84       ..
    beq osbyte_read_himem                                             ; faa6: f0 48       .H
    pha                                                               ; faa8: 48          H
    lda #6                                                            ; faa9: a9 06       ..
; Wait for R2 free, send command
; &faab referenced 1 time by &faae
.loop_cfaab
    bit lfefa                                                         ; faab: 2c fa fe    ,..
    bvc loop_cfaab                                                    ; faae: 50 fb       P.
    sta lfefb                                                         ; fab0: 8d fb fe    ...
; Send X parameter
; &fab3 referenced 1 time by &fab6
.loop_cfab3
    bit lfefa                                                         ; fab3: 2c fa fe    ,..
    bvc loop_cfab3                                                    ; fab6: 50 fb       P.
    stx lfefb                                                         ; fab8: 8e fb fe    ...
; Send Y parameter
; &fabb referenced 1 time by &fabe
.loop_cfabb
    bit lfefa                                                         ; fabb: 2c fa fe    ,..
    bvc loop_cfabb                                                    ; fabe: 50 fb       P.
    sty lfefb                                                         ; fac0: 8c fb fe    ...
    pla                                                               ; fac3: 68          h
; Send function code from A
; &fac4 referenced 1 time by &fac7
.loop_cfac4
    bit lfefa                                                         ; fac4: 2c fa fe    ,..
    bvc loop_cfac4                                                    ; fac7: 50 fb       P.
    sta lfefb                                                         ; fac9: 8d fb fe    ...
; OSBYTE &8E: select language, check for code
    cmp #&8e                                                          ; facc: c9 8e       ..
    beq check_oscli_ack                                               ; face: f0 a1       ..
; OSBYTE &9D: fast BPUT, no response expected
    cmp #&9d                                                          ; fad0: c9 9d       ..
    beq return_2                                                      ; fad2: f0 1b       ..
    pha                                                               ; fad4: 48          H
; Wait for carry byte from host
; &fad5 referenced 1 time by &fad8
.loop_cfad5
    bit lfefa                                                         ; fad5: 2c fa fe    ,..
    bpl loop_cfad5                                                    ; fad8: 10 fb       ..
    lda lfefb                                                         ; fada: ad fb fe    ...
    asl a                                                             ; fadd: 0a          .
    pla                                                               ; fade: 68          h
; Wait for Y return value
; &fadf referenced 1 time by &fae2
.loop_cfadf
    bit lfefa                                                         ; fadf: 2c fa fe    ,..
    bpl loop_cfadf                                                    ; fae2: 10 fb       ..
    ldy lfefb                                                         ; fae4: ac fb fe    ...
; Wait for X return value
; &fae7 referenced 1 time by &faea
.loop_cfae7
    bit lfefa                                                         ; fae7: 2c fa fe    ,..
    bpl loop_cfae7                                                    ; faea: 10 fb       ..
    ldx lfefb                                                         ; faec: ae fb fe    ...
; &faef referenced 1 time by &fad2
.return_2
    rts                                                               ; faef: 60          `

; Return memory top from &F2/F3
; &faf0 referenced 1 time by &faa6
.osbyte_read_himem
    ldx memory_top                                                    ; faf0: a6 f2       ..
    ldy memory_top_hi                                                 ; faf2: a4 f3       ..
; Bottom of memory is always &0800
.osbyte_read_lomem
    rts                                                               ; faf4: 60          `

; &faf5 referenced 1 time by &faa2
.cfaf5
    ldx #0                                                            ; faf5: a2 00       ..
.sub_cfaf7
osbyte_read_high_word = sub_cfaf7+1
    ldy #8                                                            ; faf7: a0 08       ..
; Memory high word is &0000 (16-bit address space)
    rts                                                               ; faf9: 60          `

; &fafa referenced 1 time by &fa9e
.cfafa
    ldx #0                                                            ; fafa: a2 00       ..
    ldy #0                                                            ; fafc: a0 00       ..
    rts                                                               ; fafe: 60          `

; ***************************************************************************************
; Handle OSWORD calls. OSWORD 0 (read line) is handled
;     specially via rdline. All other functions send the
;     control block to the host and receive the response,
;     with block sizes determined by lookup tables.
; 
;     On entry:
;       A = function, XY => control block
; ***************************************************************************************
; Store control block address, check for OSWORD 0
.osword_impl
    stx string_ptr                                                    ; faff: 86 f8       ..
    sty string_ptr_hi                                                 ; fb01: 84 f9       ..
; OSWORD 0: jump to read line handler
    tay                                                               ; fb03: a8          .
    beq rdline                                                        ; fb04: f0 71       .q             ; Read a line of text from the host.
; 
;     Sends command &0A with the control block parameters,
;     then receives the input string character by character.
; 
;     Tube protocol: &0A block -- &FF or &7F string &0D
; 
;     On exit:
;       Y = length of string (excluding CR)
;       C = 0 if OK, 1 if Escape
; Send command &08 to host: OSWORD
    pha                                                               ; fb06: 48          H
    ldy #8                                                            ; fb07: a0 08       ..
; &fb09 referenced 1 time by &fb0c
.loop_cfb09
    bit lfefa                                                         ; fb09: 2c fa fe    ,..
    bvc loop_cfb09                                                    ; fb0c: 50 fb       P.
    sty lfefb                                                         ; fb0e: 8c fb fe    ...
; Send function number
; &fb11 referenced 1 time by &fb14
.loop_cfb11
    bit lfefa                                                         ; fb11: 2c fa fe    ,..
    bvc loop_cfb11                                                    ; fb14: 50 fb       P.
; Functions >= &80: length in control block
    sta lfefb                                                         ; fb16: 8d fb fe    ...
    tax                                                               ; fb19: aa          .
    bpl cfb24                                                         ; fb1a: 10 08       ..
    ldy #0                                                            ; fb1c: a0 00       ..
    lda (string_ptr),y                                                ; fb1e: b1 f8       ..
; Functions < &80: length from lookup table
    tay                                                               ; fb20: a8          .
    jmp cfb2d                                                         ; fb21: 4c 2d fb    L-.

; &fb24 referenced 1 time by &fb1a
.cfb24
    ldy osword_send_lengths,x                                         ; fb24: bc bc fc    ...
; Functions &15-&7F: send 16 bytes
    cpx #&15                                                          ; fb27: e0 15       ..
; Send block length byte
    bcc cfb2d                                                         ; fb29: 90 02       ..
    ldy #&10                                                          ; fb2b: a0 10       ..
; Send control block bytes in reverse order
; &fb2d referenced 3 times by &fb21, &fb29, &fb30
.cfb2d
    bit lfefa                                                         ; fb2d: 2c fa fe    ,..
    bvc cfb2d                                                         ; fb30: 50 fb       P.
    sty lfefb                                                         ; fb32: 8c fb fe    ...
    dey                                                               ; fb35: 88          .
    bmi cfb45                                                         ; fb36: 30 0d       0.
; &fb38 referenced 2 times by &fb3b, &fb43
.cfb38
    bit lfefa                                                         ; fb38: 2c fa fe    ,..
    bvc cfb38                                                         ; fb3b: 50 fb       P.
    lda (string_ptr),y                                                ; fb3d: b1 f8       ..
    sta lfefb                                                         ; fb3f: 8d fb fe    ...
    dey                                                               ; fb42: 88          .
    bpl cfb38                                                         ; fb43: 10 f3       ..
; Functions >= &80: receive length from control block
; &fb45 referenced 1 time by &fb36
.cfb45
    txa                                                               ; fb45: 8a          .
    bpl cfb50                                                         ; fb46: 10 08       ..
    ldy #1                                                            ; fb48: a0 01       ..
    lda (string_ptr),y                                                ; fb4a: b1 f8       ..
    tay                                                               ; fb4c: a8          .
    jmp cfb59                                                         ; fb4d: 4c 59 fb    LY.

; Functions < &80: receive length from lookup table
; &fb50 referenced 1 time by &fb46
.cfb50
    ldy osword_recv_lengths,x                                         ; fb50: bc d0 fc    ...
    cpx #&15                                                          ; fb53: e0 15       ..
; Functions &15-&7F: receive 16 bytes
    bcc cfb59                                                         ; fb55: 90 02       ..
    ldy #&10                                                          ; fb57: a0 10       ..
; Send receive block length
; &fb59 referenced 3 times by &fb4d, &fb55, &fb5c
.cfb59
    bit lfefa                                                         ; fb59: 2c fa fe    ,..
    bvc cfb59                                                         ; fb5c: 50 fb       P.
; Receive response bytes into control block
    sty lfefb                                                         ; fb5e: 8c fb fe    ...
    dey                                                               ; fb61: 88          .
    bmi cfb71                                                         ; fb62: 30 0d       0.
; &fb64 referenced 2 times by &fb67, &fb6f
.cfb64
    bit lfefa                                                         ; fb64: 2c fa fe    ,..
    bpl cfb64                                                         ; fb67: 10 fb       ..
    lda lfefb                                                         ; fb69: ad fb fe    ...
    sta (string_ptr),y                                                ; fb6c: 91 f8       ..
    dey                                                               ; fb6e: 88          .
    bpl cfb64                                                         ; fb6f: 10 f3       ..
; Restore registers and return
; &fb71 referenced 1 time by &fb62
.cfb71
    ldy string_ptr_hi                                                 ; fb71: a4 f9       ..
    ldx string_ptr                                                    ; fb73: a6 f8       ..
    pla                                                               ; fb75: 68          h
    rts                                                               ; fb76: 60          `

; ***************************************************************************************
; Read a line of text from the host.
; 
;     Sends command &0A with the control block parameters,
;     then receives the input string character by character.
; 
;     Tube protocol: &0A block -- &FF or &7F string &0D
; 
;     On exit:
;       Y = length of string (excluding CR)
;       C = 0 if OK, 1 if Escape
; ***************************************************************************************
; Send command &0A to host: RDLINE
; &fb77 referenced 1 time by &fb04
.rdline
    lda #&0a                                                          ; fb77: a9 0a       ..
    jsr send_command                                                  ; fb79: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Send control block bytes 4..2
    ldy #4                                                            ; fb7c: a0 04       ..
; &fb7e referenced 2 times by &fb81, &fb8b
.cfb7e
    bit lfefa                                                         ; fb7e: 2c fa fe    ,..
    bvc cfb7e                                                         ; fb81: 50 fb       P.
    lda (string_ptr),y                                                ; fb83: b1 f8       ..
    sta lfefb                                                         ; fb85: 8d fb fe    ...
    dey                                                               ; fb88: 88          .
    cpy #1                                                            ; fb89: c0 01       ..
    bne cfb7e                                                         ; fb8b: d0 f1       ..
; Send &07 as high byte of buffer address
    lda #7                                                            ; fb8d: a9 07       ..
    jsr send_command                                                  ; fb8f: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Save buffer high byte from control block
    lda (string_ptr),y                                                ; fb92: b1 f8       ..
    pha                                                               ; fb94: 48          H
    dey                                                               ; fb95: 88          .
; Send &00 as low byte of buffer address
; &fb96 referenced 1 time by &fb99
.loop_cfb96
    bit lfefa                                                         ; fb96: 2c fa fe    ,..
    bvc loop_cfb96                                                    ; fb99: 50 fb       P.
; Save buffer low byte from control block
    sty lfefb                                                         ; fb9b: 8c fb fe    ...
; Wait for response; &80+ means Escape
    lda (string_ptr),y                                                ; fb9e: b1 f8       ..
    pha                                                               ; fba0: 48          H
    ldx #&ff                                                          ; fba1: a2 ff       ..
    jsr wait_for_tube_r2_byte                                         ; fba3: 20 75 f9     u.
    cmp #&80                                                          ; fba6: c9 80       ..
; Set string_ptr to buffer address from stack
    bcs cfbc7                                                         ; fba8: b0 1d       ..
    pla                                                               ; fbaa: 68          h
    sta string_ptr                                                    ; fbab: 85 f8       ..
    pla                                                               ; fbad: 68          h
    sta string_ptr_hi                                                 ; fbae: 85 f9       ..
; Receive characters into buffer until CR
    ldy #0                                                            ; fbb0: a0 00       ..
; &fbb2 referenced 2 times by &fbb5, &fbbf
.cfbb2
    bit lfefa                                                         ; fbb2: 2c fa fe    ,..
    bpl cfbb2                                                         ; fbb5: 10 fb       ..
    lda lfefb                                                         ; fbb7: ad fb fe    ...
    sta (string_ptr),y                                                ; fbba: 91 f8       ..
    iny                                                               ; fbbc: c8          .
    cmp #&0d                                                          ; fbbd: c9 0d       ..
; Return A=0, Y=length, C=0 (OK)
    bne cfbb2                                                         ; fbbf: d0 f1       ..
    lda #0                                                            ; fbc1: a9 00       ..
    dey                                                               ; fbc3: 88          .
    clc                                                               ; fbc4: 18          .
    inx                                                               ; fbc5: e8          .
; Escape: return A=0, C=1
    rts                                                               ; fbc6: 60          `

; &fbc7 referenced 1 time by &fba8
.cfbc7
    pla                                                               ; fbc7: 68          h
    pla                                                               ; fbc8: 68          h
    lda #0                                                            ; fbc9: a9 00       ..
    rts                                                               ; fbcb: 60          `

; ***************************************************************************************
; Read or write information about an open file.
; 
;     Sends command &0C with handle, 4-byte data word,
;     and function code. Receives result and updated data.
; 
;     On entry:
;       A = function, X => data word in zero page, Y = handle
;     On exit:
;       A = result, data word at X updated
; ***************************************************************************************
; Send command &0C: OSARGS
.osargs_impl
    pha                                                               ; fbcc: 48          H
    lda #&0c                                                          ; fbcd: a9 0c       ..
    jsr send_command                                                  ; fbcf: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Send handle
; &fbd2 referenced 1 time by &fbd5
.loop_cfbd2
    bit lfefa                                                         ; fbd2: 2c fa fe    ,..
    bvc loop_cfbd2                                                    ; fbd5: 50 fb       P.
; Send 4-byte data word (high to low)
    sty lfefb                                                         ; fbd7: 8c fb fe    ...
    lda l0003,x                                                       ; fbda: b5 03       ..
    jsr send_command                                                  ; fbdc: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    lda l0002,x                                                       ; fbdf: b5 02       ..
    jsr send_command                                                  ; fbe1: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    lda l0001,x                                                       ; fbe4: b5 01       ..
    jsr send_command                                                  ; fbe6: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    lda l0000,x                                                       ; fbe9: b5 00       ..
    jsr send_command                                                  ; fbeb: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Send function code
    pla                                                               ; fbee: 68          h
    jsr send_command                                                  ; fbef: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Receive result byte
    jsr wait_for_tube_r2_byte                                         ; fbf2: 20 75 f9     u.
; Receive updated 4-byte data word
    pha                                                               ; fbf5: 48          H
    jsr wait_for_tube_r2_byte                                         ; fbf6: 20 75 f9     u.
    sta l0003,x                                                       ; fbf9: 95 03       ..
    jsr wait_for_tube_r2_byte                                         ; fbfb: 20 75 f9     u.
    sta l0002,x                                                       ; fbfe: 95 02       ..
    jsr wait_for_tube_r2_byte                                         ; fc00: 20 75 f9     u.
    sta l0001,x                                                       ; fc03: 95 01       ..
    jsr wait_for_tube_r2_byte                                         ; fc05: 20 75 f9     u.
    sta l0000,x                                                       ; fc08: 95 00       ..
    pla                                                               ; fc0a: 68          h
    rts                                                               ; fc0b: 60          `

; ***************************************************************************************
; Open or close a file.
; 
;     For close (A=0): sends command &12, function, handle.
;     For open (A<>0): sends command &12, function, filename.
; 
;     On entry:
;       A = function, XY => filename (open) or Y = handle (close)
;     On exit:
;       A = handle (open) or preserved (close)
; ***************************************************************************************
; Send command &12: OSFIND
.osfind_impl
    pha                                                               ; fc0c: 48          H
    lda #&12                                                          ; fc0d: a9 12       ..
    jsr send_command                                                  ; fc0f: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Send function code
    pla                                                               ; fc12: 68          h
    jsr send_command                                                  ; fc13: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; A=0 means close: send handle and wait for ack
    cmp #0                                                            ; fc16: c9 00       ..
    bne cfc24                                                         ; fc18: d0 0a       ..
    pha                                                               ; fc1a: 48          H
    tya                                                               ; fc1b: 98          .
    jsr send_command                                                  ; fc1c: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Wait for acknowledge, restore A and return
    jsr wait_for_tube_r2_byte                                         ; fc1f: 20 75 f9     u.
    pla                                                               ; fc22: 68          h
    rts                                                               ; fc23: 60          `

; Open: send filename string
; &fc24 referenced 1 time by &fc18
.cfc24
    jsr send_string                                                   ; fc24: 20 b2 f9     ..            ; Send a CR-terminated string to the host via Tube R2.
; 
;     On entry:
;       X = string address low byte
;       Y = string address high byte
;     On exit:
;       Y restored from string_ptr_hi
; Wait for and return handle
    jmp wait_for_tube_r2_byte                                         ; fc27: 4c 75 f9    Lu.

; ***************************************************************************************
; Read a byte from an open file.
; 
;     Sends command &0E with handle, waits for carry and byte.
; 
;     On entry:
;       Y = handle
;     On exit:
;       A = byte read, C = set if EOF
; ***************************************************************************************
; Send command &0E: OSBGET
.osbget_impl
    lda #&0e                                                          ; fc2a: a9 0e       ..
    jsr send_command                                                  ; fc2c: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Send handle
    tya                                                               ; fc2f: 98          .
; Wait for carry and data byte
    jsr send_command                                                  ; fc30: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    jmp wait_carry_and_byte                                           ; fc33: 4c 71 f9    Lq.

; ***************************************************************************************
; Write a byte to an open file.
; 
;     Sends command &10 with handle and byte.
; 
;     On entry:
;       A = byte, Y = handle
;     On exit:
;       A preserved
; ***************************************************************************************
; Save A, send command &10: OSBPUT
.osbput_impl
    pha                                                               ; fc36: 48          H
    lda #&10                                                          ; fc37: a9 10       ..
    jsr send_command                                                  ; fc39: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Send handle
    tya                                                               ; fc3c: 98          .
    jsr send_command                                                  ; fc3d: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Send byte to write
; Wait for acknowledge, restore A and return
    pla                                                               ; fc40: 68          h
    jsr send_command                                                  ; fc41: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    pha                                                               ; fc44: 48          H
    jsr wait_for_tube_r2_byte                                         ; fc45: 20 75 f9     u.
    pla                                                               ; fc48: 68          h
    rts                                                               ; fc49: 60          `

; ***************************************************************************************
; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; ***************************************************************************************
; Wait for Tube R2 free
; &fc4a referenced 25 times by &f96e, &fa2f, &fb79, &fb8f, &fbcf, &fbdc, &fbe1, &fbe6, &fbeb, &fbef, &fc0f, &fc13, &fc1c, &fc2c, &fc30, &fc39, &fc3d, &fc41, &fc4d, &fc5a, &fc61, &fc75, &fc95, &fc9c, &fca3
.send_command
.send_byte_to_tube_r2
    bit lfefa                                                         ; fc4a: 2c fa fe    ,..
    bvc send_command                                                  ; fc4d: 50 fb       P.             ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Send byte to Tube R2 data register
    sta lfefb                                                         ; fc4f: 8d fb fe    ...
    rts                                                               ; fc52: 60          `

; ***************************************************************************************
; Operate on whole files (load, save, read/write attributes).
; 
;     Sends command &14 with 16-byte control block, filename,
;     and function code. Receives result and updated control block.
; 
;     On entry:
;       A = function, XY => control block
; ***************************************************************************************
; Store control block pointer in &FA/FB
.osfile_impl
    sty control_block_ptr_hi                                          ; fc53: 84 fb       ..
    stx control_block_ptr                                             ; fc55: 86 fa       ..
; Send command &14: OSFILE
    pha                                                               ; fc57: 48          H
    lda #&14                                                          ; fc58: a9 14       ..
    jsr send_command                                                  ; fc5a: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    ldy #&11                                                          ; fc5d: a0 11       ..
; Send control block bytes &11..&02
; &fc5f referenced 1 time by &fc67
.loop_cfc5f
    lda (control_block_ptr),y                                         ; fc5f: b1 fa       ..
    jsr send_command                                                  ; fc61: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    dey                                                               ; fc64: 88          .
    cpy #1                                                            ; fc65: c0 01       ..
    bne loop_cfc5f                                                    ; fc67: d0 f6       ..
; Get filename pointer from control block
    dey                                                               ; fc69: 88          .
    lda (control_block_ptr),y                                         ; fc6a: b1 fa       ..
    tax                                                               ; fc6c: aa          .
    iny                                                               ; fc6d: c8          .
    lda (control_block_ptr),y                                         ; fc6e: b1 fa       ..
    tay                                                               ; fc70: a8          .
; Send filename string
    jsr send_string                                                   ; fc71: 20 b2 f9     ..            ; Send a CR-terminated string to the host via Tube R2.
; 
;     On entry:
;       X = string address low byte
;       Y = string address high byte
;     On exit:
;       Y restored from string_ptr_hi
; Send function code
    pla                                                               ; fc74: 68          h
    jsr send_command                                                  ; fc75: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
; Wait for result byte
    jsr wait_for_tube_r2_byte                                         ; fc78: 20 75 f9     u.
    pha                                                               ; fc7b: 48          H
    ldy #&11                                                          ; fc7c: a0 11       ..
; Receive updated control block bytes &11..&02
; &fc7e referenced 1 time by &fc86
.loop_cfc7e
    jsr wait_for_tube_r2_byte                                         ; fc7e: 20 75 f9     u.
    sta (control_block_ptr),y                                         ; fc81: 91 fa       ..
    dey                                                               ; fc83: 88          .
    cpy #1                                                            ; fc84: c0 01       ..
    bne loop_cfc7e                                                    ; fc86: d0 f6       ..
; Restore XY registers
    ldy control_block_ptr_hi                                          ; fc88: a4 fb       ..
    ldx control_block_ptr                                             ; fc8a: a6 fa       ..
; Return result in A
    pla                                                               ; fc8c: 68          h
    rts                                                               ; fc8d: 60          `

; ***************************************************************************************
; Multiple byte read and write.
; 
;     Sends command &16 with 13-byte control block and function.
;     Receives updated control block, carry, and result.
; 
;     On entry:
;       A = function, XY => control block
; ***************************************************************************************
; Store control block pointer in &FA/FB
.osgbpb_impl
    sty control_block_ptr_hi                                          ; fc8e: 84 fb       ..
    stx control_block_ptr                                             ; fc90: 86 fa       ..
    pha                                                               ; fc92: 48          H
    lda #&16                                                          ; fc93: a9 16       ..
; Send command &16: OSGBPB
    jsr send_command                                                  ; fc95: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    ldy #&0c                                                          ; fc98: a0 0c       ..
; Send control block bytes &0C..&00
; &fc9a referenced 1 time by &fca0
.loop_cfc9a
    lda (control_block_ptr),y                                         ; fc9a: b1 fa       ..
    jsr send_command                                                  ; fc9c: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    dey                                                               ; fc9f: 88          .
    bpl loop_cfc9a                                                    ; fca0: 10 f8       ..
; Send function code
    pla                                                               ; fca2: 68          h
    jsr send_command                                                  ; fca3: 20 4a fc     J.            ; Wait for Tube R2 to be free, then send byte.
; 
;     On entry:
;       A = byte to send
;     On exit:
;       A preserved
    ldy #&0c                                                          ; fca6: a0 0c       ..
; Receive updated control block
; &fca8 referenced 1 time by &fcae
.loop_cfca8
    jsr wait_for_tube_r2_byte                                         ; fca8: 20 75 f9     u.
    sta (control_block_ptr),y                                         ; fcab: 91 fa       ..
    dey                                                               ; fcad: 88          .
    bpl loop_cfca8                                                    ; fcae: 10 f8       ..
    ldy control_block_ptr_hi                                          ; fcb0: a4 fb       ..
; Restore XY registers
    ldx control_block_ptr                                             ; fcb2: a6 fa       ..
; Get carry and result
    jmp wait_carry_and_byte                                           ; fcb4: 4c 71 f9    Lq.

; ***************************************************************************************
; Generate a 'Bad' error for unsupported MOS calls.
; ***************************************************************************************
; BRK with error 255: 'Bad'
; &fcb7 referenced 1 time by &ffb9
.unsupported
    brk                                                               ; fcb7: 00          .

    equb &ff                                                          ; fcb8: ff          .
    equs "Bad"                                                        ; fcb9: 42 61 64    Bad
; OSWORD 1-20 send block lengths
; &fcbc referenced 1 time by &fb24
.osword_send_lengths
    equb 0                                                            ; fcbc: 00          .
    equb 0                                                            ; fcbd: 00          .
    equb 5                                                            ; fcbe: 05          .
    equb 0                                                            ; fcbf: 00          .
    equb 5                                                            ; fcc0: 05          .
    equb 2                                                            ; fcc1: 02          .
    equb 5                                                            ; fcc2: 05          .
    equb 8                                                            ; fcc3: 08          .
    equb &0e                                                          ; fcc4: 0e          .
    equb 4                                                            ; fcc5: 04          .
    equb 1                                                            ; fcc6: 01          .
    equb 1                                                            ; fcc7: 01          .
    equb 5                                                            ; fcc8: 05          .
    equb 0                                                            ; fcc9: 00          .
    equb 1                                                            ; fcca: 01          .
    equb &20                                                          ; fccb: 20
    equb &10                                                          ; fccc: 10          .
    equb &0d                                                          ; fccd: 0d          .
    equb 0                                                            ; fcce: 00          .
    equb 4                                                            ; fccf: 04          .
; OSWORD 1-20 receive block lengths
; &fcd0 referenced 1 time by &fb50
.osword_recv_lengths
    equb &80                                                          ; fcd0: 80          .
    equb 5                                                            ; fcd1: 05          .
    equb 0                                                            ; fcd2: 00          .
    equb 5                                                            ; fcd3: 05          .
    equb 0                                                            ; fcd4: 00          .
    equb 5                                                            ; fcd5: 05          .
    equb 0                                                            ; fcd6: 00          .
    equb 0                                                            ; fcd7: 00          .
    equb 0                                                            ; fcd8: 00          .
    equb 5                                                            ; fcd9: 05          .
    equb 9                                                            ; fcda: 09          .
    equb 5                                                            ; fcdb: 05          .
    equb 0                                                            ; fcdc: 00          .
    equb 8                                                            ; fcdd: 08          .
    equb &18                                                          ; fcde: 18          .
    equb 0                                                            ; fcdf: 00          .
    equb 1                                                            ; fce0: 01          .
    equb &0d                                                          ; fce1: 0d          .
    equb &80                                                          ; fce2: 80          .
    equb 4                                                            ; fce3: 04          .
    equb &80                                                          ; fce4: 80          .

; ***************************************************************************************
; Hardware interrupt entry point. Saves A, checks the
;     break flag in the stacked processor status to distinguish
;     BRK from IRQ, and dispatches accordingly.
; ***************************************************************************************
; Save A in irq_a_store
.interrupt_handler
    sta irq_a_store                                                   ; fce5: 85 fc       ..
; Pull stacked flags to check BRK bit
    pla                                                               ; fce7: 68          h
    pha                                                               ; fce8: 48          H
    and #&10                                                          ; fce9: 29 10       ).
; B flag set: BRK instruction
    bne cfcfd                                                         ; fceb: d0 10       ..
; Not BRK: dispatch via IRQ1V
    jmp (irq1v)                                                       ; fced: 6c 04 02    l..

; ***************************************************************************************
; First-level IRQ handler. Checks Tube R4 for data
;     transfer requests, then Tube R1 for escape/event
;     notifications. Falls through to IRQ2V if neither.
; ***************************************************************************************
; Data in Tube R4: process transfers/errors
.irq1_handler
    bit lfefe                                                         ; fcf0: 2c fe fe    ,..
; Data in Tube R1: process escape/events
    bmi tube_r4_interrupt                                             ; fcf3: 30 4a       0J             ; Process data received via Tube R4. If bit 7 is set,
;     it is an error from the host: reads the error number
;     and message via R2 into the error buffer, then
;     executes the error via a JMP to the buffer (which
;     starts with a BRK opcode).
; 
;     If bit 7 is clear, it is a data transfer request:
;     falls through to data_transfer_setup.
    bit lfef8                                                         ; fcf5: 2c f8 fe    ,..
; Neither: pass on via IRQ2V
    bmi tube_r1_interrupt                                             ; fcf8: 30 1e       0.             ; Process data received via Tube R1. If bit 7 is set,
;     it is an Escape state change (stored in escape_flag).
;     Otherwise, it is an event notification: reads the
;     event parameters (Y, X, event number) from R1 and
;     dispatches via EVNTV.
    equb &6c                                                          ; fcfa: 6c          l

; ***************************************************************************************
; Extract the return address from the stack, subtract 1
;     to point to the byte after the BRK opcode, store in
;     last_error, then dispatch via BRKV.
; ***************************************************************************************
; Save X
.brk_handler
    asl l0002                                                         ; fcfb: 06 02       ..
; &fcfd referenced 1 time by &fceb
.cfcfd
    txa                                                               ; fcfd: 8a          .
; Get return address from stack
    pha                                                               ; fcfe: 48          H
    tsx                                                               ; fcff: ba          .
; Subtract 1 to point at the BRK error block
    lda irq_return_addr_lo,x                                          ; fd00: bd 03 01    ...
    cld                                                               ; fd03: d8          .
    sec                                                               ; fd04: 38          8
    sbc #1                                                            ; fd05: e9 01       ..
    sta last_error                                                    ; fd07: 85 fd       ..
    lda irq_return_addr_hi,x                                          ; fd09: bd 04 01    ...
    sbc #0                                                            ; fd0c: e9 00       ..
; Restore registers
    sta last_error_hi                                                 ; fd0e: 85 fe       ..
    pla                                                               ; fd10: 68          h
    tax                                                               ; fd11: aa          .
; Re-enable interrupts, dispatch via BRKV
    lda irq_a_store                                                   ; fd12: a5 fc       ..
    cli                                                               ; fd14: 58          X
    jmp (brkv)                                                        ; fd15: 6c 02 02    l..

; ***************************************************************************************
; Process data received via Tube R1. If bit 7 is set,
;     it is an Escape state change (stored in escape_flag).
;     Otherwise, it is an event notification: reads the
;     event parameters (Y, X, event number) from R1 and
;     dispatches via EVNTV.
; ***************************************************************************************
; Read Tube R1 data
; &fd18 referenced 1 time by &fcf8
.tube_r1_interrupt
    lda lfef9                                                         ; fd18: ad f9 fe    ...
; Bit 7 set: Escape state change
    bmi set_escape_flag                                               ; fd1b: 30 1c       0.
; Save registers for event dispatch
    tya                                                               ; fd1d: 98          .
    pha                                                               ; fd1e: 48          H
    txa                                                               ; fd1f: 8a          .
    pha                                                               ; fd20: 48          H
    jsr wait_for_tube_r1_byte                                         ; fd21: 20 80 fe     ..            ; Wait for data in Tube R1, allowing Tube R4 transfer
;     requests to be serviced via IRQ while waiting.
; 
;     Polls R1 status; if R4 has data instead, briefly
;     enables interrupts to let the R4 handler run, then
;     resumes polling R1.
; 
;     On exit:
;       A = byte from Tube R1
; Read event Y parameter from R1
    tay                                                               ; fd24: a8          .
; Read event X parameter from R1
    jsr wait_for_tube_r1_byte                                         ; fd25: 20 80 fe     ..            ; Wait for data in Tube R1, allowing Tube R4 transfer
;     requests to be serviced via IRQ while waiting.
; 
;     Polls R1 status; if R4 has data instead, briefly
;     enables interrupts to let the R4 handler run, then
;     resumes polling R1.
; 
;     On exit:
;       A = byte from Tube R1
; Read event number from R1
    tax                                                               ; fd28: aa          .
    jsr wait_for_tube_r1_byte                                         ; fd29: 20 80 fe     ..            ; Wait for data in Tube R1, allowing Tube R4 transfer
;     requests to be serviced via IRQ while waiting.
; 
;     Polls R1 status; if R4 has data instead, briefly
;     enables interrupts to let the R4 handler run, then
;     resumes polling R1.
; 
;     On exit:
;       A = byte from Tube R1
; Dispatch event, restore registers and RTI
    jsr sub_cfd36                                                     ; fd2c: 20 36 fd     6.
    pla                                                               ; fd2f: 68          h
    tax                                                               ; fd30: aa          .
    pla                                                               ; fd31: 68          h
    tay                                                               ; fd32: a8          .
    lda irq_a_store                                                   ; fd33: a5 fc       ..
    rti                                                               ; fd35: 40          @

; Dispatch via EVNTV
; &fd36 referenced 1 time by &fd2c
.sub_cfd36
    jmp (evntv)                                                       ; fd36: 6c 20 02    l .

; Shift bit 6 of Tube data into bit 7 of escape_flag
; &fd39 referenced 1 time by &fd1b
.set_escape_flag
    asl a                                                             ; fd39: 0a          .
    sta escape_flag                                                   ; fd3a: 85 ff       ..
; Restore A from irq_a_store and return
    lda irq_a_store                                                   ; fd3c: a5 fc       ..
    rti                                                               ; fd3e: 40          @

; ***************************************************************************************
; Process data received via Tube R4. If bit 7 is set,
;     it is an error from the host: reads the error number
;     and message via R2 into the error buffer, then
;     executes the error via a JMP to the buffer (which
;     starts with a BRK opcode).
; 
;     If bit 7 is clear, it is a data transfer request:
;     falls through to data_transfer_setup.
; ***************************************************************************************
; Read Tube R4 data
; &fd3f referenced 1 time by &fcf3
.tube_r4_interrupt
    lda lfeff                                                         ; fd3f: ad ff fe    ...
; Bit 7 clear: data transfer request
    bpl data_transfer_setup                                           ; fd42: 10 21       .!             ; Configure the NMI handler for a data transfer.
; 
;     The transfer type (0-7) from R4 selects the NMI
;     routine and the address pointer. Types 0-3 are
;     single/double byte transfers. Types 4-5 are release.
;     Types 6-7 are 256-byte block transfers.
; 
;     Reads the 4-byte transfer address from R4 (only the
;     low 2 bytes are used), configures the NMI vector and
;     transfer address, then reads the sync byte from R4.
; Re-enable interrupts during error reception
    cli                                                               ; fd44: 58          X
; Wait for error data via Tube R2
; &fd45 referenced 1 time by &fd48
.loop_cfd45
    bit lfefa                                                         ; fd45: 2c fa fe    ,..
    bpl loop_cfd45                                                    ; fd48: 10 fb       ..
    lda lfefb                                                         ; fd4a: ad fb fe    ...
; Store BRK opcode at start of error buffer
    lda #0                                                            ; fd4d: a9 00       ..
    sta error_buffer                                                  ; fd4f: 8d 36 02    .6.
    tay                                                               ; fd52: a8          .              ; Y=&00
; Read error number into buffer
    jsr wait_for_tube_r2_byte                                         ; fd53: 20 75 f9     u.
    sta error_buffer_errnum                                           ; fd56: 8d 37 02    .7.
; Read error string bytes until NUL terminator
; &fd59 referenced 1 time by &fd60
.loop_cfd59
    iny                                                               ; fd59: c8          .
    jsr wait_for_tube_r2_byte                                         ; fd5a: 20 75 f9     u.
    sta error_buffer_errnum,y                                         ; fd5d: 99 37 02    .7.
    bne loop_cfd59                                                    ; fd60: d0 f7       ..
; Execute the BRK in the error buffer
    jmp error_buffer                                                  ; fd62: 4c 36 02    L6.

; ***************************************************************************************
; Configure the NMI handler for a data transfer.
; 
;     The transfer type (0-7) from R4 selects the NMI
;     routine and the address pointer. Types 0-3 are
;     single/double byte transfers. Types 4-5 are release.
;     Types 6-7 are 256-byte block transfers.
; 
;     Reads the 4-byte transfer address from R4 (only the
;     low 2 bytes are used), configures the NMI vector and
;     transfer address, then reads the sync byte from R4.
; ***************************************************************************************
; Save transfer type, preserve Y
; &fd65 referenced 1 time by &fd42
.data_transfer_setup
    sta nmi_vector                                                    ; fd65: 8d fa ff    ...
    tya                                                               ; fd68: 98          .
; Look up NMI routine address from table
    pha                                                               ; fd69: 48          H
    ldy nmi_vector                                                    ; fd6a: ac fa ff    ...
    lda nmi_routine_addr_table,y                                      ; fd6d: b9 70 fe    .p.
    sta nmi_vector                                                    ; fd70: 8d fa ff    ...
; Look up transfer address pointer from table
    lda nmi_routine_addr_hi_table,y                                   ; fd73: b9 78 fe    .x.
    sta lfffb                                                         ; fd76: 8d fb ff    ...
    lda transfer_addr_ptr_table,y                                     ; fd79: b9 60 fe    .`.
    sta transfer_addr_ptr                                             ; fd7c: 85 f4       ..
    lda transfer_addr_ptr_hi_table,y                                  ; fd7e: b9 68 fe    .h.
    sta transfer_addr_ptr_hi                                          ; fd81: 85 f5       ..
; Wait for called ID byte from Tube R4
; &fd83 referenced 1 time by &fd86
.loop_cfd83
    bit lfefe                                                         ; fd83: 2c fe fe    ,..
    bpl loop_cfd83                                                    ; fd86: 10 fb       ..
    lda lfeff                                                         ; fd88: ad ff fe    ...
; Type 5 = TubeRelease: exit immediately
    cpy #5                                                            ; fd8b: c0 05       ..
    beq restore_regs_and_rti                                          ; fd8d: f0 58       .X
; Save transfer type, read 4-byte address
    tya                                                               ; fd8f: 98          .
    pha                                                               ; fd90: 48          H
    ldy #1                                                            ; fd91: a0 01       ..
; Read and discard address byte 4 (bits 31-24)
; &fd93 referenced 1 time by &fd96
.loop_cfd93
    bit lfefe                                                         ; fd93: 2c fe fe    ,..
    bpl loop_cfd93                                                    ; fd96: 10 fb       ..
    lda lfeff                                                         ; fd98: ad ff fe    ...
; Read and discard address byte 3 (bits 23-16)
; &fd9b referenced 1 time by &fd9e
.loop_cfd9b
    bit lfefe                                                         ; fd9b: 2c fe fe    ,..
    bpl loop_cfd9b                                                    ; fd9e: 10 fb       ..
    lda lfeff                                                         ; fda0: ad ff fe    ...
; Read address byte 2 (high), store via pointer
; &fda3 referenced 1 time by &fda6
.loop_cfda3
    bit lfefe                                                         ; fda3: 2c fe fe    ,..
    bpl loop_cfda3                                                    ; fda6: 10 fb       ..
    lda lfeff                                                         ; fda8: ad ff fe    ...
    sta (transfer_addr_ptr),y                                         ; fdab: 91 f4       ..
    dey                                                               ; fdad: 88          .
; Read address byte 1 (low), store via pointer
; &fdae referenced 1 time by &fdb1
.loop_cfdae
    bit lfefe                                                         ; fdae: 2c fe fe    ,..
    bpl loop_cfdae                                                    ; fdb1: 10 fb       ..
    lda lfeff                                                         ; fdb3: ad ff fe    ...
; Dummy reads of Tube R3 to synchronise
    sta (transfer_addr_ptr),y                                         ; fdb6: 91 f4       ..
    bit lfefd                                                         ; fdb8: 2c fd fe    ,..
    bit lfefd                                                         ; fdbb: 2c fd fe    ,..
; Wait for sync byte from Tube R4
; &fdbe referenced 1 time by &fdc1
.loop_cfdbe
    bit lfefe                                                         ; fdbe: 2c fe fe    ,..
    bpl loop_cfdbe                                                    ; fdc1: 10 fb       ..
    lda lfeff                                                         ; fdc3: ad ff fe    ...
; Type < 6: not 256-byte transfer, exit
    pla                                                               ; fdc6: 68          h
    cmp #6                                                            ; fdc7: c9 06       ..
; Type != 6: must be type 7 (read from Tube)
    bcc restore_regs_and_rti                                          ; fdc9: 90 1c       ..
; Send 256 bytes from transfer address to Tube R3
    bne transfer_256_bytes_from_tube                                  ; fdcb: d0 1f       ..
    ldy #0                                                            ; fdcd: a0 00       ..
; Wait for Tube R3 free
; &fdcf referenced 2 times by &fdd4, &fddd
.cfdcf
    lda lfefc                                                         ; fdcf: ad fc fe    ...
    and #&80                                                          ; fdd2: 29 80       ).
    bpl cfdcf                                                         ; fdd4: 10 f9       ..
; Self-modifying: address patched during setup
.sub_cfdd6
nmi6_transfer_addr = sub_cfdd6+1
    lda lffff,y                                                       ; fdd6: b9 ff ff    ...
    sta lfefd                                                         ; fdd9: 8d fd fe    ...
    iny                                                               ; fddc: c8          .
    bne cfdcf                                                         ; fddd: d0 f0       ..
; Send final sync byte to Tube R3
; &fddf referenced 1 time by &fde2
.loop_cfddf
    bit lfefc                                                         ; fddf: 2c fc fe    ,..
    bpl loop_cfddf                                                    ; fde2: 10 fb       ..
    sta lfefd                                                         ; fde4: 8d fd fe    ...
; &fde7 referenced 3 times by &fd8d, &fdc9, &fdfe
.restore_regs_and_rti
    pla                                                               ; fde7: 68          h
    tay                                                               ; fde8: a8          .
    lda irq_a_store                                                   ; fde9: a5 fc       ..
    rti                                                               ; fdeb: 40          @

; &fdec referenced 1 time by &fdcb
.transfer_256_bytes_from_tube
    ldy #0                                                            ; fdec: a0 00       ..
; Wait for Tube R3 data available
; &fdee referenced 2 times by &fdf3, &fdfc
.cfdee
    lda lfefc                                                         ; fdee: ad fc fe    ...
    and #&80                                                          ; fdf1: 29 80       ).
    bpl cfdee                                                         ; fdf3: 10 f9       ..
; Read byte from Tube R3
    lda lfefd                                                         ; fdf5: ad fd fe    ...
; Self-modifying: address patched during setup
.sub_cfdf8
nmi7_transfer_addr = sub_cfdf8+1
    sta lffff,y                                                       ; fdf8: 99 ff ff    ...
    iny                                                               ; fdfb: c8          .
    bne cfdee                                                         ; fdfc: d0 f0       ..
.sub_cfdfe
lfdff = sub_cfdfe+1
    beq restore_regs_and_rti                                          ; fdfe: f0 e7       ..             ; ALWAYS branch

; &fdff referenced 2 times by &f819, &f81c
; ***************************************************************************************
; Transfer type 0. Sends one byte from the transfer
;     address to Tube R3, then increments the address.
; ***************************************************************************************
.nmi_single_byte_to_tube
    pha                                                               ; fe00: 48          H
; Self-modifying: address patched during setup
.sub_cfe01
lfe02 = sub_cfe01+1
nmi0_transfer_addr = sub_cfe01+2
    lda lffff                                                         ; fe01: ad ff ff    ...
; &fe02 referenced 1 time by &fe07
; &fe03 referenced 1 time by &fe0c
    sta lfefd                                                         ; fe04: 8d fd fe    ...
; Send byte to Tube R3
    inc lfe02                                                         ; fe07: ee 02 fe    ...
; Increment transfer address (16-bit)
    bne cfe0f                                                         ; fe0a: d0 03       ..
    inc nmi0_transfer_addr                                            ; fe0c: ee 03 fe    ...
; &fe0f referenced 1 time by &fe0a
.cfe0f
    pla                                                               ; fe0f: 68          h
    rti                                                               ; fe10: 40          @

; ***************************************************************************************
; Transfer type 1. Reads one byte from Tube R3 and
;     stores it at the transfer address, then increments
;     the address.
; ***************************************************************************************
.nmi_single_byte_from_tube
    pha                                                               ; fe11: 48          H
    lda lfefd                                                         ; fe12: ad fd fe    ...
; Read byte from Tube R3
; Self-modifying: store address patched during setup
.nmi1_transfer_addr
lfe16 = nmi1_transfer_addr+1
lfe17 = nmi1_transfer_addr+2
    sta lffff                                                         ; fe15: 8d ff ff    ...
; &fe16 referenced 1 time by &fe18
; &fe17 referenced 1 time by &fe1d
; Increment transfer address (16-bit)
    inc lfe16                                                         ; fe18: ee 16 fe    ...
    bne cfe20                                                         ; fe1b: d0 03       ..
    inc lfe17                                                         ; fe1d: ee 17 fe    ...
; &fe20 referenced 1 time by &fe1b
.cfe20
    pla                                                               ; fe20: 68          h
    rti                                                               ; fe21: 40          @

; ***************************************************************************************
; Transfer type 2. Sends two consecutive bytes from
;     (data_transfer_addr) to Tube R3, incrementing the
;     pointer after each byte.
; ***************************************************************************************
.nmi_two_bytes_to_tube
    pha                                                               ; fe22: 48          H
    tya                                                               ; fe23: 98          .
    pha                                                               ; fe24: 48          H
    ldy #0                                                            ; fe25: a0 00       ..
; Send first byte from (data_transfer_addr)
    lda (data_transfer_addr),y                                        ; fe27: b1 f6       ..
    sta lfefd                                                         ; fe29: 8d fd fe    ...
; Increment transfer address
    inc data_transfer_addr                                            ; fe2c: e6 f6       ..
    bne cfe32                                                         ; fe2e: d0 02       ..
    inc data_transfer_addr_hi                                         ; fe30: e6 f7       ..
; Send second byte
; &fe32 referenced 1 time by &fe2e
.cfe32
    lda (data_transfer_addr),y                                        ; fe32: b1 f6       ..
    sta lfefd                                                         ; fe34: 8d fd fe    ...
    inc data_transfer_addr                                            ; fe37: e6 f6       ..
; Increment transfer address
    bne cfe3d                                                         ; fe39: d0 02       ..
    inc data_transfer_addr_hi                                         ; fe3b: e6 f7       ..
; &fe3d referenced 1 time by &fe39
.cfe3d
    pla                                                               ; fe3d: 68          h
    tay                                                               ; fe3e: a8          .
    pla                                                               ; fe3f: 68          h
    rti                                                               ; fe40: 40          @

; ***************************************************************************************
; Transfer type 3. Reads two bytes from Tube R3 and
;     stores them at (data_transfer_addr), incrementing
;     the pointer after each byte.
; ***************************************************************************************
.nmi_two_bytes_from_tube
    pha                                                               ; fe41: 48          H
    tya                                                               ; fe42: 98          .
    pha                                                               ; fe43: 48          H
    ldy #0                                                            ; fe44: a0 00       ..
; Read first byte from Tube R3
    lda lfefd                                                         ; fe46: ad fd fe    ...
    sta (data_transfer_addr),y                                        ; fe49: 91 f6       ..
    inc data_transfer_addr                                            ; fe4b: e6 f6       ..
; Increment transfer address
    bne cfe51                                                         ; fe4d: d0 02       ..
    inc data_transfer_addr_hi                                         ; fe4f: e6 f7       ..
; Read second byte from Tube R3
; &fe51 referenced 1 time by &fe4d
.cfe51
    lda lfefd                                                         ; fe51: ad fd fe    ...
    sta (data_transfer_addr),y                                        ; fe54: 91 f6       ..
    inc data_transfer_addr                                            ; fe56: e6 f6       ..
; Increment transfer address
    bne cfe5c                                                         ; fe58: d0 02       ..
    inc data_transfer_addr_hi                                         ; fe5a: e6 f7       ..
; &fe5c referenced 1 time by &fe58
.cfe5c
    pla                                                               ; fe5c: 68          h
    tay                                                               ; fe5d: a8          .
    pla                                                               ; fe5e: 68          h
    rti                                                               ; fe5f: 40          @

; Low bytes of transfer address pointers
; &fe60 referenced 1 time by &fd79
.transfer_addr_ptr_table
    equb 2                                                            ; fe60: 02          .
    equb &16                                                          ; fe61: 16          .
    equb &f6                                                          ; fe62: f6          .
    equb &f6                                                          ; fe63: f6          .
    equb &f6                                                          ; fe64: f6          .
    equb &f6                                                          ; fe65: f6          .
    equb &d7                                                          ; fe66: d7          .
    equb &f9                                                          ; fe67: f9          .
; High bytes of transfer address pointers
; &fe68 referenced 1 time by &fd7e
.transfer_addr_ptr_hi_table
    equb &fe                                                          ; fe68: fe          .
    equb &fe                                                          ; fe69: fe          .
    equb 0                                                            ; fe6a: 00          .
    equb 0                                                            ; fe6b: 00          .
    equb 0                                                            ; fe6c: 00          .
    equb 0                                                            ; fe6d: 00          .
    equb &fd                                                          ; fe6e: fd          .
    equb &fd                                                          ; fe6f: fd          .
; Low bytes of NMI handler addresses
; &fe70 referenced 1 time by &fd6d
.nmi_routine_addr_table
    equb 0                                                            ; fe70: 00          .
    equb &11                                                          ; fe71: 11          .
    equb &22                                                          ; fe72: 22          "
    equb &41                                                          ; fe73: 41          A
    equb &b3                                                          ; fe74: b3          .
    equb &b3                                                          ; fe75: b3          .
    equb &b3                                                          ; fe76: b3          .
    equb &b3                                                          ; fe77: b3          .
; High bytes of NMI handler addresses
; &fe78 referenced 1 time by &fd73
.nmi_routine_addr_hi_table
    equb &fe                                                          ; fe78: fe          .
    equb &fe                                                          ; fe79: fe          .
    equb &fe                                                          ; fe7a: fe          .
    equb &fe                                                          ; fe7b: fe          .
    equb &fe                                                          ; fe7c: fe          .
    equb &fe                                                          ; fe7d: fe          .
    equb &fe                                                          ; fe7e: fe          .
    equb &fe                                                          ; fe7f: fe          .

; ***************************************************************************************
; Wait for data in Tube R1, allowing Tube R4 transfer
;     requests to be serviced via IRQ while waiting.
; 
;     Polls R1 status; if R4 has data instead, briefly
;     enables interrupts to let the R4 handler run, then
;     resumes polling R1.
; 
;     On exit:
;       A = byte from Tube R1
; ***************************************************************************************
; Data available in Tube R1?
; &fe80 referenced 5 times by &fd21, &fd25, &fd29, &fe88, &fe91
.wait_for_tube_r1_byte
    bit lfef8                                                         ; fe80: 2c f8 fe    ,..
; Yes: go read it
    bmi cfe94                                                         ; fe83: 30 0f       0.
; Check Tube R4 for pending transfer requests
    bit lfefe                                                         ; fe85: 2c fe fe    ,..
; Nothing pending: keep polling R1
    bpl wait_for_tube_r1_byte                                         ; fe88: 10 f6       ..             ; Wait for data in Tube R1, allowing Tube R4 transfer
;     requests to be serviced via IRQ while waiting.
; 
;     Polls R1 status; if R4 has data instead, briefly
;     enables interrupts to let the R4 handler run, then
;     resumes polling R1.
; 
;     On exit:
;       A = byte from Tube R1
; Save irq_a_store before enabling interrupts
    lda irq_a_store                                                   ; fe8a: a5 fc       ..
    php                                                               ; fe8c: 08          .
; Allow one IRQ through to service R4
    cli                                                               ; fe8d: 58          X
    plp                                                               ; fe8e: 28          (
; Restore irq_a_store and continue polling
    sta irq_a_store                                                   ; fe8f: 85 fc       ..
    jmp wait_for_tube_r1_byte                                         ; fe91: 4c 80 fe    L..            ; Wait for data in Tube R1, allowing Tube R4 transfer
;     requests to be serviced via IRQ while waiting.
; 
;     Polls R1 status; if R4 has data instead, briefly
;     enables interrupts to let the R4 handler run, then
;     resumes polling R1.
; 
;     On exit:
;       A = byte from Tube R1

; Read byte from Tube R1
; &fe94 referenced 1 time by &fe83
.cfe94
    lda lfef9                                                         ; fe94: ad f9 fe    ...
    rts                                                               ; fe97: 60          `

; ***************************************************************************************
; Print the text string embedded immediately after the
;     JSR to this routine. Characters are sent to OSWRCH
;     until a byte with bit 7 set is encountered, which
;     terminates the string. Execution resumes after the
;     terminator byte.
; 
;     On exit:
;       A = terminator byte (bit 7 set)
; ***************************************************************************************
; Pull return address into control_block_ptr
; &fe98 referenced 1 time by &f860
.print_embedded_text
    pla                                                               ; fe98: 68          h
    sta control_block_ptr                                             ; fe99: 85 fa       ..
    pla                                                               ; fe9b: 68          h
    sta control_block_ptr_hi                                          ; fe9c: 85 fb       ..
; Increment past the JSR return address
    ldy #0                                                            ; fe9e: a0 00       ..
; &fea0 referenced 1 time by &fead
.loop_cfea0
    inc control_block_ptr                                             ; fea0: e6 fa       ..
    bne cfea6                                                         ; fea2: d0 02       ..
; Read next character from inline string
    inc control_block_ptr_hi                                          ; fea4: e6 fb       ..
; Bit 7 set: end of string
; &fea6 referenced 1 time by &fea2
.cfea6
    lda (control_block_ptr),y                                         ; fea6: b1 fa       ..
; Print character via OSWRCH
    bmi cfeb0                                                         ; fea8: 30 06       0.
    jsr oswrch_entry                                                  ; feaa: 20 ee ff     ..
    jmp loop_cfea0                                                    ; fead: 4c a0 fe    L..

; Resume execution after the string
; &feb0 referenced 1 time by &fea8
.cfeb0
    jmp (control_block_ptr)                                           ; feb0: 6c fa 00    l..

; ***************************************************************************************
; Acknowledge an NMI by writing A to Tube R3, then
;     return from interrupt. Used as the default NMI
;     handler for transfer types 4-7.
; ***************************************************************************************
; Write to Tube R3 to acknowledge NMI
.nmi_acknowledge
    equb &8d, &fd                                                     ; feb3: 8d fd       ..
; Unused ROM space, filled with &FF
    equb &fe                                                          ; feb5: fe          .
    equb &40                                                          ; feb6: 40          @
    equb &ff                                                          ; feb7: ff          .
    equb &ff                                                          ; feb8: ff          .
    equb &ff                                                          ; feb9: ff          .
    equb &ff                                                          ; feba: ff          .
    equb &ff                                                          ; febb: ff          .
    equb &ff                                                          ; febc: ff          .
    equb &ff                                                          ; febd: ff          .
    equb &ff                                                          ; febe: ff          .
    equb &ff                                                          ; febf: ff          .
    equb &ff                                                          ; fec0: ff          .
    equb &ff                                                          ; fec1: ff          .
    equb &ff                                                          ; fec2: ff          .
    equb &ff                                                          ; fec3: ff          .
    equb &ff                                                          ; fec4: ff          .
    equb &ff                                                          ; fec5: ff          .
    equb &ff                                                          ; fec6: ff          .
    equb &ff                                                          ; fec7: ff          .
    equb &ff                                                          ; fec8: ff          .
    equb &ff                                                          ; fec9: ff          .
    equb &ff                                                          ; feca: ff          .
    equb &ff                                                          ; fecb: ff          .
    equb &ff                                                          ; fecc: ff          .
    equb &ff                                                          ; fecd: ff          .
    equb &ff                                                          ; fece: ff          .
    equb &ff                                                          ; fecf: ff          .
    equb &ff                                                          ; fed0: ff          .
    equb &ff                                                          ; fed1: ff          .
    equb &ff                                                          ; fed2: ff          .
    equb &ff                                                          ; fed3: ff          .
    equb &ff                                                          ; fed4: ff          .
    equb &ff                                                          ; fed5: ff          .
    equb &ff                                                          ; fed6: ff          .
    equb &ff                                                          ; fed7: ff          .
    equb &ff                                                          ; fed8: ff          .
    equb &ff                                                          ; fed9: ff          .
    equb &ff                                                          ; feda: ff          .
    equb &ff                                                          ; fedb: ff          .
    equb &ff                                                          ; fedc: ff          .
    equb &ff                                                          ; fedd: ff          .
    equb &ff                                                          ; fede: ff          .
    equb &ff                                                          ; fedf: ff          .
    equb &ff                                                          ; fee0: ff          .
    equb &ff                                                          ; fee1: ff          .
    equb &ff                                                          ; fee2: ff          .
    equb &ff                                                          ; fee3: ff          .
    equb &ff                                                          ; fee4: ff          .
    equb &ff                                                          ; fee5: ff          .
    equb &ff                                                          ; fee6: ff          .
    equb &ff                                                          ; fee7: ff          .
    equb &ff                                                          ; fee8: ff          .
    equb &ff                                                          ; fee9: ff          .
    equb &ff                                                          ; feea: ff          .
    equb &ff                                                          ; feeb: ff          .
    equb &ff                                                          ; feec: ff          .
    equb &ff                                                          ; feed: ff          .
    equb &ff                                                          ; feee: ff          .
    equb &ff                                                          ; feef: ff          .
    equb &ff                                                          ; fef0: ff          .
    equb &ff                                                          ; fef1: ff          .
    equb &ff                                                          ; fef2: ff          .
    equb &ff                                                          ; fef3: ff          .
    equb &ff                                                          ; fef4: ff          .
    equb &ff                                                          ; fef5: ff          .
    equb &ff                                                          ; fef6: ff          .
    equb &ff                                                          ; fef7: ff          .
; &fef8 referenced 4 times by &f859, &f962, &fcf5, &fe80
.lfef8
    equb &ff                                                          ; fef8: ff          .
; &fef9 referenced 3 times by &f968, &fd18, &fe94
.lfef9
    equb &ff                                                          ; fef9: ff          .
; &fefa referenced 25 times by &f975, &f9b8, &fa7a, &fa82, &fa8b, &fa93, &faab, &fab3, &fabb, &fac4, &fad5, &fadf, &fae7, &fb09, &fb11, &fb2d, &fb38, &fb59, &fb64, &fb7e, &fb96, &fbb2, &fbd2, &fc4a, &fd45
.lfefa
    equb &ff                                                          ; fefa: ff          .
; &fefb referenced 25 times by &f97a, &f9bf, &fa7f, &fa87, &fa90, &fa98, &fab0, &fab8, &fac0, &fac9, &fada, &fae4, &faec, &fb0e, &fb16, &fb32, &fb3f, &fb5e, &fb69, &fb85, &fb9b, &fbb7, &fbd7, &fc4f, &fd4a
.lfefb
    equb &ff                                                          ; fefb: ff          .
; &fefc referenced 3 times by &fdcf, &fddf, &fdee
.lfefc
    equb &ff                                                          ; fefc: ff          .
; &fefd referenced 11 times by &fdb8, &fdbb, &fdd9, &fde4, &fdf5, &fe04, &fe12, &fe29, &fe34, &fe46, &fe51
.lfefd
    equb &ff                                                          ; fefd: ff          .
; &fefe referenced 8 times by &fcf0, &fd83, &fd93, &fd9b, &fda3, &fdae, &fdbe, &fe85
.lfefe
    equb &ff                                                          ; fefe: ff          .
; &feff referenced 7 times by &fd3f, &fd88, &fd98, &fda0, &fda8, &fdb3, &fdc3
.lfeff
    equb &ff                                                          ; feff: ff          .
; Unused ROM space, filled with &FF
; &ff00 referenced 2 times by &f802, &f805
.lff00
    equb &ff                                                          ; ff00: ff          .
    equb &ff                                                          ; ff01: ff          .
    equb &ff                                                          ; ff02: ff          .
    equb &ff                                                          ; ff03: ff          .
    equb &ff                                                          ; ff04: ff          .
    equb &ff                                                          ; ff05: ff          .
    equb &ff                                                          ; ff06: ff          .
    equb &ff                                                          ; ff07: ff          .
    equb &ff                                                          ; ff08: ff          .
    equb &ff                                                          ; ff09: ff          .
    equb &ff                                                          ; ff0a: ff          .
    equb &ff                                                          ; ff0b: ff          .
    equb &ff                                                          ; ff0c: ff          .
    equb &ff                                                          ; ff0d: ff          .
    equb &ff                                                          ; ff0e: ff          .
    equb &ff                                                          ; ff0f: ff          .
    equb &ff                                                          ; ff10: ff          .
    equb &ff                                                          ; ff11: ff          .
    equb &ff                                                          ; ff12: ff          .
    equb &ff                                                          ; ff13: ff          .
    equb &ff                                                          ; ff14: ff          .
    equb &ff                                                          ; ff15: ff          .
    equb &ff                                                          ; ff16: ff          .
    equb &ff                                                          ; ff17: ff          .
    equb &ff                                                          ; ff18: ff          .
    equb &ff                                                          ; ff19: ff          .
    equb &ff                                                          ; ff1a: ff          .
    equb &ff                                                          ; ff1b: ff          .
    equb &ff                                                          ; ff1c: ff          .
    equb &ff                                                          ; ff1d: ff          .
    equb &ff                                                          ; ff1e: ff          .
    equb &ff                                                          ; ff1f: ff          .
    equb &ff                                                          ; ff20: ff          .
    equb &ff                                                          ; ff21: ff          .
    equb &ff                                                          ; ff22: ff          .
    equb &ff                                                          ; ff23: ff          .
    equb &ff                                                          ; ff24: ff          .
    equb &ff                                                          ; ff25: ff          .
    equb &ff                                                          ; ff26: ff          .
    equb &ff                                                          ; ff27: ff          .
    equb &ff                                                          ; ff28: ff          .
    equb &ff                                                          ; ff29: ff          .
    equb &ff                                                          ; ff2a: ff          .
    equb &ff                                                          ; ff2b: ff          .
    equb &ff                                                          ; ff2c: ff          .
    equb &ff                                                          ; ff2d: ff          .
    equb &ff                                                          ; ff2e: ff          .
    equb &ff                                                          ; ff2f: ff          .
    equb &ff                                                          ; ff30: ff          .
    equb &ff                                                          ; ff31: ff          .
    equb &ff                                                          ; ff32: ff          .
    equb &ff                                                          ; ff33: ff          .
    equb &ff                                                          ; ff34: ff          .
    equb &ff                                                          ; ff35: ff          .
    equb &ff                                                          ; ff36: ff          .
    equb &ff                                                          ; ff37: ff          .
    equb &ff                                                          ; ff38: ff          .
    equb &ff                                                          ; ff39: ff          .
    equb &ff                                                          ; ff3a: ff          .
    equb &ff                                                          ; ff3b: ff          .
    equb &ff                                                          ; ff3c: ff          .
    equb &ff                                                          ; ff3d: ff          .
    equb &ff                                                          ; ff3e: ff          .
    equb &ff                                                          ; ff3f: ff          .
    equb &ff                                                          ; ff40: ff          .
    equb &ff                                                          ; ff41: ff          .
    equb &ff                                                          ; ff42: ff          .
    equb &ff                                                          ; ff43: ff          .
    equb &ff                                                          ; ff44: ff          .
    equb &ff                                                          ; ff45: ff          .
    equb &ff                                                          ; ff46: ff          .
    equb &ff                                                          ; ff47: ff          .
    equb &ff                                                          ; ff48: ff          .
    equb &ff                                                          ; ff49: ff          .
    equb &ff                                                          ; ff4a: ff          .
    equb &ff                                                          ; ff4b: ff          .
    equb &ff                                                          ; ff4c: ff          .
    equb &ff                                                          ; ff4d: ff          .
    equb &ff                                                          ; ff4e: ff          .
    equb &ff                                                          ; ff4f: ff          .
    equb &ff                                                          ; ff50: ff          .
    equb &ff                                                          ; ff51: ff          .
    equb &ff                                                          ; ff52: ff          .
    equb &ff                                                          ; ff53: ff          .
    equb &ff                                                          ; ff54: ff          .
    equb &ff                                                          ; ff55: ff          .
    equb &ff                                                          ; ff56: ff          .
    equb &ff                                                          ; ff57: ff          .
    equb &ff                                                          ; ff58: ff          .
    equb &ff                                                          ; ff59: ff          .
    equb &ff                                                          ; ff5a: ff          .
    equb &ff                                                          ; ff5b: ff          .
    equb &ff                                                          ; ff5c: ff          .
    equb &ff                                                          ; ff5d: ff          .
    equb &ff                                                          ; ff5e: ff          .
    equb &ff                                                          ; ff5f: ff          .
    equb &ff                                                          ; ff60: ff          .
    equb &ff                                                          ; ff61: ff          .
    equb &ff                                                          ; ff62: ff          .
    equb &ff                                                          ; ff63: ff          .
    equb &ff                                                          ; ff64: ff          .
    equb &ff                                                          ; ff65: ff          .
    equb &ff                                                          ; ff66: ff          .
    equb &ff                                                          ; ff67: ff          .
    equb &ff                                                          ; ff68: ff          .
    equb &ff                                                          ; ff69: ff          .
    equb &ff                                                          ; ff6a: ff          .
    equb &ff                                                          ; ff6b: ff          .
    equb &ff                                                          ; ff6c: ff          .
    equb &ff                                                          ; ff6d: ff          .
    equb &ff                                                          ; ff6e: ff          .
    equb &ff                                                          ; ff6f: ff          .
    equb &ff                                                          ; ff70: ff          .
    equb &ff                                                          ; ff71: ff          .
    equb &ff                                                          ; ff72: ff          .
    equb &ff                                                          ; ff73: ff          .
    equb &ff                                                          ; ff74: ff          .
    equb &ff                                                          ; ff75: ff          .
    equb &ff                                                          ; ff76: ff          .
    equb &ff                                                          ; ff77: ff          .
    equb &ff                                                          ; ff78: ff          .
    equb &ff                                                          ; ff79: ff          .
    equb &ff                                                          ; ff7a: ff          .
    equb &ff                                                          ; ff7b: ff          .
    equb &ff                                                          ; ff7c: ff          .
    equb &ff                                                          ; ff7d: ff          .
    equb &ff                                                          ; ff7e: ff          .
    equb &ff                                                          ; ff7f: ff          .
; Default MOS vector table (27 entries)
; &ff80 referenced 1 time by &f80d
.default_vector_table
    equw &fcb7                                                        ; ff80: b7 fc       ..
    equw &f945                                                        ; ff82: 45 f9       E.
    equw &fcf0                                                        ; ff84: f0 fc       ..
    equw &fcb7                                                        ; ff86: b7 fc       ..
    equw &f9ca                                                        ; ff88: ca f9       ..
    equw &fa73                                                        ; ff8a: 73 fa       s.
    equw &faff                                                        ; ff8c: ff fa       ..
    equw &f962                                                        ; ff8e: 62 f9       b.
    equw &f96c                                                        ; ff90: 6c f9       l.
    equw &fc53                                                        ; ff92: 53 fc       S.
    equw &fbcc                                                        ; ff94: cc fb       ..
    equw &fc2a                                                        ; ff96: 2a fc       *.
    equw &fc36                                                        ; ff98: 36 fc       6.
    equw &fc8e                                                        ; ff9a: 8e fc       ..
    equw &fc0c                                                        ; ff9c: 0c fc       ..
    equw &fcb7                                                        ; ff9e: b7 fc       ..
    equw &f97d                                                        ; ffa0: 7d f9       }.
    equw &fcb7                                                        ; ffa2: b7 fc       ..
    equw &fcb7                                                        ; ffa4: b7 fc       ..
    equw &fcb7                                                        ; ffa6: b7 fc       ..
    equw &fcb7                                                        ; ffa8: b7 fc       ..
    equw &fcb7                                                        ; ffaa: b7 fc       ..
    equw &fcb7                                                        ; ffac: b7 fc       ..
    equw &fcb7                                                        ; ffae: b7 fc       ..
    equw &f97d                                                        ; ffb0: 7d f9       }.
    equw &f97d                                                        ; ffb2: 7d f9       }.
    equw &f97d                                                        ; ffb4: 7d f9       }.
; Vector table info: length &36, table at &FF80
.vector_table_info
    equb &36                                                          ; ffb6: 36          6
    equw &ff80                                                        ; ffb7: 80 ff       ..

.mos_stub_unsupported_1
    jmp unsupported                                                   ; ffb9: 4c b7 fc    L..            ; Generate a 'Bad' error for unsupported MOS calls.

.mos_stub_unsupported_2
    equb &4c, &b7, &fc                                                ; ffbc: 4c b7 fc    L..
.mos_stub_unsupported_3
    equb &4c, &b7, &fc                                                ; ffbf: 4c b7 fc    L..
.mos_stub_unsupported_4
    equb &4c, &b7, &fc                                                ; ffc2: 4c b7 fc    L..
.mos_stub_unsupported_5
    equb &4c, &b7, &fc                                                ; ffc5: 4c b7 fc    L..

.nvrdch
    jmp osrdch_impl                                                   ; ffc8: 4c 6c f9    Ll.            ; Read a character from the host via the Tube.
; 
;     Sends command &00 to the host, then waits for
;     a carry byte and the character.
; 
;     On exit:
;       A = character received
;       C = Escape flag

.nvwrch
    jmp oswrch_impl                                                   ; ffcb: 4c 62 f9    Lb.            ; Send character in A to the host via Tube R1.
; 
;     On entry:
;       A = character to send
;     On exit:
;       A preserved

.osfind_entry
    jmp (findv)                                                       ; ffce: 6c 1c 02    l..

.osgbpb_entry
    jmp (gbpbv)                                                       ; ffd1: 6c 1a 02    l..

.osbput_entry
    jmp (bputv)                                                       ; ffd4: 6c 18 02    l..

.osbget_entry
    jmp (bgetv)                                                       ; ffd7: 6c 16 02    l..

.osargs_entry
    jmp (argsv)                                                       ; ffda: 6c 14 02    l..

.osfile_entry
    jmp (filev)                                                       ; ffdd: 6c 12 02    l..

.osrdch_entry
    jmp (rdchv)                                                       ; ffe0: 6c 10 02    l..

.osasci_entry
    cmp #&0d                                                          ; ffe3: c9 0d       ..
    bne oswrch_entry                                                  ; ffe5: d0 07       ..
; &ffe7 referenced 2 times by &f948, &f957
.osnewl_entry
    lda #&0a                                                          ; ffe7: a9 0a       ..
    jsr oswrch_entry                                                  ; ffe9: 20 ee ff     ..
.oswrcr_entry
    lda #&0d                                                          ; ffec: a9 0d       ..
; &ffee referenced 5 times by &f88f, &f951, &feaa, &ffe5, &ffe9
.oswrch_entry
    jmp (wrchv)                                                       ; ffee: 6c 0e 02    l..

; &fff1 referenced 1 time by &f898
.osword_entry
    jmp (wordv)                                                       ; fff1: 6c 0c 02    l..

; &fff4 referenced 1 time by &f8a9
.osbyte_entry
    jmp (bytev)                                                       ; fff4: 6c 0a 02    l..

; &fff7 referenced 1 time by &f8a1
.oscli_entry
    jmp (cliv)                                                        ; fff7: 6c 08 02    l..

; NMI vector
; &fffa referenced 3 times by &fd65, &fd6a, &fd70
.nmi_vector
lfffb = nmi_vector+1
    equw &feb3                                                        ; fffa: b3 fe       ..
; &fffb referenced 1 time by &fd76
; RESET vector
.reset_vector
    equw &f800                                                        ; fffc: 00 f8       ..
; IRQ/BRK vector
.irq_vector
lffff = irq_vector+1
    equw &fce5                                                        ; fffe: e5 fc       ..
; &ffff referenced 4 times by &fdd6, &fdf8, &fe01, &fe15
.pydis_end


save pydis_start, pydis_end

; Label references by decreasing frequency:
;     Send byte to Tube R2:                   25
;     lfefa:                                  25
;     lfefb:                                  25
;     send_byte_to_tube_r2:                   25
;     send_command:                           25
;     string_ptr:                             23
;     wait_for_tube_r2_byte:                  18
;     control_block_ptr:                      14
;     data_transfer_addr:                     11
;     lfefd:                                  11
;     string_ptr_hi:                           9
;     lfefe:                                   8
;     Send OSCLI command to host:              7
;     current_program:                         7
;     data_transfer_addr_hi:                   7
;     irq_a_store:                             7
;     last_error:                              7
;     lfeff:                                   7
;     oscli_send_to_host:                      7
;     control_block_ptr_hi:                    6
;     Wait for byte in Tube R1:                5
;     current_program_hi:                      5
;     memory_top:                              5
;     oswrch_entry:                            5
;     wait_for_tube_r1_byte:                   5
;     Handle *HELP command:                    4
;     command_help:                            4
;     enter_raw_code:                          4
;     lfef8:                                   4
;     lffff:                                   4
;     memory_top_hi:                           4
;     brkv:                                    3
;     cfb2d:                                   3
;     cfb59:                                   3
;     hex_accumulator:                         3
;     hex_accumulator_hi:                      3
;     l0002:                                   3
;     lfef9:                                   3
;     lfefc:                                   3
;     nmi_vector:                              3
;     restore_regs_and_rti:                    3
;     return_1:                                3
;     transfer_addr_ptr:                       3
;     Command prompt loop:                     2
;     Enter code at transfer address:          2
;     Execute code and restore state:          2
;     OSWRCH implementation:                   2
;     Send string to Tube R2:                  2
;     Skip spaces in command string:           2
;     brkv_hi:                                 2
;     cf82a:                                   2
;     cf9b8:                                   2
;     cfb38:                                   2
;     cfb64:                                   2
;     cfb7e:                                   2
;     cfbb2:                                   2
;     cfdcf:                                   2
;     cfdee:                                   2
;     command_prompt:                          2
;     enter_code:                              2
;     error_buffer:                            2
;     error_buffer_errnum:                     2
;     escape_flag:                             2
;     execute_code:                            2
;     l0000:                                   2
;     l0001:                                   2
;     l0003:                                   2
;     last_error_hi:                           2
;     lfdff:                                   2
;     lff00:                                   2
;     low_memory_code:                         2
;     osnewl_entry:                            2
;     oswrch_impl:                             2
;     send_string:                             2
;     skip_spaces:                             2
;     skip_spaces_step:                        2
;     wait_carry_and_byte:                     2
;     Display startup banner and initialise:   1
;     Handle *GO command:                      1
;     Handle Tube R1 interrupt:                1
;     Handle Tube R4 interrupt:                1
;     Low memory startup code:                 1
;     OSRDCH implementation:                   1
;     Parse hexadecimal number:                1
;     Print inline text:                       1
;     Read line of input (OSWORD 0):           1
;     Set up data transfer via NMI:            1
;     Unsupported MOS call:                    1
;     argsv:                                   1
;     bgetv:                                   1
;     bputv:                                   1
;     bytev:                                   1
;     cf957:                                   1
;     cf98c:                                   1
;     cf9a0:                                   1
;     cfaf5:                                   1
;     cfafa:                                   1
;     cfb24:                                   1
;     cfb45:                                   1
;     cfb50:                                   1
;     cfb71:                                   1
;     cfbc7:                                   1
;     cfc24:                                   1
;     cfcfd:                                   1
;     cfe0f:                                   1
;     cfe20:                                   1
;     cfe32:                                   1
;     cfe3d:                                   1
;     cfe51:                                   1
;     cfe5c:                                   1
;     cfe94:                                   1
;     cfea6:                                   1
;     cfeb0:                                   1
;     check_oscli_ack:                         1
;     cliv:                                    1
;     command_go:                              1
;     command_prompt_escape:                   1
;     data_transfer_setup:                     1
;     default_vector_table:                    1
;     error_not_6502_code:                     1
;     error_not_a_language:                    1
;     evntv:                                   1
;     filev:                                   1
;     findv:                                   1
;     gbpbv:                                   1
;     irq1v:                                   1
;     irq_return_addr_hi:                      1
;     irq_return_addr_lo:                      1
;     lf85e:                                   1
;     lf85f:                                   1
;     lfe02:                                   1
;     lfe16:                                   1
;     lfe17:                                   1
;     lfffb:                                   1
;     loop_cf802:                              1
;     loop_cf80d:                              1
;     loop_cf819:                              1
;     loop_cf83b:                              1
;     loop_cf94d:                              1
;     loop_cf9a6:                              1
;     loop_cf9d1:                              1
;     loop_cfa7a:                              1
;     loop_cfa82:                              1
;     loop_cfa8b:                              1
;     loop_cfa93:                              1
;     loop_cfaab:                              1
;     loop_cfab3:                              1
;     loop_cfabb:                              1
;     loop_cfac4:                              1
;     loop_cfad5:                              1
;     loop_cfadf:                              1
;     loop_cfae7:                              1
;     loop_cfb09:                              1
;     loop_cfb11:                              1
;     loop_cfb96:                              1
;     loop_cfbd2:                              1
;     loop_cfc5f:                              1
;     loop_cfc7e:                              1
;     loop_cfc9a:                              1
;     loop_cfca8:                              1
;     loop_cfd45:                              1
;     loop_cfd59:                              1
;     loop_cfd83:                              1
;     loop_cfd93:                              1
;     loop_cfd9b:                              1
;     loop_cfda3:                              1
;     loop_cfdae:                              1
;     loop_cfdbe:                              1
;     loop_cfddf:                              1
;     loop_cfea0:                              1
;     low_memory_startup_code:                 1
;     nmi0_transfer_addr:                      1
;     nmi_routine_addr_hi_table:               1
;     nmi_routine_addr_table:                  1
;     osbyte_entry:                            1
;     osbyte_high:                             1
;     osbyte_read_himem:                       1
;     oscli_entry:                             1
;     oscli_wait_ack:                          1
;     osrdch_impl:                             1
;     osword_entry:                            1
;     osword_recv_lengths:                     1
;     osword_send_lengths:                     1
;     print_embedded_text:                     1
;     rdchv:                                   1
;     rdline:                                  1
;     return_2:                                1
;     scan_hex:                                1
;     send_string_via_ptr:                     1
;     set_escape_flag:                         1
;     startup_banner:                          1
;     sub_cfd36:                               1
;     transfer_256_bytes_from_tube:            1
;     transfer_addr_ptr_hi:                    1
;     transfer_addr_ptr_hi_table:              1
;     transfer_addr_ptr_table:                 1
;     tube_r1_interrupt:                       1
;     tube_r4_interrupt:                       1
;     unsupported:                             1
;     userv:                                   1
;     wordv:                                   1
;     wrchv:                                   1

; Automatically generated labels:
;     cf82a
;     cf957
;     cf98c
;     cf9a0
;     cf9b8
;     cfaf5
;     cfafa
;     cfb24
;     cfb2d
;     cfb38
;     cfb45
;     cfb50
;     cfb59
;     cfb64
;     cfb71
;     cfb7e
;     cfbb2
;     cfbc7
;     cfc24
;     cfcfd
;     cfdcf
;     cfdee
;     cfe0f
;     cfe20
;     cfe32
;     cfe3d
;     cfe51
;     cfe5c
;     cfe94
;     cfea6
;     cfeb0
;     l0000
;     l0001
;     l0002
;     l0003
;     lf85e
;     lf85f
;     lfdff
;     lfe02
;     lfe16
;     lfe17
;     lfef8
;     lfef9
;     lfefa
;     lfefb
;     lfefc
;     lfefd
;     lfefe
;     lfeff
;     lff00
;     lfffb
;     lffff
;     loop_cf802
;     loop_cf80d
;     loop_cf819
;     loop_cf83b
;     loop_cf94d
;     loop_cf9a6
;     loop_cf9d1
;     loop_cfa7a
;     loop_cfa82
;     loop_cfa8b
;     loop_cfa93
;     loop_cfaab
;     loop_cfab3
;     loop_cfabb
;     loop_cfac4
;     loop_cfad5
;     loop_cfadf
;     loop_cfae7
;     loop_cfb09
;     loop_cfb11
;     loop_cfb96
;     loop_cfbd2
;     loop_cfc5f
;     loop_cfc7e
;     loop_cfc9a
;     loop_cfca8
;     loop_cfd45
;     loop_cfd59
;     loop_cfd83
;     loop_cfd93
;     loop_cfd9b
;     loop_cfda3
;     loop_cfdae
;     loop_cfdbe
;     loop_cfddf
;     loop_cfea0
;     return_1
;     return_2
;     sub_cf85d
;     sub_cfaf7
;     sub_cfd36
;     sub_cfdd6
;     sub_cfdf8
;     sub_cfdfe
;     sub_cfe01

; Stats:
;     Total size (Code + Data) = 2048 bytes
;     Code                     = 1585 bytes (77%)
;     Data                     = 463 bytes (23%)
;
;     Number of instructions   = 778
;     Number of data bytes     = 306 bytes
;     Number of data words     = 62 bytes
;     Number of string bytes   = 95 bytes
;     Number of strings        = 6
