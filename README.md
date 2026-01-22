# Транслятор Pascal → C++

## Описание

Данный транслятор преобразует программы на языке Pascal в эквивалентный код на языке C++. 

## Архитектура

Транслятор состоит из следующих модулей:

1. **lexernew.py** - Лексический анализатор
2. **parsernew.py** - Синтаксический анализатор (парсер)
3. **semantic.py** - Семантический анализатор
4. **codegen.py** - Генератор C++ кода
5. **errors.py** - Система обработки ошибок
6. **app.py** - Веб-интерфейс (Streamlit)
7. **test_compiler.py** - Модуль тестирования
8. **generat_0.2.py** - Консольный интерфейс

## Установка и запуск

### Консольный режим

```bash
# Запуск трансляции файла
python generat_0.2.py input.pas output.cpp

# Вывод результата в stdout
python generat_0.2.py input.pas
```

### Веб-интерфейс

```bash
# Установите Streamlit
pip install streamlit

# Запуск веб-интерфейса
streamlit run app.py
```

## Поддерживаемые конструкции

### Базовые типы данных

```pascal
var
    i: integer;    // → int
    f: real;       // → double  
    b: boolean;    // → bool
    s: string;     // → std::string
```

### Множественное объявление переменных

```pascal
var
    a, b, c: integer;      // → int a, b, c;
    x, y: real;            // → double x, y;
    flag1, flag2: boolean; // → bool flag1, flag2;
```

### Массивы

```pascal
var
    numbers: array[10] of integer;  // → int numbers[10];
    values: array[5] of real;       // → double values[5];
```

Использование массивов:

```pascal
numbers[0] := 42;      // → numbers[0] = 42;
x := numbers[5];       // → x = numbers[5];
```

### Булев тип и логические операции

```pascal
var
    flag: boolean;
    result: boolean;

flag := true;          // → flag = true;
result := false;       // → result = false;
result := not flag;    // → result = !flag;
result := a and b;     // → result = a && b;
result := a or b;      // → result = a || b;
```

### Строки и конкатенация

```pascal
var
    s1, s2: string;

s1 := "Hello";                    // → s1 = "Hello";
s2 := "World";                    // → s2 = "World";
writeln(s1 + " " + s2);           // → cout << s1 << " " << s2 << endl;
```

### Комментарии

Поддерживаются два типа комментариев:

```pascal
// Однострочный комментарий (C++ стиль)

{ Блочный комментарий (Pascal стиль) }

var
    x: integer; // Комментарий после кода
```

### Функции и процедуры

#### Процедуры (void функции)

```pascal
procedure print_sum(a: integer; b: integer; c: integer);
begin
    writeln(a + b + c);
end;

// Вызов
print_sum(1, 2, 3);
```

#### Функции с возвращаемым значением

```pascal
function max(a: integer; b: integer): integer;
begin
    if a > b then
        max := a
    else
        max := b;
end;

// Вызов
x := max(10, 20);
```

### Локальные переменные в функциях

```pascal
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
```

### Управляющие конструкции

#### Условный оператор

```pascal
if x > 0 then
    writeln("Positive")
else
    writeln("Negative");
```

#### Цикл while

```pascal
while x < 10 do
begin
    x := x + 1;
    writeln(x);
end;
```

#### Цикл for

```pascal
for i := 1 to 10 do
    writeln(i);
```

### Ввод/вывод

```pascal
// Вывод
writeln("Hello, World!");           // → cout << "Hello, World!" << endl;
writeln(x, y, z);                   // → cout << x << " " << y << " " << z << endl;

// Ввод
readln(x);                          // → cin >> x;
```

## Примеры программ

### Пример 1: Факториал

```pascal
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
```

Результат:
```cpp
#include <iostream>
#include <string>
#include <cmath>
using namespace std;

int factorial(int n) {
    int result, i;
    result = 1;
    for (int i = 1; i <= n; i++) {
        result = result * i;
    }
    return result;
}

int main() {
    int x;
    x = factorial(5);
    cout << x << endl;
}
```

### Пример 2: Работа с массивами

```pascal
var
    arr: array[10] of integer;
    i: integer;
begin
    // Заполнение массива
    for i := 0 to 9 do
        arr[i] := i * i;
    
    // Вывод элементов
    for i := 0 to 9 do
        writeln(arr[i]);
end
```

### Пример 3: Строки

```pascal
var
    first_name: string;
    last_name: string;
    full_name: string;
begin
    first_name := "John";
    last_name := "Doe";
    full_name := first_name + " " + last_name;
    writeln("Full name: " + full_name);
end
```

## Ограничения

1. Транслятор поддерживает только структурированное подмножество Pascal
2. Не поддерживаются:
   - Записи (records)
   - Указатели
   - Многомерные массивы
   - Динамические массивы
   - Наследование и полиморфизм
   - Модули и юниты

## Тестирование

Для запуска тестов:

```bash
python test_compiler.py
```

## Разработка

### Структура проекта

```
.
├── lexernew.py          # Лексический анализатор
├── parsernew.py         # Синтаксический анализатор
├── semantic.py          # Семантический анализатор
├── codegen.py           # Генератор кода
├── errors.py            # Обработка ошибок
├── app.py               # Веб-интерфейс
├── test_compiler.py     # Тесты
├── generat_0.2.py       # Консольный интерфейс
└── README.md            # Документация
```

### Добавление новых функций

1. **Лексический анализатор (lexernew.py)**:
   - Добавьте новые типы токенов в `TokenType`
   - Реализуйте обработку в `get_next_token()`

2. **Синтаксический анализатор (parsernew.py)**:
   - Добавьте новые AST-узлы
   - Реализуйте разбор в соответствующих методах

3. **Семантический анализатор (semantic.py)**:
   - Добавьте проверки типов и области видимости

4. **Генератор кода (codegen.py)**:
   - Реализуйте генерацию C++ кода для новых конструкций

## Лицензия

Проект разработан для учебных целей.
