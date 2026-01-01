#!/usr/bin/env python3
# tools/gen_spaces_compiler.py
# Fixes:
# 1. Main Flag overwrite bug (caused premature exit).
# 2. Pointer underflow risks (by verifying offsets).
# 3. Indentation errors (by simplifying structure).

import sys
import argparse

def build_bf(debug=False):
    bf = []
    BF_CHARS = set("><+-.,[]")
    
    def emit(s):
        cleaned = "".join(c for c in s if c in BF_CHARS)
        if cleaned:
            bf.append(cleaned)

    # --- ELF Header ---
    # Output binary structure
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

    # --- MEMORY LAYOUT ---
    # C0: Input Character
    # C1: Check / Copy
    # C2: Flag S
    # C3: Flag F
    # C4: Temp Copy
    # C5: Main Loop Flag (Controls compilation loop)
    # C6: Opcode Accumulator (Where bits are assembled)
    # C7: Output Scratch (For emit_bytes)

    # --- Helper: Read ONE Valid Bit ---
    def read_valid_bit(weight):
        emit('[-]+[')   # Loop C0=1
        emit(',')       # Read C0
        
        # Check EOF 0
        emit('[')
        
        # Check EOF 255
        emit('>[-]+< + [ - >-< ]')
        
        # If C1=1 (EOF), Clear Main Flag (C5) and Exit
        emit('>') # At C1
        emit('[ >>>>[-]<<<< [-]<[-] ]') # Clear C5, Clear C1, Clear C0
        emit('<') # Back to C0
        
        # Clear Flags C2, C3, Temp C4
        emit('>> [-] > [-] > [-] <<<<')
        
        # Copy C0 -> C1 using C4 as temp
        emit('>[-]>[-]>[-]>[-]<<<<') # Clear C1..C4
        emit('[ >+ >>>+ <<<< -] >>>> [- <<<<+>>>> ] <<<<')
        
        # Check S (32) on C1
        emit('>[-]+<')      # C2=1 (Assume S). Back at C0.
        emit('>' + '-'*32)  # To C1. C1 -= 32
        emit('[')           # If C1!=0 (Not S)
            emit('[-] > [-] <') # Clear C1, Clear C2. Back at C1.
            
            # Check F (227). Recopy C0 -> C1
            emit('< [ >+ >>>+ <<<< -] >>>> [- <<<<+>>>> ] <<<<')
            emit('>>> [-]+ <<<') # C3=1 (Assume F). At C0.
            emit('>' + '-'*227)  # To C1. C1 -= 227
            emit('[')       # If C1!=0 (Not F)
                emit('[-] >> [-] <<') # Clear C1, Clear C3. Back at C1.
            emit(']')
        emit(']') # End Not S logic. At C1.
        
        # If Flags C2(S) or C3(F) set, Clear C0 to Exit Loop
        emit('>') # To C2
        emit('[ << [-] >> - + ]') # If C2, Clear C0
        emit('>') # To C3
        emit('[ <<< [-] >>> - + ]') # If C3, Clear C0
        
        emit('<<<') # Back to C0
        
        emit(']') # End Not 255
        emit(']') # End Not 0
        emit(']') # End Search Loop
        
        # --- ACTION ---
        # If F (C3=1), Add Weight to Acc (C6)
        emit('>>>') # To C3
        emit('[')
        emit('[-] <<< ,,') # Clear C3, Consume 2 bytes at C0
        emit('>>>>>>' + '+' * weight + '<<<<<<') # Add to C6
        emit('>>>') # Back to C3 (now 0)
        emit(']')
        
        # If S (C2=1)
        emit('<[-]') # Clear C2
        
        emit('<<') # Back to C0

    # --- MAIN LOOP ---
    emit('>>>>>') # To C5 (Main Flag)
    emit('[-]+')  # Set Main Flag = 1
    emit('[')

    emit('>[-]<') # Clear C6 (Acc)
    emit('<<<<<') # To C0

    read_valid_bit(4)
    emit('>>>>>[<<<<<') # Check C5 (Main Flag)
    read_valid_bit(2)
    emit('>>>>>[<<<<<')
    read_valid_bit(1)
    emit('>>>>>[<<<<<')

    emit('>>>>>>') # To C6 (Opcode Acc)

    def emit_bytes(bs):
        for b in bs:
            # Use C7 as scratch (>)
            emit('>' + '+' * b + '.[-]<')

    # Case 0: > (3 bytes)
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x49, 0xff, 0xc5])
    emit('[-]]<')

    # Case 1: < (3 bytes)
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x49, 0xff, 0xcd])
    emit('[-]]<')

    # Case 2: + (4 bytes)
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x41, 0xfe, 0x45, 0x00])
    emit('[-]]<')

    # Case 3: - (4 bytes)
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x41, 0xfe, 0x4d, 0x00])
    emit('[-]]<')

    # Case 4: . (20 bytes)
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05
    ])
    emit('[-]]<')

    # Case 5: , (Input not implemented, strict loop)
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[-]]<')

    # Case 6: [ (11 bytes)
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    emit('[-]]<')

    # Case 7: ] (11 bytes)
    emit('-')
    emit('>[-]+<[>[-]<[-]]>[')
    emit_bytes([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    emit('[-]]<')

    emit('<') # To C5 (Main Flag)
    emit(']]]') # Close checks
    emit(']')   # End Main Loop

    # Padding to 64KB
    emit('>>[-]' + '+' * 255 + '[>[-]' + '+' * 255 + '[>.<-]<-]')
    emit('>>[-]' + '+' * 255 + '[>[-]' + '+' * 255 + '[>.<-]<-]')

    full_bf = "".join(bf)
    if debug:
        print("=== DEBUG: Generated Brainfuck ===", file=sys.stderr)
        print(full_bf[:200] + "...", file=sys.stderr)
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
