import streamlit as st
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

# Импортируем тестовый модуль
import test_compiler
from test_compiler import Lexer, Parser, SemanticAnalyzer, CppCodeGenerator, Error


st.set_page_config(layout="wide")
st.subheader("Pascal to C++")

# ---------- UI ----------
col_code, col_output = st.columns([2, 2])

with col_code:
    st.markdown("""
<style>
 textarea[aria-label="Введите код на Pascal:"] { margin-top: 0 !important; }

}
</style>
""", unsafe_allow_html=True)
    st.text("Введите код на Pascal")

    code = st.text_area(
        "",
        height=400,
        placeholder="program test;\nbegin\n  writeln('Hello');\nend."
    )
   
    run_button = st.button("Запустить компиляцию")


with col_output:
   
   st.text("Код на c++")
   st.markdown(f"""<div id="cpp_box" style=" margin-top:45px;">""",unsafe_allow_html=True)
   cpp_output_box = st.empty()
    

st.subheader("Терминал (вывод ошибок и print)")
terminal_placeholder = st.empty()


# ---------- ЛОГИКА ----------
if run_button and code.strip():

    # Буфер для stdout / stderr
    log_buffer = io.StringIO()

    with redirect_stdout(log_buffer), redirect_stderr(log_buffer):

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
            generated_cpp = generator.generate_program(ast)

            print("SUCCESS: Компиляция прошла успешно.")

            # показать C++ код справа
            cpp_output_box.code(generated_cpp, language="cpp")

        except Error as e:
            print("ERROR:", e)
            cpp_output_box.code("Ошибка. C++ код не был сгенерирован.", language="text")
        except Exception as e:
            print("Python internal error:", e)
            import traceback
            traceback.print_exc()
            cpp_output_box.code("Внутренняя ошибка Python.", language="text")

    # вывод лога терминала
    terminal_placeholder.code(log_buffer.getvalue(), language="text")
