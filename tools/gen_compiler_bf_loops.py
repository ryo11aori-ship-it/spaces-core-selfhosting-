#!/usr/bin/env python3
# tools/gen_compiler_bf_loops.py — conservative rework with chunked emission + diagnostics

import sys, os, hashlib

S = " "
F = "\u3000"

def emit(s): sys.stdout.write(s + "\n")
def eprint(s): sys.stderr.write(s + "\n")

def r_right(n=1): emit((S+S+S)*n)
def r_left(n=1):  emit((S+S+F)*n)
def r_inc(n=1):   emit((S+F+S)*n)
def r_dec(n=1):   emit((S+F+F)*n)
def r_out():      emit(F+S+S)
def r_loop_o():   emit(F+F+S)
def r_loop_c():   emit(F+F+F)

# position tracking
cur = 0
def go_to(t):
    global cur
    d = t - cur
    if d>0: r_right(d)
    elif d<0: r_left(-d)
    cur = t

def clear_cell():
    r_loop_o(); r_dec(1); r_loop_c()

OUTPUT_CELL = int(os.environ.get("OUTPUT_CELL", "64"))
CHUNK = int(os.environ.get("EMIT_CHUNK", "64"))

def emit_byte(v):
    global cur
    saved = cur
    go_to(OUTPUT_CELL)
    clear_cell()
    if v:
        # naive inc; could be optimized with loops but keep simple for correctness
        r_inc(v)
    r_out()
    go_to(saved)

def emit_bytes_sequence(seq):
    # emit in chunks with minor dbg lines to stderr (so CI log shows progress when large)
    total = len(seq)
    i = 0
    while i < total:
        end = min(i+CHUNK, total)
        for b in seq[i:end]:
            emit_byte(b)
        eprint(f"EMIT: emitted bytes {i}-{end-1}")
        i = end

def p64(v): return v.to_bytes(8, 'little')
def p32(v): return v.to_bytes(4, 'little')

def main():
    target_file_size = int(os.environ.get("TARGET_FILE_SIZE", "500"))
    load_addr = 0x400000
    header_len = 120

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
    prog_header.extend(p64(0)); prog_header.extend(p64(load_addr)); prog_header.extend(p64(load_addr))
    prog_header.extend(p64(target_file_size)); prog_header.extend(p64(0x10000)); prog_header.extend(p64(0x1000))

    code_stub = bytearray([0x48, 0xc7, 0xc3, 0x00, 0x20, 0x40, 0x00])
    exit_stub = bytearray([0x48,0x31,0xff,0xb8,0x3c,0x00,0x00,0x00,0x0f,0x05])

    logical = bytearray()
    logical.extend(header); logical.extend(prog_header); logical.extend(code_stub); logical.extend(exit_stub)

    if len(logical) > target_file_size:
        eprint(f"ERROR: header+stub too large ({len(logical)}) > target {target_file_size}")
        sys.exit(2)
    pad_needed = target_file_size - len(logical)
    logical.extend(b"\x00"*pad_needed)

    # embed trailer in last 16 bytes if possible
    if target_file_size >= 16:
        h = hashlib.sha256(logical).digest()[:8]
        marker = b"GENCHK"
        tr = marker + h
        logical[-len(tr):] = tr

    eprint(f"PLANNED: {len(logical)} bytes sha={hashlib.sha256(logical).hexdigest()[:16]}")
    eprint(f"PLANNED_HEAD: {' '.join(f'{b:02x}' for b in logical[:8])}")
    eprint(f"PLANNED_TAIL: {' '.join(f'{b:02x}' for b in logical[-16:])}")

    # Now produce BF that outputs logical as bytes using emit_byte (chunked)
    emit_bytes_sequence(logical)

    eprint("DONE: generator emitted Spaces source to stdout")

if __name__ == '__main__':
    main()