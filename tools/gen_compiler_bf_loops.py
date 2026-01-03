#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py (改良版)
# - cur_pos 管理によりセル移動不整合を防止
# - emit_byte によりバイト出力を原子的に行う
# - 生成前に論理的出力量を検査し、診断を stderr に出力する
# 出力: stdout -> BF (Spaces) ソース
# 診断: stderr に出力 (GEN_DEBUG=1 で詳細)

from __future__ import annotations
import sys, os

# ----- 言語マッピング（Spaces 方言） -----
S = " "        # halfwidth space
F = "\u3000"   # fullwidth space

def emit(s: str) -> None:
    """stdout に BF ソース行を出力（改行付き）。"""
    sys.stdout.write(s + "\n")

def dbg(msg: str) -> None:
    """診断は stderr に出す。環境変数 GEN_DEBUG=1 で詳細出力。"""
    if os.environ.get("GEN_DEBUG", "0") == "1":
        sys.stderr.write("GEN_DBG: " + msg + "\n")
    else:
        # 常に重要な警告は出力
        if msg.startswith("WARN:") or msg.startswith("ERROR:"):
            sys.stderr.write(msg + "\n")

# ----- 低レベル BF 命令（Spaces での表現） -----
def raw_right(n=1): emit((S+S+S) * n)
def raw_left(n=1):  emit((S+S+F) * n)
def raw_inc(n=1):   emit((S+F+S) * n)
def raw_dec(n=1):   emit((S+F+F) * n)
def raw_out():      emit(F + S + S)
def raw_inp():      emit(F + S + F)
def raw_loop_open():  emit(F + F + S)
def raw_loop_close(): emit(F + F + F)

# ----- 高レベル位置管理 -----
cur_pos = 0
def move_by(delta: int) -> None:
    """相対移動（cur_pos を更新）。"""
    global cur_pos
    if delta > 0:
        raw_right(delta)
    elif delta < 0:
        raw_left(-delta)
    cur_pos += delta
    dbg(f"move_by({delta}) -> cur_pos={cur_pos}")

def go_to(target: int) -> None:
    """絶対位置へ移動。"""
    global cur_pos
    move_by(target - cur_pos)

def clear_cell() -> None:
    """現在セルを確実に 0 にする ([-])"""
    raw_loop_open()
    raw_dec(1)
    raw_loop_close()

def inc_cell(n:int) -> None:
    if n > 0:
        raw_inc(n)

def dec_cell(n:int) -> None:
    if n > 0:
        raw_dec(n)

# ----- 出力の安全化: emit_byte / emit_bytes / stream_bytes -----
# 出力は必ず OUTPUT_CELL にセットしてから `.` することで
# 他セルを上書きするリスクを回避する。
OUTPUT_CELL = int(os.environ.get("OUTPUT_CELL", "200"))  # 必要に応じて小さく（例: 64, 100）
dbg(f"OUTPUT_CELL={OUTPUT_CELL}")

# 論理的に何バイトを吐くか追跡するためのバッファ（生成前に評価）
logical_output: list[int] = []

def enqueue_bytes(vals: list[int]) -> None:
    """論理出力列に追加（実際の BF コード生成は後で行う）。"""
    logical_output.extend(vals)

def emit_byte(v: int) -> None:
    """
    BF 命令列として v を出力する（emit 直接呼び出しバージョン）。
    - 保存位置（cur_pos の値）に戻るように移動を行う。
    注意: 生成済み BF 命令数が多くなる点に注意。
    """
    saved = cur_pos
    go_to(OUTPUT_CELL)
    clear_cell()
    if v:
        # 単純に v 回インクリメント（簡潔・確実）
        inc_cell(v)
    raw_out()
    go_to(saved)

def produce_all_bytes_from_logical() -> None:
    """logical_output にある順に emit_byte を呼んで BF ソースを出力する。"""
    dbg(f"Producing {len(logical_output)} bytes via emit_byte")
    for i, b in enumerate(logical_output):
        dbg(f"  -> byte[{i}] = {b:02x}")
        emit_byte(b)

# ----- ヘッダ作成ユーティリティ -----
def p64(v:int)->list[int]:
    return list(v.to_bytes(8, "little"))
def p32(v:int)->list[int]:
    return list(v.to_bytes(4, "little"))

# ----- pad 用（論理バイト列に 0 を追加） -----
def enqueue_pad(count:int) -> None:
    for _ in range(count):
        logical_output.append(0)

# ----- main: 論理バイト列を構築し、検査→BF コードを吐く -----
def main():
    # 設定（必要に応じて env で上書き）
    target_file_size = int(os.environ.get("TARGET_FILE_SIZE", "500"))
    load_addr = int(os.environ.get("LOAD_ADDR", hex(0x400000)), 16) if isinstance(os.environ.get("LOAD_ADDR"), str) else 0x400000
    header_len = 120

    dbg(f"target_file_size={target_file_size}, load_addr=0x{load_addr:x}, header_len={header_len}")

    # ELF ヘッダ（既存ロジックを踏襲）
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

    # 基本的なペイロード（短いスタブ、後で必要なら差し替え）
    code_stub = [0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00]

    # 論理出力列を組み立てる（順序通り）
    logical_output.clear()
    logical_output.extend(header)
    logical_output.extend(prog_header)
    logical_output.extend(code_stub)

    # 最低限ここで EOF 判定/終了シーケンスを加える（既存コードの意図を簡素化）
    exit_stub = [0x48, 0x31, 0xff, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05]
    logical_output.extend(exit_stub)

    # パディング（target_file_size に合わせる）
    if target_file_size < len(logical_output):
        sys.stderr.write(f"ERROR: target_file_size ({target_file_size}) is smaller than header+stub ({len(logical_output)}). Aborting.\n")
        # それでも BF を出すかは設計次第。ここでは続行せず終了。
        sys.exit(2)

    pad_needed = target_file_size - len(logical_output)
    enqueue_pad(pad_needed)

    # ここまでで「期待される出力バイト列」が logical_output に入っている。
    # まず診断: ELF マジックとサイズ
    if len(logical_output) >= 4:
        magic = logical_output[:4]
        ok_magic = (magic[0] == 0x7f and magic[1] == 0x45 and magic[2] == 0x4c and magic[3] == 0x46)
        sys.stderr.write(f"INFO: Logical output size = {len(logical_output)} bytes (target {target_file_size}).\n")
        sys.stderr.write(f"INFO: ELF magic (expected 7f 45 4c 46) = {'OK' if ok_magic else 'MISMATCH'}; bytes = {' '.join(f'{b:02x}' for b in magic)}\n")
    else:
        sys.stderr.write("ERROR: logical_output too small to contain ELF magic.\n")

    # 追加診断（readelf 相当の簡易情報）
    # e_phoff は header 内に入れてある p64(load_addr + header_len) の直後あたりにある。ここでは簡単に報告。
    sys.stderr.write(f"DEBUG: header bytes = {len(header)}, prog_header bytes = {len(prog_header)}, code_stub bytes = {len(code_stub)}, exit_stub bytes = {len(exit_stub)}\n")

    # BF ソース生成開始（ここから stdout に命令を吐く）
    # まずワーク領域初期化（BUFFER_BASE 等の概念を保つためのセル初期化）
    # ここで出力する BF 命令は「ref_vm が期待する Spaces 方言」であることを前提。
    # note: 以降のemit*は stdout に BF 命令ラインを出力します。
    # 初期位置は cur_pos == 0 と仮定

    # 出力命令群を作る（logical_output を逐次出力）
    produce_all_bytes_from_logical()

    # 最後に追加のパディング（BF 側で余剰なゼロを埋めたければここで更に emit_byte(0) を繰り返す）
    # ただし logical_output に既に pad を入れているためここでは何もしない。

    # 最終診断（stderr）
    sys.stderr.write(f"INFO: Finished generating BF source. Logical bytes planned: {len(logical_output)}. OUTPUT_CELL={OUTPUT_CELL}\n")
    if len(logical_output) != target_file_size:
        sys.stderr.write(f"WARN: Planned output size ({len(logical_output)}) != target_file_size ({target_file_size}).\n")
    sys.stderr.write("INFO: Note: Diagnostics were printed to stderr. stdout contains only BF (Spaces) source.\n")

if __name__ == "__main__":
    main()