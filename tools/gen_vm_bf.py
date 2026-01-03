#!/usr/bin/env python3
import sys

# --- Spaces Dialect ---
S=" "; F="\u3000"
def e(s): sys.stdout.write(s+"\n")
def R(n=1): 
    if n>0: e((S+S+S)*n)
def L(n=1): 
    if n>0: e((S+S+F)*n)
def I(n=1): 
    if n>0: e((S+F+S)*n)
def D(n=1): 
    if n>0: e((S+F+F)*n)
def O(): e(F+S+S)
def N(): e(F+S+F)
def B(): e(F+F+S)
def C(): e(F+F+F)
def Z(): B(); D(); C()

def main():
    # Memory Layout:
    # 99: Initial Accumulator (Data) = 0
    # 100+: Code Segment
    
    # 1. Setup Sentinel/Accumulator at 99
    # We start at 0.
    # Cells 0-98 are 0.
    
    # 2. Read Code into 100+
    R(100)
    N() # Read first char
    B() # While char != 0
    R(1); N() # Read next
    C()
    
    # 3. Reset to Start of Code (100)
    # Scan Left until 0 (which is Cell 99, our Accumulator/Gap)
    L(1)
    B(); L(1); C() 
    # Now at Cell 99 (Value 0)
    R(1) # At Cell 100 (Code Start)
    
    # 4. Execution Loop (Bubble Strategy)
    # Invariant: Current Cell is Instruction. Left Cell (-1) is Data Accumulator.
    
    B() # While Code[IP] != 0
        # --- EXECUTE ---
        # Decode Instruction at Current
        
        # Check + (43)
        D(43)
        R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
        R(1); B(); D(); L(1)
           # Action: Increment Accumulator (Left 1)
           L(1); I(1); R(1)
        C(); L(1)
        I(43) # Restore
        
        # Check - (45)
        D(45)
        R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
        R(1); B(); D(); L(1)
           # Action: Decrement Accumulator (Left 1)
           L(1); D(1); R(1)
        C(); L(1)
        I(45) # Restore

        # Check . (46)
        D(46)
        R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
        R(1); B(); D(); L(1)
           # Action: Output Accumulator (Left 1)
           L(1); O(); R(1)
        C(); L(1)
        I(46) # Restore

        # Check , (44)
        D(44)
        R(1); Z(); I(1); L(1); B(); R(1); D(); L(1); B(); L(1); C(); C()
        R(1); B(); D(); L(1)
           # Action: Input Accumulator (Left 1)
           L(1); N(); R(1)
        C(); L(1)
        I(44) # Restore

        # --- ADVANCE (SWAP & MOVE) ---
        # Current State: [Acc, Instr, Next, Temp]
        # Goal State:    [Instr, Acc, Next, Temp]
        # Then Move Right -> [Instr, Acc, (Head)Next]
        
        # 1. Move Acc (L1) to Temp (R2)
        L(1)
        B(); D(); R(3); I(1); L(3); C()
        R(1)
        
        # 2. Move Instr (Here) to Acc (L1)
        B(); D(); L(1); I(1); R(1); C()
        
        # 3. Move Temp (R2) to Instr (Here)
        R(2)
        B(); D(); L(2); I(1); R(2); C()
        L(2)
        
        # 4. Move Head Right
        R(1)
        # Now Head is at Next. Left is Acc. Invariant maintained.
    C()

if __name__ == "__main__":
    main()
