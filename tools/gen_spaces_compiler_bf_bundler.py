#!/usr/bin/env python3
import sys

ptr = 0

def e(s):
    sys.stdout.write(s)

def move_to(target):
    global ptr
    if target > ptr:
        e(">" * (target - ptr))
    if target < ptr:
        e("<" * (ptr - target))
    ptr = target

def set_val(addr, val):
    move_to(addr)
    e("[-]")
    e("+" * val)

def add_val(addr, val):
    move_to(addr)
    e("+" * val)

def sub_val(addr, val):
    move_to(addr)
    e("-" * val)

def copy(src, dst, tmp):
    move_to(tmp)
    e("[-]")
    move_to(dst)
    e("[-]")
    move_to(src)
    e("[")
    move_to(dst)
    e("+")
    move_to(tmp)
    e("+")
    move_to(src)
    e("-")
    e("]")
    move_to(tmp)
    e("[")
    move_to(src)
    e("+")
    move_to(tmp)
    e("-")
    e("]")

def emit_elf_bytes_bf(byte_arr):
    for b in byte_arr:
        move_to(20)
        e("[-]")
        e("+" * b)
        e(".")

def main():
    elf_header = [
        0x7f, 0x45, 0x4c, 0x46, 0x02, 0x01, 0x01, 0x00, 0,0,0,0,0,0,0,0,
        0x02, 0x00, 0x3e, 0x00, 0x01, 0x00, 0x00, 0x00,
        0x78, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0,0,0,0,0,0,0,0,
        0,0,0,0, 64,0, 56,0, 1,0, 64,0, 0,0, 0,0,
        0x01, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0,0,0,0,0,0,0,0,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    interpreter = [
        0x49, 0xC7, 0xC5, 0x00, 0x00, 0x50, 0x00,
        0x49, 0xC7, 0xC4, 0x00, 0x02, 0x40, 0x00,
        0x41, 0x0F, 0xB6, 0x04, 0x24,
        0x49, 0xFF, 0xC4,
        0x84, 0xC0,
        0x0F, 0x84, 0xB7, 0x00, 0x00, 0x00,
        0x3C, 0x2B,
        0x75, 0x04,
        0x41, 0xFE, 0x45, 0x00,
        0x3C, 0x2D,
        0x75, 0x04,
        0x41, 0xFE, 0x4D, 0x00,
        0x3C, 0x3E,
        0x75, 0x03,
        0x49, 0xFF, 0xC5,
        0x3C, 0x3C,
        0x75, 0x03,
        0x49, 0xFF, 0xCD,
        0x3C, 0x2E,
        0x75, 0x14,
        0xB8, 0x01, 0x00, 0x00, 0x00,
        0xBF, 0x01, 0x00, 0x00, 0x00,
        0x4C, 0x89, 0xEE,
        0xBA, 0x01, 0x00, 0x00, 0x00,
        0x0F, 0x05,
        0x3C, 0x2C,
        0x75, 0x18,
        0x31, 0xC0,
        0x31, 0xFF,
        0x4C, 0x89, 0xEE,
        0xBA, 0x01, 0x00, 0x00, 0x00,
        0x0F, 0x05,
        0x48, 0x85, 0xC0,
        0x7F, 0x05,
        0x41, 0xC6, 0x45, 0x00, 0x00,
        0x3C, 0x5B,
        0x75, 0x28,
        0x41, 0x80, 0x7D, 0x00, 0x00,
        0x75, 0x21,
        0x41, 0xBE, 0x01, 0x00, 0x00, 0x00,
        0x41, 0x0F, 0xB6, 0x04, 0x24,
        0x49, 0xFF, 0xC4,
        0x3C, 0x5B,
        0x75, 0x03,
        0x41, 0xFF, 0xC6,
        0x3C, 0x5D,
        0x75, 0x03,
        0x41, 0xFF, 0xCE,
        0x4D, 0x85, 0xF6,
        0x75, 0xE5,
        0x3C, 0x5D,
        0x75, 0x30,
        0x41, 0x80, 0x7D, 0x00, 0x00,
        0x74, 0x29,
        0x49, 0x83, 0xEC, 0x02,
        0x41, 0xBE, 0x01, 0x00, 0x00, 0x00,
        0x41, 0x0F, 0xB6, 0x04, 0x24,
        0x49, 0xFF, 0xCC,
        0x3C, 0x5D,
        0x75, 0x03,
        0x41, 0xFF, 0xC6,
        0x3C, 0x5B,
        0x75, 0x03,
        0x41, 0xFF, 0xCE,
        0x4D, 0x85, 0xF6,
        0x75, 0xE5,
        0x49, 0x83, 0xC4, 0x02,
        0xE9, 0x39, 0xFF, 0xFF, 0xFF,
        0xB8, 0x3C, 0x00, 0x00, 0x00,
        0x31, 0xFF,
        0x0F, 0x05
    ]
    header_data = elf_header + interpreter
    pad_len = 512 - len(header_data)
    header_data += [0] * pad_len
    emit_elf_bytes_bf(header_data)
    
    set_val(0, 0)
    set_val(1, 0)
    move_to(2)
    e(",")
    e("[")
    
    set_val(6, 0)
    set_val(7, 0)
    
    copy(2, 3, 4)
    sub_val(3, 32)
    set_val(5, 1)
    move_to(3)
    e("[")
    set_val(5, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(5)
    e("[")
    set_val(6, 0)
    set_val(7, 1)
    move_to(5)
    e("[-]")
    e("]")
    
    copy(2, 3, 4)
    sub_val(3, 227)
    set_val(5, 1)
    move_to(3)
    e("[")
    set_val(5, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(5)
    e("[")
    set_val(6, 1)
    set_val(7, 1)
    
    move_to(2)
    e("[-]")
    e(",")
    e("[-]")
    e(",")
    
    move_to(5)
    e("[-]")
    e("]")
    
    move_to(7)
    e("[")
    
    move_to(3)
    e("[-]")
    move_to(1)
    e("[")
    move_to(3)
    e("++")
    move_to(1)
    e("-")
    e("]")
    move_to(1)
    e("[-]")
    move_to(3)
    e("[")
    move_to(1)
    e("+")
    move_to(3)
    e("-")
    e("]")
    
    move_to(6)
    e("[")
    move_to(1)
    e("+")
    move_to(6)
    e("-")
    e("]")
    
    add_val(0, 1)
    
    copy(0, 3, 4)
    sub_val(3, 3)
    set_val(5, 1)
    move_to(3)
    e("[")
    set_val(5, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(5)
    e("[")
    
    copy(1, 3, 4)
    set_val(8, 1)
    move_to(3)
    e("[")
    set_val(8, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(8)
    e("[")
    emit_elf_bytes_bf([ord('>')])
    move_to(8)
    e("[-]")
    e("]")
    
    copy(1, 3, 4)
    sub_val(3, 1)
    set_val(8, 1)
    move_to(3)
    e("[")
    set_val(8, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(8)
    e("[")
    emit_elf_bytes_bf([ord('<')])
    move_to(8)
    e("[-]")
    e("]")
    
    copy(1, 3, 4)
    sub_val(3, 2)
    set_val(8, 1)
    move_to(3)
    e("[")
    set_val(8, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(8)
    e("[")
    emit_elf_bytes_bf([ord('+')])
    move_to(8)
    e("[-]")
    e("]")
    
    copy(1, 3, 4)
    sub_val(3, 3)
    set_val(8, 1)
    move_to(3)
    e("[")
    set_val(8, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(8)
    e("[")
    emit_elf_bytes_bf([ord('-')])
    move_to(8)
    e("[-]")
    e("]")
    
    copy(1, 3, 4)
    sub_val(3, 4)
    set_val(8, 1)
    move_to(3)
    e("[")
    set_val(8, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(8)
    e("[")
    emit_elf_bytes_bf([ord('.')])
    move_to(8)
    e("[-]")
    e("]")
    
    copy(1, 3, 4)
    sub_val(3, 5)
    set_val(8, 1)
    move_to(3)
    e("[")
    set_val(8, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(8)
    e("[")
    emit_elf_bytes_bf([ord(',')])
    move_to(8)
    e("[-]")
    e("]")
    
    copy(1, 3, 4)
    sub_val(3, 6)
    set_val(8, 1)
    move_to(3)
    e("[")
    set_val(8, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(8)
    e("[")
    emit_elf_bytes_bf([ord('[')])
    move_to(8)
    e("[-]")
    e("]")
    
    copy(1, 3, 4)
    sub_val(3, 7)
    set_val(8, 1)
    move_to(3)
    e("[")
    set_val(8, 0)
    move_to(3)
    e("[-]")
    e("]")
    move_to(8)
    e("[")
    emit_elf_bytes_bf([ord(']')])
    move_to(8)
    e("[-]")
    e("]")
    
    set_val(0, 0)
    set_val(1, 0)
    move_to(5)
    e("[-]")
    e("]")
    
    move_to(7)
    e("[-]")
    e("]")
    
    move_to(2)
    e("[-]")
    e(",")
    e("]")

if __name__ == "__main__":
    main()
