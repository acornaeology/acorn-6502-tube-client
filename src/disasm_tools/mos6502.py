"""MOS 6502 processor constants for disassembly tools."""

# Tube Client ROM base address and size.
# The 65C02 parasite processor Tube client occupies the top 2 kB of
# the 64 kB address space. The base address will be confirmed when the
# ROM image is provided.
ROM_BASE = 0xF800
ROM_SIZE = 2048

# Instruction lengths indexed by opcode byte (0-255).
# 0 = invalid/undefined, 1 = implied/accumulator,
# 2 = immediate/zp/rel, 3 = absolute
OPCODE_LENGTHS = [
    # $00-$0F
    1, 2, 0, 0, 0, 2, 2, 0, 1, 2, 1, 0, 0, 3, 3, 0,
    # $10-$1F
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    # $20-$2F
    3, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    # $30-$3F
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    # $40-$4F
    1, 2, 0, 0, 0, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    # $50-$5F
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    # $60-$6F
    1, 2, 0, 0, 0, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    # $70-$7F
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    # $80-$8F
    0, 2, 0, 0, 2, 2, 2, 0, 1, 0, 1, 0, 3, 3, 3, 0,
    # $90-$9F
    2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 0, 3, 0, 0,
    # $A0-$AF
    2, 2, 2, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    # $B0-$BF
    2, 2, 0, 0, 2, 2, 2, 0, 1, 3, 1, 0, 3, 3, 3, 0,
    # $C0-$CF
    2, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    # $D0-$DF
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
    # $E0-$EF
    2, 2, 0, 0, 2, 2, 2, 0, 1, 2, 1, 0, 3, 3, 3, 0,
    # $F0-$FF
    2, 2, 0, 0, 0, 2, 2, 0, 1, 3, 0, 0, 0, 3, 3, 0,
]

# Mnemonics indexed by opcode byte (0-255).
# "???" for invalid/undefined opcodes.
OPCODE_MNEMONICS = [
    # $00-$0F
    "BRK", "ORA", "???", "???", "???", "ORA", "ASL", "???",
    "PHP", "ORA", "ASL", "???", "???", "ORA", "ASL", "???",
    # $10-$1F
    "BPL", "ORA", "???", "???", "???", "ORA", "ASL", "???",
    "CLC", "ORA", "???", "???", "???", "ORA", "ASL", "???",
    # $20-$2F
    "JSR", "AND", "???", "???", "BIT", "AND", "ROL", "???",
    "PLP", "AND", "ROL", "???", "BIT", "AND", "ROL", "???",
    # $30-$3F
    "BMI", "AND", "???", "???", "???", "AND", "ROL", "???",
    "SEC", "AND", "???", "???", "???", "AND", "ROL", "???",
    # $40-$4F
    "RTI", "EOR", "???", "???", "???", "EOR", "LSR", "???",
    "PHA", "EOR", "LSR", "???", "JMP", "EOR", "LSR", "???",
    # $50-$5F
    "BVC", "EOR", "???", "???", "???", "EOR", "LSR", "???",
    "CLI", "EOR", "???", "???", "???", "EOR", "LSR", "???",
    # $60-$6F
    "RTS", "ADC", "???", "???", "???", "ADC", "ROR", "???",
    "PLA", "ADC", "ROR", "???", "JMP", "ADC", "ROR", "???",
    # $70-$7F
    "BVS", "ADC", "???", "???", "???", "ADC", "ROR", "???",
    "SEI", "ADC", "???", "???", "???", "ADC", "ROR", "???",
    # $80-$8F
    "???", "STA", "???", "???", "STY", "STA", "STX", "???",
    "DEY", "???", "TXA", "???", "STY", "STA", "STX", "???",
    # $90-$9F
    "BCC", "STA", "???", "???", "STY", "STA", "STX", "???",
    "TYA", "STA", "TXS", "???", "???", "STA", "???", "???",
    # $A0-$AF
    "LDY", "LDA", "LDX", "???", "LDY", "LDA", "LDX", "???",
    "TAY", "LDA", "TAX", "???", "LDY", "LDA", "LDX", "???",
    # $B0-$BF
    "BCS", "LDA", "???", "???", "LDY", "LDA", "LDX", "???",
    "CLV", "LDA", "TSX", "???", "LDY", "LDA", "LDX", "???",
    # $C0-$CF
    "CPY", "CMP", "???", "???", "CPY", "CMP", "DEC", "???",
    "INY", "CMP", "DEX", "???", "CPY", "CMP", "DEC", "???",
    # $D0-$DF
    "BNE", "CMP", "???", "???", "???", "CMP", "DEC", "???",
    "CLD", "CMP", "???", "???", "???", "CMP", "DEC", "???",
    # $E0-$EF
    "CPX", "SBC", "???", "???", "CPX", "SBC", "INC", "???",
    "INX", "SBC", "NOP", "???", "CPX", "SBC", "INC", "???",
    # $F0-$FF
    "BEQ", "SBC", "???", "???", "???", "SBC", "INC", "???",
    "SED", "SBC", "???", "???", "???", "SBC", "INC", "???",
]
