import ply.lex as lex


keywords = ("do end while repeat until if then elseif else " 
            "for in function local return break nil false true "
            "and or not").split()

reserved = {v: v.upper() for v in keywords}

tokens = "ELLIPSIS CONC LEQ GEQ EQ NEQ STRING NAME NUMBER".split() \
         + list(reserved.values())

t_ELLIPSIS = r'\.\.\.'
t_CONC = r'\.\.'

t_LEQ = r'<='
t_GEQ = r'>='
t_EQ = r'=='
t_NEQ = r'~='

t_STRING = r'".*?"'

t_ignore = ' \t\n'
t_ignore_MULTILINE_COMMENT = r'--\[\[(.|\n)*?\]\]--'
t_ignore_COMMENT = r'--.*?\n'

literals = ";=,.:()[]{}+-*/^%<>#"


# Для Graphviz нужен уникальный id, а Python экономит на новых строках
class UniqueVar:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return str(self.val)

    __repr__ = __str__


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')
    t.value = UniqueVar(t.value)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = UniqueVar(t.value)
    return t

def t_error(t):
    print(f"Illegal character {t.value[0]}")
    exit(1)


lexer = lex.lex()
