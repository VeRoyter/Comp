#lexernew.py
import re
from errors import LexerError

class TokenType:
    # Базовые
    EOF = 'EOF'
    NUMBER = 'NUMBER'
    IDENT = 'IDENT'
    STRING = 'STRING'
    BOOL = 'BOOL'

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

    # Логические операторы
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'

    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    SEMICOLON = 'SEMICOLON'
    COLON = 'COLON'
    COMMA = 'COMMA'
    LBRACKET = 'LBRACKET'  # [
    RBRACKET = 'RBRACKET'  # ]

    # Ключевые слова
    VAR = 'VAR'
    INTEGER = 'INTEGER_TYPE'
    REAL = 'REAL_TYPE'
    BOOLEAN = 'BOOLEAN_TYPE'
    STRING_TYPE = 'STRING_TYPE'
    ARRAY = 'ARRAY'
    OF = 'OF'
    IF = 'IF'
    THEN = 'THEN'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    DO = 'DO'
    FOR = 'FOR'
    TO = 'TO'
    PROCEDURE = 'PROCEDURE'
    FUNCTION = 'FUNCTION'
    BEGIN = 'BEGIN'
    END = 'END'
    WRITELN = 'WRITELN'
    READLN = 'READLN'
    TRUE = 'TRUE'
    FALSE = 'FALSE'

    COMMENT = 'COMMENT'
    RANGE = 'RANGE'
    DOT = 'DOT'

class Token:
    def __init__(self, type_, value=None, lineno=None, column=None):
        self.type = type_
        self.value = value
        self.lineno = lineno
        self.column = column

    def __repr__(self):
        val = f", {self.value}" if self.value else ""
        return f"Token({self.type}{val}, pos={self.lineno}:{self.column})"


class Lexer:
    KEYWORDS = {
        "var": TokenType.VAR,
        "integer": TokenType.INTEGER,
        "real": TokenType.REAL,
        "boolean": TokenType.BOOLEAN,
        "string": TokenType.STRING_TYPE,
        "array": TokenType.ARRAY,
        "of": TokenType.OF,
        "if": TokenType.IF,
        "then": TokenType.THEN,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "do": TokenType.DO,
        "for": TokenType.FOR,
        "to": TokenType.TO,
        "procedure": TokenType.PROCEDURE,
        "function": TokenType.FUNCTION,
        "begin": TokenType.BEGIN,
        "end": TokenType.END,
        "writeln": TokenType.WRITELN,
        "readln": TokenType.READLN,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
    }

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[0] if text else None
        self.lineno = 1
        self.column = 1

    def error(self):
        raise LexerError((self.lineno, self.column), f"Unexpected character: '{self.current_char}'")

    def advance(self):
        if self.current_char == '\n':
            self.lineno += 1
            self.column = 0  # Станет 1 после инкремента в конце

        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            self.column += 1
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def comment(self):
        line = self.lineno
        col = self.column
        text = ""

        # { comment }
        if self.current_char == '{':
            self.advance()
            while self.current_char and self.current_char != '}':
                text += self.current_char
                self.advance()
            if self.current_char == '}':
                self.advance()
            return Token(TokenType.COMMENT, text.strip(), line, col)

        # // comment
        if self.current_char == '/' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '/':
            self.advance()
            self.advance()
            while self.current_char and self.current_char != '\n':
                text += self.current_char
                self.advance()
            return Token(TokenType.COMMENT, text.strip(), line, col)


    def number(self):
        line = self.lineno
        col = self.column
        s = ""

        while self.current_char and self.current_char.isdigit():
            s += self.current_char
            self.advance()

        # Проверяем дробную часть
        if self.current_char == ".":
            # ⚠️ ВАЖНО: если это '..' — НЕ часть числа
            if self.pos + 1 < len(self.text) and self.text[self.pos + 1] == ".":
                return Token(TokenType.NUMBER, int(s), line, col)

            # иначе это вещественное число
            s += "."
            self.advance()

            while self.current_char and self.current_char.isdigit():
                s += self.current_char
                self.advance()

            return Token(TokenType.NUMBER, float(s), line, col)

        return Token(TokenType.NUMBER, int(s), line, col)



    def string(self):
        """Обработка строкового литерала в кавычках"""
        line = self.lineno
        col = self.column
        s = ""
        quote_char = self.current_char  # ' или "
        self.advance()  # skip opening quote
        
        while self.current_char and self.current_char != quote_char:
            if self.current_char == '\\' and self.pos + 1 < len(self.text):
                # Обработка escape-последовательностей
                self.advance()
                if self.current_char == 'n':
                    s += '\n'
                elif self.current_char == 't':
                    s += '\t'
                elif self.current_char == '\\':
                    s += '\\'
                elif self.current_char == quote_char:
                    s += quote_char
                else:
                    s += self.current_char
            else:
                s += self.current_char
            self.advance()
        
        if self.current_char == quote_char:
            self.advance()  # skip closing quote
        
        return Token(TokenType.STRING, s, line, col)

    def identifier(self):
        line = self.lineno
        col = self.column
        s = ""
        while self.current_char and (self.current_char.isalnum() or self.current_char == "_"):
            s += self.current_char
            self.advance()

        lower = s.lower()
        if lower in self.KEYWORDS:
            return Token(self.KEYWORDS[lower], None, line, col)

        return Token(TokenType.IDENT, s, line, col)

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Обработка комментариев
            if self.current_char == '{' or (
                self.current_char == '/' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '/'
            ):
                return self.comment()

            # Сохраняем позицию начала токена
            start_line, start_col = self.lineno, self.column

            if self.current_char.isalpha() or self.current_char == "_":
                return self.identifier()

            if self.current_char == '.' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '.':
                line, col = self.lineno, self.column
                self.advance()
                self.advance()
                return Token(TokenType.RANGE, None, line, col)

            if self.current_char == '.':
                line, col = self.lineno, self.column
                self.advance()
                return Token(TokenType.DOT, None, line, col)

            if self.current_char.isdigit():
                return self.number()
            
            # Строковые литералы
            if self.current_char in ('"', "'"):
                return self.string()
            
            # Вспомогательная лямбда для создания токена с текущей позицией
            token = lambda t, v=None: Token(t, v, start_line, start_col)

            if self.current_char == ":":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    return token(TokenType.ASSIGN)
                return token(TokenType.COLON)

            if self.current_char == "=":
                self.advance()
                return token(TokenType.EQ)

            if self.current_char == "<":
                self.advance()
                if self.current_char == ">":
                    self.advance()
                    return token(TokenType.NE)
                if self.current_char == "=":
                    self.advance()
                    return token(TokenType.LE)
                return token(TokenType.LT)

            if self.current_char == ">":
                self.advance()
                if self.current_char == "=":
                    self.advance()
                    return token(TokenType.GE)
                return token(TokenType.GT)

            # Односимвольные токены
            char_map = {
                "+": TokenType.PLUS, "-": TokenType.MINUS, "*": TokenType.MULTIPLY, "/": TokenType.DIVIDE,
                "(": TokenType.LPAREN, ")": TokenType.RPAREN, ";": TokenType.SEMICOLON, ",": TokenType.COMMA,
                "[": TokenType.LBRACKET, "]": TokenType.RBRACKET
            }
            
            if self.current_char in char_map:
                tk_type = char_map[self.current_char]
                self.advance()
                return token(tk_type)

            self.error()

        return Token(TokenType.EOF, None, self.lineno, self.column)
