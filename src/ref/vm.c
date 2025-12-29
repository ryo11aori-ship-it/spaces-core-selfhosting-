#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAPE_SIZE 30000
#define MAX_PROG 99999

unsigned char tape[TAPE_SIZE];
unsigned char *ptr = tape;
int op_map[8] = {'>', '<', '+', '-', '.', ',', '[', ']'}; 

int is_full_space(unsigned char *s, int *idx) {
    if (s[*idx] == 0xE3 && s[*idx+1] == 0x80 && s[*idx+2] == 0x80) {
        *idx += 2; return 1;
    }
    return 0;
}

int parse_line(char *input, char *output) {
    int out_idx = 0, bit_buf = 0, bit_cnt = 0;
    for (int i = 0; input[i] != 0; i++) {
        int bit = -1;
        if (input[i] == ' ') bit = 0;
        else if ((unsigned char)input[i] == 0xE3) {
            if (is_full_space((unsigned char*)input, &i)) bit = 1;
        }
        if (bit != -1) {
            bit_buf = (bit_buf << 1) | bit;
            bit_cnt++;
            if (bit_cnt == 3) {
                output[out_idx++] = op_map[bit_buf];
                bit_buf = 0; bit_cnt = 0;
            }
        }
    }
    output[out_idx] = 0;
    return out_idx;
}

void run_bf(char *code) {
    char *pc = code;
    while (*pc) {
        switch (*pc) {
            case '>': ptr++; break;
            case '<': ptr--; break;
            case '+': (*ptr)++; break;
            case '-': (*ptr)--; break;
            case '.': putchar(*ptr); fflush(stdout); break;
            
            // ★ここを修正: EOF(-1)が来たら 0 を入れる
            case ',': {
                int c = getchar();
                *ptr = (c == EOF) ? 0 : c;
                break;
            }
            
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
    ptr = tape;
    if (argc > 1) {
        FILE *f = fopen(argv[1], "rb");
        if (!f) return 1;
        fseek(f,0,SEEK_END); long s=ftell(f); fseek(f,0,SEEK_SET);
        char *in = malloc(s+1); fread(in,1,s,f); fclose(f); in[s]=0;
        char *bc = malloc(s);
        parse_line(in, bc); run_bf(bc);
        free(in); free(bc);
        return 0;
    }
    // Interactive Mode
    char line[MAX_PROG], bc[MAX_PROG];
    while (1) {
        if (!fgets(line, sizeof(line), stdin)) break;
        if(parse_line(line, bc)>0) { run_bf(bc); printf("\n"); }
    }
    return 0;
}
