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
            # print("Output C++ starts with:", res[:50].replace('\n', ' ') + "...")

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
    
    # 1. Тест на успешную компиляцию
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