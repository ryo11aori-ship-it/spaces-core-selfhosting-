#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAPE_SIZE 30000
#define MAX_PROG 99999

unsigned char tape[TAPE_SIZE];
unsigned char *ptr = tape;

/* op_map: index 0..7 => BF characters for bits-based parsing (Spaces -> BF) */
int op_map[8] = {'>', '<', '+', '-', '.', ',', '[', ']'};

/* UTF-8 full-width space (U+3000) detection used for Spaces parsing */
int is_full_space(unsigned char *s, int *idx) {
    /* ensure we don't read past buffer in callers: callers pass valid bounds */
    if ((unsigned char)s[*idx] == 0xE3 && (unsigned char)s[*idx+1] == 0x80 && (unsigned char)s[*idx+2] == 0x80) {
        *idx += 2; /* outer loop will increment once more -> skip 3 bytes total */
        return 1;
    }
    return 0;
}

/* Parse textual Spaces source into BF ASCII bytes.
   input: null-terminated buffer containing Spaces text (mix of 0x20 and 0xE3 0x80 0x80 sequences).
   output: buffer to write BF ASCII chars; must be large enough.
   returns: number of BF bytes written.
*/
int parse_line(char *input, char *output) {
    int out_idx = 0, bit_buf = 0, bit_cnt = 0;
    for (int i = 0; input[i] != 0; i++) {
        int bit = -1;
        unsigned char uc = (unsigned char)input[i];
        if (uc == 0x20) bit = 0; /* half-width space */
        else if (uc == 0xE3) {
            if (is_full_space((unsigned char*)input, &i)) bit = 1;
        }
        if (bit != -1) {
            bit_buf = (bit_buf << 1) | bit;
            bit_cnt++;
            if (bit_cnt == 3) {
                /* map 3-bit value 0..7 to BF char using op_map */
                output[out_idx++] = (char)op_map[bit_buf & 0x7];
                bit_buf = 0; bit_cnt = 0;
            }
        }
    }
    output[out_idx] = 0;
    return out_idx;
}

/* Execute BF code (null-terminated ASCII with characters <>+-.,[]). */
void run_bf(char *code) {
    char *pc = code;
    /* tape is global; ptr points into tape */
    while (*pc) {
        switch (*pc) {
            case '>': ptr++; break;
            case '<': ptr--; break;
            case '+': (*ptr)++; break;
            case '-': (*ptr)--; break;
            case '.': putchar(*ptr); fflush(stdout); break;
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
            default:
                /* ignore other bytes (safety) */
                break;
        }
        pc++;
    }
}

int main(int argc, char **argv) {
    /* ensure tape starts zeroed; global arrays are zero-initialized by C,
       but be explicit in case of static analysis / reuse */
    memset(tape, 0, sizeof(tape));
    ptr = tape;

    if (argc > 1) {
        FILE *f = fopen(argv[1], "rb");
        if (!f) { perror("File open error"); return 1; }
        fseek(f,0,SEEK_END); long s=ftell(f); fseek(f,0,SEEK_SET);
        if (s < 0) { fclose(f); return 1; }

        /* read file (binary-safe) */
        unsigned char *in = malloc(s + 1);
        if (!in) { fclose(f); fprintf(stderr,"alloc fail\n"); return 1; }
        size_t n = fread(in,1,s,f);
        fclose(f);
        in[n] = 0; /* null-terminate so parse_line can treat as string if needed */

        /* prepare buffer for BF ASCII code */
        char *bc = malloc((s + 16)); /* s is upper bound; +16 for safety and NUL */
        if (!bc) { free(in); fprintf(stderr,"alloc fail\n"); return 1; }

        /* Detect binary compiled format: starts with "SPA" */
        if (n >= 3 && in[0] == 'S' && in[1] == 'P' && in[2] == 'A') {
            /* Map subsequent opcode bytes (1..8) to BF ASCII characters */
            size_t out_idx = 0;
            for (long i = 3; i < n; i++) {
                unsigned char op = in[i];
                char mapped = 0;
                switch (op) {
                    case 0x01: mapped = '>'; break; /* INC_PTR */
                    case 0x02: mapped = '<'; break; /* DEC_PTR */
                    case 0x03: mapped = '+'; break; /* INC_VAL */
                    case 0x04: mapped = '-'; break; /* DEC_VAL */
                    case 0x05: mapped = '.'; break; /* OUT */
                    case 0x06: mapped = ','; break; /* IN */
                    case 0x07: mapped = '['; break; /* JMP_FWD */
                    case 0x08: mapped = ']'; break; /* JMP_BCK */
                    default:
                        /* ignore unknown bytes (skip) */
                        mapped = 0;
                        break;
                }
                if (mapped) bc[out_idx++] = mapped;
            }
            bc[out_idx] = 0;
            /* run BF from bc */
            run_bf(bc);
        } else {
            /* Treat as textual Spaces source (existing behavior) */
            parse_line((char*)in, bc);
            run_bf(bc);
        }

        free(in);
        free(bc);
        return 0;
    }

    /* Interactive Mode: read lines from stdin as Spaces source */
    char line[MAX_PROG], bc[MAX_PROG];
    while (1) {
        if (!fgets(line, sizeof(line), stdin)) break;
        if(parse_line(line, bc) > 0) { run_bf(bc); printf("\n"); }
    }
    return 0;
}