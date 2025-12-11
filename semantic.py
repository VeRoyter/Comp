# semantic.py
from parsernew import (
    BlockNode, VarDeclNode, VarNode, AssignNode, ProcedureNode, ForNode
)
from errors import SemanticError

class SymbolTable:
    def __init__(self):
        self.symbols = {}  # {name: type}

    def define(self, name, type_):
        self.symbols[name] = type_

    def lookup(self, name):
        return self.symbols.get(name)

    def is_defined(self, name):
        return name in self.symbols

class SemanticAnalyzer:
    """
    Проходит по AST и проверяет семантические правила:
    1. Переменные должны быть объявлены перед использованием.
    2. Нельзя объявлять переменную дважды.
    """
    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        method = getattr(self, method_name, self.generic_visit)
        method(node)

    def generic_visit(self, node):
        # Если у узла есть дочерние элементы, посещаем их,
        # но так как структура AST разнородна, придется делать проверки
        # Для простоты пропишем основные узлы
        pass

    def visit_BlockNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDeclNode(self, node):
        # Проверка: переменная уже есть?
        if self.symbol_table.is_defined(node.name):
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Variable '{node.name}' is already declared"
            )
        self.symbol_table.define(node.name, node.type_)

    def visit_AssignNode(self, node):
        # Проверка: переменная объявлена?
        if not self.symbol_table.is_defined(node.name):
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Variable '{node.name}' not declared (assignment)"
            )
        self.visit(node.expr)

    def visit_VarNode(self, node):
        # Проверка использования переменной в выражении
        if not self.symbol_table.is_defined(node.name):
            raise SemanticError(
                (node.token.lineno, node.token.column),
                f"Variable '{node.name}' not declared (usage)"
            )

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
        # Переменная счетчика должна быть объявлена (или объявляется тут?
        # В Pascal счетчик обычно должен быть объявлен в var. Проверим это.
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
        
        # Для пользовательских процедур проверка декларации
        # (В текущем примере процедуры не добавляются в таблицу символов, но можно добавить)
        # Пока просто проверяем аргументы
        for arg in node.args:
            self.visit(arg)

    def visit_ProcedureNode(self, node):
        # Здесь нужно создавать новую область видимости (Scope)
        # Но для простоты примера добавим параметры в текущую (глобальную) или временную
        # Упрощенно: считаем параметры объявленными переменными
        for param_name, param_type in node.params:
             self.symbol_table.define(param_name, param_type)
        
        self.visit(node.body)

    def visit_NumberNode(self, node):
        pass