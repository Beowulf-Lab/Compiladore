from flask import Flask, request, render_template
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definir los tokens para el lexer
tokens = ['RESERVED', 'IDENTIFIER', 'FREE_WORD']

# Lista de palabras reservadas
reserved = {
    'for': 'RESERVED',
    'while': 'RESERVED',
    'if': 'RESERVED',
    'else': 'RESERVED',
}

# Expresión regular para identificar identificadores (variables, nombres, etc.)
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if t.value == "hola mundo":
        t.type = 'IDENTIFIER'
    else:
        t.type = reserved.get(t.value, 'IDENTIFIER')
    
    # Incrementa el número de línea si encuentras un salto de línea
    t.lexer.lineno += t.value.count('\n')
    
    return t

# Expresión regular para la palabra "fora"
def t_FREE_WORD(t):
    r'fora'
    t.type = 'FREE_WORD'
    return t

# Ignorar espacios y tabs
t_ignore = ' \t'

# Manejar saltos de línea explícitos
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Definir el manejador de errores
def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Crear el lexer
lexer = lex.lex()

# Reglas gramaticales para el análisis sintáctico
def p_statement_reserved(p):
    '''statement : RESERVED'''
    p[0] = ('reserved', p[1])

def p_statement_identifier(p):
    '''statement : IDENTIFIER'''
    p[0] = ('identifier', p[1])

def p_statement_free_word(p):
    '''statement : FREE_WORD'''
    p[0] = ('free_word', p[1])

def p_error(p):
    print("Error sintáctico en '%s'" % p.value)

# Crear el parser
parser = yacc.yacc()

# Función para analizar el texto léxicamente
def lexico(text):
    lines = text.splitlines()
    tokens_list = []
    line_info = []

    for i, line in enumerate(lines, start=1):
        lexer.input(line)
        for token in lexer:
            tokens_list.append((i, token.type, token.value))  # Guardar línea, tipo y valor del token
            tipo_palabra = 'Palabra Reservada' if token.type == 'RESERVED' else 'Identificador' if token.type == 'IDENTIFIER' else 'Palabra Libre' if token.type == 'FREE_WORD' else 'Desconocido'
            line_info.append((i, tipo_palabra, token.value))

    return tokens_list, line_info

# Función para el análisis sintáctico usando yacc
def sintactico(tokens_list):
    sintactico_info = []

    for token in tokens_list:
        line_number, token_type, token_value = token
        result = parser.parse(token_value)
        if result:
            token_type, token_value = result
            if token_type == 'reserved' and token_value == 'for':
                sintactico_info.append((line_number, token_value, 'X', ''))  # Correcto
            elif token_type == 'free_word' and token_value == 'fora':
                sintactico_info.append((line_number, token_value, '', 'X'))  # Incorrecto
            elif token_type == 'identifier' and token_value == 'hola mundo':
                sintactico_info.append((line_number, token_value, '', 'ID'))  # Incorrecto
            else:
                sintactico_info.append((line_number, token_value, '', 'X'))  # Incorrecto
        else:
            sintactico_info.append((line_number, token_value, '', 'X'))  # Incorrecto o vacío

    return sintactico_info

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        tokens, line_info = lexico(text)
        sintactico_info = sintactico(tokens)
        return render_template('index.html', tokens=tokens, line_info=line_info, sintactico_info=sintactico_info)
    
    return render_template('index.html', tokens=None, line_info=None, sintactico_info=None)

if __name__ == '__main__':
    app.run(debug=True)