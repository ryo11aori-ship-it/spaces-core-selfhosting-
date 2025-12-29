import sys

# 0 = 半角スペース(U+0020), 1 = 全角スペース(U+3000)
MAPPING = {
    '>': '\u0020\u0020\u0020', # 000
    '<': '\u0020\u0020\u3000', # 001
    '+': '\u0020\u3000\u0020', # 010
    '-': '\u0020\u3000\u3000', # 011
    '.': '\u3000\u0020\u0020', # 100
    ',': '\u3000\u0020\u3000', # 101
    '[': '\u3000\u3000\u0020', # 110
    ']': '\u3000\u3000\u3000', # 111
}

def compile_to_spaces(bf_code):
    # マッピングにない文字は無視して連結
    return "".join(MAPPING[c] for c in bf_code if c in MAPPING)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # パイプ入力対応
        source = sys.stdin.read()
    else:
        # ファイル入力対応
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            source = f.read()
            
    result = compile_to_spaces(source)
    
    # 【重要修正】
    # 環境のエンコーディング設定を無視して、強制的にUTF-8のバイト列として出力する
    # これにより全角スペースが確実に書き込まれる
    sys.stdout.buffer.write(result.encode('utf-8'))
