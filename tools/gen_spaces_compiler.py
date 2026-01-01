# tools/gen_spaces_compiler.py — 修正版（CI 用）
import sys

def main():
    bf = []

    # BF 命令文字のみを受け取るフィルタ付き emit
    BF_CHARS = set("><+-.,[]")
    def emit(s: str):
        cleaned = "".join(ch for ch in s if ch in BF_CHARS)
        if cleaned:
            bf.append(cleaned)

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
        if b:
            emit('+' * b + '.[-]')
        else:
            emit('.')

    init_code = [0x49, 0xbd, 0x00, 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00]
    for b in init_code:
        if b:
            emit('+' * b + '.[-]')
        else:
            emit('.')

    # --- Helper: Read ONE Valid Bit ---
    def read_valid_bit(weight: int):
        emit('[-]+[')
        emit(',')
        # Check EOF 0
        emit('[')
        # Check EOF 255
        emit('>[-]+<[- >-<]'.replace(' ', ''))  # keep exact BF tokens
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
        emit('[-]<<<<,,')   # input twice
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

    # Padding
    emit('>>[-]' + '+' * 255 + '[>[-]' + '+' * 255 + '[>.<-]<-]')
    emit('>>[-]' + '+' * 255 + '[>[-]' + '+' * 255 + '[>.<-]<-]')

    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    full_bf = "".join(bf)
    sys.stdout.buffer.write("".join([mapping.get(c, '') for c in full_bf]).encode('utf-8'))


if __name__ == "__main__":
    main()