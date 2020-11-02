import random
import bitarray
import multiprocessing
import sys


class BipartiteAdjacencyMatrix():
    def __init__(self):
        self.u = set()
        self.v = set()

        self.edges = set()
        self.frozen_edges = None

    def add_u(self, u):
        self.u.add(u)

    def add_v(self, v):
        self.v.add(v)

    def add_edge(self, ui, vj):
        assert ui in self.u
        assert vj in self.v
        self.edges.add((ui, vj))

    def build(self):
        self.u = sorted(self.u)
        self.v = sorted(self.v)

        edges = self.edges
        self.edges = None
        self.frozen_edges = edges

        self.ui_to_idx = {}
        self.vj_to_idx = {}

        for idx, ui in enumerate(self.u):
            self.ui_to_idx[ui] = idx

        for idx, vj in enumerate(self.v):
            self.vj_to_idx[vj] = idx

        self.u_to_v = [
            bitarray.bitarray(len(self.v)) for _ in range(len(self.u))
        ]
        self.v_to_u = [
            bitarray.bitarray(len(self.u)) for _ in range(len(self.v))
        ]

        for arr in self.u_to_v:
            arr.setall(False)

        for arr in self.v_to_u:
            arr.setall(False)

        def add_edge(ui, vj):
            ui_idx = self.ui_to_idx[ui]
            vj_idx = self.vj_to_idx[vj]

            self.u_to_v[ui_idx][vj_idx] = True
            self.v_to_u[vj_idx][ui_idx] = True

        for ui, vj in edges:
            add_edge(ui, vj)
            assert self.is_edge(ui, vj)
            assert self.is_edge_reverse(ui, vj)

        for ui_idx in range(len(self.u)):
            for vj_idx in range(len(self.v)):
                ui = self.u[ui_idx]
                vj = self.v[vj_idx]

                if self.u_to_v[ui_idx][vj_idx]:
                    assert self.v_to_u[vj_idx][ui_idx]
                    assert (ui, vj) in self.frozen_edges
                else:
                    assert not self.v_to_u[vj_idx][ui_idx]
                    assert (ui, vj) not in self.frozen_edges

    def get_row(self, ui):
        ui_idx = self.ui_to_idx[ui]
        return self.u_to_v[ui_idx]

    def get_col(self, vj):
        vj_idx = self.vj_to_idx[vj]
        return self.v_to_u[vj_idx]

    def is_edge(self, ui, vj):
        ui_idx = self.ui_to_idx[ui]
        vj_idx = self.vj_to_idx[vj]

        return self.u_to_v[ui_idx][vj_idx]

    def is_edge_reverse(self, ui, vj):
        ui_idx = self.ui_to_idx[ui]
        vj_idx = self.vj_to_idx[vj]

        return self.v_to_u[vj_idx][ui_idx]

    def density(self):
        return len(self.frozen_edges) / (len(self.u) * len(self.v))


def test_selected_rows(graph, selected_rows, test_col, test_row):
    rows = graph.u
    columns = graph.v
    test_col.setall(False)
    test_row.setall(False)

    for row in selected_rows:
        test_col[graph.ui_to_idx[row]] = True

    I = set()
    J = set()

    for j in columns:
        if test_col & graph.get_col(j) == test_col:
            J.add(j)
            test_row[graph.vj_to_idx[j]] = True

    if len(J) > 0:
        for i in rows:
            if test_row & graph.get_row(i) == test_row:
                I.add(i)

        if len(I) > 0:
            for i in I:
                for j in J:
                    assert graph.is_edge(i, j), (i, j, selected_rows)

            return frozenset(I), frozenset(J)


def one_iteration_bsc_row(graph, P, test_col, test_row):
    selected_rows = random.choices(graph.u, k=P)
    return test_selected_rows(graph, selected_rows, test_col, test_row)


def test_selected_cols(graph, selected_cols, test_col, test_row):
    rows = graph.u
    columns = graph.v

    test_col.setall(False)
    test_row.setall(False)

    for col in selected_cols:
        test_row[graph.vj_to_idx[col]] = True

    I = set()
    J = set()

    for i in rows:
        if test_row & graph.get_row(i) == test_row:
            I.add(i)
            test_col[graph.ui_to_idx[i]] = True

    if len(I) > 0:
        for j in columns:
            if test_col & graph.get_col(j) == test_col:
                J.add(j)

        if len(J) > 0:
            for i in I:
                for j in J:
                    assert graph.is_edge(i, j), (i, j, selected_cols)

            return frozenset(I), frozenset(J)


def one_iteration_bsc_col(graph, P, test_col, test_row):
    selected_cols = random.choices(graph.v, k=P)
    return test_selected_cols(graph, selected_cols, test_col, test_row)


def worker(graph, P, work_queue, cancel_queue, result_queue):
    test_col = bitarray.bitarray(len(graph.u))
    test_row = bitarray.bitarray(len(graph.v))

    while True:
        if not cancel_queue.empty():
            _ = cancel_queue.get()
            break

        itrs = work_queue.get()

        if itrs is None:
            break

        iter_type, start_iter, stop_iter = itrs

        if iter_type == 'random':
            for itr in range(start_iter, stop_iter):
                result = one_iteration_bsc_row(graph, P, test_col, test_row)
                if result is not None:
                    result_queue.put((itr, result))

                result = one_iteration_bsc_col(graph, P, test_col, test_row)
                if result is not None:
                    result_queue.put((itr, result))
        elif iter_type == 'row':
            for row in range(start_iter, stop_iter):
                selected_rows = [graph.u[row]]
                result = test_selected_rows(
                    graph, selected_rows, test_col, test_row)
                if result is not None:
                    result_queue.put((row, result))
        elif iter_type == 'col':
            for col in range(start_iter, stop_iter):
                selected_cols = [graph.v[col]]
                result = test_selected_cols(
                    graph, selected_cols, test_col, test_row)
                if result is not None:
                    result_queue.put((len(graph.u) + col, result))
        else:
            print(
                'Failed to understand iter_type = {}'.format(iter_type),
                file=sys.stderr)
            break

    # Mark that this worker has terminated.
    result_queue.put(None)


VERBOSE = False


def find_bsc_par(num_workers, batch_size, graph, N, P):
    remaining_edges = set(graph.frozen_edges)
    num_edges = len(remaining_edges)
    graph.frozen_edges = None

    work_queue = multiprocessing.Queue()
    cancel_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    #if P == 1 and len(graph.u)+len(graph.v) < 4*N:
    #    all_row_and_col = True
    #    P = 2
    #else:
    #    all_row_and_col = False
    all_row_and_col = True

    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(
            target=worker,
            args=(
                graph,
                P,
                work_queue,
                cancel_queue,
                result_queue,
            ))
        processes.append(p)
        p.start()

    #for start_iter in range(0, N, batch_size):
    #    work_queue.put(('random', start_iter, start_iter+batch_size))

    if all_row_and_col:
        # Just test every row and col rather than doing it randomly.
        for start_iter in range(0, len(graph.u), batch_size):
            work_queue.put(
                (
                    'row', start_iter,
                    min(start_iter + batch_size, len(graph.u))))

        for start_iter in range(0, len(graph.v), batch_size):
            work_queue.put(
                (
                    'col', start_iter,
                    min(start_iter + batch_size, len(graph.v))))

    for _ in range(num_workers):
        work_queue.put(None)

    remaining_workers = num_workers
    found_solutions = set()
    while remaining_workers > 0 or not result_queue.empty():
        result = result_queue.get()

        if result is None:
            # A worker finished and has terminated
            remaining_workers -= 1
        else:
            itr, (I, J) = result

            if (I, J) not in found_solutions:
                found_solutions.add((I, J))
                for i in I:
                    for j in J:
                        remaining_edges.discard((i, j))

            if VERBOSE:
                print(
                    '{: 10d}/{: 10d} ({: 10.3g} %) ({: 10d}, {: 10d}) = {: 10d}, remaining {: 10d} / {: 10d} ({: 10.3g} %)'
                    .format(
                        itr, N, 100 * itr / N, len(I), len(J),
                        len(I) * len(J), len(remaining_edges), num_edges,
                        100 - 100 * len(remaining_edges) / num_edges))

            #if len(remaining_edges) == 0:
            #    # Stop once we have an initial set.
            #    # We still need to wait for all workers to finish, so don't
            #    # break out of the loop.
            #    for _ in range(num_workers):
            #        cancel_queue.put(None)

    for p in processes:
        p.join()

    while not work_queue.empty():
        _ = work_queue.get()

    while not cancel_queue.empty():
        _ = cancel_queue.get()

    return found_solutions, remaining_edges


def find_bsc(graph, N, P):
    rows = graph.u
    columns = graph.v

    remaining_edges = graph.frozen_edges

    test_col = bitarray.bitarray(len(rows))
    test_row = bitarray.bitarray(len(columns))
    for itr in range(N):
        result = one_iteration_bsc_row(graph, N, P, test_col, test_row)

        if result is not None:
            I, J = result
            print(
                '{}/{} ({} %) ({}, {}) = {}, remaining {}'.format(
                    itr, N, itr / N, len(I), len(J),
                    len(I) * len(J), len(remaining_edges)))
        else:
            print('No I or no J!')


def do_subgraph_intersect(I, J, edge_to_idx):
    subgraph_intersect = bitarray.bitarray(len(edge_to_idx))
    subgraph_intersect.setall(False)

    for i in I:
        for j in J:
            edge_idx = edge_to_idx.get((i, j), None)
            if edge_idx is not None:
                subgraph_intersect[edge_idx] = True

    return subgraph_intersect


def greedy_set_cover_with_complete_bipartite_subgraphs(
        edges, complete_bipartite_subgraphs):
    # Order by largest to smallest graph.  At a minimum should speed up the
    # first loop because the largest complete_bipartite_subgraphs always will
    # be the first selected in a greedy algo.
    complete_bipartite_subgraphs = sorted(
        complete_bipartite_subgraphs,
        key=lambda k: len(k[0]) * len(k[1]),
        reverse=True)

    edges = sorted(edges)
    edge_to_idx = {}
    for idx, edge in enumerate(edges):
        assert edge not in edge_to_idx
        edge_to_idx[edge] = idx

    remaining_edges = bitarray.bitarray(len(edges))
    remaining_edges.setall(True)

    intersect = [None for _ in range(len(complete_bipartite_subgraphs))]

    unused_set = set()
    for idx, (I, J) in enumerate(complete_bipartite_subgraphs):
        subgraph_intersect = do_subgraph_intersect(I, J, edge_to_idx)
        if subgraph_intersect.count() != 0:
            intersect[idx] = subgraph_intersect
        else:
            unused_set.add(idx)

    output_idx = set()

    right_nodes = [0, set()]

    def add_index_to_output(idx):
        nonlocal remaining_edges
        output_idx.add(idx)
        I, J = complete_bipartite_subgraphs[idx]

        mask = ~intersect[idx]
        remaining_edges &= mask

        for inter_idx, s in enumerate(intersect):
            if inter_idx in unused_set:
                continue

            if inter_idx in output_idx:
                continue

            intersect[inter_idx] = s & mask

        right_nodes[0] += len(J)
        right_nodes[1] |= J

    def get_cost_for_subset(idx):
        I, J = complete_bipartite_subgraphs[idx]

        count = intersect[idx].count()
        #cost = len(I)+len(J)
        cost = 1

        return cost, count

    while remaining_edges.count() > 0:
        if VERBOSE:
            print(
                len(output_idx), remaining_edges.count(), right_nodes[0],
                len(right_nodes[1]))

        best_idx = None
        lowest_cost = None
        for idx, (I, J) in enumerate(complete_bipartite_subgraphs):
            if idx in output_idx:
                continue

            if idx in unused_set:
                continue

            cost, count = get_cost_for_subset(idx)

            if count == 0:
                unused_set.add(idx)
            else:
                cost = cost / count

                if lowest_cost is None or cost < lowest_cost:
                    lowest_cost = cost
                    best_idx = idx

        assert best_idx is not None, len(output_idx)

        add_index_to_output(best_idx)

    return [complete_bipartite_subgraphs[idx] for idx in output_idx]


def greedy_set_cover_worker(required_solutions, work_queue, result_queue):
    while True:
        work = work_queue.get()
        if work is None:
            break

        key, edges = work
        subgraphs = greedy_set_cover_with_complete_bipartite_subgraphs(
            edges, required_solutions)
        result_queue.put((key, subgraphs))

    result_queue.put(None)


def greed_set_cover_par(num_workers, required_solutions, edges_iter):
    work_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(
            target=greedy_set_cover_worker,
            args=(
                required_solutions,
                work_queue,
                result_queue,
            ))
        processes.append(p)
        p.start()

    for key, edges in edges_iter:
        work_queue.put((key, edges))

    for _ in range(num_workers):
        work_queue.put(None)

    remaining_workers = num_workers
    while remaining_workers > 0 or not result_queue.empty():
        result = result_queue.get()

        if result is None:
            remaining_workers -= 1
        else:
            yield result

    for p in processes:
        p.join()

    assert work_queue.empty()
    assert result_queue.empty()
