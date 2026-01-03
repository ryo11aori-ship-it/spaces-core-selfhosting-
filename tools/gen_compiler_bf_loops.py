#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py — 改良版（機能維持 + 位置管理 + 診断）
# stdout: Spaces (BF 方言) ソース
# stderr: 診断ログ (CI に残る)

import sys, os, hashlib

# ----------------------------
# 表記（Spaces 方言）
# ----------------------------
S = " "        # halfwidth space (右移動系)
F = "\u3000"   # fullwidth space (制御系)

def emit(s: str) -> None:
    sys.stdout.write(s + "\n")

def eprint(s: str) -> None:
    sys.stderr.write(s + "\n")

def dbg(s: str) -> None:
    if s.startswith("WARN:") or s.startswith("ERROR:"):
        eprint(s)
    elif os.environ.get("GEN_DEBUG", "0") == "1":
        eprint("DBG: " + s)

# ----------------------------
# 低レベル命令（Spaces の出力）
# ----------------------------
def raw_right(n=1): emit((S+S+S) * n)
def raw_left(n=1):  emit((S+S+F) * n)
def raw_inc(n=1):   emit((S+F+S) * n)
def raw_dec(n=1):   emit((S+F+F) * n)
def raw_out():      emit(F + S + S)
def raw_inp():      emit(F + S + F)
def raw_loop_open():  emit(F + F + S)
def raw_loop_close(): emit(F + F + F)

# ----------------------------
# 生成時の「テープ位置」追跡（重要）
# ----------------------------
cur_pos = 0
def move_by(delta:int):
    """生成する BF ソースに対してポインタ移動を発行し、cur_pos を更新する"""
    global cur_pos
    if delta > 0:
        raw_right(delta)
    elif delta < 0:
        raw_left(-delta)
    cur_pos += delta
    dbg(f"move_by({delta}) -> cur_pos={cur_pos}")

def go_to(target:int):
    global cur_pos
    move_by(target - cur_pos)

def clear_cell():
    raw_loop_open(); raw_dec(1); raw_loop_close()

def inc_cell(n:int):
    if n>0: raw_inc(n)
def dec_cell(n:int):
    if n>0: raw_dec(n)

# ----------------------------
# 安全なバイト出力（常に OUTPUT_CELL を使用）
# ----------------------------
OUTPUT_CELL = int(os.environ.get("OUTPUT_CELL", "200"))
dbg(f"OUTPUT_CELL={OUTPUT_CELL}")

def emit_byte_literal(v:int):
    """
    生成される BF プログラムが実行時に「1バイト」を出力するようにする命令列を出力。
    (移動→クリア→インクリメント v 回→出力→復帰) の原子処理。
    """
    global cur_pos
    saved = cur_pos
    go_to(OUTPUT_CELL)
    clear_cell()
    if v:
        # 単純に v 回インクリメント。v の大きさで命令数が増える点は許容。
        inc_cell(v)
    raw_out()
    go_to(saved)

def emit_bytes_literal(vals):
    for b in vals:
        emit_byte_literal(b)

# ----------------------------
# 元のジェネレータ論理（入力処理 / switch-case）を再実装
#  — 元コードの流れを保ちつつ、出力を emit_byte_literal に置換
# ----------------------------

WALL_POS = 98
BUFFER_BASE = 100

def go_home_from_cursor():
    # 元の意味合い: tape 上のホームへ戻す。ここでは単純に 0 へ。
    go_to(0)

def return_to_cursor_simple():
    # 元の単純復帰 (home -> cursor pos). 実行時に意味あるよう単純化
    go_to(WALL_POS)

def sub_and_check(delta:int, action_func):
    """
    元実装の意図を踏襲（現在セルから delta を引き、ゼロであれば action を実行）
    実装は破壊的（現在セルをデクリメント）だが簡潔で確実。
    action_func は「生成時に BF 命令を出力する関数」で、emit_byte_literal 等を呼ぶ。
    """
    # デクリメント delta
    dec_cell(delta)
    # BF でゼロ判定: [ ... ] -> 0 なら中に入らない
    raw_loop_open()
    # If non-zero, clear then leave (original used flag/copy; 我々は簡潔にする)
    raw_loop_close()
    
    # ゼロ判定ロジック:
    # 現在のセル(P)を非破壊チェックするため、一時領域(P+1, P+2, P+3)を使用
    move_by(1)  # temp1
    raw_loop_open(); raw_left(1); raw_inc(1); raw_right(2); raw_inc(1); raw_left(1); raw_dec(1); raw_loop_close()
    move_by(1)  # temp2
    raw_loop_open(); raw_left(1); raw_inc(1); raw_right(1); raw_dec(1); raw_loop_close()
    move_by(-1) # P+1 (temp1)

    # Now test temp2: go to temp2 (which is current+2)
    move_by(2)
    # prepare flag in temp3 (current+3)
    move_by(1); clear_cell(); inc_cell(1); move_by(-1)  # set flag=1 at temp3; then back to temp2
    # If temp2 != 0 -> decrement temp2 until zero while clearing flag
    raw_loop_open()
    raw_right(1); raw_dec(1); raw_left(1); clear_cell()  # clear temp3
    raw_loop_close()
    # After this, if flag still 1 -> temp2 was zero -> we execute action
    # Move to temp3 and check flag by loop
    move_by(1)
    raw_loop_open()
    # inside flag-loop -> execute action_func (emit BF seq)
    action_func()
    # clear flag and exit
    clear_cell()
    raw_loop_close()
    # return pointer to original cell (we are at temp3)
    move_by(-3)

def pad_zeros(count:int):
    # emit count zeros by outputting zero bytes via OUTPUT_CELL
    for _ in range(count):
        emit_byte_literal(0)

# ----------------------------
# main: ヘッダ出力＋外側ループ（入力読み取り）＋スイッチ
# ----------------------------
def main():
    # configuration
    target_file_size = int(os.environ.get("TARGET_FILE_SIZE", "500"))
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
        *p64(target_file_size), *p64(0x10000), *p64(0x1000)
    ]

    # Emit static header bytes first
    emit_bytes_literal(header + prog_header)

    # Emit a small code stub
    emit_bytes_literal([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])

    # Initialize tape: place buffer flag at BUFFER_BASE
    go_to(BUFFER_BASE)
    clear_cell()
    inc_cell(2)
    go_to(0)  # back home

    # --- Outer loop: read input and process each character ---
    raw_loop_open()   
    raw_inp()

    # Non-destructive copy of input into temps
    # copy current -> L1,L2
    raw_loop_open(); raw_left(1); raw_inc(1); raw_left(1); raw_inc(1); raw_right(2); raw_dec(1); raw_loop_close()

    # Check EOF
    move_by(-1)  # to L1
    clear_cell(); inc_cell(1)  # L3=1
    move_by(-1)
    raw_loop_open(); raw_right(1); raw_dec(1); raw_left(1); clear_cell(); raw_loop_close()
    move_by(1)

    # If L3==1 (EOF) -> flush buffer and exit.
    move_by(0)
    raw_loop_open()
    go_home_from_cursor()
    emit_bytes_literal([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])
    pad_zeros(target_file_size - (len(header) + len(prog_header) + 10 + 7))
    # Break loops
    go_to(BUFFER_BASE); clear_cell()
    raw_loop_close()

    # Restore data from L2 -> R1
    move_by(1)
    raw_loop_open(); raw_right(2); raw_inc(1); raw_left(2); raw_dec(1); raw_loop_close()
    move_by(2)

    # --- Process character: dense switch ---
    raw_loop_open()
    sub_and_check(43, lambda: emit_bytes_literal([0xfe, 0x03]))
    sub_and_check(1, lambda: emit_bytes_literal([0xb8,0x00,0x00,0x00,0x00,0xbf,0x00,0x00,0x00,0x00,0x48,0x89,0xde,0xba,0x01,0x00,0x00,0x00,0x0f,0x05]))
    sub_and_check(1, lambda: emit_bytes_literal([0xfe,0x0b]))
    sub_and_check(1, lambda: emit_bytes_literal([0xb8,0x01,0x00,0x00,0x00,0xbf,0x01,0x00,0x00,0x00,0x48,0x89,0xde,0xba,0x01,0x00,0x00,0x00,0x0f,0x05]))
    sub_and_check(14, lambda: emit_bytes_literal([0x48,0xff,0xcb]))
    sub_and_check(2, lambda: emit_bytes_literal([0x48,0xff,0xc3]))

    # Skip '[' and ']' tokens
    move_by(1); dec_cell(29); move_by(-1)  # Skip '['
    move_by(1); dec_cell(2); move_by(-1)   # Skip ']'
    clear_cell()
    raw_loop_close()

    # Return home and close outer loop
    go_home_from_cursor()
    move_by(-10)
    raw_loop_close()

if __name__ == "__main__":
    main()
