#!/usr/bin/env python3
# tools/gen_spaces_direct.py
# Brainfuckを経由せず、Spacesのコードを直接生成します。
# これによりインデントエラーや中間変換のバグを根絶します。

import sys

def main():
    # Spacesの定義
    S = " "      # Space
    F = "\u3000" # Ideographic Space (Fullwidth Space)
    
    # Spacesの命令マップ
    # > : SSS
    # < : SSF
    # + : SFS
    # - : SFF
    # . : FSS
    # , : FSF
    # [ : FFS
    # ] : FFF
    
    cmds = []
    
    def emit(s_instructions):
        """Spacesの命令文字列（例: 'SSS', 'SFS'）を追加"""
        cmds.append(s_instructions)

    # 便利なヘルパー関数（命令単位）
    def right(n=1):  
        for _ in range(n): emit(S+S+S)
    def left(n=1):   
        for _ in range(n): emit(S+S+F)
    def inc(n=1):    
        for _ in range(n): emit(S+F+S)
    def dec(n=1):    
        for _ in range(n): emit(S+F+F)
    def out():       emit(F+S+S)
    def inp():       emit(F+S+F) # 今回は使わないが定義
    def loop_start(): emit(F+F+S)
    def loop_end():   emit(F+F+F)
    
    # ループ内でクリア [-]
    def clear():
        loop_start()
        dec()
        loop_end()

    # 値を出力してクリア (ELF生成用)
    # 以前の emit('>' + '+'*b + '. [-] <') に相当
    def emit_byte(val):
        right()
        clear() # 安全のためクリア
        inc(val)
        out()
        clear()
        left()

    # --- 1. 安全マージン ---
    # Underflow防止のため右へ移動
    right(8)

    # --- 2. ELF Header (64-bit Linux) ---
    # ここが修正ポイント！ p_filesz と p_memsz を大きく確保する。
    # 以前はここが 01 00 ... (1バイト) だったため、実行時にメモリ違反で落ちていた。
    # 0x20000 (131KB) 確保する。
    
    header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0, # e_ident
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00, # e_type, e_machine, e_version
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, # e_entry (0x400078)
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # e_phoff (64 bytes)
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # e_shoff
        0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x38, 0x00, # e_flags, e_ehsize, e_phentsize, e_phnum
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # e_shentsize, e_shnum, e_shstrndx
        # Program Header
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, # p_type (LOAD), p_flags (RWE)
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # p_offset
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, # p_vaddr (0x400000)
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, # p_paddr
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # p_filesz (Fix: 0x20000 bytes)
        0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, # p_memsz  (Fix: 0x20000 bytes)
        0x00, 16, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00    # p_align
    ]
    for b in header:
        emit_byte(b)

    # --- 3. Init Code ---
    # mov r13, 0x408000 (Tape memory start)
    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code:
        emit_byte(b)

    # --- 4. Compiler Logic (Direct Spaces) ---
    # Memory Layout:
    # C0: Input, C1: Copy, C2: FlagS, C3: FlagF, C4: Temp, C5: Acc, C6: MainFlag
    
    def read_valid_bit(weight):
        # Loop while C0 != 0
        clear()
        inc()
        loop_start() # [
        
        inp() # , (Read C0)
        
        loop_start() # [ (EOF check)
        
        # Check 255 (EOF) logic
        right(); clear(); inc(); left() # C1 = 1
        inc() # C0 += 1
        loop_start(); dec(); right(); dec(); left(); loop_end() # If C0!=0 then C0-=1, C1=0
        
        # If C1 is 1 (EOF found)
        right()
        loop_start()
            # Exit All: Clear C6, C1, C0
            right(5); clear(); left(5) # Clear C6
            clear() # Clear C1
            left(); clear() # Clear C0
        loop_end()
        left() # Back to C0
        
        # Clear Flags C2, C3, C4
        right(2); clear(); right(); clear(); right(); clear(); left(4)
        
        # Copy C0 to C1 using C4
        right(); clear(); right(); clear(); right(); clear(); left(3) # Clear dests
        loop_start(); right(); inc(); right(3); inc(); left(4); dec(); loop_end() # Move C0->C1,C4
        right(4); loop_start(); left(4); inc(); right(4); dec(); loop_end() # Move C4->C0
        left(4) # Back to C0
        
        # Check S (32) on C1
        right(); clear(); inc(); left() # C2=1 (Assume S)
        right(); dec(32) # C1 -= 32
        loop_start() # If C1!=0 (Not S)
            clear(); right(); clear(); left() # Clear C1, C2
            
            # Check F (227). Recopy C0 -> C1
            left() # To C0
            loop_start(); right(); inc(); right(3); inc(); left(4); dec(); loop_end() # Copy
            right(4); loop_start(); left(4); inc(); right(4); dec(); loop_end() # Restore
            left() # To C3 (Wait, layout: C0 C1 C2 C3)
            # Layout: C0 C1 C2 C3 C4
            # Currently at C0.
            right(3); clear(); inc(); left(3) # C3=1 (Assume F)
            right(); dec(227) # C1 -= 227
            loop_start() # If C1!=0 (Not F)
                clear(); right(2); clear(); left(2) # Clear C1, C3
            loop_end()
        loop_end()
        
        # Check Flags C2, C3. If set, Clear C0 to Exit Loop
        right(2) # To C2
        loop_start(); left(2); clear(); right(2); dec(); inc(); loop_end() # If C2, Clear C0
        right() # To C3
        loop_start(); left(3); clear(); right(3); dec(); inc(); loop_end() # If C3, Clear C0
        
        left(3) # Back to C0
        
        loop_end() # End Not 255 check
        loop_end() # End Not 0 check
        loop_end() # End Search Loop
        
        # Action Phase
        # If F (C3=1), Add Weight to C6
        right(3)
        loop_start()
             clear()
             left(3); inp(); inp() # Consume 2 chars
             right(6); inc(weight); left(6) # Add weight to C6
             right(3)
        loop_end()
        
        # If S (C2=1), just clear C2
        left(); clear()
        left(2) # Back to C0

    # --- Main Loop ---
    right(6); clear(); inc(); loop_start() # C6=1, Loop
    
    left(); clear() # Clear C5 (Acc)
    left(5) # To C0
    
    read_valid_bit(4)
    right(6); loop_start(); left(6); # Check C6
    read_valid_bit(2)
    right(6); loop_start(); left(6);
    read_valid_bit(1)
    right(6); loop_start(); left(6);
    
    left() # To C5 (Acc)
    
    # Emit Bytes Helper
    def emit_machine_code(bytes_list):
        for b in bytes_list:
            # Use C7 as scratch
            right(2); clear(); inc(b); out(); clear(); left(2)

    # --- Opcode Processing (C5) ---
    
    # Case 0: > (3 bytes)
    right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x49, 0xff, 0xc5])
    clear(); loop_end(); left()
    
    # Case 1: < (3 bytes)
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x49, 0xff, 0xcd])
    clear(); loop_end(); left()

    # Case 2: + (4 bytes)
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x41, 0xfe, 0x45, 0x00])
    clear(); loop_end(); left()

    # Case 3: - (4 bytes)
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x41, 0xfe, 0x4d, 0x00])
    clear(); loop_end(); left()

    # Case 4: . (20 bytes)
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x4c, 0x89, 0xee, 0xba, 0x01, 0x00, 0x00, 0x00, 0x0f, 0x05
    ])
    clear(); loop_end(); left()

    # Case 5: , (Ignored)
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); clear(); loop_end(); left()

    # Case 6: [ (11 bytes, offset 118)
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x84, 0x76, 0x00, 0x00, 0x00])
    clear(); loop_end(); left()
    
    # Case 7: ] (11 bytes, offset -140)
    dec(); right(); clear(); inc(); left(); loop_start(); right(); clear(); left(); clear(); loop_end(); right(); loop_start()
    emit_machine_code([0x41, 0x80, 0x7d, 0x00, 0x00, 0x0f, 0x85, 0x74, 0xff, 0xff, 0xff])
    clear(); loop_end(); left()
    
    right() # To C6
    loop_end(); loop_end(); loop_end() # Close checks
    loop_end() # End Main Loop
    
    # Padding
    right(2); clear(); inc(255); loop_start()
    right(); clear(); inc(255); loop_start()
    right(); out(); left(); dec()
    loop_end(); left(); dec()
    loop_end()
    
    # Output to stdout
    sys.stdout.buffer.write("".join(cmds).encode('utf-8'))

if __name__ == '__main__':
    main()
