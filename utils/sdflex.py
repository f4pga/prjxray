import ply.lex as lex

reserved = {
    'DELAYFILE': 'DELAYFILE',
    'SDFVERSION': 'SDFVERSION',
    'DESIGN': 'DESIGN',
    'VENDOR': 'VENDOR',
    'PROGRAM': 'PROGRAM',
    'VERSION': 'VERSION',
    'TIMESCALE': 'TIMESCALE',
    'CELL': 'CELL',
    'CELLTYPE': 'CELLTYPE',
    'INSTANCE': 'INSTANCE',
    'DELAY': 'DELAY',
    'ABSOLUTE': 'ABSOLUTE',
    'IOPATH': 'IOPATH',
    'posedge': 'POSEDGE',
    'negedge': 'NEGEDGE',
    'SETUP': 'SETUP',
    'HOLD': 'HOLD',
    'REMOVAL': 'REMOVAL',
    'RECOVERY': 'RECOVERY',
    'TIMINGCHECK': 'TIMINGCHECK',
    'DIVIDER': 'DIVIDER',
}

tokens = (
    'LPAR',
    'RPAR',
    'COLON',
    'FLOAT',
    'QFLOAT',
    'QSTRING',
    'STRING',
) + tuple(reserved.values())

t_LPAR = r'\('
t_RPAR = r'\)'
t_COLON = r':'
t_QFLOAT = r'\"[-+]?(?: [0-9]+)(?: \.[0-9]+)\"'
t_QSTRING = r'\"[a-zA-Z0-9_/]+\"'

t_ignore = ' \t'


# define FLOAT as function so it takes precendence over STRING
def t_FLOAT(t):
    r'[-+]?(?: [0-9]+)(?: \.[0-9]+)'
    return t


def t_STRING(t):
    r'[a-zA-Z0-9_/]+'
    t.type = reserved.get(t.value, 'STRING')
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
