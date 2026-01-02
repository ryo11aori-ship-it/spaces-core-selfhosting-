#!/usr/bin/env python3
# tools/gen_compiler_v1.py
# Robust generator v0.91 — pointer-tracking + atomic chunk rendering.
#
# Key ideas:
#  - Maintain `cur` pointer (absolute cell index) in the generator so every move
#    is deterministic: move_to(target_index).
#  - Emit atomic chunks (with real '\n' separators) to avoid accidental FFS/FFF merging.
#  - Count loop_start / loop_end; refuse output if negative min-balance; append missing
#    closing loops at EOF if positive imbalance.
#  - Use C1 as preserved copy for comparisons (fix of prior bug).
#
# Usage:
#   python3 tools/gen_compiler_v1.py > spaces/self/compiler_v1.spaces

import sys

# tokens
S = " "           # half-width space
F = "\u3000"      # full-width ideographic space

# Renderer: collects atomic chunks, tracks loop start/end counts.
class Renderer:
    def __init__(self):
        self.chunks = []
        self.ls = 0
        self.le = 0

    def emit(self, s: str):
        # append physical newline to avoid adjacent-chunk token merging
        self.chunks.append(s + "\n")

    def loop_start(self):
        self.ls += 1
        self.emit(F + F + S)

    def loop_end(self):
        self.le += 1
        self.emit(F + F + F)

    def join(self) -> str:
        return "".join(self.chunks)

    def finalize(self) -> str:
        out = self.join()
        # compute streaming min balance to detect premature LE
        ls_pat = F + F + S
        le_pat = F + F + F
        i = 0
        bal = 0
        min_bal = 0
        while True:
            idx_ls = out.find(ls_pat, i)
            idx_le = out.find(le_pat, i)
            if idx_ls == -1 and idx_le == -1:
                break
            if idx_ls != -1 and (idx_ls < idx_le or idx_le == -1):
                bal += 1
                i = idx_ls + len(ls_pat)
            else:
                bal -= 1
                i = idx_le + len(le_pat)
            if bal < min_bal:
                min_bal = bal
        if min_bal < 0:
            # generator produced an LE before corresponding LS in-stream => BUG
            raise RuntimeError(f"Generator sanity: min_balance {min_bal} < 0; aborting.")
        # if more LS than LE, append missing LE at EOF (pragmatic safety)
        if self.ls > self.le:
            missing = self.ls - self.le
            out += (le_pat * missing)
        return out

R = Renderer()

# We'll maintain an absolute pointer index `cur`. We'll place C0 at base_index.
# We choose base = 16 to match original right(16) safety margin.
BASE = 16
# Logical cell indices:
C0 = BASE + 0
C1 = BASE + 1
C2 = BASE + 2
C3 = BASE + 3
C4 = BASE + 4
C5 = BASE + 5
C6 = BASE + 6
C7 = BASE + 7
# We'll track current cell (start as BASE because we begin with right(16) in generation).
cur = 0  # will initialize in main to BASE after performing initial right(16) chunk

# low-level emit primitives (do NOT change without updating `cur` tracking)
def raw_emit(s: str):
    R.emit(s)

def raw_loop_start():
    R.loop_start()

def raw_loop_end():
    R.loop_end()

# move by emitting right or left commands; caller updates cur
def emit_right(n=1):
    if n <= 0: return
    raw_emit((S+S+S) * n)

def emit_left(n=1):
    if n <= 0: return
    raw_emit((S+S+F) * n)

# helpers to move cur to target absolute index
def move_to(target):
    global cur
    delta = target - cur
    if delta > 0:
        emit_right(delta)
    elif delta < 0:
        emit_left(-delta)
    cur = target

# high-level cell operations (use move_to internals)
def inc_at(target, n=1):
    if n <= 0: return
    move_to(target)
    raw_emit((S + F + S) * n)

def dec_at(target, n=1):
    if n <= 0: return
    move_to(target)
    raw_emit((S + F + F) * n)

def out_at(target):
    move_to(target)
    raw_emit(F + S + S)

def inp_at(target):
    move_to(target)
    raw_emit(F + S + F)

def loop_start_at(target):
    move_to(target)
    raw_loop_start()

def loop_end_at(target):
    move_to(target)
    raw_loop_end()

def clear_at(target):
    # loop_start; dec; loop_end on target
    loop_start_at(target)
    dec_at(target, 1)
    loop_end_at(target)

# emit machine byte using tracked-output pattern (C0->C9->C0, increment C7)
def emit_byte_tracked_at_cell(byte_val):
    # Move to C9, clear, inc(byte), out, clear, move back; then increment C7
    move_to(C9 := BASE + 9)
    clear_at(C9)
    inc_at(C9, byte_val)
    out_at(C9)
    clear_at(C9)
    move_to(C0)
    move_to(C7)  # increment counter C7
    inc_at(C7, 1)
    move_to(C0)

# wrapper iterating list
def emit_machine_code_tracked_at(bytes_list):
    for b in bytes_list:
        # ensure byte in 0..255
        emit_byte_tracked_at_cell(b & 0xff)

# ELF helpers
def p64(v):
    return list(v.to_bytes(8, 'little'))

def p32(v):
    return list(v.to_bytes(4, 'little'))

# Main generation: replicate original logic but with safe move_to management
def generate():
    global cur
    # Start: safety margin right(16)
    # emulate right(16)
    cur = BASE - 16  # so that moving to BASE via right(16) sets cur=BASE
    emit_right(16)
    cur = BASE

    # 1) ELF header
    load_addr = 0x400000
    header_len = 120
    total_size = 200

    header = [
        0x7f,0x45,0x4c,0x46,0x02,0x01,0x01,0x00,0,0,0,0,0,0,0,0,
        0x02,0x00,0x3e,0x00,0x01,0x00,0x00,0x00,
        *p64(load_addr + header_len), *p64(64), *p64(0), *p32(0),
        0x40,0x00,0x38,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00
    ]
    prog_header = [
        0x01,0x00,0x00,0x00,0x07,0x00,0x00,0x00,
        *p64(0), *p64(load_addr), *p64(load_addr),
        *p64(total_size), *p64(total_size), *p64(0x1000)
    ]
    for b in header + prog_header:
        # emit each byte via tracked output
        emit_machine_code_tracked_at([b])

    # 2) xor rbx, rbx
    emit_machine_code_tracked_at([0x48, 0x31, 0xdb])

    # 3) Main loop setup: set C2=1 and start loop
    inc_at(C2, 1)
    loop_start_at(C2)
    # leave pointer at C2? original did left(2) to go to C0; we'll move to C0 for next steps
    move_to(C0)

    # STEP1: read input into C0
    clear_at(C0)
    inp_at(C0)

    # STEP2: EOF check
    # Clear C1
    clear_at(C1)

    # Copy C0 -> C1 & C3: We'll do:
    #   move to C3; clear
    #   loop on C0: while C0 != 0: dec C0; inc C3; inc C1
    #   restore: loop on C3: while C3 != 0: dec C3; inc C0
    move_to(C3); clear_at(C3)
    # loop start on C0
    loop_start_at(C0)
    dec_at(C0, 1)
    inc_at(C3, 1)
    inc_at(C1, 1)
    loop_end_at(C0)
    # restore C0 from C3
    loop_start_at(C3)
    dec_at(C3, 1)
    inc_at(C0, 1)
    loop_end_at(C3)

    # Assume EOF: set C5 = 1
    clear_at(C5)
    inc_at(C5, 1)

    # If C1 != 0 then clear C5 (we check C1)
    loop_start_at(C1)
    # body: clear C5
    clear_at(C5)
    loop_end_at(C1)

    # If C5 == 1 then break main loop (decrement C2)
    loop_start_at(C5)
    # clear C5 and dec C2
    clear_at(C5)
    dec_at(C2, 1)
    loop_end_at(C5)

    # STEP3: check '+'
    # Only run if main loop still active (we're still inside loop_start(C2)...)
    # Clear scratch C1 (we'll reuse)
    clear_at(C1)

    # Copy C0 -> C1 & C3 again (same pattern)
    move_to(C3); clear_at(C3)
    loop_start_at(C0)
    dec_at(C0, 1)
    inc_at(C3, 1)
    inc_at(C1, 1)
    loop_end_at(C0)
    loop_start_at(C3)
    dec_at(C3, 1)
    inc_at(C0, 1)
    loop_end_at(C3)

    # Subtract 43 from C1
    dec_at(C1, 43)

    # Check if C1 == 0 (match): set C5=1 then if non-zero clear it (pattern)
    clear_at(C5)
    inc_at(C5, 1)
    loop_start_at(C1)
    # if C1 != 0 inside loop: clear C5
    clear_at(C5)
    loop_end_at(C1)

    # If match (C5==1) emit inc rbx machine code
    loop_start_at(C5)
    clear_at(C5)
    # emit machine inc rbx bytes
    emit_machine_code_tracked_at([0x48, 0xff, 0xc3])
    loop_end_at(C5)

    # STEP4: check '-'
    # Clear scratch C1
    clear_at(C1)

    # Copy C0 -> C1 & C3 again
    move_to(C3); clear_at(C3)
    loop_start_at(C0)
    dec_at(C0, 1)
    inc_at(C3, 1)
    inc_at(C1, 1)
    loop_end_at(C0)
    loop_start_at(C3)
    dec_at(C3, 1)
    inc_at(C0, 1)
    loop_end_at(C3)

    # Subtract 45 from C1
    dec_at(C1, 45)

    # Check match
    clear_at(C5)
    inc_at(C5, 1)
    loop_start_at(C1)
    clear_at(C5)
    loop_end_at(C1)

    loop_start_at(C5)
    clear_at(C5)
    emit_machine_code_tracked_at([0x48, 0xff, 0xcb])
    loop_end_at(C5)

    # End main loop: close loop_started on C2
    loop_end_at(C2)

    # 4) exit sequence: mov edi, ebx; mov eax,60; syscall
    emit_machine_code_tracked_at([0x89, 0xdf, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

    # 5) pad: emit zero via tracked helper
    # We'll do the same padding pattern as before
    move_to(C7)
    dec_at(C7, 200)
    loop_start_at(C7)
    inc_at(C7, 200)
    loop_end_at(C7)
    # emit one zero
    emit_machine_code_tracked_at([0])
    # reverse pad ops to leave balanced tokens
    move_to(C7)
    dec_at(C7, 200)
    loop_start_at(C7)
    inc_at(C7, 200)
    loop_end_at(C7)

# entrypoint
def main():
    try:
        generate()
    except Exception as e:
        print("Generation failed:", e, file=sys.stderr)
        raise

    # finalize and sanity-check
    try:
        out = R.finalize()
    except Exception as e:
        print("Finalize failed:", e, file=sys.stderr)
        sys.exit(2)

    # optional: write a small loop balance debug to stderr (counts)
    ls = R.ls
    le = R.le
    print(f"[generator debug] loop_start={ls}, loop_end(before append)={le}", file=sys.stderr)

    sys.stdout.buffer.write(out.encode("utf-8"))

if __name__ == "__main__":
    main()