from __future__ import annotations
from typing import Literal
from dataclasses import dataclass

class CPU:
    """
    les primitives du processeur LOAD, STORE, BLT...
    prennent toutes trois arguments
    pour faciliter le traitement
    les lettres z et t sont des variables vides
    """
    def __init__(self) -> None:
        self.POSX = 0
        self.POSY = 1
        self.ANGL = 2
        self.SHIELD = 3
        self.MEM = {self.POSX: 0, self.POSY: 0, self.ANGL: 0, self.SHIELD: 0}
        self.REG = {}
        self.PC = 1
        self.IR = None
        self.CMD = {}

    def temp_reg(self) -> None:
        return max(self.MEM.keys()) + 1
    
    def STORE(self, M1, X, z):
        self.MEM[M1] = self.REG[X]

    def LOAD(self, R, M, z):
        self.REG[R] = self.MEM[M]

    def LOADI(self, R, v, z):
        self.REG[R] = v

    def ADDI(self, dest, src1, v):
        self.REG[dest] = self.REG[src1] + v

    def BEQ(self, R1, R2, LAB):
        if self.REG[R1] == self.REG[R2]:
            self.PC = LAB

    def BLT(self, R1, R2, LAB):
        if self.REG[R1] < self.REG[R2]:
            self.PC = LAB

    def J(self, LAB,z,t):
        self.PC = LAB

    def register_cmd(self):
        self.CMD['STORE'] = self.STORE
        self.CMD['LOAD'] = self.LOAD
        self.CMD['LOADI'] = self.LOADI
        self.CMD['ADDI'] = self.ADDI
        self.CMD['BEQ'] = self.BEQ
        self.CMD['BLT'] = self.BLT
        self.CMD['J']= self.J

    def fetchdecode(self, code,line):
        x,y,z,t = code[line]
        return lambda:self.CMD[x](y,z,t)

    # à réécrire vu que dans l'ASM je mets juste le op_code ('LOADI')
    def RUN(self, code):
        self.register_cmd()
        while self.PC < len(code):
            self.IR = self.fetchdecode(code,self.PC)
            self.PC += 1
            self.IR()
            print(f"REG: {self.REG}, PC: {self.PC}, POSX: {self.POSX}, POSY: {self.POSY}")
            input("$ hit Enter to proceed")

OP_CODE = Literal['REPEAT', 'GAUCHE', 'DROITE', 'BAS', 'HAUT' 'IFTHENELSE', 'WAIT', 'SHIELD']

class NOOP:
    """the empty ast"""
    pass

@dataclass
class OP:
    op_code: OP_CODE 
    args: tuple[int, list[OP]]

ast = OP('REPEAT', (7,[
    OP('AV', (1, [])), 
    OP('TD',(0, [])),
    OP('AV',(2,[])),
    OP('TG',(0,[])),
    OP('TG',(0,[])),
        ])
        )

class ASM:
    """
    prog in assembly code
   {1: ('LOADI',0,0,),
    2: ('BEQ',0,1,9),
    3: ('ADDI',1,1,-1),
    4: ('J',4,,),
    5: ('NOOP',,,)}
    """

    def __init__(self, c: CPU) -> None:
        self.cpu = c
        self.prog = {}


def compile(source: OP, p: CPU) -> ASM:
    asm = ASM(p)
    TEMP = p.temp_reg() # addresse registre temporaire
    match source:
        case OP(op_code='GAUCHE', args=_):
            asm.prog[1] = ('LOAD', TEMP, p.POSX,0)
            asm.prog[2] = ('ADDI', TEMP, TEMP, -1)
            asm.prog[3] = ('STORE', p.POSX, TEMP,0)
            asm.prog[4] = ('LOADI', p.ANGL, 180)
        case OP(op_code='DROITE', args=_ ):
            asm.prog[1] = ('LOAD', TEMP, p.POSX,0)
            asm.prog[2] = ('ADDI', TEMP, TEMP, 1)
            asm.prog[3] = ('STORE', p.POSX, TEMP,0)
            asm.prog[4] = ('LOADI', p.ANGL, 0)
        case OP(op_code='BAS', args=_):
            asm.prog[1] = ('LOAD', TEMP, p.POSY,0)
            asm.prog[2] = ('ADDI', TEMP, TEMP, 1)
            asm.prog[3] = ('STORE', p.POSY, TEMP,0)
            asm.prog[4] = ('LOADI', p.ANGL, 270)
        case OP(op_code='HAUT', args=_):
            asm.prog[1] = ('LOAD', TEMP, p.POSY,0)
            asm.prog[2] = ('ADDI', TEMP, TEMP, -1)
            asm.prog[3] = ('STORE', p.POSY, TEMP,0)
            asm.prog[4] = ('LOADI', p.ANGL, 90)
        case OP(op_code="WAIT", args=_):
            asm.prog[1] = ('NOOP')
        case OP(op_code="SHIELD", args=(X,_)):
            ...
        case OP(op_code="REPEAT", args=(X,L)):
            # Créé une variable pour le repeat, jump si fin du repeat
            ## Faire une loop pour avoir l'assembleur dans le repeat (UTILISER SEQ(A, B))
            # jump back 
            ...
    return asm

def read_args(code:str)->tuple[str, int]:
    res = [""]
    for _,c in enumerate(code):
        if c == ")":
            return res
        elif c == ",":
            res.append("")
        elif c != " ":
            res[len(res)-1] += c

def lexxer(code:str)->list[OP]:
    """
    Returns the code as a list of instructions, that can get compiled
    """
    prog:list[OP] = []
    temp:str = ""
    repeating:bool = False
    repeat_list:list[list] = []
    for i,c in enumerate(code):
        temp += c
        if temp == "shield(":
            a = read_args(code[i+1:])
            if repeating:
                repeat_list[len(repeat_list)-1].append(OP(op_code='SHIELD', args=(a[0], [])))
            else:
                prog.append(OP(op_code='SHIELD', args=(a[0], [])))
        elif temp in ["gauche()", "droite()", "bas()", "haut()", "wait()"]:
            if repeating:
                repeat_list[len(repeat_list)-1].append(OP(op_code=temp.removesuffix("()").upper(), args=(0, [])))
            else:
                prog.append(OP(op_code=temp.removesuffix("()"), args=(0, [])))
        elif c in ["{",";"]:
            temp = ""
        elif temp == "repeat(":
            a = read_args(code[i+1:])
            repeat_list.append(a)
            repeating = True
        elif c == "}":
            if len(repeat_list) >= 2:
                repeat_list[len(repeat_list)-1].append(OP(op_code="REPEAT", args=(repeat_list[len(repeat_list)-1][0], repeat_list[len(repeat_list)-1][1:])))
            else:
                prog.append(OP(op_code="REPEAT", args=(repeat_list[len(repeat_list)-1][0], repeat_list[len(repeat_list)-1][1:])))
            repeat_list.pop(len(repeat_list)-1)
            repeating = False
            temp = ""
    return prog






"""
A FAIRE:
- Ajouter les instructions assembleurs pour shield et repeat
- Trouver un moyen pour etiquetter chaque instruction assembleur par cmd
- Faire le parser à partir de ce qui a été lexxé
"""