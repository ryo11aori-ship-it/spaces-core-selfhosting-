#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define TAPE_SIZE 30000
#define MAX_PROG 99999

unsigned char tape[TAPE_SIZE];
unsigned char *ptr = tape;
int op_map[8] = {'>', '<', '+', '-', '.', ',', '[', ']'}; // 000 to 111

// 全角スペース(UTF-8: E3 80 80)か判定
int is_full_space(unsigned char *s, int *idx) {
    if (s[*idx] == 0xE3 && s[*idx+1] == 0x80 && s[*idx+2] == 0x80) {
        *idx += 2; // 3バイト進める
        return 1;
    }
    return 0;
}

// SpacesコードをBF命令列に変換
int parse_line(char *input, char *output) {
    int out_idx = 0;
    int bit_buf = 0;
    int bit_cnt = 0;
    
    for (int i = 0; input[i] != 0; i++) {
        int bit = -1;
        if (input[i] == ' ') bit = 0; // 半角
        else if ((unsigned char)input[i] == 0xE3) { // 全角の可能性
            if (is_full_space((unsigned char*)input, &i)) bit = 1;
        }
        
        if (bit != -1) {
            bit_buf = (bit_buf << 1) | bit;
            bit_cnt++;
            if (bit_cnt == 3) {
                output[out_idx++] = op_map[bit_buf];
                bit_buf = 0;
                bit_cnt = 0;
            }
        }
    }
    output[out_idx] = 0;
    return out_idx;
}

// BF命令を実行
void run_bf(char *code) {
    char *pc = code;
    while (*pc) {
        switch (*pc) {
            case '>': ptr++; break;
            case '<': ptr--; break;
            case '+': (*ptr)++; break;
            case '-': (*ptr)--; break;
            case '.': putchar(*ptr); fflush(stdout); break;
            case ',': *ptr = getchar(); break;
            case '[':
                if (!*ptr) {
                    int loop = 1;
                    while (loop > 0) {
                        pc++;
                        if (*pc == '[') loop++;
                        if (*pc == ']') loop--;
                    }
                }
                break;
            case ']':
                if (*ptr) {
                    int loop = 1;
                    while (loop > 0) {
                        pc--;
                        if (*pc == '[') loop--;
                        if (*pc == ']') loop++;
                    }
                }
                break;
        }
        pc++;
    }
}

int main(int argc, char **argv) {
    ptr = tape; // リセット
    
    // ファイル実行モード
    if (argc > 1) {
        FILE *f = fopen(argv[1], "rb");
        if (!f) { perror("File not found"); return 1; }
        
        fseek(f, 0, SEEK_END);
        long fsize = ftell(f);
        fseek(f, 0, SEEK_SET);
        
        char *input = malloc(fsize + 1);
        fread(input, 1, fsize, f);
        fclose(f);
        input[fsize] = 0;

        char *bytecode = malloc(fsize); // 十分なサイズ
        parse_line(input, bytecode);
        run_bf(bytecode);
        
        free(input);
        free(bytecode);
        return 0;
    }

    // 対話モード (REPL)
    printf("Spaces VM v1.0 (Interactive Mode)\n");
    printf("Input Spaces code directly. (Ctrl+C to exit)\n");
    printf("Format: [Space]=0, [FullSpace]=1. 3 bits = 1 command.\n");
    printf("-----------------------------------------------------\n");

    char line[MAX_PROG];
    char bytecode[MAX_PROG];

    while (1) {
        printf("Spaces > ");
        if (!fgets(line, sizeof(line), stdin)) break;
        
        // 解析して実行
        if (parse_line(line, bytecode) > 0) {
            run_bf(bytecode);
            printf("\n"); // 出力後の改行
        }
    }

    return 0;
}
