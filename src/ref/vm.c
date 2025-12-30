#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAPE_SIZE 65536  /* 拡張: 30000 -> 64KB (アラインメント考慮) */
#define MAX_FILE_SIZE 1048576 /* 1MB limit for sanity */

unsigned char tape[TAPE_SIZE];
int ptr = 0; /* ポインタを int index に変更（境界チェックのため） */

/* op_map: index 0..7 => BF characters */
int op_map[8] = {'>', '<', '+', '-', '.', ',', '[', ']'};

void panic(const char *msg) {
    fprintf(stderr, "[VM Error] %s\n", msg);
    exit(1);
}

/* UTF-8 full-width space (U+3000) detection with Bounds Checking */
int is_full_space(unsigned char *s, int idx, int len) {
    if (idx + 2 >= len) return 0; /* Safety Check */
    if (s[idx] == 0xE3 && s[idx+1] == 0x80 && s[idx+2] == 0x80) {
        return 1;
    }
    return 0;
}

/* Parse textual Spaces source into BF ASCII bytes. */
int parse_line(char *input, int input_len, char *output, int max_out) {
    int out_idx = 0;
    int bit_buf = 0;
    int bit_cnt = 0;

    for (int i = 0; i < input_len && input[i] != 0; i++) {
        int bit = -1;
        unsigned char uc = (unsigned char)input[i];
        
        if (uc == 0x20) {
            bit = 0;
        } else if (uc == 0xE3) {
            if (is_full_space((unsigned char*)input, i, input_len)) {
                bit = 1;
                i += 2; /* Skip next 2 bytes safely */
            }
        }

        if (bit != -1) {
            bit_buf = (bit_buf << 1) | bit;
            bit_cnt++;
            if (bit_cnt == 3) {
                if (out_idx >= max_out - 1) panic("Output buffer overflow during parsing");
                output[out_idx++] = (char)op_map[bit_buf & 0x7];
                bit_buf = 0;
                bit_cnt = 0;
            }
        }
    }
    output[out_idx] = 0;
    return out_idx;
}

/* Execute BF code safely */
void run_bf(char *code) {
    char *pc = code;
    /* Reset tape and ptr */
    memset(tape, 0, sizeof(tape));
    ptr = 0;

    while (*pc) {
        switch (*pc) {
            case '>': 
                ptr++; 
                if (ptr >= TAPE_SIZE) panic("Tape pointer overflow (Right)");
                break;
            case '<': 
                ptr--; 
                if (ptr < 0) panic("Tape pointer underflow (Left)");
                break;
            case '+': 
                tape[ptr]++; 
                break;
            case '-': 
                tape[ptr]--; 
                break;
            case '.': 
                putchar(tape[ptr]); 
                fflush(stdout); 
                break;
            case ',': {
                int c = getchar();
                tape[ptr] = (c == EOF) ? 0 : c;
                break;
            }
            case '[':
                if (!tape[ptr]) {
                    int loop = 1;
                    while (loop > 0) {
                        pc++;
                        if (!*pc) panic("Unmatched '[' (missing ']')");
                        if (*pc == '[') loop++;
                        if (*pc == ']') loop--;
                    }
                }
                break;
            case ']':
                if (tape[ptr]) {
                    int loop = 1;
                    while (loop > 0) {
                        if (pc == code) panic("Unmatched ']' (missing '[')");
                        pc--;
                        if (*pc == '[') loop--;
                        if (*pc == ']') loop++;
                    }
                }
                break;
            default:
                break;
        }
        pc++;
    }
}

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *f = fopen(argv[1], "rb");
        if (!f) { perror("File open error"); return 1; }
        
        fseek(f, 0, SEEK_END); 
        long s = ftell(f); 
        fseek(f, 0, SEEK_SET);
        
        if (s < 0 || s > MAX_FILE_SIZE) { 
            fclose(f); 
            fprintf(stderr, "File too large or invalid\n"); 
            return 1; 
        }

        unsigned char *in = malloc(s + 1);
        if (!in) panic("Alloc fail (input)");
        
        size_t n = fread(in, 1, s, f);
        fclose(f);
        in[n] = 0;

        char *bc = malloc(s + 128); /* Buffer for decoded BF */
        if (!bc) panic("Alloc fail (bytecode)");

        /* Detect binary format: SPA */
        if (n >= 3 && in[0] == 'S' && in[1] == 'P' && in[2] == 'A') {
            size_t out_idx = 0;
            /* Start from index 3 (skip SPA) */
            for (long i = 3; i < n; i++) {
                unsigned char op = in[i];
                char mapped = 0;
                /* Validate Opcode Range 1-8 */
                if (op >= 1 && op <= 8) {
                    mapped = op_map[op - 1]; /* 1-based to 0-based index */
                }
                if (mapped) bc[out_idx++] = mapped;
            }
            bc[out_idx] = 0;
            run_bf(bc);
        } else {
            /* Textual Spaces */
            parse_line((char*)in, n, bc, s + 128);
            run_bf(bc);
        }

        free(in);
        free(bc);
        return 0;
    }

    /* Interactive Mode */
    fprintf(stderr, "Spaces REPL (Safe Mode)\n");
    char line[4096];
    char bc[4096];
    while (1) {
        if (!fgets(line, sizeof(line), stdin)) break;
        if (parse_line(line, strlen(line), bc, sizeof(bc)) > 0) {
            run_bf(bc);
            printf("\n");
        }
    }
    return 0;
}
