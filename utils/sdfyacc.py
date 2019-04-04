import ply.yacc as yacc

from sdflex import tokens

timings = dict()

header = dict()
io_path_list = list()
tcheck_list = list()
cells = dict()


def remove_quotation(s):
    return s.replace('"', '')


def p_sdf_file(p):
    '''sdf_file : LPAR DELAYFILE sdf_header RPAR
                | LPAR DELAYFILE sdf_header cell_list RPAR'''

    timings['header'] = p[3]
    if p[4] is not ')':
        timings['cells'] = p[4]

    p[0] = timings


def p_sdf_header(p):
    '''sdf_header : sdf_version
                  | sdf_header design
                  | sdf_header vendor
                  | sdf_header program
                  | sdf_header version
                  | sdf_header hierarchy_divider
                  | sdf_header timescale'''

    p[0] = p[1]


def p_sdf_sdfversion(p):
    'sdf_version : LPAR SDFVERSION QFLOAT RPAR'
    header['sdf_version'] = remove_quotation(p[3])
    p[0] = header


def p_sdf_design(p):
    'design : LPAR DESIGN QSTRING RPAR'
    header['design'] = remove_qutation(p[3])
    p[0] = header


def p_sdf_vendor(p):
    'vendor : LPAR VENDOR QSTRING RPAR'
    header['vendor'] = remove_quotation(p[3])
    p[0] = header


def p_sdf_program(p):
    'program : LPAR PROGRAM QSTRING RPAR'
    header['program'] = remove_quotation(p[3])
    p[0] = header


def p_sdf_version(p):
    'version : LPAR VERSION QSTRING RPAR'
    header['version'] = remove_quotation(p[3])
    p[0] = header


def p_sdf_divider(p):
    'hierarchy_divider : LPAR DIVIDER QFLOAT RPAR'
    header['divider'] = remove_quotation(p[3])
    p[0] = header


def p_sdf_timescale(p):
    'timescale : LPAR TIMESCALE STRING RPAR'
    header['timescale'] = p[3]
    p[0] = header


def p_cell_list(p):
    '''cell_list : cell
                 | cell_list cell'''
    p[0] = p[1]


def add_delays_to_cell(p, delays):

    # delays list
    for delay in delays:
        delay_name = delay['input'] + "_" + delay['output']
        cells[p[3]][p[4]][delay_name] = delay


def add_timings_to_cell(p, timings):

    for timing in timings:
        timing_name = timing['input'] + "_" + timing['clk'] \
                       + "_" + timing['timing']
        cells[p[3]][p[4]][timing_name] = timing


def add_cell(p):

    # name
    if p[3] not in cells:
        cells[p[3]] = dict()
    # instance
    if p[4] not in cells[p[3]]:
        cells[p[3]][p[4]] = dict()


def p_timing_cell(p):
    'cell : LPAR CELL celltype instance timing_check RPAR'

    add_cell(p)
    add_timings_to_cell(p, p[5])
    p[0] = cells


def p_empty_cell(p):
    'cell : LPAR CELL celltype instance RPAR'

    add_cell(p)
    p[0] = cells


def p_delay_timing_cell(p):
    'cell : LPAR CELL celltype instance delay timing_check RPAR'

    add_cell(p)
    add_delays_to_cell(p, p[5])
    add_timings_to_cell(p, p[6])
    p[0] = cells


def p_delay_cell(p):
    'cell : LPAR CELL celltype instance delay RPAR'

    add_cell(p)
    add_delays_to_cell(p, p[5])
    p[0] = cells


def p_celltype(p):
    'celltype : LPAR CELLTYPE QSTRING RPAR'
    p[0] = remove_quotation(p[3])


def p_instance(p):
    'instance : LPAR INSTANCE STRING RPAR'
    p[0] = p[3]


def p_timing_check(p):
    '''timing_check : LPAR TIMINGCHECK timing_check_list RPAR'''
    p[0] = list(p[3])
    tcheck_list.clear()


def p_timing_check_list(p):
    '''timing_check_list : t_check
                         | timing_check_list t_check'''
    # copy the list
    p[0] = p[1]


def p_t_check(p):
    '''t_check : removal_check
               | recovery_check
               | hold_check
               | setup_check'''

    p[0] = tcheck_list


def prepare_check(p):

    tcheck = dict()

    tcheck['input'] = p[3]
    tcheck['clk'] = p[4]
    tcheck['output'] = None
    tcheck['path'] = p[5]

    return tcheck


def p_removal_check(p):
    'removal_check : LPAR REMOVAL port_spec port_spec real_triple RPAR'

    tcheck = dict()
    tcheck = prepare_check(p)
    tcheck['timing'] = 'removal'
    tcheck_list.append(tcheck)


def p_recovery_check(p):
    'recovery_check : LPAR RECOVERY port_spec port_spec real_triple RPAR'

    tcheck = dict()
    tcheck = prepare_check(p)
    tcheck['timing'] = 'recovery'
    tcheck_list.append(tcheck)


def p_hold_check(p):
    'hold_check : LPAR HOLD port_spec port_spec real_triple RPAR'

    tcheck = dict()
    tcheck = prepare_check(p)
    tcheck['timing'] = 'hold'
    tcheck_list.append(tcheck)


def p_setup_check(p):
    'setup_check : LPAR SETUP port_spec port_spec real_triple RPAR'

    tcheck = dict()
    tcheck = prepare_check(p)
    tcheck['timing'] = 'setup'
    tcheck_list.append(tcheck)


def p_delay(p):
    'delay : LPAR DELAY absolute RPAR'
    p[0] = p[3]


def p_absolute(p):
    '''absolute : LPAR ABSOLUTE RPAR
                | LPAR ABSOLUTE iopath_list RPAR'''

    if p[3] is not ')':
        # copy the iopath list
        p[0] = list(p[3])
    else:
        p[0] = None
    # clean the list
    io_path_list.clear()


def p_iopath_list(p):
    '''iopath_list : iopath
                   | iopath_list iopath'''

    p[0] = io_path_list


def p_iopath(p):
    'iopath : LPAR IOPATH port_spec port_spec real_triple real_triple RPAR'
    delay_path = dict()
    delay_path['input'] = p[3]
    delay_path['output'] = p[4]
    delay_path['clk'] = None
    delay_path['fast_path'] = p[5]
    delay_path['slow_path'] = p[6]

    io_path_list.append(delay_path)


def p_port_spec(p):
    '''port_spec : STRING
                 | LPAR port_condition STRING RPAR
                 | FLOAT'''

    if p[1] != '(':
        p[0] = str(p[1])
    else:
        p[0] = p[3]


def p_port_condition(p):
    '''port_condition : POSEDGE
                      | NEGEDGE'''
    p[0] = p[1]


def p_real_triple(p):
    '''real_triple : LPAR FLOAT COLON FLOAT COLON FLOAT RPAR
                   | LPAR RPAR
                   | LPAR FLOAT COLON COLON FLOAT RPAR'''

    delays_triple = dict()
    if len(p) > 3:
        if p[4] == ':':
            delays_triple['min'] = float(p[2])
            delays_triple['avg'] = None
            delays_triple['max'] = float(p[5])
        else:
            delays_triple['min'] = float(p[2])
            delays_triple['avg'] = float(p[4])
            delays_triple['max'] = float(p[6])
    else:
        delays_triple['min'] = None
        delays_triple['avg'] = None
        delays_triple['max'] = None

    p[0] = delays_triple


def p_error(p):
    print("Syntax error at '%s' line: %d" % (p.value, p.lineno))


parser = yacc.yacc()
