# parsernew.py
from lexernew import TokenType
from errors import ParserError

# ==== AST ====
# Добавляем поле token в узлы, чтобы семантический анализатор знал, где ошибка

class AST:
    def __init__(self, token=None):
        self.token = token # Сохраняем токен для позиции ошибки

class NumberNode(AST):
    def __init__(self, token):
        super().__init__(token)
        self.value = token.value

class VarNode(AST):
    def __init__(self, token):
        super().__init__(token)
        self.name = token.value

class BinOpNode(AST):
    def __init__(self, left, op_token, right):
        super().__init__(op_token)
        self.left = left
        self.op_token = op_token
        self.right = right

class UnaryOpNode(AST):
    def __init__(self, op_token, node):
        super().__init__(op_token)
        self.op_token = op_token
        self.node = node

class AssignNode(AST):
    def __init__(self, token, expr):
        super().__init__(token)
        self.name = token.value
        self.expr = expr

class IfNode(AST):
    def __init__(self, condition, then_branch, else_branch=None):
        super().__init__(None) # Сложный узел
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileNode(AST):
    def __init__(self, condition, body):
        super().__init__(None)
        self.condition = condition
        self.body = body

class ForNode(AST):
    def __init__(self, var_token, start, end, body):
        super().__init__(var_token)
        self.var = var_token.value
        self.start = start
        self.end = end
        self.body = body

class CallNode(AST):
    def __init__(self, token, args):
        super().__init__(token)
        self.name = token.value if token.value else str(token.type).lower()
        self.args = args

class BlockNode(AST):
    def __init__(self, statements):
        super().__init__(None)
        self.statements = statements

class VarDeclNode(AST):
    def __init__(self, var_token, type_token):
        super().__init__(var_token)
        self.name = var_token.value
        self.type_ = "integer" if type_token.type == TokenType.INTEGER else "real"

class ProcedureNode(AST):
    def __init__(self, token, params, body):
        super().__init__(token)
        self.name = token.value
        self.params = params
        self.body = body


# ===== PARSER =====

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def error(self, msg="Syntax error"):
        # Используем данные из текущего токена
        raise ParserError(
            (self.current_token.lineno, self.current_token.column), 
            f"{msg}. Got {self.current_token.type}"
        )

    def eat(self, type_):
        if self.current_token.type == type_:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {type_}")

    # ... (Остальные методы остаются почти такими же, но при создании узлов передаем токены) ...

    def parse(self):
        statements = []
        while self.current_token.type != TokenType.EOF:
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return BlockNode(statements)

    def statement(self):
        tk = self.current_token.type
        if tk == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            return None
        if tk == TokenType.VAR:
            return self.var_decl()
        if tk == TokenType.IF:
            return self.if_statement()
        if tk == TokenType.WHILE:
            return self.while_statement()
        if tk == TokenType.FOR:
            return self.for_statement()
        if tk == TokenType.BEGIN:
            return self.block()
        if tk == TokenType.PROCEDURE:
            return self.procedure_decl()
        if tk in (TokenType.IDENT, TokenType.WRITELN, TokenType.READLN):
            return self.assignment_or_call()
        
        self.error(f"Unexpected token in statement")

    def assignment_or_call(self):
        token = self.current_token # Сохраняем токен имени
        name = token.value if token.value else str(token.type).lower()
        self.eat(token.type)

        if self.current_token.type == TokenType.LPAREN:
            return self.func_call(token)
        
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            expr = self.expr()
            return AssignNode(token, expr)
        
        self.error("Expected '(' or ':=' after identifier")

    def func_call(self, token):
        self.eat(TokenType.LPAREN)
        args = []
        if self.current_token.type != TokenType.RPAREN:
            args.append(self.expr())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args.append(self.expr())
        self.eat(TokenType.RPAREN)
        return CallNode(token, args)

    # parsernew.py

    def var_decl(self):
        self.eat(TokenType.VAR)
        decls = []
        while True:
            var_token = self.current_token
            self.eat(TokenType.IDENT)
            self.eat(TokenType.COLON)
            
            type_token = self.current_token
            if type_token.type not in (TokenType.INTEGER, TokenType.REAL):
                self.error("Expected type")
            self.eat(type_token.type)
            
            decls.append(VarDeclNode(var_token, type_token))
            
            # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
            # Раньше тут была проверка if, теперь мы требуем (eat) точку с запятой.
            # Если её нет, метод eat() выбросит ParserError.
            self.eat(TokenType.SEMICOLON)
            
            # Если следующий токен - идентификатор, значит объявление переменных продолжается
            if self.current_token.type == TokenType.IDENT:
                continue
            # Иначе выходим
            break
            # -----------------------
        
        if len(decls) == 1:
            return decls[0]
        return BlockNode(decls)

    def if_statement(self):
        self.eat(TokenType.IF)
        condition = self.expr()
        self.eat(TokenType.THEN)
        then_stmt = self.statement()
        else_stmt = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_stmt = self.statement()
        return IfNode(condition, then_stmt, else_stmt)

    def while_statement(self):
        self.eat(TokenType.WHILE)
        cond = self.expr()
        self.eat(TokenType.DO)
        body = self.statement()
        return WhileNode(cond, body)

    def for_statement(self):
        self.eat(TokenType.FOR)
        var_token = self.current_token
        self.eat(TokenType.IDENT)
        self.eat(TokenType.ASSIGN)
        start = self.expr()
        self.eat(TokenType.TO)
        end = self.expr()
        self.eat(TokenType.DO)
        body = self.statement()
        return ForNode(var_token, start, end, body)

    def block(self):
        self.eat(TokenType.BEGIN)
        stmts = []
        while self.current_token.type != TokenType.END:
            stmt = self.statement()
            if stmt: stmts.append(stmt)
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
        self.eat(TokenType.END)
        return BlockNode(stmts)

    def procedure_decl(self):
        self.eat(TokenType.PROCEDURE)
        name_token = self.current_token
        self.eat(TokenType.IDENT)
        self.eat(TokenType.LPAREN)
        
        params = [] # (name, type)
        if self.current_token.type != TokenType.RPAREN:
            while True:
                p_name = self.current_token.value
                self.eat(TokenType.IDENT)
                self.eat(TokenType.COLON)
                t_token = self.current_token
                if t_token.type not in (TokenType.INTEGER, TokenType.REAL):
                    self.error("Expected type")
                t_str = "integer" if t_token.type == TokenType.INTEGER else "real"
                self.eat(t_token.type)
                params.append((p_name, t_str))
                
                if self.current_token.type == TokenType.SEMICOLON:
                    self.eat(TokenType.SEMICOLON)
                    continue
                break

        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
        body = self.block()
        self.eat(TokenType.SEMICOLON)
        return ProcedureNode(name_token, params, body)

    # Выражения (минимальные изменения, только передача токена)
    def expr(self):
        node = self.simple_expr()
        if self.current_token.type in (TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.EQ, TokenType.NE):
            op = self.current_token
            self.eat(op.type)
            right = self.simple_expr()
            node = BinOpNode(node, op, right)
        return node

    def simple_expr(self):
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            self.eat(op.type)
            node = BinOpNode(node, op, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.current_token
            self.eat(op.type)
            node = BinOpNode(node, op, self.factor())
        return node

    def factor(self):
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOpNode(token, self.factor())
        if token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOpNode(token, self.factor())
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return NumberNode(token)
        if token.type == TokenType.IDENT:
            self.eat(TokenType.IDENT)
            return VarNode(token)
        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        self.error("Invalid expression")