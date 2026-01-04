#!/usr/bin/env python3
import sys

S = " "
F = "\u3000"

def e(s):
    sys.stdout.write(s + "\n")

def R(n=1):
    if n > 0: e((S + S + S) * n)

def L(n=1):
    if n > 0: e((S + S + F) * n)

def I(n=1):
    if n > 0: e((S + F + S) * n)

def D(n=1):
    if n > 0: e((S + F + F) * n)

def O():
    e(F + S + S)

def N():
    e(F + S + F)

def B():
    e(F + F + S)

def C():
    e(F + F + F)

def Z():
    B()
    D()
    C()

def DEBUG(char_code):
    R(1)
    Z()
    I(char_code)
    O()
    Z()
    L(1)

def main():
    # Diagnostic: Start 'S'
    DEBUG(83)
    
    # 1. Setup Sentinel (255) at 0
    Z()
    I(255)

    # 2. Read Code into 100+
    R(100)
    N()
    B()
    R(1)
    N()
    C()
    
    # Diagnostic: Read Done 'R'
    L(100)
    DEBUG(82)
    R(100)
    
    # 3. Reset to Start of Code (100)
    L(1)
    B()
    L(1)
    C()
    R(1)
    
    # 4. Execution Loop
    # Diagnostic: Loop Start 'L'
    L(100)
    DEBUG(76)
    R(100)
    
    B()
    # Check + (43)
    D(43)
    R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1); B(); D(); L(1)
    # Action +
    L(1); I(1); R(1)
    C(); L(1); I(43)
    
    # Check - (45)
    D(45)
    R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1); B(); D(); L(1)
    # Action -
    L(1); D(1); R(1)
    C(); L(1); I(45)
    
    # Check . (46)
    D(46)
    R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1); B(); D(); L(1)
    # Action .
    L(1); O(); R(1)
    C(); L(1); I(46)
    
    # Check , (44)
    D(44)
    R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
    R(1); B(); D(); L(1)
    # Action ,
    L(1); N(); R(1)
    C(); L(1); I(44)
    
    # Advance
    L(1)
    B()
    D()
    R(2)
    I(1)
    L(2)
    C()
    R(1)
    B()
    D()
    L(1)
    I(1)
    R(1)
    C()
    R(1)
    B()
    D()
    L(1)
    I(1)
    R(1)
    C()
    L(1)
    R(1)
    C()
    
    # Diagnostic: End 'E'
    L(100)
    DEBUG(69)
    R(100)

if __name__ == "__main__":
    main()
