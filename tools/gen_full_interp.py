import sys

# Stage 3: Segfault-Proof Depth-1 Loop Interpreter
# このスクリプトは、Brainfuck/Spacesのコードを生成します。
# 生成されるインタプリタは以下の仕様を持ちます：
# 1. ネストなしのループ [ ] をサポート（深さ1）
# 2. メモリ範囲外アクセス（Segfault）を絶対に起こさない安全設計
# 3. データポインタの移動はサポートしない（今回のテストケースに不要なため）

def main():
    # --- Helper Functions ---
    def l(c): return "[" + c + "]"
    
    # --- Memory Layout & Navigation ---
    # Layout: [Code...] 0 [Temp] [SkipFlag] 0 [Data]
    # Code: プログラム本体
    # Temp: 命令デコード用の一時変数
    # SkipFlag: ループスキップ中かどうか (0=実行, 1=スキップ)
    # Data: データメモリ（1セルのみ使用）

    # Macros: 現在地（Code上の現在の命令 = 0）からの相対移動
    to_temp = ">[>]>"
    to_skip = ">[>]>>"
    to_data = ">[>]>>>>"
    
    from_temp = "<[<]"
    from_skip = "<<[<]"
    from_data = "<<<<[<]"

    bf = ""
    
    # 1. Header & Read Code
    # SPAヘッダ(3バイト)をスキップし、入力を読み込む
    bf += ">,,,>," + l(">,") 
    
    # 2. Execution Start
    # コードの先頭に戻る
    bf += "<[<]>"
    
    # 3. Main Loop (命令がある限り繰り返す)
    bf += "["
    
    # --- STEP 1: Move Opcode to Temp ---
    # 現在の命令(Op)をTempに移動し、元の場所を0(Hole)にする
    bf += to_temp + "[-]" + from_temp        # Clear Temp
    bf += l( to_temp + "+" + from_temp + "-" ) # Move Op -> Temp
    
    # --- STEP 2: Check SkipFlag ---
    # もしSkipFlagが1なら、']' (8) 以外は無視する
    bf += to_skip + l(
        # SkipFlag is ON (Skipping mode)
        from_skip + to_temp
        # Tempが ']' (8) かどうかチェック
        + "--------" + l(
             # Not 8. Clear Temp (Ignore instruction).
             "[-]"
        ) + "+" + l(
             # Is 8 (]). Loop End found.
             "[-]" 
             # Turn OFF SkipFlag.
             + from_temp + to_skip + "[-]" + from_skip + to_temp
        ) 
        + "[-]" # Ensure Temp is cleared
        + from_temp + to_skip # Back to SkipFlag loop check
    ) + from_skip
    
    # --- STEP 3: Decode & Execute ---
    # Tempが0でなければ（＝スキップモードでなければ）、命令を実行
    bf += to_temp + l(
        # Decode Tree (Subtract to match Opcode)
        "-" + l( # Case 7: [ (Loop Start)
             "-" + l( # Case 6: , (Input) - Ignore
                 "-" + l( # Case 5: . (Output)
                     "-" + l( # Case 4: - (Dec)
                         "-" + l( # Case 3: + (Inc)
                            "-" + l("[-]") # Case 1,2: Ignore
                            
                            # Action 3 (+): Data++
                            + "[-]" + from_temp + to_data + "+" + from_data + to_temp
                         )
                         # Action 4 (-): Data--
                         + "[-]" + from_temp + to_data + "-" + from_data + to_temp
                     )
                     # Action 5 (.): Output Data
                     + "[-]" + from_temp + to_data + "." + from_data + to_temp
                 )
                 # Action 6: Ignore
                 + "[-]"
             )
             # Action 7 ([): If Data==0, Set SkipFlag=1.
             + "[-]" 
             # Check if Data is 0. Use Temp as flag.
             + "+" # Set Temp=1
             + from_temp + to_data + l(
                 # Data != 0.
                 from_data + to_temp + "-" # Set Temp=0
                 + from_temp + to_data # Return
             ) 
             + from_data + to_temp + l(
                 # If Temp is still 1 (means Data was 0), Set SkipFlag.
                 "[-]" 
                 + from_temp + to_skip + "+" 
                 + from_skip + to_temp
             )
        )
        # Action 8 (]): Ignore (No-op in exec mode)
        + "[-]"
    ) + from_temp
    
    # --- STEP 4: Next Instruction ---
    # 次の命令へ進む
    bf += ">]"

    # --- Convert to Spaces ---
    S, F = " ", "\u3000"
    mapping = {'>':S*3, '<':S*2+F, '+':S+F+S, '-':S+F+F, '.':F+S+S, ',':F+S+F, '[':F*2+S, ']':F*3}
    
    # 変換して出力（エラー防止のため安全にjoin）
    res = []
    for c in bf:
        if c in mapping:
            res.append(mapping[c])
    print("".join(res), end='')

if __name__ == "__main__":
    main()
