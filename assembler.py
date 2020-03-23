import re
import instfile
import sys

# THERE IS PROBLEM WITH SYMTABLE, SOME VALUES HAVE WRONG ATT (DONE)
# I THINK THE PROBLEM is how to use defid(done)
# some opcode dose not use ebit(pc) like JSUB
# WE NEED TO FIND OUT HOW TO USE @NUM
class Entry:
    def __init__(self, string, token, attribute):
        self.string = string
        self.token = token
        self.att = attribute


symtable = []


def lookup(s):
    for i in range(0, symtable.__len__()):
        if s == symtable[i].string:
            return i
    return -1


def insert(s, t, a):
    symtable.append(Entry(s, t, a))
    return symtable.__len__() - 1


def init():
    for i in range(0, instfile.inst.__len__()):
        insert(instfile.inst[i], instfile.token[i], instfile.opcode[i])
    for i in range(0, instfile.directives.__len__()):
        insert(instfile.directives[i], instfile.dirtoken[i], instfile.dircode[i])


file = open("input.sic", "r")
output = open("output.obj", "+w")
filecontent = []
bufferindex = 0
tokenval = 0
lineno = 1
pass1or2 = 1
locctr = 0
lookahead = ""
defid = True
totalsize = 0
startaddress = 0
inst = 0
is_xe = False
extend = False

Xbit4set = 0x800000
Bbit4set = 0x400000
Pbit4set = 0x200000
Ebit4set = 0x100000

Nbitset = 2
Ibitset = 1

Xbit3set = 0x8000
Bbit3set = 0x4000
Pbit3set = 0x2000
Ebit3set = 0x1000


def is_hex(s):
    if s[0:2].upper() == "0X":
        try:
            int(s[2:], 16)
            return True
        except ValueError:
            return False
    else:
        return False


def lexan():
    global filecontent, tokenval, lineno, bufferindex, locctr, defid

    while True:
        # if filecontent == []:
        if len(filecontent) == bufferindex:
            return "EOF"
        elif filecontent[bufferindex] == ".":
            defid = True
            while filecontent[bufferindex] != "\n":
                bufferindex = bufferindex + 1
            lineno += 1
            bufferindex = bufferindex + 1
        elif filecontent[bufferindex] == "\n":
            defid = True
            # del filecontent[bufferindex]
            bufferindex = bufferindex + 1
            lineno += 1
        else:
            break
    if filecontent[bufferindex].isdigit():
        # all number are considered as decimals
        tokenval = int(filecontent[bufferindex])
        # del filecontent[bufferindex]
        bufferindex = bufferindex + 1
        return "NUM"
    elif is_hex(filecontent[bufferindex]):
        # all number starting with 0x are considered as hex
        tokenval = int(filecontent[bufferindex][2:], 16)
        # del filecontent[bufferindex]
        bufferindex = bufferindex + 1
        return "NUM"
    elif filecontent[bufferindex] in ["+", "#", ",", "@"]:
        c = filecontent[bufferindex]
        # del filecontent[bufferindex]
        bufferindex = bufferindex + 1
        return c
    else:
        # check if there is a string or hex starting with C'string' or X'hex'
        if (
            filecontent[bufferindex].upper() == "C"
            and filecontent[bufferindex + 1] == "'"
        ):
            bytestring = ""
            bufferindex += 2
            # should we take into account the missing ' error?
            while filecontent[bufferindex] != "'":
                bytestring += filecontent[bufferindex]
                bufferindex += 1
                if filecontent[bufferindex] != "'":
                    bytestring += " "
            bufferindex += 1
            bytestringvalue = "".join("%02X" % ord(c) for c in bytestring)
            bytestring = "_" + bytestring
            p = lookup(bytestring)
            if p == -1:
                # should we deal with literals?
                p = insert(bytestring, "STRING", bytestringvalue)
            tokenval = p
        # a string can start with C' or only with '
        elif filecontent[bufferindex] == "'":
            bytestring = ""
            bufferindex += 1
            # should we take into account the missing ' error?
            while filecontent[bufferindex] != "'":
                bytestring += filecontent[bufferindex]
                bufferindex += 1
                if filecontent[bufferindex] != "'":
                    bytestring += " "
            bufferindex += 1
            bytestringvalue = "".join("%02X" % ord(c) for c in bytestring)
            bytestring = "_" + bytestring
            p = lookup(bytestring)
            if p == -1:
                # should we deal with literals?
                p = insert(bytestring, "STRING", bytestringvalue)
            tokenval = p
        elif (
            filecontent[bufferindex].upper() == "X"
            and filecontent[bufferindex + 1] == "'"
        ):
            bufferindex += 2
            bytestring = filecontent[bufferindex]
            bufferindex += 2
            # if filecontent[bufferindex] != '\'':# should we take into account the missing ' error?

            bytestringvalue = bytestring
            if len(bytestringvalue) % 2 == 1:
                bytestringvalue = "0" + bytestringvalue
            bytestring = "_" + bytestring
            p = lookup(bytestring)
            if p == -1:
                # should we deal with literals?
                p = insert(bytestring, "HEX", bytestringvalue)
            tokenval = p
        else:
            p = lookup(filecontent[bufferindex].upper())
            if p == -1:
                if defid == True:
                    # should we deal with case-sensitive?
                    p = insert(filecontent[bufferindex].upper(), "ID", locctr)
                else:
                    # forward reference
                    p = insert(filecontent[bufferindex].upper(), "ID", -1)
            else:
                if symtable[p].att == -1 and defid == True:
                    symtable[p].att = locctr
            tokenval = p
            # del filecontent[bufferindex]
            bufferindex = bufferindex + 1
        return symtable[p].token


def error(s):
    global lineno
    print("line " + str(lineno) + ": " + s)


def match(token):
    global lookahead
    if lookahead == token:
        lookahead = lexan()
    else:
        error("Syntax error")


def checkindex():
    global bufferindex, symtable, tokenval
    if lookahead == ",":
        match(",")
        if symtable[tokenval].att != 1:
            error("Index register should be X")
        match("REG")
        return True
    return False


def parse():
    global file, filecontent, locctr, pass1or2, bufferindex, lineno, lookahead
    sic()

    if pass1or2 == 2:
        print("\nSTRING\t TOKEN\t ATT")
        for i in symtable:
            if i.token == "ID":
                print(i.string, "\t", i.token, "\t", i.att)
        print(f"\nSIZE\t {totalsize}\t {totalsize:x}")
        # print(filecontent)

def sic():
    header()
    body()
    tail()


def header():
    global lookahead, locctr, defid, pass1or2, startaddress
    lookahead = lexan()
    if pass1or2 == 2:
        output.write(f"H{symtable[tokenval].string}")
    match("ID")
    # defid = False
    match("START")
    if pass1or2 == 2:
        output.write(f" {tokenval:06} {totalsize:06x}\n")
    locctr = startaddress = tokenval
    match("NUM")


def body():
    global lookahead, defid, inst, extend
    extend = False
    defid = False
    if pass1or2 == 2:
        inst = 0
    if lookahead == "ID":
        match("ID")
        rest1()
        body()
    elif lookahead == "f3" or lookahead == "+":
        if pass1or2 == 2:
            inst = 0
        stmt()
        body()
    else:
        return


def stmt():
    global lookahead, locctr, inst, extend
    if is_xe:
        if lookahead == "f1":
            locctr += 1
            if pass1or2 == 2:
                inst = symtable[tokenval].att
                output.write(f"T{locctr-1:06x} 01 {inst:02x}\n".upper())
            match("f1")

        elif lookahead == "f2":
            locctr += 2
            if pass1or2 == 2:
                inst = symtable[tokenval].att << 8
            match("f2")
            if pass1or2 == 2:
                inst += symtable[tokenval].att << 4
            match("REG")
            rest3()
            output.write(f"T{locctr-3:06x} 02 {inst:04x}\n".upper())

        elif lookahead == "f3":
            locctr += 3

            if pass1or2 == 2:
                inst = symtable[tokenval].att << 16
                # some opcode do spcial things
                # if "J" in symtable[tokenval].string:
                #     match("f3")
                #     if lookahead == "@":
                #         # need to do somthing here try to do it
                #         match("@")
                #         l = lookup(symtable[tokenval].string)
                #         inst += symtable[l].att
                #         output.write(f"T{locctr-3:06x} 03 {inst:06x}\n".upper())
                #         match("ID")
                #         index()
                #         return
                #     elif lookahead == "ID":
                #         inst += symtable[tokenval].att
                #         output.write(f"T{locctr-3:06x} 03 {inst:06x}\n".upper())
                #         match("ID")
                #         index()
                #         return
                # else:
                #     output.write(f"T{locctr-3:06x} 03 ".upper())
                output.write(f"T{locctr-3:06x} 03 ".upper())
            match("f3")
            rest4()
        elif lookahead == "+":
            extend = True
            locctr += 4
            match("+")
            if pass1or2 == 2:
                inst = symtable[tokenval].att << 24
                # some opcode do spcial things
                # if "J" in symtable[tokenval].string:
                #     match("f3")
                #     inst += symtable[tokenval].att
                #     output.write(f"T{locctr-3:06x} 04 {inst:08x}\n".upper())
                #     match("ID")
                #     index()
                #     return
                # else:
                #     output.write(f"T{locctr-4:06x} 04 ".upper())
                output.write(f"T{locctr-4:06x} 04 ".upper())
            match("f3")
            rest4()
        else:
            error("Syntax error")
    else:
        locctr += 3
        if pass1or2 == 2:
            inst = symtable[tokenval].att << 16
        match("f3")
        if pass1or2 == 2:
            inst += symtable[tokenval].att
        match("ID")
        if pass1or2 == 2:
            output.write(f"T{locctr-3:06x} 03 {inst:06x}\n".upper())
        index()


def rest1():
    global lookahead
    if lookahead == "f1" or lookahead == "f2" or lookahead == "f3" or lookahead == "+":
        stmt()

    elif (
        lookahead == "WORD"
        or lookahead == "RESW"
        or lookahead == "RESB"
        or lookahead == "BYTE"
    ):
        data()
    else:
        error("Syntax error")


def rest2():
    global lookahead, locctr
    if lookahead == "STRING":
        if pass1or2 == 2:
            inst = symtable[tokenval].att
            output.write(f"T{locctr-1:06x} {int(len(inst)/2):02x} {inst}\n".upper())
        locctr += int(len(symtable[tokenval].att) / 2)
        match("STRING")
    elif lookahead == "HEX":
        if pass1or2 == 2:
            inst = symtable[tokenval].att
            output.write(f"T{locctr-1:06x} {int(len(inst)/2):02x} {inst}\n".upper())
        locctr += int(len(symtable[tokenval].att) / 2)
        match("HEX")
    else:
        error("Syntax error")


def rest3():
    global lookahead, inst
    if lookahead == ",":
        match(",")
        if pass1or2 == 2:
            inst += symtable[tokenval].att
        match("REG")
    else:
        return


def rest4():
    global lookahead, defid, inst, extend
    position = 0
    if lookahead == "ID":
        if pass1or2 == 2:
            position = symtable[tokenval].att
            if position > locctr:
                position -= locctr
            else:
                position -= locctr + 0xF

            if extend:
                inst += (Nbitset + Ibitset) << 24
                inst += Ebit4set
                # inst += Pbit4set
                inst += symtable[tokenval].att
                output.write(f"{inst:08x}\n".upper())
            else:
                inst += (Nbitset + Ibitset) << 16
                inst += Pbit3set
                inst += position
                output.write(f"{inst:06x}\n".upper())

        match("ID")
        index()
    elif lookahead == "#":
        if pass1or2 == 2:
            if extend:
                inst += Ibitset << 24
            else:
                inst += Ibitset << 16
        match("#")
        if lookahead == "ID":
            if pass1or2 == 2:
                position = symtable[tokenval].att
                if position > locctr:
                    position -= locctr
                else:
                    position -= locctr + 0xF
                if extend:
                    # inst += Pbit4set
                    inst += Ebit4set
                    inst += symtable[tokenval].att
                    output.write(f"{inst:08x}\n".upper())
                else:
                    inst += Pbit3set
                    inst += position
                    output.write(f"{inst:06x}\n".upper())
            match("ID")
        elif lookahead == "NUM":
            if pass1or2 == 2:
                inst += tokenval
                if extend:
                    inst += Ebit4set
                    output.write(f"{inst:08x}\n".upper())
                else:
                    output.write(f"{inst:06x}\n".upper())
            match("NUM")
        else:
            error("Syntax error")

        index()
    elif lookahead == "@":
        match("@")
        if pass1or2 == 2:
            if extend:
                inst += Nbitset << 24
                inst += Ebit4set
                # inst += Pbit4set
            else:
                inst += Nbitset << 16
                inst += Pbit3set
        if lookahead == "ID":
            if pass1or2 == 2:
                inst += symtable[tokenval].att
                if extend:
                    output.write(f"{inst:08x}\n".upper())
                else:
                    output.write(f"{inst:06x}\n".upper())
            match("ID")
        elif lookahead == "NUM":
            match("NUM")
        else:
            error("Syntax error")
        index()
    elif lookahead == "NUM":
        if pass1or2 == 2:
            inst += hex(tokenval)
        match("NUM")
        index()
    else:
        error("Syntax error")


def index():
    global lookahead, inst
    if lookahead == ",":
        match(",")
        if pass1or2 == 2:
            if extend:
                inst += Xbit4set
            else:
                inst += Xbit3set
        match("REG")
    else:
        return


def data():
    global lookahead, tokenval, locctr
    if lookahead == "WORD":
        match("WORD")
        if pass1or2 == 2:
            output.write(f"T{locctr-1:06x} {3:02x} {tokenval:06x}\n".upper())
        locctr += 3
        match("NUM")
    elif lookahead == "RESW":
        match("RESW")
        locctr += 3 * tokenval
        match("NUM")
    elif lookahead == "RESB":
        match("RESB")
        locctr += tokenval
        match("NUM")
    elif lookahead == "BYTE":
        match("BYTE")
        rest2()
    else:
        error("Syntax error")


def tail():
    global totalsize, locctr, tokenval, startaddress
    match("END")
    totalsize = locctr - startaddress
    if pass1or2 == 2:
        output.write(f"E{symtable[tokenval].att:06x}")
    match("ID")


def main():
    global file, filecontent, locctr, pass1or2, bufferindex, lineno, is_xe
    mode = file.readline()  # SICXE Check
    if "sicxe" in mode:
        is_xe = True
    init()
    w = file.read()
    filecontent = re.split(r"([\W])", w)
    i = 0
    while True:
        while (
            (filecontent[i] == " ")
            or (filecontent[i] == "")
            or (filecontent[i] == "\t")
        ):
            del filecontent[i]
            if len(filecontent) == i:
                break
        i += 1
        if len(filecontent) <= i:
            break
    # to be sure that the content ends with new line
    if filecontent[len(filecontent) - 1] != "\n":
        filecontent.append("\n")
    for pass1or2 in range(1, 3):
        parse()
        bufferindex = 0
        locctr = 0
        lineno = 1

    file.close()
    output.close()


main()
