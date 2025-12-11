from lexernew import TokenType

# ==== AST ====

class NumberNode:
    def __init__(self, value):
        self.value = value

class VarNode:
    def __init__(self, name):
        self.name = name

class BinOpNode:
    def __init__(self, left, op_token, right):
        self.left = left
        self.op_token = op_token
        self.right = right

class UnaryOpNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node

class AssignNode:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class IfNode:
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForNode:
    def __init__(self, var, start, end, body):
        self.var = var
        self.start = start
        self.end = end
        self.body = body

class CallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class BlockNode:
    def __init__(self, statements):
        self.statements = statements

class VarDeclNode:
    def __init__(self, name, type_):
        self.name = name
        self.type_ = type_

class ProcedureNode:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # list of (name, type)
        self.body = body


# ===== PARSER =====

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def error(self, msg="Syntax error"):
        raise Exception(msg + f" at token {self.current_token}")

    def eat(self, type_):
        if self.current_token.type == type_:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {type_}")
    def peek(self):
        """Возвращает следующий токен, не потребляя его."""
        saved_pos = self.lexer.pos
        saved_char = self.lexer.current_char

        token = self.lexer.get_next_token()

        self.lexer.pos = saved_pos
        self.lexer.current_char = saved_char

        return token

    # ---------- Program ----------

    def parse(self):
        statements = []

        while self.current_token.type != TokenType.EOF:
            statements.append(self.statement())

        return BlockNode(statements)

    # ---------- Statements ----------

    def statement(self):
        tk = self.current_token.type

        # пустой оператор
        if tk == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            return None

        # VAR declaration
        if tk == TokenType.VAR:
            return self.var_decl()

        # IF
        if tk == TokenType.IF:
            return self.if_statement()

        # WHILE
        if tk == TokenType.WHILE:
            return self.while_statement()

        # FOR
        if tk == TokenType.FOR:
            return self.for_statement()

        # BLOCK begin ... end
        if tk == TokenType.BEGIN:
            return self.block()

        # PROCEDURE
        if tk == TokenType.PROCEDURE:
            return self.procedure_decl()

        if tk in (TokenType.IDENT, TokenType.WRITELN, TokenType.READLN):
            return self.assignment_or_call()


    # a := expr  OR  writeln(x)
    def assignment_or_call(self):
        # имя: либо value, либо сам type как строка
        if self.current_token.value is not None:
            name = self.current_token.value
        else:
            name = str(self.current_token.type).lower()

        # съедаем сам идентификатор или builtin
        self.eat(self.current_token.type)

        # function call
        if self.current_token.type == TokenType.LPAREN:
            return self.func_call(name)

        # assignment
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            expr = self.expr()
            return AssignNode(name, expr)

        self.error("Expected '(' or ':=' after identifier")

    def func_call(self, name):
        self.eat(TokenType.LPAREN)
        args = []

        if self.current_token.type != TokenType.RPAREN:
            args.append(self.expr())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args.append(self.expr())

        self.eat(TokenType.RPAREN)
        return CallNode(name, args)

    def var_decl(self):
        self.eat(TokenType.VAR)

        decls = []

        while True:
            name = self.current_token.value
            self.eat(TokenType.IDENT)
            self.eat(TokenType.COLON)

            t = self.current_token.type
            if t not in (TokenType.INTEGER, TokenType.REAL):
                self.error("Expected type")

            type_ = "integer" if t == TokenType.INTEGER else "real"
            self.eat(t)

            decls.append(VarDeclNode(name, type_))

            # если дальше точка с запятой — продолжаем
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
                # если следующее — IDENT, значит ещё одна переменная
                if self.current_token.type == TokenType.IDENT:
                    continue
            break

        # если объявили несколько переменных — вернуть блок
        if len(decls) == 1:
            return decls[0]
        return BlockNode(decls)


    # if expr then stmt else stmt
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

    # for i := start to end do stmt
    def for_statement(self):
        self.eat(TokenType.FOR)
        var_name = self.current_token.value
        self.eat(TokenType.IDENT)

        self.eat(TokenType.ASSIGN)
        start = self.expr()

        self.eat(TokenType.TO)
        end = self.expr()

        self.eat(TokenType.DO)
        body = self.statement()

        return ForNode(var_name, start, end, body)

    # begin statements end
    def block(self):
        self.eat(TokenType.BEGIN)
        stmts = []
        while self.current_token.type != TokenType.END:
            stmts.append(self.statement())
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)

        self.eat(TokenType.END)
        return BlockNode(stmts)


    # параметры процедуры
    def param_list(self):
        params = []

        if self.current_token.type == TokenType.RPAREN:
            return params

        while True:
            name = self.current_token.value
            self.eat(TokenType.IDENT)

            self.eat(TokenType.COLON)

            t = self.current_token.type
            if t not in (TokenType.INTEGER, TokenType.REAL):
                self.error("Expected type in parameter list")

            type_ = "integer" if t == TokenType.INTEGER else "real"
            self.eat(t)

            params.append((name, type_))

            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
                continue

            break

        return params




    # procedure name(a: integer; b: real);
    def procedure_decl(self):
        self.eat(TokenType.PROCEDURE)

        name = self.current_token.value
        self.eat(TokenType.IDENT)

        self.eat(TokenType.LPAREN)
        params = self.param_list()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)

        body = self.block()  # BEGIN ... END

        self.eat(TokenType.SEMICOLON)  # ← ВАЖНО! Конец процедуры

        return ProcedureNode(name, params, body)

    # ========== EXPRESSIONS ==========

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
        tk = self.current_token.type

        if tk == TokenType.PLUS:
            op = self.current_token
            self.eat(TokenType.PLUS)
            return UnaryOpNode(op, self.factor())

        if tk == TokenType.MINUS:
            op = self.current_token
            self.eat(TokenType.MINUS)
            return UnaryOpNode(op, self.factor())

        if tk == TokenType.NUMBER:
            val = self.current_token.value
            self.eat(TokenType.NUMBER)
            return NumberNode(val)

        if tk == TokenType.IDENT:
            # Если это идентификатор в выражении, просто VarNode
            name = self.current_token.value
            self.eat(TokenType.IDENT)
            return VarNode(name)

        if tk == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node

        self.error("Invalid expression")
