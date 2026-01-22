#!/usr/bin/env python3
"""
Основной исполняемый модуль транслятора Pascal -> C++
Демонстрирует работу компилятора в консольном режиме
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from errors import Error
from lexernew import Lexer
from parsernew import Parser
from semantic import SemanticAnalyzer
from codegen import CppCodeGenerator

def compile_pascal_to_cpp(source_code):
    """
    Основная функция компиляции
    Возвращает сгенерированный C++ код или выбрасывает исключение
    """
    # 1. Лексический анализ
    lexer = Lexer(source_code)
    
    # 2. Синтаксический анализ
    parser = Parser(lexer)
    ast = parser.parse()
    
    # 3. Семантический анализ
    semantic = SemanticAnalyzer()
    semantic.visit(ast)
    
    # 4. Генерация кода
    generator = CppCodeGenerator()
    generated_code = generator.generate_program(ast)
    
    return generated_code

def main():
    """
    Главная функция - обрабатывает аргументы командной строки и запускает компиляцию
    """
    if len(sys.argv) < 2:
        print("Использование: python generat_0.2.py <файл.pas> [выход.cpp]")
        print("Если выходной файл не указан, результат выводится в stdout")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Читаем исходный файл
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Компилируем
        cpp_code = compile_pascal_to_cpp(source_code)
        
        # Выводим результат
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cpp_code)
            print(f"Скомпилировано успешно! Результат сохранен в {output_file}")
        else:
            print("=== Сгенерированный C++ код ===")
            print(cpp_code)
    
    except Error as e:
        print(f"Ошибка компиляции: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Файл {input_file} не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Внутренняя ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
