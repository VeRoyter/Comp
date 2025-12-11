import re

class TokenType:
    # Базовые
    EOF = 'EOF'
    NUMBER = 'NUMBER'
    IDENT = 'IDENT'

    # Операторы
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    ASSIGN = 'ASSIGN'      # :=
    EQ = 'EQ'              # =
    LT = 'LT'              # <
    GT = 'GT'              # >
    LE = 'LE'              # <=
    GE = 'GE'              # >=
    NE = 'NE'              # <>

    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    SEMICOLON = 'SEMICOLON'
    COLON = 'COLON'
    COMMA = 'COMMA'

    # Ключевые слова
    VAR = 'VAR'
    INTEGER = 'INTEGER_TYPE'
    REAL = 'REAL_TYPE'
    IF = 'IF'
    THEN = 'THEN'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    DO = 'DO'
    FOR = 'FOR'
    TO = 'TO'
    PROCEDURE = 'PROCEDURE'
    BEGIN = 'BEGIN'
    END = 'END'
    WRITELN = 'WRITELN'
    READLN = 'READLN'


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f"Token({self.type}, {self.value})"
        return f"Token({self.type})"


class Lexer:
    KEYWORDS = {
        "var": TokenType.VAR,
        "integer": TokenType.INTEGER,
        "real": TokenType.REAL,
        "if": TokenType.IF,
        "then": TokenType.THEN,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "do": TokenType.DO,
        "for": TokenType.FOR,
        "to": TokenType.TO,
        "procedure": TokenType.PROCEDURE,
        "begin": TokenType.BEGIN,
        "end": TokenType.END,
        "writeln": TokenType.WRITELN,
        "readln": TokenType.READLN,
    }

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[0] if text else None

    def error(self):
        raise Exception(f"Unexpected character: '{self.current_char}'")

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def number(self):
        s = ""
        while self.current_char and (self.current_char.isdigit() or self.current_char == "."):
            s += self.current_char
            self.advance()
        return Token(TokenType.NUMBER, float(s) if "." in s else int(s))

    def identifier(self):
        s = ""
        while self.current_char and (self.current_char.isalnum() or self.current_char == "_"):
            s += self.current_char
            self.advance()

        lower = s.lower()
        if lower in self.KEYWORDS:
            return Token(self.KEYWORDS[lower])

        return Token(TokenType.IDENT, s)

    def get_next_token(self):
        while self.current_char:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha() or self.current_char == "_":
                return self.identifier()

            if self.current_char.isdigit():
                return self.number()

            # :=
            if self.current_char == ":":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    return Token(TokenType.ASSIGN)
                return Token(TokenType.COLON)

            # =
            if self.current_char == "=":
                self.advance()
                return Token(TokenType.EQ)

            # <>
            if self.current_char == "<":
                self.advance()
                if self.current_char == ">":
                    self.advance()
                    return Token(TokenType.NE)
                if self.current_char == "=":
                    self.advance()
                    return Token(TokenType.LE)
                return Token(TokenType.LT)

            # >
            if self.current_char == ">":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    return Token(TokenType.GE)
                return Token(TokenType.GT)

            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS)

            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS)

            if self.current_char == "*":
                self.advance()
                return Token(TokenType.MULTIPLY)

            if self.current_char == "/":
                self.advance()
                return Token(TokenType.DIVIDE)

            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN)

            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN)

            if self.current_char == ";":
                self.advance()
                return Token(TokenType.SEMICOLON)

            if self.current_char == ",":
                self.advance()
                return Token(TokenType.COMMA)

            self.error()

        return Token(TokenType.EOF)
