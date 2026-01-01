#!/usr/bin/env python3
# tools/gen_spaces_compiler.py
# 修正版：ポインタ移動量を厳密に修正 (Underflow解消)

import sys
import argparse

def build_bf(debug=False):
    bf = []
    BF_CHARS = set("><+-.,[]")
    def emit(s: str):
        cleaned = "".join(ch for ch in s if ch in BF_CHARS)
        if cleaned:
            bf.append(cleaned)

    # --- ELF Header ---
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 16, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    for b in header:
        if b: emit('+' * b + '.[-]')
        else: emit('.[-]')

    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code:
        if b: emit('+' * b + '.[-]')
        else: emit('.[-]')

    # --- Helper: Read ONE Valid Bit ---
    # Layout: C0(In), C1(Check), C2(FlagS), C3(FlagF), C4(Temp)
    # Acc is at C5
    def read_valid_bit(weight: int):
        emit('[-]+[')   # Loop C0=1
        emit(',')       # Read C0
        
        # Check EOF 0
        emit('[')
        
        # Check EOF 255 (or -1): If 255, C0+1=0, loop skips.
        # Logic: C1=1. C0+=1. If C0!=0: C0-=1, C1=0.
        emit('>[-]+< + [ - >-< ]')
        
        # If C1=1 (EOF), Clear Main Flag (C6) and Exit
        emit('>') # C1
        emit('[ >>>>>[-]<<<<< [-]<[-] ]') 
        emit('<') # Back to C0
        
        # Clear Flags C2, C3
        emit('>> [-] > [-] <<<')
        
        # Copy C0 -> C1 using C4 as temp
        # Layout: C0, C1, C2, C3, C4
        # Clear C1 and C4 first
        emit('>[-]>[-]>[-]>[-]<<<<')
        # Copy
        emit('[ >+ >>>+ <<<< -] >>>> [- <<<<+>>>> ] <<<<')
        
        # Check S (32) on C1
        emit('>[-]+<')      # C2=1 (Assume S). Back at C0.
        emit('>' + '-'*32)  # To C1. C1 -= 32
        emit('[')           # If C1!=0 (Not S)
            emit('[-] > [-] <') # Clear C1, Clear C2. Back at C1.
            
            # Check F (227). Recopy C0 -> C1
            # C0 is at offset -1 from C1.
            # Copy C0(L-1) -> C1(L0) using C4(L3)
            emit('< [ >+ >>>+ <<<< -] >>>> [- <<<<+>>>> ] <<<<')
            emit('>>> [-]+ <<<') # C3=1 (Assume F). At C0.
            emit('>' + '-'*227)  # To C1. C1 -= 227
            emit('[')       # If C1!=0 (Not F)
                emit('[-] >> [-] <<') # Clear C1, Clear C3. Back at C1.
            emit(']')
        emit(']') # End Not S logic. At C1.
        
        # Flags C2(S) and C3(F) are set.
        # If either is set, we must Clear C0 to Exit Search Loop.
        
        # Check C2 (S Found)
        emit('>') # To C2 (From C1) -- FIXED (Was >>)
        emit('[ << [-] >> - + ]') # If C2, Clear C0 (<<), Keep C2.
        
        # Check C3 (F Found)
        emit('>') # To C3 (From C2) -- FIXED (Was >)
        emit('[ <<< [-] >>> - + ]') # If C3, Clear C0 (<<<), Keep C3.
        
        emit('<<<') # Back to C0 (From C3)
        
        emit(']') # End Not 255
        emit(']') # End Not 0
        emit(']') # End Search Loop
        
        # --- ACTION ---
        # If F (C3=1)
        emit('>>>') # To C3 (From C0)
        emit('[')
        # FIXED: From C3 to C0 is <<<, not <<<<.
        emit('[-] <<< ,,') # Clear C3, Go to C0, Consume 2 bytes
        emit('>>>>>' + '+' * weight + '<<<<<') # Add to C5
        emit('>>>') # Back to C3 (now 0)
        emit(']')
        
        # If S (C2=1)
        emit('<[-]') # To C2. Clear C2.
        
        emit('<<') # Back to C0

    # --- MAIN LOOP ---
    emit('>>>>>>') # To C6
    emit('[-]+')   # C6 = 1
    emit('[')

    emit('<[-]')   # Clear C5
    emit('<<<<<')  # To C0

    read_valid_bit(4)
    emit('>>>>>>[<<<<<<') # Check C6
    read_valid_bit(2)
    emit('>>>>>>[<<<<<<')
    read_valid_bit(1)
    emit('>>>>>>[<<<<<<')

    emit('>>>>>') # To C5

    def emit_bytes(bs):
        for b in bs:
            if not (0 <= b <= 0xFF):
                raise ValueError(f"byte value out of range: {b}")
            emit('>' + '+' * b + '.[-]<')

    # Case 0: >
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x49, 0xff, 0xc5])
    emit('[-]]<')

    # Case 1: <
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x49, 0xff, 0xcd])
    emit('[-]]<')

    # Case 2: +
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x41, 0xfe, 0x45, 0x00])
    emit('[-]]<')

    # Case 3: -
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x41, 0xfe, 0x4d, 0x00])
    emit('[-]]<')

    # Case 4: .
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05
    ])
    emit('[-]]<')

    # Case 5: ,
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[-]]<')

    # Case 6: [
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    emit('[-]]<')

    # Case 7: ]
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    emit('[-]]<')

    emit('>') # To C6
    emit(']]]') # Close checks
    emit(']')   # End Main Loop

    # Padding
    emit('>>[-]' + '+' * 255 + '[>[-]' + '+' * 255 + '[>.<-]<-]')
    emit('>>[-]' + '+' * 255 + '[>[-]' + '+' * 255 + '[>.<-]<-]')

    full_bf = "".join(bf)
    if debug:
        print("=== DEBUG: Generated Brainfuck (first 400 chars) ===", file=sys.stderr)
        print(full_bf[:400], file=sys.stderr)
        print("=== DEBUG END ===", file=sys.stderr)
    return full_bf

def bf_to_spaces(bf):
    S, F = " ", "\u3000"
    mapping = {
        '>': S*3, '<': S*2+F, '+': S+F+S, '-': S+F+F,
        '.': F+S+S, ',': F+S+F, '[': F*2+S, ']': F*3
    }
    return "".join(mapping.get(c, '') for c in bf)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--debug', action='store_true')
    args = p.parse_args()

    full_bf = build_bf(debug=args.debug)
    out = bf_to_spaces(full_bf)
    sys.stdout.buffer.write(out.encode('utf-8'))

if __name__ == '__main__':
    main()
