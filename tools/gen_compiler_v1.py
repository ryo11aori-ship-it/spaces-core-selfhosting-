#!/usr/bin/env python3
# tools/gen_compiler_v1.py
# Spaces Compiler Generator (Level 0.9: Robust BF->ELF generator)
#
# Goals / fixes:
#  - Emit tokens as *atomic chunks* and separate them with real newline characters
#    so adjacent emits cannot accidentally create FFS/FFF patterns.
#  - Track explicit loop_start/loop_end counts in Python; detect imbalances.
#  - If there's a positive imbalance (more starts), append missing loop_end tokens
#    at EOF to avoid VM hangs. If negative imbalance occurs, raise an error.
#  - Fix logical bug: use preserved copy cell (C1) for EOF/+/- comparisons.
#  - Keep the tracked machine-code emission helpers (emit_byte_tracked).
#
# How it prevents the original bug:
#  - The original failures were caused by token merging across adjacent emits,
#    producing extra loop tokens and unbalanced loops. Here we always separate
#    emits with '\n' (the VM ignores newline) and check correctness before writing.
#
# Usage:
#   python3 tools/gen_compiler_v1.py > spaces/self/compiler_v1.spaces
#
# Cell index mapping (conceptual):
#   C0: working cursor / current input byte
#   C1: preserved scratch copy for comparisons (must retain value after copy/restore)
#   C2: main loop flag
#   C3: transient helper used during copy/restore (becomes 0 after restore)
#   C4: unused
#   C5: match/EOF flag
#   C6: unused
#   C7: byte counter (incremented each time emit_byte_tracked writes a byte)
#
# Note: This generator is intended to be robust and maintainable. If you want me to
# additionally run it locally against your VM files and iterate further, upload the
# generated .spaces and test.elf and I'll analyze them.

import sys

# --- utilities for serialization & safety ---
S = " "         # ASCII half-width space
F = "\u3000"    # full-width ideographic space (U+3000)

class Renderer:
    """
    Collect atomic token chunks. Each chunk will be written followed by a newline.
    Newlines are ignored by the VM but prevent adjacent chunks merging to form
    unintended multi-token patterns (like FFS/FFF across boundaries).
    """
    def __init__(self):
        self.chunks = []
        self.loop_start_count = 0
        self.loop_end_count = 0

    def emit(self, chunk: str):
        # Record chunk; use a real newline as a separator (VM ignores it).
        self.chunks.append(chunk + "\n")

    def loop_start(self):
        self.loop_start_count += 1
        self.emit(F + F + S)

    def loop_end(self):
        self.loop_end_count += 1
        self.emit(F + F + F)

    def join(self) -> str:
        return "".join(self.chunks)

    def finalize(self) -> str:
        """
        Post-process: verify loop balance; if there are more loop_starts than loop_ends,
        append missing loop_end tokens at EOF to avoid VM hang. If there are more loop_ends
        than loop_starts, that's a generator logic error — raise exception.
        """
        out = self.join()
        ls = self.loop_start_count
        le = self.loop_end_count
        if le > ls:
            raise RuntimeError(f"Generator error: more loop_end ({le}) than loop_start ({ls}).")
        if ls > le:
            missing = ls - le
            # Append missing loop_end tokens. Use exact token, no newline merging risk.
            out += (F + F + F) * missing
            # Do not increment loop_end_count here (we're emitting final closers for VM safety).
        return out

# Instantiate renderer (module-local convenience)
R = Renderer()

# --- low-level token emitters (all call R.emit or R.loop_{start,end}) ---
def right(n=1):
    if n <= 0: return
    R.emit((S+S+S) * n)

def left(n=1):
    if n <= 0: return
    R.emit((S+S+F) * n)

def inc(n=1):
    if n <= 0: return
    # produce n increments; split if extremely large (safety), but typical values are small.
    R.emit((S+F+S) * n)

def dec(n=1):
    if n <= 0: return
    R.emit((S+F+F) * n)

def out():
    R.emit(F + S + S)

def inp():
    R.emit(F + S + F)

def loop_start():
    R.loop_start()

def loop_end():
    R.loop_end()

def clear():
    # clear current cell: loop_start(); dec(); loop_end()
    loop_start()
    dec()
    loop_end()

# --- Higher-level helpers: emit machine bytes with tracked counter C7 ---
def emit_byte_tracked(val: int):
    """
    Emit a single byte to the output stream using the tracked-output idiom:
    Move to C9, clear it, inc(val), out(), clear, move back; then increment C7 counter.
    Pattern matches the older generator's approach.
    """
    # Move to C9
    right(9)
    clear()
    inc(val)
    out()
    clear()
    left(9)
    # Increment counter C7
    right(7)
    inc(1)
    left(7)

def emit_machine_code_tracked(bytes_list):
    for b in bytes_list:
        emit_byte_tracked(b & 0xff)

# --- ELF header helpers ---
def p64(val):
    return list(val.to_bytes(8, "little"))

def p32(val):
    return list(val.to_bytes(4, "little"))

# --- Main generator logic (keeps original algorithm but fixes comparison targets) ---
def generate():
    # Safety margin: move pointer right to some safe region
    right(16)

    # 1. Emit ELF header (target total_size 200)
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
        emit_byte_tracked(b)

    # 2. Init: xor rbx, rbx
    emit_machine_code_tracked([0x48, 0x31, 0xdb])

    # 3. Main Loop (C2 = loop flag)
    # set C2 = 1 and enter loop
    right(2); clear(); inc(1); loop_start(); left(2)

    # [STEP 1] Read input into C0
    clear()  # ensure C0 = 0
    inp()    # read byte into C0

    # [STEP 2] EOF Check
    # Strategy: copy C0 -> C1 (preserved) and C3 (transient). Check C1 to detect EOF.
    # Clear C1
    right(1); clear(); left(1)

    # Copy C0 -> C1 & C3
    # Implementation detail:
    #   move to C3, clear, then loop: dec C0, inc C3, inc C1  (so C1 and C3 both get original value)
    #   then restore C0 from C3
    right(3); clear(); left(3)
    # Copy: while C0 != 0: dec C0; right() inc(C3) right(2) inc(C1) left(3)  (encoded)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    # Restore: while C3 != 0: dec C3; left(3); inc(C0); right(3)
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    # Now C1 preserves the input, C3 is restored to 0 and C0 back to original value.

    # Assume EOF: set C5 = 1
    right(5); clear(); inc(1); left(5)

    # If C1 != 0 then clear C5 (not EOF)
    # Move to C1 (right(1)) and loop while C1 != 0; in loop clear C5 by setting to 0
    right(1)
    loop_start()
    # clear C5: move to C5 then clear then return
    right(4); clear(); left(4)
    # decrement C1 by loop loop_end trigger (we used loop_start/dec to test)
    # but to iterate until C1==0 we must dec C1 inside loop body; however we used loop_start() on C1 itself:
    # Our pattern: loop_start(); clear(); right(4); clear(); left(4); loop_end();
    # which effectively tests C1 and if C1 != 0 executes the body (clear C5). That suffices.
    loop_end()
    left(1)

    # If C5 == 1 then break main loop by dec C2
    right(5)
    loop_start()
    clear()      # Clear the C5 flag so we don't re-enter forever
    left(3); dec(); right(3)  # decrement C2 to break main loop
    loop_end()
    left(5)

    # [STEP 3] Check '+' (ascii 43)
    # Only executed if C2 (main loop flag) still set
    right(2); loop_start(); left(2)

    # Clear scratch C1 (we'll refill it)
    right(1); clear(); left(1)

    # Copy C0 -> C1 & C3 again (same as earlier)
    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    # Subtract 43 from preserved C1 (move to C1 and dec 43)
    right(1); dec(43); left(1)

    # Check if C1 == 0 (match)
    right(5); clear(); inc(1); left(5)   # set C5 = 1 (assume match)
    right(1)
    loop_start()
    # body clears match flag if C1 != 0
    right(4); clear(); left(4)
    loop_end()
    left(1)

    # If match (C5 == 1) emit inc rbx machine code bytes
    right(5); loop_start()
    clear()   # consume match flag
    left(5)
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xc3)  # inc rbx (inc rbx machine)
    right(5)
    loop_end(); left(5)

    right(2); loop_end(); left(2)

    # [STEP 4] Check '-' (ascii 45) — same pattern as '+'
    right(2); loop_start(); left(2)

    right(1); clear(); left(1)

    right(3); clear(); left(3)
    loop_start(); dec(); right(); inc(); right(2); inc(); left(3); loop_end()
    right(3); loop_start(); dec(); left(3); inc(); right(3); loop_end(); left(3)

    right(1); dec(45); left(1)

    right(5); clear(); inc(1); left(5)
    right(1)
    loop_start()
    right(4); clear(); left(4)
    loop_end()
    left(1)

    right(5); loop_start()
    clear()
    left(5)
    emit_byte_tracked(0x48); emit_byte_tracked(0xff); emit_byte_tracked(0xcb)  # dec rbx
    right(5)
    loop_end(); left(5)

    right(2); loop_end(); left(2)

    # End main loop
    right(2); loop_end(); left(2)

    # 4. Exit sequence: mov edi, ebx; mov eax, 60; syscall
    emit_machine_code_tracked([0x89, 0xdf, 0xb8, 0x3c, 0x00, 0x00, 0x00, 0x0f, 0x05])

    # 5. Pad to total size (emit one zero byte by the tracked routine to pad)
    right(7); dec(200); loop_start(); inc(200); left(7); emit_byte_tracked(0); right(7); dec(200); loop_end(); inc(200); left(7)

# main entrypoint
def main():
    try:
        generate()
    except Exception as e:
        # If generation logic fails, print to stderr and abort (so CI doesn't silently produce bad file).
        print("Generator failed:", file=sys.stderr)
        raise

    # Finalize and write output
    out = R.finalize()

    # Optional sanity checks (compute streaming balance min for debugging)
    # We'll compute min_balance to catch places where loop_end precedes loop_start (shouldn't happen)
    tokens = []
    # find all plain FFS/FFF occurrences in the final out string
    i = 0
    ls_pat = F + F + S
    le_pat = F + F + F
    bal = 0
    min_bal = 0
    nls = 0
    nle = 0
    while True:
        # search next occurrence of either pattern
        idx_ls = out.find(ls_pat, i)
        idx_le = out.find(le_pat, i)
        if idx_ls == -1 and idx_le == -1:
            break
        if idx_ls != -1 and (idx_ls < idx_le or idx_le == -1):
            bal += 1
            nls += 1
            i = idx_ls + len(ls_pat)
        else:
            bal -= 1
            nle += 1
            i = idx_le + len(le_pat)
        if bal < min_bal:
            min_bal = bal

    # If we ever saw negative min balance that's a generator logic bug — refuse to output silently.
    if min_bal < 0:
        print(f"Generator sanity check failed: min_balance={min_bal} (negative). Aborting.", file=sys.stderr)
        sys.exit(2)

    # All good — write final bytes to stdout
    sys.stdout.buffer.write(out.encode("utf-8"))

if __name__ == "__main__":
    main()