#!/usr/bin/env python3

def run_corner(A_ubd, b_ub, names, verbose=0, opts={}, meta={}):
    # Given timing scores for above delays (-ps)
    names_orig = names

    #print_eqns(A_ub, b_ub, verbose=verbose)
    names, A_ubd, b_ub = massage_equations(A_ubd, b_ub, opts, names, verbose=verbose)

    print
    print_eqns(A_ubd, b_ub, verbose=verbose)

    print
    col_dist(A_ubd, 'final', names)

    A_ub, b_ub = Ab_d2np(A_ubd, b_ub, names)

    # Its having trouble giving me solutions as this gets bigger
    # Make a terrible baseline guess to confirm we aren't doing something bad
    #print_names(names, verbose=verbose)
    check_feasible(A_ub=A_ub, b_ub=b_ub)

    '''
    Be mindful of signs
    Have something like
    timing1/timing 2 are constants
    delay1 +   delay2 +               delay4     >= timing1
               delay2 +   delay3                 >= timing2

    But need it in compliant form:
    -delay1 +   -delay2 +               -delay4     <= -timing1
                -delay2 +   -delay3                 <= -timing2
    '''
    rows = len(A_ub)
    cols = len(A_ub[0])
    # Minimization function scalars
    # Treat all logic elements as equally important
    c = [1 for _i in range(len(names))]
    # Delays cannot be negative
    # (this is also the default constraint)
    #bounds =  [(0, None) for _i in range(len(names))]
    # Also you can provide one to apply to all
    bounds = (0, None)

    # Seems to take about rows + 3 iterations
    # Give some margin
    #maxiter = int(1.1 * rows + 100)
    #maxiter = max(1000, int(1000 * rows + 1000))
    # Most of the time I want it to just keep going unless I ^C it
    maxiter = 1000000

    if verbose >= 2:
        print('b_ub', b_ub)
    print('Unique delay elements: %d' % len(names))
    print('  # delay minimization weights: %d' % len(c))
    print('  # delay constraints: %d' % len(bounds))
    print('Input paths')
    print('  # timing scores: %d' % len(b_ub))
    print('  Rows: %d' % rows)

    tlast = [time.time()]
    iters = [0]
    printn = [0]
    def callback(xk, **kwargs):
        iters[0] = kwargs['nit']
        if time.time() - tlast[0] > 1.0:
            sys.stdout.write('I:%d ' % kwargs['nit'])
            tlast[0] = time.time()
            printn[0] += 1
            if printn[0] % 10 == 0:
                sys.stdout.write('\n')
            sys.stdout.flush()

    print('')
    # Now find smallest values for delay constants
    # Due to input bounds (ex: column limit), some delay elements may get eliminated entirely
    print('Running linprog w/ %d r, %d c (%d name)' % (rows, cols, len(names_orig)))
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, callback=callback,
          options={"disp": True, 'maxiter': maxiter, 'bland': True, 'tol': 1e-6,})
    nonzeros = 0
    print('Ran %d iters' % iters[0])
    if res.success:
        print('Result sample (%d elements)' % (len(res.x)))
        plim = 3
        for xi, (name, x) in enumerate(zip(names, res.x)):
            nonzero = x >= 0.001
            if nonzero:
                nonzeros += 1
            #if nonzero and (verbose >= 1 or xi > 30):
            if nonzero and (verbose or ((nonzeros < 100 or nonzeros % 20 == 0) and nonzeros <= plim)):
                print('  % 4u % -80s % 10.1f' % (xi, name, x))
        print('Delay on %d / %d' % (nonzeros, len(res.x)))
        if not os.path.exists('res'):
            os.mkdir('res')
        fn_out = 'res/%s' % datetime.datetime.utcnow().isoformat().split('.')[0]
        print('Writing %s' % fn_out)
        np.save(fn_out, (3, c, A_ub, b_ub, bounds, names, res, meta))

