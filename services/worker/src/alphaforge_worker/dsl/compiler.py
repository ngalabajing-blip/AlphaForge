"""
Tiny expression compiler — turns a string like ``cross_up(fast, slow)`` into
an AST node tree.

Supported tokens:

* numeric literals (``42``, ``3.14``)
* string literals (``"foo"``)
* booleans (``true``, ``false``)
* identifiers (``fast``, ``rsi_14``)
* function calls (``cross_up(a, b)``)
* binary operators: ``+ - * / % > < >= <= == != and or``
* unary operators: ``- not``
* parenthesised expressions

This is intentionally hand-written (no dependencies) so it stays auditable.
"""

from __future__ import annotations

import re

from alphaforge_shared.exceptions import StrategyParseError

from alphaforge_worker.dsl.ast import (
    BinOp,
    Bool,
    Expr,
    FunctionCall,
    Number,
    String,
    Symbol,
    UnaryOp,
)

_TOKEN_RE = re.compile(
    r"\s*(?:"
    r"(?P<NUMBER>\d+(?:\.\d+)?)"
    r"|(?P<STRING>'[^']*'|\"[^\"]*\")"
    r"|(?P<NAME>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<OP>>=|<=|==|!=|&&|\|\||[+\-*/%(),><=])"
    r")"
)
KEYWORDS_TRUE = {"true", "True", "yes"}
KEYWORDS_FALSE = {"false", "False", "no"}
LOGICAL = {"and", "or", "not"}
COMPARATORS = {">", "<", ">=", "<=", "==", "!="}


def _tokenise(expr: str) -> list[tuple[str, str]]:
    pos = 0
    tokens: list[tuple[str, str]] = []
    while pos < len(expr):
        m = _TOKEN_RE.match(expr, pos)
        if m is None or m.end() == pos:
            raise StrategyParseError(f"unexpected character at column {pos}: {expr[pos:pos+10]!r}")
        kind = m.lastgroup or ""
        value = m.group(kind) if kind else ""
        if kind == "NAME":
            if value in KEYWORDS_TRUE:
                tokens.append(("BOOL", "true"))
            elif value in KEYWORDS_FALSE:
                tokens.append(("BOOL", "false"))
            elif value in LOGICAL:
                tokens.append(("OP", value))
            else:
                tokens.append(("NAME", value))
        else:
            tokens.append((kind, value))
        pos = m.end()
    tokens.append(("EOF", ""))
    return tokens


# ── recursive-descent parser ──────────────────────────────────────────────────
class _Parser:
    def __init__(self, tokens: list[tuple[str, str]]) -> None:
        self.tokens = tokens
        self.i = 0

    def peek(self, n: int = 0) -> tuple[str, str]:
        return self.tokens[self.i + n] if self.i + n < len(self.tokens) else ("EOF", "")

    def consume(self) -> tuple[str, str]:
        t = self.peek()
        self.i += 1
        return t

    def expect(self, kind: str, value: str | None = None) -> tuple[str, str]:
        t = self.consume()
        if t[0] != kind or (value is not None and t[1] != value):
            raise StrategyParseError(f"expected {kind} {value or ''}, got {t}")
        return t

    # grammar:
    #   expr   := or_expr
    #   or     := and ( "or" and )*
    #   and    := not ( "and" not )*
    #   not    := "not" not | cmp
    #   cmp    := add ( ( "==" | "!=" | "<=" | ">=" | "<" | ">" ) add )*
    #   add    := mul ( ( "+" | "-" ) mul )*
    #   mul    := unary ( ( "*" | "/" | "%" ) unary )*
    #   unary  := "-" unary | atom
    #   atom   := NUMBER | STRING | BOOL | NAME ( "(" args ")" )? | "(" expr ")"

    def expr(self) -> Expr:
        return self.or_expr()

    def or_expr(self) -> Expr:
        left = self.and_expr()
        while self.peek() == ("OP", "or") or self.peek() == ("OP", "||"):
            self.consume()
            left = BinOp("or", left, self.and_expr())
        return left

    def and_expr(self) -> Expr:
        left = self.not_expr()
        while self.peek() == ("OP", "and") or self.peek() == ("OP", "&&"):
            self.consume()
            left = BinOp("and", left, self.not_expr())
        return left

    def not_expr(self) -> Expr:
        if self.peek() == ("OP", "not"):
            self.consume()
            return UnaryOp("not", self.not_expr())
        return self.cmp_expr()

    def cmp_expr(self) -> Expr:
        left = self.add_expr()
        while self.peek()[0] == "OP" and self.peek()[1] in COMPARATORS:
            op = self.consume()[1]
            left = BinOp(op, left, self.add_expr())
        return left

    def add_expr(self) -> Expr:
        left = self.mul_expr()
        while self.peek()[0] == "OP" and self.peek()[1] in ("+", "-"):
            op = self.consume()[1]
            left = BinOp(op, left, self.mul_expr())
        return left

    def mul_expr(self) -> Expr:
        left = self.unary_expr()
        while self.peek()[0] == "OP" and self.peek()[1] in ("*", "/", "%"):
            op = self.consume()[1]
            left = BinOp(op, left, self.unary_expr())
        return left

    def unary_expr(self) -> Expr:
        if self.peek() == ("OP", "-"):
            self.consume()
            return UnaryOp("-", self.unary_expr())
        return self.atom()

    def atom(self) -> Expr:
        kind, value = self.peek()
        if kind == "NUMBER":
            self.consume()
            return Number(float(value))
        if kind == "STRING":
            self.consume()
            return String(value[1:-1])
        if kind == "BOOL":
            self.consume()
            return Bool(value == "true")
        if kind == "NAME":
            self.consume()
            if self.peek() == ("OP", "("):
                self.consume()
                args: list[Expr] = []
                if self.peek() != ("OP", ")"):
                    args.append(self.expr())
                    while self.peek() == ("OP", ","):
                        self.consume()
                        args.append(self.expr())
                self.expect("OP", ")")
                return FunctionCall(value, tuple(args))
            return Symbol(value)
        if kind == "OP" and value == "(":
            self.consume()
            inner = self.expr()
            self.expect("OP", ")")
            return inner
        raise StrategyParseError(f"unexpected token {self.peek()}")


def compile_expression(expr: str) -> Expr:
    tokens = _tokenise(expr)
    p = _Parser(tokens)
    tree = p.expr()
    if p.peek()[0] != "EOF":
        raise StrategyParseError(f"trailing tokens after expression: {p.peek()}")
    return tree
