# errors.py

class Error(Exception):
    def __init__(self, pos, msg, type_name):
        self.pos = pos  # tuple (line, col)
        self.msg = msg
        self.type_name = type_name

    def __str__(self):
        return f"[{self.type_name}] Error at line {self.pos[0]}, col {self.pos[1]}: {self.msg}"

class LexerError(Error):
    def __init__(self, pos, msg):
        super().__init__(pos, msg, 'Lexer')

class ParserError(Error):
    def __init__(self, pos, msg):
        super().__init__(pos, msg, 'Parser')

class SemanticError(Error):
    def __init__(self, pos, msg):
        super().__init__(pos, msg, 'Semantic')