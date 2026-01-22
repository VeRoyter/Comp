import sys
from errors import Error
from lexernew import Lexer
from parsernew import Parser
from semantic import SemanticAnalyzer
from codegen import CppCodeGenerator

def run_test(name, code, should_fail=False, expected_error_type=None):
    print(f"\n--- TEST: {name} ---")
    print(f"Code:\n{code.strip()}")
    print("-" * 20)

    try:
        # 1. Lexer
        lexer = Lexer(code)
        
        # 2. Parser
        parser = Parser(lexer)
        ast = parser.parse()
        
        # 3. Semantic
        semantic = SemanticAnalyzer()
        semantic.visit(ast)
        
        # 4. Codegen
        generator = CppCodeGenerator()
        res = generator.generate_program(ast)
        
        if should_fail:
            print(f"FAILED. Ожидалась ошибка {expected_error_type}, но компиляция прошла успешно.")
        else:
            print("SUCCESS. Компиляция прошла успешно.")
            print("Generated C++ code:")
            print(res)

    except Error as e:
        if should_fail and e.type_name == expected_error_type:
            print(f"SUCCESS (Caught expected error).")
            print(f"Сообщение: {e}")
        else:
            print(f"FAILED. Неожиданная ошибка или неправильный тип ошибки.")
            print(f"Получено: {e}")
            if should_fail:
                print(f"   Ожидалось: {expected_error_type}")
    except Exception as e:
        print(f"FAILED. Внутренняя ошибка Python: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    
    # 1. Тест на успешную компиляцию (исходный)
    code_success = """
    var
        x: integer;
        y: integer;
    begin
        x := 10;
        y := x * 2;
        if y > 10 then
            writeln(y);
    end
    """
    run_test("Valid Code", code_success, should_fail=False)

    # 2. Тест на ошибку Лексера (недопустимый символ)
    code_lexer_err = """
    var x: integer;
    begin
        x := 10 $ 5; 
    end
    """
    run_test("Lexer Error (Symbol)", code_lexer_err, should_fail=True, expected_error_type="Lexer")

    # 3. Тест на ошибку Парсера (забытая точка с запятой)
    code_parser_err = """
    var x: integer
    begin
        x := 10;
    end
    """
    run_test("Parser Error (Missing Semicolon)", code_parser_err, should_fail=True, expected_error_type="Parser")

    # 4. Тест на ошибку Парсера (неожиданный токен)
    code_parser_err2 = """
    var x: integer;
    begin
        x := ;
    end
    """
    run_test("Parser Error (Empty Expression)", code_parser_err2, should_fail=True, expected_error_type="Parser")

    # 5. Тест на Семантику (необъявленная переменная)
    code_semantic_err1 = """
    begin
        x := 5;
    end
    """
    run_test("Semantic Error (Undeclared Var)", code_semantic_err1, should_fail=True, expected_error_type="Semantic")

    # 6. Тест на Семантику (повторное объявление)
    code_semantic_err2 = """
    var
        a: integer;
        a: real;
    begin
        a := 5;
    end
    """
    run_test("Semantic Error (Duplicate Var)", code_semantic_err2, should_fail=True, expected_error_type="Semantic")

    # ===== НОВЫЕ ТЕСТЫ =====

    # 7. Тест на множественное объявление переменных
    code_multiple_vars = """
    var
        a, b, c: integer;
        x, y: real;
    begin
        a := 1;
        b := 2;
        c := 3;
        x := 1.5;
        y := 2.5;
        writeln(a, b, c, x, y);
    end
    """
    run_test("Multiple Variables Declaration", code_multiple_vars, should_fail=False)

    # 8. Тест на булев тип
    code_boolean = """
    var
        flag: boolean;
        result: boolean;
    begin
        flag := true;
        result := not flag;
        if result or true then
            writeln(1);
    end
    """
    run_test("Boolean Type", code_boolean, should_fail=False)

    # 9. Тест на строки
    code_strings = """
    var
        s1: string;
        s2: string;
    begin
        s1 := "Hello";
        s2 := "World";
        writeln(s1 + " " + s2);
    end
    """
    run_test("String Type and Concatenation", code_strings, should_fail=False)

    # 10. Тест на массивы
    code_arrays = """
    var
        arr: array[10] of integer;
        i: integer;
    begin
        for i := 0 to 9 do
            arr[i] := i * 2;
        writeln(arr[5]);
    end
    """
    run_test("Arrays", code_arrays, should_fail=False)

    # 11. Тест на процедуры с несколькими параметрами
    code_procedures = """
    procedure print_sum(a: integer; b: integer; c: integer);
    begin
        writeln(a + b + c);
    end;
    
    var
        x, y, z: integer;
    begin
        x := 1;
        y := 2;
        z := 3;
        print_sum(x, y, z);
    end
    """
    run_test("Procedures with Multiple Parameters", code_procedures, should_fail=False)

    # 12. Тест на комментарии
    code_comments = """
    // This is a comment
    var
        x: integer; { another comment }
    begin
        x := 10; // assign value
        writeln(x);
    end
    """
    run_test("Comments", code_comments, should_fail=False)

    # 13. Тест на переменные внутри функций
    code_local_vars = """
    function factorial(n: integer): integer;
    var
        result: integer;
        i: integer;
    begin
        result := 1;
        for i := 1 to n do
            result := result * i;
        factorial := result;
    end;
    
    var
        x: integer;
    begin
        x := factorial(5);
        writeln(x);
    end
    """
    run_test("Local Variables in Functions", code_local_vars, should_fail=False)

    # 14. Тест на вызов функций в выражениях
    code_func_calls = """
    function add(a: integer; b: integer): integer;
    begin
        add := a + b;
    end;
    
    var
        x, y: integer;
    begin
        x := 10;
        y := add(x, 5);
        writeln(y);
    end
    """
    run_test("Function Calls in Expressions", code_func_calls, should_fail=False)

    # 15. Тест на сложные выражения с функциями
    code_complex = """
    function square(n: integer): integer;
    begin
        square := n * n;
    end;
    
    function cube(n: integer): integer;
    begin
        cube := n * n * n;
    end;
    
    var
        x: integer;
    begin
        x := square(3) + cube(2);
        writeln(x);
    end
    """
    run_test("Complex Expressions with Functions", code_complex, should_fail=False)
