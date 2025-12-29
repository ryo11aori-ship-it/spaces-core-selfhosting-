import sys

def main():
    bf = []
    cur = 0

    def emit(s):
        nonlocal cur
        bf.append(s)
        for c in s:
            if c == '>': cur += 1
            elif c == '<': cur -= 1

    def goto(i):
        nonlocal cur
        if i > cur: emit('>' * (i - cur))
        elif i < cur: emit('<' * (cur - i))
        cur = i

    def clear(i):
        goto(i); emit('[-]')

    def move(src, dst):
        clear(dst)
        goto(src); emit('[')
        emit('-')
        goto(dst); emit('+')
        goto(src); emit(']')

    def copy(src, dst, tmp):
        clear(dst); clear(tmp)
        goto(src); emit('[')
        emit('-')
        goto(dst); emit('+')
        goto(tmp); emit('+')
        goto(src); emit(']')
        move(tmp, src)

    IDX_OP = 0
    IDX_TMP = 1
    IDX_DONE = 2
    IDX_DATA = 3
    IDX_A = 4
    IDX_B = 5
    IDX_MATCH = 6
    IDX_SCAN = 7
    IDX_CHAR = 8
    IDX_COPY_TMP = 9
    IDX_IP_VALID = 10   # ★ NEW

    # Header
    goto(IDX_OP); emit(',,,')

    # First opcode
    goto(IDX_OP); emit(',')
    clear(IDX_IP_VALID); emit('+')  # IP_VALID = 1

    # Main loop: while IP_VALID != 0
    goto(IDX_IP_VALID); emit('[')

    # Copy opcode
    copy(IDX_OP, IDX_TMP, IDX_COPY_TMP)
    clear(IDX_DONE)

    def check(act):
        clear(IDX_A); emit('+')
        goto(IDX_DONE); emit('[')
        goto(IDX_A); emit('-')
        goto(IDX_DONE); emit('[-]+')
        emit(']')
        goto(IDX_A); emit('[')
        move(IDX_TMP, IDX_B)
        goto(IDX_B); emit('-')
        clear(IDX_MATCH); emit('+')
        goto(IDX_B); emit('[')
        goto(IDX_MATCH); emit('-')
        emit('-')
        goto(IDX_TMP); emit('+')
        goto(IDX_B); emit(']')
        goto(IDX_MATCH); emit('[')
        act()
        goto(IDX_DONE); emit('+')
        goto(IDX_MATCH); emit('-')
        emit(']')
        clear(IDX_A)
        emit(']')

    def act_plus(): goto(IDX_DATA); emit('+')
    def act_minus(): goto(IDX_DATA); emit('-')
    def act_dot(): goto(IDX_DATA); emit('.')
    def act_scan(): clear(IDX_SCAN); emit('+')

    check(lambda: None)
    check(lambda: None)
    check(act_plus)
    check(act_minus)
    check(act_dot)
    check(lambda: None)
    check(act_scan)
    check(lambda: None)

    # Read next opcode
    goto(IDX_OP); emit(',')

    # EOF check
    goto(IDX_IP_VALID); emit('[-]')
    goto(IDX_OP); emit('[')
    goto(IDX_IP_VALID); emit('+')
    goto(IDX_OP); emit(']')
    
    goto(IDX_IP_VALID); emit(']')

    S, F = " ", "\u3000"
    m = {'>':S*3,'<':S*2+F,'+':S+F+S,'-':S+F+F,'.':F+S+S,',':F+S+F,'[':F*2+S,']':F*3}
    print("".join(m[c] for c in bf if c in m), end='')

if __name__ == "__main__":
    main()