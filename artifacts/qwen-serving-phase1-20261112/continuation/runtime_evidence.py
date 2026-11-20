"""Read effective llama runtime settings, not an environment flag or one wording."""
import re


def fa_enabled(log):
    match=re.search(r'(?m)^llama_context:\s*flash_attn\s*=\s*(\w+)\s*$',log)
    if not match:return False
    mode=match.group(1)
    if mode=='enabled':return True
    return mode=='auto' and bool(re.search(r'(?m)^resolve_fused_ops: Flash Attention enabled\s*$',log))
