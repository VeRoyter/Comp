# semantic.py
from parsernew import (
    BlockNode, MultiVarDeclNode, VarNode, AssignNode, ArrayAssignNode, 
    ArrayAccessNode, ProcedureNode, FunctionNode, ForNode, StringNode, BoolNode
)
from errors import SemanticError

class SymbolTable:
    def __init__(self):
        self.symbols = {}  # {name: (type, is_array, array_size)}

    def define(self, name, type_, is_array=False, array_size=None):
        self.symbols[name] = (type_, is_array, array_size)

    def lookup(self, name):
        return self.symbols.get(name)

    def is_defined(self, name):
        return name in self.symbols

class SemanticAnalyzer:
    """
    Проходит по AST и проверяет семантические правила:
    1. Переменные должны быть объявлены перед использованием.
    2. Нельзя объявлять переменную дважды.
    3. Проверка типов для массивов и функций.
    """
    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        method = getattr(self, method_name, self.generic_visit)
        method(node)

    def generic_visit(self, node):
        pass

    def visit_BlockNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_MultiVarDeclNode(self, node):
        # Проверка: переменные уже есть?
        for name in node.var_names:
            if self.symbol_table.is_defined(name):
                raise SemanticError(
                    (node.token.lineno, node.token.column),
                    f"Variable '{name}' is already declared"
                )
            self.symbol_table.define(name, node.type_, node.is_array, node.array_size)

    def visit_AssignNode(self, node):
        # Проверка: переменная объявлена?
        var_info = self.symbol_table.lookup(node.name)
        if not var_info:
            # Это может быть присваивание результата функции
            # В Pascal: function_name := value
            # Проверим, есть ли такая функция в текущем контексте
            # Пока что пропускаем проверку для имен функций
            pass
        else:
            # Проверка: не присваиваем массиву как целому
            type_, is_array, _ = var_info
            if is_array:
                raise SemanticError(
                    (node.token.lineno, node.token.column),
                    f"Array '{node.name}' requires index for assignment"
                )
        self.visit(node.expr)

    def visit_ArrayAssignNode(self, node):
        # Проверка: массив объявлен?
        var_info = self.symbol_table.lookup(node.name)
        if not var_info:
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Array '{node.name}' not declared"
            )
        type_, is_array, array_size = var_info
        if not is_array:
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Variable '{node.name}' is not an array"
            )
        self.visit(node.index)
        self.visit(node.expr)

    def visit_VarNode(self, node):
        # Проверка использования переменной в выражении
        var_info = self.symbol_table.lookup(node.name)
        if not var_info:
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Variable '{node.name}' not declared (usage)"
            )
        type_, is_array, _ = var_info
        if is_array:
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Array '{node.name}' requires index for access"
            )

    def visit_ArrayAccessNode(self, node):
        # Проверка: массив объявлен?
        var_info = self.symbol_table.lookup(node.name)
        if not var_info:
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Array '{node.name}' not declared"
            )
        type_, is_array, array_size = var_info
        if not is_array:
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Variable '{node.name}' is not an array"
            )
        self.visit(node.index)

    def visit_BinOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOpNode(self, node):
        self.visit(node.node)

    def visit_IfNode(self, node):
        self.visit(node.condition)
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_WhileNode(self, node):
        self.visit(node.condition)
        self.visit(node.body)
    
    def visit_ForNode(self, node):
        # Переменная счетчика должна быть объявлена
        if not self.symbol_table.is_defined(node.var):
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Loop variable '{node.var}' not declared"
            )
        self.visit(node.start)
        self.visit(node.end)
        self.visit(node.body)

    def visit_CallNode(self, node):
        # Writeln/Readln встроенные, их не проверяем в таблице
        if node.name.lower() in ('writeln', 'readln'):
            for arg in node.args:
                self.visit(arg)
            return
        
        # Для пользовательских процедур проверка аргументов
        for arg in node.args:
            self.visit(arg)

    def visit_ProcedureNode(self, node):
        # Создаем новую область видимости для параметров
        old_symbols = self.symbol_table.symbols.copy()
        
        # Добавляем параметры в таблицу символов
        for param_name, param_type in node.params:
            self.symbol_table.define(param_name, param_type)
        
        self.visit(node.body)
        
        # Восстанавливаем старую таблицу символов
        self.symbol_table.symbols = old_symbols

    def visit_FunctionNode(self, node):
        # Создаем новую область видимости для параметров
        old_symbols = self.symbol_table.symbols.copy()
        
        # Добавляем параметры в таблицу символов
        for param_name, param_type in node.params:
            self.symbol_table.define(param_name, param_type)
        
        self.visit(node.body)
        
        # Восстанавливаем старую таблицу символов
        self.symbol_table.symbols = old_symbols

    def visit_NumberNode(self, node):
        pass

    def visit_StringNode(self, node):
        pass

    def visit_BoolNode(self, node):
        pass

    def visit_CommentNode(self, node):
        pass