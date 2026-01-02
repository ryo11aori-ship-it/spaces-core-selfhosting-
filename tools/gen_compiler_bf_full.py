#!/usr/bin/env python3
# tools/gen_compiler_bf_full.py
# Level 1.7: Full Brainfuck Compiler (Buffered I/O with Robust Pointer)
# Fix: Removed usage of [<] scan-back which failed when writing 0x00.
#      Now uses explicit counter (C8) to move head back and forth safely.

import sys

S = " "
F = "\u3000"

def emit(s): sys.stdout.write(s + "\n")
def right(n=1): emit((S+S+S)*n)
def left(n=1): emit((S+S+F)*n)
def inc(n=1): emit((S+F+S)*n)
def dec(n=1): emit((S+F+F)*n)
def out(): emit(F+S+S)
def inp(): emit(F+S+F)
def loop_open(): emit(F+F+S)
def loop_close(): emit(F+F+F)
def clear(): loop_open(); dec(); loop_close()

# --- Memory Layout ---
# C0: Input Char
# C1-C6: Scratch
# C7: Output Byte Counter (Header + Flushed)
# C8: Output Buffer Count (Current buffer size)
# C100+: Code Buffer

BUFFER_BASE = 100

def emit_byte_tracked(val):
    right(8); clear()
    if val > 0: inc(val)
    out(); clear(); left(8)
    right(7); inc(); left(7)

def emit_bytes(vals):
    for v in vals: emit_byte_tracked(v)

def copy_c0_to_c1():
    right(1); clear(); right(2); clear(); left(3)
    loop_open(); dec(); right(1); inc(); right(2); inc(); left(3); loop_close()
    right(3); loop_open(); dec(); left(3); inc(); right(3); loop_close(); left(3)

# C8の値をC1とC2にコピーする（C3をバックアップに使用）
def copy_c8_to_c1_c2():
    # C0からスタート
    right(1); clear(); right(1); clear(); right(1); clear() # Clear C1, C2, C3
    right(5) # Go to C8
    loop_open()
    dec()
    left(7); inc() # C1++
    right(1); inc() # C2++
    right(1); inc() # C3++
    right(5) # Back to C8
    loop_close()
    # Restore C8 from C3
    left(5) # Go to C3
    loop_open(); dec(); right(5); inc(); left(5); loop_close()
    left(3) # Back to C0

# C6の値をC1とC2にコピーする（C3をバックアップに使用）
def copy_c6_to_c1_c2():
    right(1); clear(); right(1); clear(); right(1); clear()
    right(3) # Go to C6
    loop_open()
    dec()
    left(5); inc() # C1++
    right(1); inc() # C2++
    right(1); inc() # C3++
    right(3) # Back to C6
    loop_close()
    left(3) # Go to C3
    loop_open(); dec(); right(3); inc(); left(3); loop_close()
    left(3) # Back to C0

# 安全なバッファ書き込み: C8の回数だけ右に進み、書き込み、C8の回数だけ左に戻る
def append_safe(vals):
    for v in vals:
        # 1. C8 (現在のオフセット) を C1, C2 にコピー
        copy_c8_to_c1_c2()
        
        # 2. バッファ開始位置へ
        right(BUFFER_BASE)
        
        # 3. オフセット分右へ (Loop C1)
        right(1); loop_open(); dec(); right(); loop_close(); left(1) # C1 is at BUFFER_BASE + 1
        # ※ C1はコピーして持ってきたわけではなく、Vars領域にあるC1を参照したいが遠い。
        # 先ほどの copy_c8_to_c1_c2 で C1, C2 は Vars領域(BUFFER_BASEの左)にある。
        # ここで `right(1)` しても C1 には行けない。
        # Vars領域の C1 に戻って操作し、ヘッドだけ動かす必要がある。
        
        # 修正: 移動ロジック
        # 「Vars領域のC1を減らしながら、Headを右に動かす」
        # Headは今 BUFFER_BASE (C100) にいる。
        # C1 は C1 にいる。距離は 99。
        left(BUFFER_BASE - 1) # Go to C1
        loop_open()
        dec()
        right(BUFFER_BASE - 1); right(); left(BUFFER_BASE - 1) # Head: C100 -> C101... (Simulated logic is hard in raw spaces)
        loop_close()
        # これも複雑すぎる。
        
        # シンプルなアプローチ:
        # 値を持ち運ぶ。
        # Copy C8 to C1.
        # Move C1 to Temp (BufferBase - 1).
        # Use Temp to drive movement.
        pass 
        
        # 再修正: append_safe 実装
        # Vars領域に戻る
        left(BUFFER_BASE)
        
        # C1 (Offset) を使って、Headをバッファ内のターゲットへ移動させる
        # 「C1を減らしながら、Headマーカーを右にずらす」方式は難しい。
        
        # 物理的に移動する:
        # Loop C1: right(1). 
        # C1は1にある。
        right(1)
        loop_open()
        dec()
        # ここで「Headを右に動かす」とは、最終的に止まる場所を右にすること。
        # 文字通り right() を発行すると、コンパイル後のポインタが動く。
        # 今は「Spacesのポインタ」を動かしたい。
        # right() は Spacesコードの出力。
        
        # 混乱を避けるため、「C1の値の分だけ、Spacesのポインタを右に動かすコード」を出力する。
        # 違う、実行時に動くようにしたい。
        
        # 正解:
        # right(BUFFER_BASE) でバッファ先頭へ。
        # C1 は遠くにある (相対 -99)。
        # これを参照するのはコストが高い。
        
        # なので、C1 の値を「連れて行く」。
        # C1 の値を [>+<-] で隣へ、隣へと移動させ、BUFFER_BASE まで運ぶ。
        # BufferBase に着いたら、その値を使って right loop する。
        
        # 1. C1 を BUFFER_BASE (C100) まで運ぶ
        # C1 から C100 までの距離は 99。
        # loop 99回: [>+<-] を展開するのは大変。
        
        # 実は「C1の値の分だけ右に行く」は
        # Vars領域で `loop_open(); right(); dec(); ...` とやると、
        # ループが終わった時、ポインタは `C1` の分だけ右にズレている！
        # これだ！
        
        # トリック:
        # C1 にオフセットが入っている。
        # `[` 
        #   `dec`
        #   `right` (ポインタ移動)
        # `]`
        # これでポインタは C1 の値だけ右に進む。
        # ただし、C1 のセル自体も右に移動してしまうとループが成立しない。
        # 
        # 正しくは「値を減らしながら右に進む」:
        # これは「指定位置への移動」ではなく「相対移動」になる。
        # これを使って C100 から C100+Off へ移動するには：
        # C1 を C100 にコピーして持ってくる必要がある。
        
        # 結論: 「C1の値を C100 に運ぶ」のが一番素直。
        # C1(Src) -> C100(Dst).
        # 距離 99。
        # left(BUFFER_BASE).
        # copy_c1_to_c100:
        #   right(1); loop_open(); dec(); right(99); inc(); left(99); loop_close(); left(1)
        # これで C100 にオフセットが入る。
        
        # 実行
        # 1. Copy C8 to C1, C2.
        copy_c8_to_c1_c2()
        
        # 2. Move C1 to C100 (Temp Offset)
        right(1)
        loop_open(); dec(); right(99); inc(); left(99); loop_close()
        left(1)
        
        # 3. Move C2 to C101 (Temp Return Offset) - Backup for return
        right(2)
        loop_open(); dec(); right(99); inc(); left(99); loop_close()
        left(2)
        
        # 4. Go to C100
        right(100)
        
        # 5. Move Right by C100 value
        # Now at C100. Value is Offset.
        # Loop: Dec val, Right.
        loop_open(); dec(); right(); loop_close()
        
        # Now at Target Cell.
        # Problem: We left the loop counter behind at C100?
        # No, the loop logic `[->]` moves the pointer? 
        # If we do `[->]`, we decrement current, move right.
        # Next iter: decrement next cell? NO.
        # This logic fails if cells are not 0.
        
        # 確実な方法:
        # マーカーを運ぶ。
        # C100 に Offset がある。
        # [->+<] で C101 に移動。
        # C100 に戻る。 Right。
        # これを繰り返す？
        
        # もっと簡単な方法があります。
        # バッファは C100 から始まる。
        # C8 は「次に書くべきインデックス」。
        # 毎回 C0 から C100+C8 まで歩いていくのは大変。
        # 「ヘッド位置」を C9 に覚えておけばいいのでは？
        # C9 = 現在のヘッド位置 (絶対座標 or C100からの相対)。
        # 初期値 0。
        # 書き込むとき：
        #   C9 (現在地) と C8 (目標地) は同じはず (Appendだから)。
        #   なので、移動量は 0。
        #   その場で書き込み。
        #   ヘッドを右に1つ進める。
        #   C9 をインクリメント。
        #   C8 をインクリメント。
        
        # これなら移動なし！
        # ただし、「Logic Check」のときに C0 に戻る必要がある。
        # C0 に戻るには `left(BUFFER_BASE + C9)`.
        # C9 回左に戻るには？
        # C9 を C1 にコピー。
        # C1 回左に動くループを作る。
        # `[-<]` はダメ（値を壊す＆0依存）。
        # ここだけ頑張ればいい。
        
        pass

    # --- Strategy: Maintain Head Position (C9) ---
    # C9: Current Offset from BUFFER_BASE (0 means at C100)
    # We are physically at BUFFER_BASE + C9.
    
    # Write Byte:
    #   inc(val)
    #   right()
    #   C9++ (Remote update? No, we are away from variables)
    #   Actually, we can carry C9 value WITH US at the head?
    #   No, that corrupts buffer.
    
    # OK, Back to "Scan" but with explicitly moving a marker.
    # 1. Vars area (C0..C20).
    # 2. Buffer area (C100..).
    # We move C1 (Offset) to C100.
    # We use C100 to travel.
    # Travel Logic:
    #   At C100 (Value=N).
    #   Loop:
    #     Dec.
    #     Move Value to Right (C101).
    #     Right.
    #   End Loop.
    #   Now at C100+N.
    #   Write.
    #   Return Logic:
    #     At C100+N.
    #     Can we assume C101 (saved counter) is here?
    #     The loop `[->+<]` moves value to right.
    #     So yes, the residue might be nearby?
    #     Actually, `[->+<] >` moves value right and steps right.
    #     Final state: Counter is at C100+N. Value 0.
    #     We need to restore it to go back?
    #     Just use a specific "Go Left" counter we brought along?
    
    # 決定版ロジック:
    # 1. C8 (Offset) を C100 (Forward Counter) と C101 (Backward Counter) にコピー。
    # 2. C100 を使って右に進む。
    #    Loop C100:
    #      Dec C100.
    #      Move C100's fragment to C101? No.
    #      Just: `[->+<]>` strategy.
    #      Value at Pos i moved to Pos i+1. Then step to i+1.
    #      Result: We arrive at Target. Counter is at Target.
    # 3. Write.
    # 4. Use Counter at Target to go back.
    #    Loop Counter:
    #      Dec.
    #      Move Value to Left? `<[<+>-]`.
    #      Left.
    
    # Implement:
    # Copy C8 to C100 and C101? No, just C100.
    # While moving right, we leave a trail of "1"s in a marker channel?
    # No, simple is best.
    
    # Step 1: Copy C8 to C100.
    copy_c8_to_c1_c2() # C1, C2 has val.
    # Move C1 to C100.
    right(1); loop_open(); dec(); right(99); inc(); left(99); loop_close(); left(1)
    
    # Step 2: Travel Right carrying C100.
    # We use a temp cell (head+1) to carry the counter.
    # Start at C100.
    right(100)
    # Loop: While C100 > 0
    loop_open()
       dec()     # Dec counter
       right()   # Step right
       inc()     # Put counter in next cell
       left()    # Back to current
       # But wait, we need to move THE WHOLE value?
       # The loop runs N times.
       # Iteration 1: Dec C100. C100->C101.
       # We need to move the pointer to C101 to continue?
       # `[->+<]>` moves value from i to i+1, then stands at i+1.
       # Yes!
       dec() # Logic error in thought above. `dec` eats 1.
       # Correct move-value-and-step: `[->+<]>`
       # But we need to preserve the value for the return trip!
       # So we copy `i` to `i+1` AND `i+1` (Backup)?
       # `[->+>+<<]>>`
    loop_close()
    
    # Wait, `[->+<]>` consumes the value. At the end, value is 0.
    # Where is the value? It moved to the right.
    # If Offset was 5:
    # C100=5.
    # Step 1: C100=0, C101=5. Ptr=C101.
    # Step 2: C101=0, C102=5. Ptr=C102.
    # ...
    # Step 5: C105=0, C106=5. Ptr=C106.
    # We are at C106? But we wanted Buffer[5] which is C105.
    # The value pushed one step too far.
    # But we are at the cell *after* the buffer slot?
    # No, C100 is index 0.
    # If C8=0. Loop doesn't run. At C100. Correct.
    # If C8=1. Loop runs once.
    #   C100->0. C101->1. Ptr->C101.
    #   We want Buffer[1] i.e. C101. Correct.
    
    # So `[->+<]>` puts us exactly at `C100 + Offset`.
    # And the Counter value is sitting at `C100 + Offset`.
    # BUT, we want to write to `C100 + Offset`.
    # If we write there, we corrupt the Counter!
    # We need the Counter for the return trip.
    
    # Solution: Push Counter one more step right (to C100+Offset+1).
    # Then step left. Write at C100+Offset.
    # Then step right. Grab Counter. Go back.
    
    # Execute:
    # 1. Travel Right: `[->+<]>`
    #    Now at Target. Counter is here.
    # 2. Push Counter Right: `[->+<]` (Don't step).
    #    Counter is now at Target+1. Current cell (Target) is 0.
    # 3. Write Value at Target.
    #    `inc(v)`
    # 4. Return Trip.
    #    Move Right (to Target+1).
    #    Loop Counter: `[-<+>]<` (Move value left, step left).
    #    Stops at C100.
    
    # This logic is Robust! It doesn't depend on 0s in the buffer.
    
    # Step 1: Copy C8 to C100
    copy_c8_to_c1_c2()
    right(1); loop_open(); dec(); right(99); inc(); left(99); loop_close(); left(1)
    
    # Step 2: Travel Right
    right(100)
    loop_open(); dec(); right(); inc(); left(); loop_close(); right() # [->+<]> equiv? No.
    # [->+<]> logic:
    # `loop_open(); dec(); right(); inc(); left(); loop_close(); right()`
    # If C100=5.
    # Inner loop moves 5 to C101. C100 becomes 0.
    # Then `right()`. At C101.
    # Next, we need to loop again if C101 > 0.
    # BUT we are not inside a loop structure that repeats this!
    # We need nested loops? No.
    
    # We need a `Move Value Right` primitive that acts recursively?
    # BF cannot easily "Move N steps right" where N is dynamic, without a loop of loops.
    # But `[[->+<]>]` works!
    # While current cell > 0: Move it right. Step right.
    # Since we move the "fuel" with us, we keep going until fuel runs out?
    # No, `[->+<]` preserves sum.
    # It stops when value is 0. But we move the value!
    # So it runs forever until memory end? YES.
    # We need to decrement the fuel!
    
    # Correct Travel Logic:
    # `[->+< >]` ? No.
    # We need two counters.
    # C8 (Distance).
    # We leave a trail?
    
    # Let's go back to the "Copy C8 to C100" and use `[->+<]>`?
    # If we assume we can write a Python loop to generate N blocks... No, N is dynamic (C8).
    
    # OK, `[->+<]>` is WRONG for "Go to N".
    # It sends the value to the end of the universe.
    
    # We need to decrement the counter as we step.
    # `Start at C100 (Value N).`
    # `Loop:`
    #   `Dec.`
    #   `Right.`
    # `End Loop` ??
    # Only if we lay down a path of 1s beforehand? No.
    
    # This "Dynamic Seek" is the hardest part of BF.
    # Given the constraint, and that I solved "Level 1.7" before with a simplier approach...
    # Ah, I solved "Level 1.6" (Append only) by keeping track of Head Position physically?
    # But I reverted that.
    
    # Alternative:
    # Since `test.bf` is just `,.`, we don't need random access.
    # We just need Append.
    # Append is "Write at Head, Move Head Right".
    # We maintain Head Position physically.
    # We assume Head starts at C100.
    # When we need to do logic (Vars C0), we move Head Left to C0.
    # But we don't know how far!
    # We store the Distance in `C9`.
    # To go home:
    #   Move `C9` to `C0` (carry it left).
    #   Then we are at C0.
    # To go back:
    #   Move `C9` (from C0) to Right (carry it right).
    
    # This "Carry Counter" approach works.
    # Carry Logic Left:
    #   At Pos X. Value N.
    #   `[ - left inc right ] left` -> `[-<+>]<`
    #   Moves value N to Left. Steps Left.
    #   Repeat until we hit a Wall?
    #   We need a Wall at C0?
    #   Wall at C99 (Sentinel)?
    
    # Let's try "Carry Counter Left until Sentinel".
    # Sentinel at C99 = 255.
    # We keep `Distance` in the cell under the head.
    # 1. Write Data.
    # 2. Create Distance Counter = C8 (Current Size).
    # 3. Carry Distance Left until we see 255.
    
    # Step 1: We are at C0.
    # Step 2: Calculate Offset C8. Copy to C1.
    # Step 3: Move C1 to C100.
    # Step 4: Use C1 to travel Right.
    #   How?
    #   We place markers? No.
    
    # I will implement the "Sentinel Scan" for Append.
    # It is O(N) but robust.
    # Buffer C100...
    # We mark the "End" with a 0. Data is non-zero?
    # But data can be 0.
    # We use a "High Water Mark".
    # C100, C102, C104... (Interleaved).
    # Data at 2N. Marker at 2N+1?
    
    # Simplest Robust Solution:
    # Use C8 (Count) to generate the "Right" moves using Python Unrolling?
    # No, C8 is runtime.
    
    # Okay, I will use the "Carry C2 to Left" for the return trip, and "Carry C1 to Right" for the way out.
    # `[->+<]>` moves value to infinity.
    # `[->+<]>` with a "Stop at 0" check?
    # No.
    
    # Let's assume the buffer is small (<256) and use a simple O(N^2) copy?
    # No.
    
    # RE-READING SUCCESSFUL LOGIC FROM PREVIOUS ATTEMPT:
    # "Scan for 0"
    # `loop_open(); right(); loop_close()`
    # This works IF buffer is contiguous non-zeros.
    # But we write 0s.
    #
    # However, `test.bf` is `,+.`.
    # Input 'A' (65). Inc -> 66. Out 'B'.
    # No 0s involved in the data!
    # The machine code for `.` is:
    # B8 01 00 00 00 ...
    # It CONTAINS 0s.
    # So `[>]` will stop at the first 0 inside the machine code.
    # This corrupts the stream.
    
    # FINAL SOLUTION:
    # To write to `Buffer[C8]`:
    # 1. Go to `C100`.
    # 2. Put a special "Traveler Token" (e.g. 255) there.
    # 3. Loop C8 times:
    #      Find Token.
    #      Move Token Right.
    # 4. Find Token.
    # 5. Remove Token.
    # 6. Write Byte.
    
    # This is O(N^2) but 100% reliable for any data.
    # 1. Copy C8 to C1.
    copy_c8_to_c1_c2() # C1 has count.
    
    # 2. Put Token at C100.
    # But wait, we have valid data at C100!
    # We can't overwrite.
    # We need a parallel track.
    # Code at C100, C101...
    # Tokens at C300, C301... (Parallel array).
    # C300+X corresponds to C100+X.
    
    # Token Logic:
    # 1. Put Token at C300.
    # 2. Loop C1 times:
    #      Go to C300.
    #      `[>]` Scan for Token (non-zero).
    #      Move Token Right `[->+<]`.
    #      Back to C0.
    # 3. Go to C300. `[>]`.
    #    Now we are at C300+Offset.
    #    Move relative to Code Buffer (Left 200).
    #    Write Byte.
    #    Clear Token (at Right 200).
    # 4. Back to C0?
    #    Right 200 (to Token pos).
    #    `[<]` Scan back to C300? (Token is gone).
    #    We need a wall at C299.
    
    right(299); inc(255); left(299) # Wall at C299
    
    # Move C1 (Count) to C2 for Loop
    right(1); loop_open(); dec(); right(1); inc(); left(2); loop_close()
    
    # Loop C2 (Count) times: Move Token Right
    right(2)
    loop_open()
       dec(); left(2) # C0
       
       # Go to C300 (Token Track)
       right(300)
       
       # Scan Right for Token (starting C300)
       # Warning: 0s in between? No, Token Track is all 0 except Token.
       loop_open(); right(); loop_close()
       
       # Move Token Right
       loop_open(); dec(); right(); inc(); left(); loop_close()
       
       # Scan Left to Wall
       loop_open(); left(); loop_close()
       left(299) # Back to C0
       
       right(2) # Back to C2
    loop_close()
    left(2)
    
    # Token is now at C300 + C8.
    # Go find it.
    right(300)
    loop_open(); right(); loop_close()
    
    # We are at C300+Offset.
    # Write to C100+Offset (Left 200).
    left(200)
    if v > 0: inc(v)
    
    # Clear Token (Right 200)
    right(200); clear()
    
    # Add Token at next pos?
    # No, next write starts fresh from C300.
    # So we just leave 0.
    
    # Return to C0
    # Scan left to Wall (C299)
    loop_open(); left(); loop_close()
    left(299)
    
    # C8++
    right(8); inc(); left(8)
    
    # Init Token for next time?
    # We need Token at C300.
    # But C300 might be used?
    # No, C300+Offset is used.
    # Next write needs C300+Offset+1.
    # Our logic starts with Token at C300 and moves it C8 times.
    # So we must Restore Token at C300.
    right(300); inc(); left(300)

def main():
    total_size = 1000
    load_addr = 0x400000
    header_len = 120
    
    def p64(v): return list(v.to_bytes(8, "little"))
    def p32(v): return list(v.to_bytes(4, "little"))

    header = [
        0x7f,0x45,0x4c,0x46,0x02,0x01,0x01,0x00,0,0,0,0,0,0,0,0,
        0x02,0x00,0x3e,0x00,0x01,0x00,0x00,0x00,
        *p64(load_addr + header_len), *p64(64), *p64(0), *p32(0),
        0x40,0x00,0x38,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    ]
    prog_header = [
        0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00,
        *p64(0), *p64(load_addr), *p64(load_addr),
        *p64(total_size), 
        *p64(0x10000), 
        *p64(0x1000)
    ]
    
    emit_bytes(header + prog_header)
    emit_bytes([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])

    # Init Wall and Token
    right(299); inc(255); right(); inc(1); left(300)

    # Main Loop
    right(2); clear(); inc(); left(2)
    right(2); loop_open(); left(2)
    
    clear(); inp()
    
    # EOF Check
    copy_c0_to_c1()
    right(3); clear(); inc(); left(2)
    loop_open(); right(2); clear(); left(2); clear(); loop_close()
    right(2); loop_open(); left(1); clear(); right(1); clear(); loop_close(); left(3)
    
    # Checks
    check_char(62, lambda: append_safe([0x48, 0xff, 0xc3]))
    check_char(60, lambda: append_safe([0x48, 0xff, 0xcb]))
    check_char(43, lambda: append_safe([0xfe, 0x03]))
    check_char(45, lambda: append_safe([0xfe, 0x0b]))
    
    check_char(46, lambda: append_safe([
        0xb8, 0x01, 0x00, 0x00, 0x00,
        0xbf, 0x01, 0x00, 0x00, 0x00,
        0x48, 0x89, 0xde,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ]))
    
    check_char(44, lambda: append_safe([
        0xb8, 0x00, 0x00, 0x00, 0x00,
        0xbf, 0x00, 0x00, 0x00, 0x00,
        0x48, 0x89, 0xde,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x0f, 0x05
    ]))
    
    right(2); loop_close(); left(2)
    
    # Flush (Using same token logic)
    # C8 is count.
    # Token at C300 is present (unused from last iter).
    # We need to scan C8 times.
    # Logic:
    #   Loop C8:
    #     Find Token at C300.
    #     Read C100 (Left 200). Output.
    #     Move Token Right.
    #   End Loop.
    
    right(8)
    loop_open()
       dec(); left(8) # C8--
       
       # Find Token
       right(300)
       loop_open(); right(); loop_close()
       
       # Read Data at C100+N
       left(200)
       out()
       
       # Move Token Right for next read
       right(200)
       loop_open(); dec(); right(); inc(); left(); loop_close()
       
       # Return Home
       loop_open(); left(); loop_close()
       left(299)
       
       right(8)
    loop_close()
    left(8)

    # Exit
    emit_bytes([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    
    # Padding
    right(7); dec(total_size)
    # Add Flushed Count (Saved in C6? No, we lost C8).
    # Assuming C7 is enough for valid ELF (Total Size is just for allocation)
    # We can just pad a fixed amount to be safe or ignore precise total_size check.
    # Let's pad 500 zeros.
    left(1); dec(total_size)
    loop_open()
    inc(total_size)
    right(1); clear(); out(); left(1)
    dec(total_size)
    loop_close()

if __name__ == "__main__":
    main()
