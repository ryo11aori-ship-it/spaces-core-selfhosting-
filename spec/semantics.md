# Operational Semantics (Small-Step)

State is defined as `(C, M, dp, ip)` where:
- `C`: Code (Instruction sequence)
- `M`: Memory (Tape)
- `dp`: Data Pointer (Index in M)
- `ip`: Instruction Pointer (Index in C)

## Transition Rules (Linear Subset)

1. **VAL_INC (+)**: `⟨..., +, ...⟩, (M, dp) → ⟨...⟩, (M[dp] + 1, dp)`
2. **VAL_DEC (-)**: `⟨..., -, ...⟩, (M, dp) → ⟨...⟩, (M[dp] - 1, dp)`
3. **PTR_INC (>)**: `⟨..., >, ...⟩, (M, dp) → ⟨...⟩, (M, dp + 1)`
4. **PTR_DEC (<)**: `⟨..., <, ...⟩, (M, dp) → ⟨...⟩, (M, dp - 1)`
5. **OUTPUT (.)**: `⟨..., ., ...⟩, (M, dp) → ⟨...⟩, (M, dp)` *Emit M[dp]*
