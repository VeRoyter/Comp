from lexernew import TokenType, Lexer
from parsernew import (
    NumberNode, VarNode, BinOpNode, UnaryOpNode, AssignNode,
    IfNode, WhileNode, ForNode, CallNode, BlockNode,
    VarDeclNode, ProcedureNode, Parser
)
from codegen import CppCodeGenerator
from errors import Error
from semantic import SemanticAnalyzer

if __name__ == "__main__":

    # Пример с ошибкой (необъявленная переменная 'c')
    program_text = """
    var
        a: integer;
        b: integer;

    begin
        a := 5;
        b := 10;
        c := a + b; 
        
        writeln(c);
    end
    """
    
    # Правильный пример
    program_text_ok = """
    var
        x: integer;
    begin
        x := 10;
        if x > 5 then
            writeln(x);
    end
    """

    try:
        print("--- Compiling ---")
        
        # 1. Lexical Analysis
        lexer = Lexer(program_text)
        
        # 2. Syntax Analysis
        parser = Parser(lexer)
        ast = parser.parse()
        print("Syntax check passed.")

        # 3. Semantic Analysis (НОВОЕ)
        semantic = SemanticAnalyzer()
        semantic.visit(ast)
        print("Semantic check passed.")

        # 4. Code Generation
        generator = CppCodeGenerator()
        cpp_code = generator.generate_program(ast)

        print("\n===== СГЕНЕРИРОВАННЫЙ C++ КОД =====")
        print(cpp_code)

    except Error as e:
        print(f"\nCOMPILATION FAILED:\n{e}")
    except Exception as e:
        print(f"\nINTERNAL ERROR: {e}")