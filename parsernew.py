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

class StringNode(AST):
    def __init__(self, token):
        super().__init__(token)
        self.value = token.value

class BoolNode(AST):
    def __init__(self, token):
        super().__init__(token)
        # TRUE и FALSE - это ключевые слова, value = None
        # Определяем значение по типу токена
        self.value = (token.type == TokenType.TRUE)  # True или False

class VarNode(AST):
    def __init__(self, token):
        super().__init__(token)
        self.name = token.value

class ArrayAccessNode(AST):
    def __init__(self, token, index):
        super().__init__(token)
        self.name = token.value
        self.index = index

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

class ArrayAssignNode(AST):
    def __init__(self, token, index, expr):
        super().__init__(token)
        self.name = token.value
        self.index = index
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

class MultiVarDeclNode(AST):
    def __init__(self, var_tokens, type_token, is_array=False, array_size=None):
        super().__init__(None)
        self.var_names = [token.value for token in var_tokens]
        self.type_ = self._get_type_name(type_token)
        self.is_array = is_array
        self.array_size = array_size
        self.token = var_tokens[0] if var_tokens else None
    
    def _get_type_name(self, type_token):
        if type_token.type == TokenType.INTEGER:
            return "integer"
        elif type_token.type == TokenType.REAL:
            return "real"
        elif type_token.type == TokenType.BOOLEAN:
            return "boolean"
        elif type_token.type == TokenType.STRING_TYPE:
            return "string"
        return "unknown"

class ProcedureNode(AST):
    def __init__(self, token, params, body):
        super().__init__(token)
        self.name = token.value
        self.params = params  # list of (name, type)
        self.body = body

class FunctionNode(AST):
    def __init__(self, token, params, return_type, body):
        super().__init__(token)
        self.name = token.value
        self.params = params  # list of (name, type)
        self.return_type = return_type
        self.body = body

class CommentNode(AST):
    def __init__(self, token):
        super().__init__(token)
        self.text = token.value

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

    def parse(self):
        statements = []

        # верхний уровень: объявления + основной блок
        while self.current_token.type != TokenType.BEGIN:
            stmt = self.statement()
            if stmt:
                statements.append(stmt)

        # основной begin ... end.
        main_block = self.block()
        statements.append(main_block)

        # ОБЯЗАТЕЛЬНО: точка в конце программы
        if self.current_token.type != TokenType.DOT:
            self.error("Expected '.' after END")
        self.eat(TokenType.DOT)

        # и конец файла
        self.eat(TokenType.EOF)

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
        if tk == TokenType.FUNCTION:
            return self.function_decl()
        if tk in (TokenType.IDENT, TokenType.WRITELN, TokenType.READLN):
            return self.assignment_or_call()
        if tk == TokenType.COMMENT:
            token = self.current_token
            self.eat(TokenType.COMMENT)
            return CommentNode(token)
        
        self.error(f"Unexpected token in statement")

    def assignment_or_call(self):
        token = self.current_token # Сохраняем токен имени
        name = token.value if token.value else str(token.type).lower()
        self.eat(token.type)

        # Проверка на доступ к элементу массива: arr[index]
        if self.current_token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
            index = self.expr()
            self.eat(TokenType.RBRACKET)
            
            if self.current_token.type == TokenType.ASSIGN:
                self.eat(TokenType.ASSIGN)
                expr = self.expr()
                return ArrayAssignNode(token, index, expr)
            else:
                # Это просто доступ к элементу массива в выражении
                return ArrayAccessNode(token, index)
        
        if self.current_token.type == TokenType.LPAREN:
            return self.func_call(token)
        
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            expr = self.expr()
            return AssignNode(token, expr)
        
        self.error("Expected '[', '(' or ':=' after identifier")

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

    def var_decl(self):
        self.eat(TokenType.VAR)
        decls = []
        while True:
            # Множественное объявление переменных: a, b, c: integer;
            var_tokens = []
            var_tokens.append(self.current_token)
            self.eat(TokenType.IDENT)
            
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                var_tokens.append(self.current_token)
                self.eat(TokenType.IDENT)
            
            self.eat(TokenType.COLON)
            
            # Проверка на массив
            is_array = False
            array_size = None
            if self.current_token.type == TokenType.ARRAY:
                is_array = True
                self.eat(TokenType.ARRAY)
                self.eat(TokenType.LBRACKET)

                array_low = self.expr()

                if self.current_token.type == TokenType.RANGE:
                    self.eat(TokenType.RANGE)
                    array_high = self.expr()
                else:
                    self.error("Expected '..' in array range")

                self.eat(TokenType.RBRACKET)
                self.eat(TokenType.OF)

                if isinstance(array_low, NumberNode) and isinstance(array_high, NumberNode):
                    array_size = array_high.value - array_low.value + 1
                else:
                    self.error("Array bounds must be constant numbers")

            
            type_token = self.current_token
            if type_token.type not in (TokenType.INTEGER, TokenType.REAL, TokenType.BOOLEAN, TokenType.STRING_TYPE):
                self.error("Expected type")
            self.eat(type_token.type)
            
            # Создаем узел для множественного объявления
            decls.append(MultiVarDeclNode(var_tokens, type_token, is_array, array_size))
            
            self.eat(TokenType.SEMICOLON)
            
            # Если следующий токен - идентификатор, значит объявление переменных продолжается
            if self.current_token.type == TokenType.IDENT:
                continue
            # Иначе выходим
            break
        
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
                if t_token.type not in (TokenType.INTEGER, TokenType.REAL, TokenType.BOOLEAN, TokenType.STRING_TYPE):
                    self.error("Expected type")
                t_str = self._get_type_name(t_token)
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

    def function_decl(self):
        self.eat(TokenType.FUNCTION)
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
                if t_token.type not in (TokenType.INTEGER, TokenType.REAL, TokenType.BOOLEAN, TokenType.STRING_TYPE):
                    self.error("Expected type")
                t_str = self._get_type_name(t_token)
                self.eat(t_token.type)
                params.append((p_name, t_str))
                
                if self.current_token.type == TokenType.SEMICOLON:
                    self.eat(TokenType.SEMICOLON)
                    continue
                break

        self.eat(TokenType.RPAREN)
        self.eat(TokenType.COLON)
        
        return_type_token = self.current_token
        return_type = self._get_type_name(return_type_token)
        self.eat(return_type_token.type)
        
        self.eat(TokenType.SEMICOLON)
        
        # Проверка на локальные переменные
        local_decls = []
        if self.current_token.type == TokenType.VAR:
            local_decls.append(self.var_decl())
        
        body = self.block()
        
        # Объединяем объявления переменных и тело
        if local_decls:
            all_stmts = local_decls + [body]
            body = BlockNode(all_stmts)
        
        self.eat(TokenType.SEMICOLON)
        return FunctionNode(name_token, params, return_type, body)

    def _get_type_name(self, type_token):
        if type_token.type == TokenType.INTEGER:
            return "integer"
        elif type_token.type == TokenType.REAL:
            return "real"
        elif type_token.type == TokenType.BOOLEAN:
            return "boolean"
        elif type_token.type == TokenType.STRING_TYPE:
            return "string"
        return "unknown"

    # Выражения
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
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.OR):
            op = self.current_token
            self.eat(op.type)
            node = BinOpNode(node, op, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.AND):
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
        if token.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return UnaryOpNode(token, self.factor())
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return NumberNode(token)
        if token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return StringNode(token)
        if token.type in (TokenType.TRUE, TokenType.FALSE):
            self.eat(token.type)
            return BoolNode(token)
        if token.type == TokenType.IDENT:
            self.eat(TokenType.IDENT)
            # Проверка на вызов функции
            if self.current_token.type == TokenType.LPAREN:
                return self.func_call(token)
            # Проверка на доступ к элементу массива
            elif self.current_token.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                index = self.expr()
                self.eat(TokenType.RBRACKET)
                return ArrayAccessNode(token, index)
            else:
                return VarNode(token)
        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        self.error("Invalid expression")
