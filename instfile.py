
inst = ["ADD","ADDF","ADDR","AND","CLEAR","COMP","COMPF","COMPR","DIV","DIVF","DIVR","FIX","FLOAT","HIO","J","JEQ","JGT","JLT","JSUB","LDA","LDB","LDCH","LDF","LDL","LDS","LDT","LDX","LPS","MUL","MULF","MULR","NORM","OR","RD","RMO","RSUB","SHIFTL","SHIFTR","SIO","SSK","STA","STB","STCH","STF","STI","STL","STS","STSW","STT","STX","SUB","SUBF","SUBR","SVC","TD","TIO","TIX","TIXR","WD", "STOP"]
instformat = [3,3,2,3,2,3,3,2,3,3,2,1,1,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,1,3,3,2,3,2,2,1,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,3,1,3,2,3,3]
opcode = [0x18,0x58,0x90,0x40,0xB4,0x28,0x88,0xA0,0x24,0x64,0x9C,0xC4,0xC0,0xF4,0x3C,0x30,0x34,0x38,0x48,0x00,0x68,0x50,0x70,0x08,0x6C,0x74,0x04,0xD0,0x20,0x60,0x98,0xC8,0x44,0xD8,0xAC,0x4C,0xA4,0xA8,0xF0,0xEC,0x0C,0x78,0x54,0x80,0xD4,0x14,0x7C,0xE8,0x84,0x10,0x1C,0x5C,0x94,0xB0,0xE0,0xF8,0x2C,0xB8,0xDC, 0xFF]
token = ['f3','f3','f2','f3','f2','f3','f3','f2','f3','f3','f2','f1','f1','f1','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f2','f1','f3','f3','f2','f3','f2','f2','f1','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f3','f2','f2','f3','f1','f3','f2','f3','f3']

directives = ["WORD", "BYTE", "RESW", "RESB", "START", "END", "BASE", 'A', 'X', 'L', 'B', 'S', 'T', 'F']
dirtoken   = ["WORD", "BYTE", "RESW", "RESB", "START", "END", "BASE", 'REG', 'REG', 'REG', 'REG', 'REG', 'REG', 'REG']
dircode  = [3, 1, 3, 1, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6]

registers = ["A"]  # ????
def inst2opcode(mnemonic):
    return opcode[inst.index(mnemonic)]

def opcode2inst(op):
    return inst[opcode.index(op)]

def opcode2format(op):
    return instformat[opcode.index(op)]

def opcode2index(op):
    return opcode.index(op)