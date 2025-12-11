from lexernew import TokenType, Lexer
from parsernew import (
    NumberNode, VarNode, BinOpNode, UnaryOpNode, AssignNode,
    IfNode, WhileNode, ForNode, CallNode, BlockNode,
    VarDeclNode, ProcedureNode, Parser  # <--- УБЕДИТЕСЬ, ЧТО VarDeclNode ЗДЕСЬ ЕСТЬ
)

class CppCodeGenerator:
    """
    Генератор C++ кода из абстрактного синтаксического дерева (AST)
    Преобразует узлы AST в эквивалентный код на C++
    """

    # -----------------------------------------------------------
    # MAIN ENTRY - ГЛАВНЫЕ МЕТОДЫ ВХОДА
    # -----------------------------------------------------------

    def generate_program(self, root):
        """
        Генерирует полную C++ программу с основным каркасом
        Принимает корневой узел AST, возвращает готовую C++ программу
        """
        body = self.generate(root)

        return (
            '#include <iostream>\n'
            'using namespace std;\n'
            'int main()\n'
            f'{body}'
        )

    def generate(self, node):
        """
        Универсальный диспетчер - определяет тип узла и вызывает соответствующий метод
        Использует рефлексию для вызова gen_ИмяКлассаУзла
        """
        method = getattr(self, f'gen_{type(node).__name__}', None)
        if not method:
            raise Exception(f"Нет генератора для узла {type(node).__name__}")
        return method(node)

    # -----------------------------------------------------------
    # EXPRESSIONS - МЕТОДЫ ДЛЯ ГЕНЕРАЦИИ ВЫРАЖЕНИЙ
    # -----------------------------------------------------------

    def gen_NumberNode(self, node):
        """Преобразует числовой узел в строковое представление"""
        return str(node.value)

    def gen_VarNode(self, node):
        """Возвращает имя переменной из узла переменной"""
        return node.name

    def gen_UnaryOpNode(self, node):
        """Генерирует унарную операцию (-x или +x)"""
        op = '-' if node.op_token.type == TokenType.MINUS else '+'
        return f"({op}{self.generate(node.node)})"

    def gen_BinOpNode(self, node):
        """
        Генерирует бинарную операцию (a + b, x > y и т.д.)
        Преобразует токены операторов в соответствующие C++ операторы
        """
        op_map = {
            TokenType.PLUS: "+",
            TokenType.MINUS: "-",
            TokenType.MULTIPLY: "*",
            TokenType.DIVIDE: "/",
            TokenType.EQ: "==",
            TokenType.LT: "<",
            TokenType.GT: ">",
            TokenType.LE: "<=",
            TokenType.GE: ">=",
            TokenType.NE: "!="
        }
        op = op_map[node.op_token.type]
        return f"({self.generate(node.left)} {op} {self.generate(node.right)})"

    # -----------------------------------------------------------
    # STATEMENTS
    # -----------------------------------------------------------

    def gen_AssignNode(self, node):
        """Генерирует оператор присваивания (x = 5;)"""
        return f"{node.name} = {self.generate(node.expr)};"

    def gen_IfNode(self, node):
        """
        Генерирует условный оператор if-else
        Обрабатывает как then-ветку, так и необязательную else-ветку
        """
        text = f"if {self.generate(node.condition)} {self.generate(node.then_branch)}"
        if node.else_branch:
            text += f" else {self.generate(node.else_branch)}"
        return text

    def gen_WhileNode(self, node):
        """Генерирует цикл while с условием и телом"""
        return f"while {self.generate(node.condition)} {self.generate(node.body)}"

    def gen_ForNode(self, node):
        """
        Генерирует цикл for в C++ стиле
        Создает счетчик от начального до конечного значения с инкрементом
        """
        start = self.generate(node.start)
        end = self.generate(node.end)
        return (
            f"for (int {node.var} = {start}; {node.var} <= {end}; {node.var}++) "
            f"{self.generate(node.body)}"
        )

    def gen_CallNode(self, node):
        """
        Генерирует вызов функции или процедуры
        Специальная обработка для встроенных функций writeln и readln
        """
        # Writeln support
        if node.name.lower() == "writeln":
            if len(node.args) == 0:
                return "cout << endl;"
            parts = " << \" \" << ".join(self.generate(a) for a in node.args)
            return f"cout << {parts} << endl;"

        # Readln
        if node.name.lower() == "readln":
            if len(node.args) != 1:
                raise Exception("readln принимает ровно один аргумент")
            return f"cin >> {self.generate(node.args[0])};"

        # Generic function call
        args = ", ".join(self.generate(a) for a in node.args)
        return f"{node.name}({args});"

    def gen_BlockNode(self, node):
        """
        Генерирует блок кода, обрамленный фигурными скобками
        Оптимизирует вложенные блоки, убирая лишние скобки
        """
        lines = []
        for stmt in node.statements:
            # VarDeclNode не оборачиваем в {}
            if isinstance(stmt, VarDeclNode):
                lines.append(self.generate(stmt))
            else:
                # Если stmt — это блок с одной инструкцией, можно не делать лишние {}
                code = self.generate(stmt)
                # Убираем двойные {}
                if code.startswith("{") and code.endswith("}"):
                    code = code[1:-1].strip()
                lines.append(code)
        return "{\n    " + "\n    ".join(lines) + "\n}"

    def gen_VarDeclNode(self, node):
        """
        Генерирует объявление переменной в C++
        Преобразует типы данных из исходного языка в C++ типы
        """
        ctype = "int" if node.type_ == "integer" else "double"
        return f"{ctype} {node.name};"

    def gen_ProcedureNode(self, node):
        """
        Генерирует объявление процедуры (функции без возвращаемого значения)
        Обрабатывает параметры и тело процедуры
        """
        params_cpp = []
        for name, type_ in node.params:
            ctype = "int" if type_ == "integer" else "double"
            params_cpp.append(f"{ctype} {name}")

        params_str = ", ".join(params_cpp)

        return (
            f"void {node.name}({params_str}) "
            f"{self.generate(node.body)}"
        )