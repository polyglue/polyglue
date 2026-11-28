import json
from importlib.resources import files

from lark import Lark, Tree


_PARSER = Lark(files("polyglue").joinpath("idl.lark").read_text(encoding="utf-8"), parser="lalr", lexer="basic", propagate_positions=True)


def parse_idl(source: str, *, max_bytes: int = 16 * 1024 * 1024, max_depth: int = 256) -> Tree:
    if max_bytes <= 0 or max_depth <= 0:
        raise ValueError("IDL limits must be positive")

    if len(source) > max_bytes or len(source.encode("utf-8")) > max_bytes:
        raise ValueError("IDL input exceeds the byte limit")

    depth = 0

    for token in _PARSER.lex(source):
        if token.type == "STRING":
            json.loads(token).encode("utf-8")
        elif token.value in ("<", "{", "[", "("):
            depth += 1

            if depth > max_depth:
                raise ValueError(f"IDL nesting limit exceeded at {token.line}:{token.column}")
        elif token.value in (">", "}", "]", ")"):
            depth -= 1

            if depth < 0:
                raise ValueError(f"Unmatched closing delimiter at {token.line}:{token.column}")

    return _PARSER.parse(source)
