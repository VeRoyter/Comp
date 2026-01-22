#codegen.py
from lexernew import TokenType, Lexer
from parsernew import (
    NumberNode, StringNode, BoolNode, VarNode, BinOpNode, UnaryOpNode, 
    AssignNode, ArrayAssignNode, ArrayAccessNode, IfNode, WhileNode, ForNode, 
    CallNode, BlockNode, MultiVarDeclNode, ProcedureNode, FunctionNode, CommentNode
)

class CppCodeGenerator:
    """
    Генератор C++ кода из абстрактного синтаксического дерева (AST)
    Преобразует узлы AST в эквивалентный код на C++
    """

    def __init__(self):
        self.functions_code = []  # Для хранения кода функций

    # -----------------------------------------------------------
    # MAIN ENTRY - ГЛАВНЫЕ МЕТОДЫ ВХОДА
    # -----------------------------------------------------------

    def generate_program(self, root):
        """
        Генерирует полную C++ программу с основным каркасом
        Принимает корневой узел AST, возвращает готовую C++ программу
        """
        # Сбросим список функций
        self.functions_code = []
        
        # Генерируем тело main
        body = self.generate(root)

        # Собираем итоговый код: сначала функции, потом main
        result = (
            '#include <iostream>\n'
            '#include <string>\n'
            '#include <cmath>\n'
            'using namespace std;\n\n'
        )
        
        # Добавляем все функции перед main
        if self.functions_code:
            result += '\n'.join(self.functions_code) + '\n\n'
        
        result += 'int main()\n'
        result += f'{body}'
        
        return result

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
    # EXPRESSIONS - МЕТОТЫ ДЛЯ ГЕНЕРАЦИИ ВЫРАЖЕНИЙ
    # -----------------------------------------------------------

    def gen_NumberNode(self, node):
        """Преобразует числовой узел в строковое представление"""
        return str(node.value)

    def gen_StringNode(self, node):
        """Преобразует строковый узел в C++ строку"""
        # Экранируем специальные символы
        s = node.value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
        return f'"{s}"'

    def gen_BoolNode(self, node):
        """Преобразует булев узел в C++ bool"""
        return "true" if node.value else "false"

    def gen_VarNode(self, node):
        """Возвращает имя переменной из узла переменной"""
        return node.name

    def gen_ArrayAccessNode(self, node):
        """Генерирует доступ к элементу массива"""
        return f"{node.name}[{self.generate(node.index)}]"

    def gen_UnaryOpNode(self, node):
        """Генерирует унарную операцию (-x, +x, not x)"""
        if node.op_token.type == TokenType.NOT:
            return f"(!{self.generate(node.node)})"
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
            TokenType.NE: "!=",
            TokenType.AND: "&&",
            TokenType.OR: "||"
        }
        op = op_map[node.op_token.type]
        
        # Специальная обработка конкатенации строк
        if node.op_token.type == TokenType.PLUS:
            left_is_string = isinstance(node.left, StringNode)
            right_is_string = isinstance(node.right, StringNode)
            if left_is_string or right_is_string:
                # Для строк используем + (std::string поддерживает конкатенацию)
                pass
        
        return f"({self.generate(node.left)} {op} {self.generate(node.right)})"


    def gen_CommentNode(self, node):
        return f"// {node.text}"
    # -----------------------------------------------------------
    # STATEMENTS
    # -----------------------------------------------------------

    def gen_AssignNode(self, node):
        """Генерирует оператор присваивания (x = 5;)"""
        # Проверяем, не является ли это присваиванием результата функции
        # В Pascal: function_name := value
        # В C++: return value;
        return f"{node.name} = {self.generate(node.expr)};"

    def gen_ArrayAssignNode(self, node):
        """Генерирует присваивание элементу массива"""
        return f"{node.name}[{self.generate(node.index)}] = {self.generate(node.expr)};"

    def gen_IfNode(self, node):
        """
        Генерирует условный оператор if-else
        Обрабатывает как then-ветку, так и необязательную else-ветку
        """
        then_code = self.generate(node.then_branch)
        if not then_code.startswith("{"):
            then_code = "{\n    " + then_code + "\n}"
        text = f"if ({self.generate(node.condition)}) {then_code}"

        if node.else_branch:
            else_code = self.generate(node.else_branch)
            if not else_code.startswith("{"):
                else_code = "{\n    " + else_code + "\n}"
            text += f" else {else_code}"

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
            parts = []
            for arg in node.args:
                arg_code = self.generate(arg)
                parts.append(arg_code)
            result = "cout"
            for part in parts:
                result += f" << {part}"
            result += " << endl;"
            return result

        # Readln
        if node.name.lower() == "readln":
            if len(node.args) != 1:
                raise Exception("readln принимает ровно один аргумент")
            return f"cin >> {self.generate(node.args[0])};"

        # Generic function call
        args = ", ".join(self.generate(a) for a in node.args)
        return f"{node.name}({args})"

    def gen_BlockNode(self, node):
        """
        Генерирует блок кода, обрамленный фигурными скобками
        Оптимизирует вложенные блоки, убирая лишние скобки
        """
        lines = []
        for stmt in node.statements:
            # MultiVarDeclNode не оборачиваем в {}
            if isinstance(stmt, MultiVarDeclNode):
                lines.append(self.generate(stmt))
            else:
                # Если stmt — это блок с одной инструкцией, можно не делать лишние {}
                code = self.generate(stmt)
                # Убираем двойные скобки, но не трогаем однострочные
                if code.startswith("{") and code.endswith("}") and len(code) > 2:
                    code = code[1:-1].strip()
                if isinstance(stmt, CallNode) and not code.strip().endswith(";"):
                    code += ";"
                lines.append(code)
        return "{\n    " + "\n    ".join(lines) + "\n}"

    def gen_MultiVarDeclNode(self, node):
        """
        Генерирует объявление нескольких переменных в C++
        Поддерживает различные типы данных и массивы
        """
        ctype = self._get_cpp_type(node.type_)
        var_decls = []
        
        for name in node.var_names:
            if node.is_array:
                # Массивы в C++: int arr[10];
                var_decls.append(f"{name}[{node.array_size}]")
            else:
                var_decls.append(name)
        
        vars_str = ", ".join(var_decls)
        return f"{ctype} {vars_str};"

    def _get_cpp_type(self, pascal_type):
        """Преобразует тип Pascal в тип C++"""
        type_map = {
            "integer": "int",
            "real": "double",
            "boolean": "bool",
            "string": "string"
        }
        return type_map.get(pascal_type, "auto")

    def gen_ProcedureNode(self, node):
        """
        Генерирует объявление процедуры (функции без возвращаемого значения)
        Обрабатывает параметры и тело процедуры
        """
        params_cpp = []
        for name, type_ in node.params:
            ctype = self._get_cpp_type(type_)
            params_cpp.append(f"{ctype} {name}")

        params_str = ", ".join(params_cpp)

        code = (
            f"void {node.name}({params_str}) "
            f"{self._generate_function_body_with_return(node.body, node.name)}"
        )
        
        # Сохраняем код функции для последующего вывода перед main
        self.functions_code.append(code)
        return ""

    def gen_FunctionNode(self, node):
        """
        Генерирует объявление функции с возвращаемым значением
        Обрабатывает параметры, тип возвращаемого значения и тело функции
        """
        params_cpp = []
        for name, type_ in node.params:
            ctype = self._get_cpp_type(type_)
            params_cpp.append(f"{ctype} {name}")

        params_str = ", ".join(params_cpp)
        return_type_cpp = self._get_cpp_type(node.return_type)

        # Обрабатываем тело функции и ищем присваивание имени функции
        body_code = self._generate_function_body_with_return(node.body, node.name)
        
        code = f"{return_type_cpp} {node.name}({params_str}) {body_code}"
        
        # Сохраняем код функции для последующего вывода перед main
        self.functions_code.append(code)
        return ""
    
    def _generate_function_body_with_return(self, body_node, func_name):
        """
        Генерирует тело функции, заменяя присваивания имени функции на return
        """
        # Сначала создаем временный генератор для обработки всего тела
        temp_lines = []
        
        # Рекурсивно обходим все узлы и собираем строки кода
        def collect_statements(node, lines):
            if isinstance(node, BlockNode):
                for stmt in node.statements:
                    collect_statements(stmt, lines)
            elif isinstance(node, AssignNode) and hasattr(node, 'name') and node.name == func_name:
                # Это присваивание результата функции: func_name := value
                # Заменяем на return value;
                lines.append(f"return {self.generate(node.expr)};")
            elif isinstance(node, IfNode):
                # Обрабатываем if-else
                then_lines = []
                else_lines = []
                
                if node.then_branch:
                    collect_statements(node.then_branch, then_lines)
                if node.else_branch:
                    collect_statements(node.else_branch, else_lines)
                
                # Формируем if-else
                then_code = "{\n    " + "\n    ".join(then_lines) + "\n}" if then_lines else "{}"
                else_code = " else {\n    " + "\n    ".join(else_lines) + "\n}" if else_lines else ""
                
                lines.append(f"if {self.generate(node.condition)} {then_code}{else_code}")
            elif isinstance(node, WhileNode):
                # Обрабатываем while
                body_lines = []
                collect_statements(node.body, body_lines)
                body_code = "{\n    " + "\n    ".join(body_lines) + "\n}" if body_lines else "{}"
                lines.append(f"while {self.generate(node.condition)} {body_code}")
            elif isinstance(node, ForNode):
                # Обрабатываем for
                body_lines = []
                collect_statements(node.body, body_lines)
                body_code = "{\n    " + "\n    ".join(body_lines) + "\n}" if body_lines else "{}"
                start = self.generate(node.start)
                end = self.generate(node.end)
                lines.append(f"for (int {node.var} = {start}; {node.var} <= {end}; {node.var}++) {body_code}")
            elif isinstance(node, MultiVarDeclNode):
                lines.append(self.generate(node))
            else:
                # Для всех остальных узлов используем обычную генерацию
                code = self.generate(node)
                if code and code.strip():
                    lines.append(code)
        
        collect_statements(body_node, temp_lines)
        
        # Формируем итоговый код
        if temp_lines:
            return "{\n    " + "\n    ".join(temp_lines) + "\n}"
        else:
            return "{}"
