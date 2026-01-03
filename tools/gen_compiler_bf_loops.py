#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py — 改良版（診断強化）
# 出力: stdout = BF (Spaces) ソース
# 診断: stderr（CI ログに残る）
#
# 環境変数（任意）
#  - GEN_DEBUG=1         詳細診断ログを出す（stderr）
#  - OUTPUT_CELL=<int>   出力セル位置（デフォルト 200）
#  - TARGET_FILE_SIZE=<int>  目標ファイルサイズ（デフォルト 500）
#  - DUMP_BYTES=1        先頭/末尾バイトを stderr にダンプ（小分割）
#  - TRUNC_MARKER=1      logical_output の末尾に診断トレーラを書き込む（バイナリ検証用）
#
import sys, os, hashlib, textwrap

# -----------------------
# 表現（Spaces 方言）
# -----------------------
S = " "        # halfwidth space
F = "\u3000"   # fullwidth space

def emit(line: str) -> None:
    sys.stdout.write(line + "\n")

def eprint(line: str) -> None:
    sys.stderr.write(line + "\n")

def dbg(line: str) -> None:
    # Always print WARN/ERROR lines. Otherwise print only if GEN_DEBUG=1.
    if line.startswith("WARN:") or line.startswith("ERROR:"):
        eprint(line)
    elif os.environ.get("GEN_DEBUG", "0") == "1":
        eprint("DBG: " + line)

# -----------------------
# 低レベル BF 命令
# -----------------------
def raw_right(n=1): emit((S+S+S) * n)
def raw_left(n=1):  emit((S+S+F) * n)
def raw_inc(n=1):   emit((S+F+S) * n)
def raw_dec(n=1):   emit((S+F+F) * n)
def raw_out():      emit(F + S + S)
def raw_inp():      emit(F + S + F)
def raw_loop_open():  emit(F + F + S)
def raw_loop_close(): emit(F + F + F)

# -----------------------
# 位置管理（生成側でテープ位置を追跡）
# -----------------------
cur_pos = 0
def move_by(delta:int):
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

# -----------------------
# 論理出力バッファ（先に構築して検査）
# -----------------------
logical_output = bytearray()

def p64(v:int)->bytes:
    return v.to_bytes(8, "little")
def p32(v:int)->bytes:
    return v.to_bytes(4, "little")

# -----------------------
# 診断トレーラ（末尾に付けて変化/切断を検出）
# -----------------------
def append_trailer(buf: bytearray):
    # 末尾に ASCII マーカーと SHA256 の先頭 8 バイトを付与
    marker = b"GENCHK"
    h = hashlib.sha256(buf).digest()
    trailer = marker + h[:8]
    buf.extend(trailer)
    dbg(f"Appended trailer: marker={marker} sha8={h[:8].hex()}")

# -----------------------
# emit_byte: OUTPUT_CELL を使って原子的にバイトを出す
# -----------------------
OUTPUT_CELL = int(os.environ.get("OUTPUT_CELL", "200"))
dbg(f"OUTPUT_CELL={OUTPUT_CELL}")

def emit_byte_as_bf(v:int):
    """stdout に直接 BF 命令を吐いて 1 バイト出力する（emit_byte 版）"""
    global cur_pos
    saved = cur_pos
    go_to(OUTPUT_CELL)
    clear_cell()
    if v:
        inc_cell(v)
    raw_out()
    go_to(saved)

# ただし今回は logical_output を先に構築してから produce_all_bytes_from_logical() を使う流れ

# -----------------------
# main: 論理出力を作って検査→BF 命令を出力
# -----------------------
def main():
    # 設定
    target_file_size = int(os.environ.get("TARGET_FILE_SIZE", "500"))
    load_addr = 0x400000
    header_len = 120

    dbg(f"target_file_size={target_file_size}")

    # ELF ヘッダ（簡易、既存のフォーマットを踏襲）
    header = bytearray([
        0x7f,0x45,0x4c,0x46,0x02,0x01,0x01,0x00,0,0,0,0,0,0,0,0,
        0x02,0x00,0x3e,0x00,0x01,0x00,0x00,0x00
    ])
    header.extend(p64(load_addr + header_len))
    header.extend(p64(64))
    header.extend(p64(0))
    header.extend(p32(0))
    header.extend(bytes([0x40,0x00,0x38,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00]))

    prog_header = bytearray([
        0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00
    ])
    prog_header.extend(p64(0))
    prog_header.extend(p64(load_addr))
    prog_header.extend(p64(load_addr))
    prog_header.extend(p64(target_file_size))
    prog_header.extend(p64(0x10000))
    prog_header.extend(p64(0x1000))

    # 簡単なコードスタブ（実際の動作は ref_vm 側／compiler_linear.bf に依存）
    code_stub = bytearray([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])

    exit_stub = bytearray([0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

    # 論理出力を構築
    logical_output.clear()
    logical_output.extend(header)
    logical_output.extend(prog_header)
    logical_output.extend(code_stub)
    logical_output.extend(exit_stub)

    # ここで target_file_size と矛盾する場合は明示的に失敗する
    if len(logical_output) > target_file_size:
        eprint(f"ERROR: header+stub size ({len(logical_output)}) > TARGET_FILE_SIZE ({target_file_size})")
        sys.exit(2)

    pad_needed = target_file_size - len(logical_output)
    logical_output.extend(b"\x00" * pad_needed)

    # 追加診断トレーラ（任意）
    if os.environ.get("TRUNC_MARKER", "1") == "1":
        # Append trailer but ensure final planned size stays target_file_size:
        # Strategy: compute trailer, then place it into reserved last bytes (overwrite tail).
        # We'll compute sha256 of current planned content and store marker+sha8 in final bytes.
        h = hashlib.sha256(logical_output).digest()[:8]
        marker = b"GENCHK"  # 6 bytes
        trailer = marker + h  # 14 bytes
        if len(trailer) <= len(logical_output):
            # write trailer at very end
            logical_output[-len(trailer):] = trailer
            dbg(f"Placed trailer at end: {trailer.hex()}")
        else:
            dbg("WARN: trailer longer than planned output; skipping trailer embedding")

    # 基本診断を stderr に出力（CI ログに残る）
    eprint(f"INFO: Logical output size = {len(logical_output)} bytes (target {target_file_size}).")
    magic = logical_output[:4]
    ok_magic = (magic == b"\x7fELF")
    eprint(f"INFO: ELF magic = {'OK' if ok_magic else 'MISMATCH'}; bytes = {' '.join(f'{b:02x}' for b in magic)}")
    eprint(f"DEBUG: header bytes = {len(header)}, prog_header bytes = {len(prog_header)}, code_stub bytes = {len(code_stub)}, exit_stub bytes = {len(exit_stub)}")

    # 先頭/末尾の抜粋ダンプ（大きい場合は trunc）
    if os.environ.get("DUMP_BYTES", "0") == "1":
        max_show = 64
        head = logical_output[:max_show]
        tail = logical_output[-max_show:]
        eprint("DEBUG: logical_output head: " + " ".join(f"{b:02x}" for b in head))
        eprint("DEBUG: logical_output tail: " + " ".join(f"{b:02x}" for b in tail))
    else:
        # show compact summary
        eprint(f"DEBUG: logical_output[0..3] = {' '.join(f'{b:02x}' for b in logical_output[:4])}, tail4 = {' '.join(f'{b:02x}' for b in logical_output[-4:])}")

    # 追加: SHA256 (短い表示)
    sha = hashlib.sha256(logical_output).hexdigest()
    eprint(f"INFO: planned output sha256 (hex, first 16) = {sha[:16]}")

    # ----------------------------
    # ここから stdout に BF (Spaces) ソース命令を吐き出す
    # すべてのバイトを emit_byte_as_bf() で出す（原子的）
    # ----------------------------
    # 出力が大きいので（target が 500 固定だと問題ないが）必要ならスロットルできます
    # Reset cur_pos for generation stage
    global cur_pos
    cur_pos = 0

    # We'll produce BF commands that emit each planned byte in order.
    # Because emitting thousands of BF commands can be huge, we keep simple mapping:
    for i, b in enumerate(logical_output):
        if i % 100 == 0:
            dbg(f"producing byte {i}/{len(logical_output)} (0x{b:02x})")
        emit_byte_as_bf(b)

    # Final diagnostic footer (stderr)
    eprint("INFO: Finished generating BF (Spaces) source to stdout.")
    eprint("INFO: Diagnostics printed to stderr. stdout contains only BF source lines.")
    # also print summary to stderr for CI parsing
    eprint(f"SUMMARY:planned_bytes={len(logical_output)} target={target_file_size} elf_magic_ok={ok_magic} sha256={sha}")

if __name__ == "__main__":
    main()