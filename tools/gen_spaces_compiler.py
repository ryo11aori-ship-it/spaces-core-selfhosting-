#!/usr/bin/env python3
# tools/gen_spaces_compiler.py
# 改良版：BF 命令以外をフィルタし、--debug で生成される Brainfuck を stderr に出力します。

import sys
import argparse

def build_bf(debug=False):
    bf = []
    BF_CHARS = set("><+-.,[]")
    def emit(s: str):
        # BF 命令文字のみ抽出して蓄える
        cleaned = "".join(ch for ch in s if ch in BF_CHARS)
        if cleaned:
            bf.append(cleaned)

    # --- optional small safety margin (keep small to avoid unexpected effects) ---
    # 十分大きくすると ELF の動作に影響する可能性があるため最小限にする（例: 8）。
    emit('>' * 8)

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
        # 出力してセルをクリアするのを統一（'.[-]'）
        if b:
            emit('+' * b + '.[-]')
        else:
            emit('.[-]')

    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code:
        if b:
            emit('+' * b + '.[-]')
        else:
            emit('.[-]')

    # --- Helper: Read ONE Valid Bit ---
    def read_valid_bit(weight: int):
        emit('[-]+[')
        emit(',')
        # Check EOF 0
        emit('[')
        # Check EOF 255
        # ブレース/スペースは取り除かれるため、トークン列を直接渡す
        emit('>[-]+<[- >-<]'.replace(' ', ''))
        # If 255 (C1=1), Exit All
        emit('>')
        emit('[>>>>>[-]<<<<<[-]<[-]]')
        emit('<')
        # Copy C0 -> C1
        emit('>>[-]<<[>>+>+<<<-]>>>[-<<<+>>>]<<')
        # Check S (32) on C1. Set C2=1 if Match.
        emit('>>[-]+<<')
        emit('>' + '-' * 32)
        emit('[')
        emit('[-]>[-]<')
        emit(']')
        # Recopy C0->C1
        emit('<[>>+>+<<<-]>>>[-<<<+>>>]<<')
        # Check F (227). Set C3=1 if Match.
        emit('>>>[-]+<<<')
        emit('>' + '-' * 227)
        emit('[')
        emit('[-]>>[-]<<')
        emit(']')
        # Check Flags C2/C3. If set, Clear C0 to Exit.
        emit('>')
        emit('[<<[-]>>-+]')
        emit('>')
        emit('[<<<[-]>>>-+]')
        emit('<<<')
        emit(']')
        emit(']')
        emit(']')
        # ACTION
        # If F (C3=1)
        emit('>>>')
        emit('[')
        # 入力を2回､加重を足す
        emit('[-]<<<<,,')
        emit('>>>>>' + '+' * weight + '<<<<<')
        emit('>>>')
        emit(']')
        # If S (C2=1)
        emit('<[-]')
        emit('<<')

    # --- MAIN LOOP ---
    emit('>>>>>>')
    emit('[-]+')
    emit('[')

    emit('<[-]')
    emit('<<<<<')

    read_valid_bit(4)
    emit('>>>>>>[<<<<<<')
    read_valid_bit(2)
    emit('>>>>>>[<<<<<<')
    read_valid_bit(1)
    emit('>>>>>>[<<<<<<')

    emit('>>>>>')

    def emit_bytes(bs):
        for b in bs:
            if not (0 <= b <= 0xFF):
                raise ValueError("byte value out of range: {!r}".format(b))
            # 出力 -> クリア -> 左へ戻す
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

    emit('>')
    emit(']]]')
    emit(']')

    # Padding (元のまま)
    emit('>>[-]' + '+' * 255 + '[>[-]' + '+' * 255 + '[>.<-]<-]')
    emit('>>[-]' + '+' * 255 + '[>[-]' + '+' * 255 + '[>.<-]<-]')

    # 結合して返す
    full_bf = "".join(bf)
    if debug:
        # human-readable な BF を stderr に出す（CI のログに出る）
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
    p.add_argument('--debug', action='store_true', help='emit generated Brainfuck to stderr for debugging')
    args = p.parse_args()

    full_bf = build_bf(debug=args.debug)
    out = bf_to_spaces(full_bf)
    sys.stdout.buffer.write(out.encode('utf-8'))

if __name__ == '__main__':
    main()