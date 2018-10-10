from copy import deepcopy

import ply.yacc as yacc

from tokens import tokens, UniqueVar


def to_dict(obj):
    if isinstance(obj, Node):
        return [obj.leaf, to_dict(obj.children)]
    elif isinstance(obj, list):
        return [to_dict(elem) for elem in obj]
    else:
        return obj


class Node:
    def __init__(self, leaf=None, children=None):
        self.children = [] if children is None else children
        self.leaf = leaf

    def to_dict(self):
        return to_dict(self)

    def __str__(self):
        return str(self.to_dict())

    __repr__ = __str__


# Grammar taken from here: http://www.lua.org/manual/5.1/manual.html#8
def p_chunk(p):
    '''chunk : stmts
             | laststat
             | stmts laststat'''
    if len(p) == 2:
        if isinstance(p[1], list):
            p[0] = p[1]
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_block(p):
    'block : chunk'
    p[0] = Node("Block", children=p[1])

def p_statements(p):
    '''stmts : stmt
             | stmt stmts'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_assign_stmt(p):
    "stmt : varlist '=' explist"
    assign_nodes = [Node(leaf='=', children=[var, exp]) for var, exp in zip(p[1], p[3])]
    stmt_node = Node(leaf="Assign", children=assign_nodes)
    p[0] = stmt_node

def p_function_call_stmt(p):
    'stmt : functioncall'
    p[0] = p[1]

def p_do_block_stmt(p):
    'stmt : DO block END'
    p[0] = Node(leaf="Do", children=[p[2]])

def p_while_block_stmt(p):
    'stmt : WHILE exp DO block END'
    p[0] = Node(leaf="While", children=[p[2], p[4]])

def p_repeat_block_stmt(p):
    'stmt : REPEAT block UNTIL exp'
    p[0] = Node(leaf="Repeat", children=[p[2], p[4]])

def p_if_block_stmt(p):
    '''stmt : IF exp THEN block elifs else END
            | IF exp THEN block elifs END
            | IF exp THEN block else END'''
    if len(p) == 8:
        p[0] = Node(leaf="If", children=[p[2], p[4], p[5], p[6]])
    else:
        p[0] = Node(leaf="If", children=[p[2], p[4], p[5]])

def p_elif(p):
    'elif : ELSEIF exp THEN block'
    p[0] = Node(leaf="Elif", children=[p[2], p[4]])

def p_elifs(p):
    '''elifs : elif
             | elif elifs'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_else(p):
    '''else : ELSE block'''
    p[0] = Node(leaf="Else", children=[p[2]])

def p_for_block_stmt(p):
    '''stmt : FOR NAME '=' exp ',' exp DO block END
            | FOR NAME '=' exp ',' exp ',' exp DO block END'''

def p_foreach_block_stmt(p):
    'stmt : FOR namelist IN explist DO block END'

def p_func_def_block_stmt(p):
    'stmt : FUNCTION funcname funcbody'
    p[0] = Node(leaf="Function", children=[p[2], p[3]])

def p_local_func_def_block_stmt(p):
    'stmt : LOCAL FUNCTION NAME funcbody'

def p_local_assign_stmt(p):
    '''stmt : LOCAL namelist
            | LOCAL namelist '=' explist'''
    assign_nodes = [Node(leaf='=', children=[var, exp]) for var, exp in zip(p[2], p[4])]
    stmt_node = Node(leaf="Local Assign", children=assign_nodes)
    p[0] = stmt_node

def p_laststat(p):
    '''laststat : RETURN
                | RETURN explist
                | BREAK'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Node(leaf="Return", children=p[2])

def p_funcname(p):
    '''funcname : dotnames
                | dotnames ':' NAME'''
    p[0] = UniqueVar('.'.join(map(str, p[1])))
    if len(p) == 4:
        p[0] = UniqueVar(p[0] + ':' + p[3])

def p_dotnames(p):
    '''dotnames : NAME
                | NAME '.' dotnames'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_varlist(p):
    '''varlist : var
               | var ',' varlist'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_var(p):
    '''var : NAME
           | prefixexp '[' exp ']'
           | prefixexp '.' NAME'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Node(leaf="Complex Var", children=[p[1], p[3]])

def p_namelist(p):
    '''namelist : NAME
                | NAME ',' namelist'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_explist(p):
    '''explist : exp
               | exp ',' explist'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_exp(p):
    '''exp : NIL
           | FALSE
           | TRUE
           | NUMBER
           | STRING
           | ELLIPSIS
           | function
           | prefixexp
           | tableconstructor
           | exp binop exp
           | unop exp'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = Node(leaf=p[1], children=[p[2]])
    else:
        p[0] = Node(leaf=p[2], children=[p[1], p[3]])

def p_prefixexp(p):
    '''prefixexp : var
                 | functioncall
                 | '(' exp ')' '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_functioncall(p):
    '''functioncall : prefixexp args
                    | prefixexp ':' NAME args'''
    if len(p) == 3:
        p[0] = Node("Function Call", children=[p[1], p[2]])
    else:
        p[0] = Node("Function Call", children=[p[1], p[3], p[4]])

def p_args(p):
    '''args : '(' ')'
            | '(' explist ')'
            | tableconstructor
            | STRING'''
    if len(p) == 3:
        p[0] = []
    elif len(p) == 4:
        p[0] = Node("Args", children=p[2])
    else:
        p[0] = p[1]


def p_function(p):
    'function : FUNCTION funcbody'
    p[0] = Node("Function", children=p[2])

def p_funcbody(p):
    '''funcbody : '(' ')' block END
               | '(' parlist ')' block END'''
    if len(p) == 5:
        p[0] = [[], p[3]]
    else:
        p[0] = [Node("Params", children=p[2]), p[4]]

def p_parlist(p):
    '''parlist : namelist
               | namelist ',' ELLIPSIS
               | ELLIPSIS'''
    if p[1] == '...':
        p[0] = [p[1]]
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + [p[3]]

def p_tableconstructor(p):
    '''tableconstructor : '{' '}'
                        | '{' fieldlist '}' '''
    if len(p) == 3:
        p[0] = {}
    else:
        p[0] = Node("{}", children=p[2])

def p_fieldlist(p):
    '''fieldlist : field
                 | field ',' fieldlist
                 | field ';' fieldlist'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_field(p):
    '''field : '[' exp ']' '=' exp
             | NAME '=' exp
             | exp'''
    if len(p) == 6:
        p[0] = Node('=', children=[p[2], p[5]])
    elif len(p) == 4:
        p[0] = Node('=', children=[p[1], p[3]])
    else:
        p[0] = p[1]

def p_binop(p):
    '''binop : '+'
             | '-'
             | '*'
             | '/'
             | '^'
             | '%'
             | CONC
             | '<'
             | LEQ
             | '>'
             | GEQ
             | EQ
             | NEQ
             | AND
             | OR'''
    p[0] = p[1]

def p_unop(p):
    '''unop : '-'
            | NOT
            | '#' '''
    p[0] = p[1]

def p_error(p):
    print(f"Syntax error at token {p.type} at line {p.lineno}")
    exit(1)


parser = yacc.yacc()
