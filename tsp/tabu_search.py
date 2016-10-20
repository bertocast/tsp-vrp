import time
import numpy as np
from utils import unique

from tsp import TSP


class TSPTabuSearch(TSP):
    def __init__(self, distance_matrix, initial_solution_strategy='greedy', neighbor_selection='first',
                 neighborhood='2-opt', seed=None, tabu_size=None):
        TSP.__init__(self, distance_matrix, initial_solution_strategy, neighbor_selection, neighborhood, seed)
        self.tabu_size = tabu_size
        self.tabu = [self.current_solution]
        self.best_solution = self.current_solution
        self.best_cost = self.current_cost

    def run(self, max_iter, verbose=None):
        number_of_iterations = 0
        time_init = time.time()
        if not self.tabu_size:
            self.tabu_size = max_iter / 10

        while number_of_iterations < max_iter:
            self.prune_tabu_list()
            best_neighbor, best_neighbor_cost = self._select_neighbor(self.current_solution)
            self.current_solution = best_neighbor
            self.current_cost = best_neighbor_cost

            if best_neighbor_cost < self.best_cost:
                self.update_best_solution(best_neighbor, best_neighbor_cost)

            if verbose and number_of_iterations % verbose == 0 and number_of_iterations != 0:
                time_elapsed = time.time() - time_init
                self._report(number_of_iterations, time_elapsed)

            number_of_iterations += 1
            self.tabu.append(self.current_solution)

        time_elapsed = time.time() - time_init
        self._report(number_of_iterations, time_elapsed)
        return self.best_solution, self.best_cost

    def _select_neighbor(self, solution):

        if self.neighborhood == '2-opt':
            get_neighbor = self._neighbor_2_opt
        elif self.neighborhood == 'swap':
            get_neighbor = self._neighbor_swap
        else:
            raise AttributeError

        neighbors = self._neighborhood(solution, get_neighbor)
        tweaked_neighbors = [neighbor for neighbor in neighbors if neighbor not in self.tabu]
        costs = [self._evaluate_solution(neighbor) for neighbor in tweaked_neighbors]
        best_neighbor, best_neighbor_cost = neighbors[np.argmin(costs)], np.min(costs)
        return best_neighbor, best_neighbor_cost

    def _neighborhood(self, solution, get_neighbor):
        neighbors = [[None for i in xrange(self.number_of_cities)] for j in
                     xrange(self.number_of_cities * (self.number_of_cities - 1) / 2)]
        idx = 0
        for i in range(self.number_of_cities):
            for j in range(i + 1, self.number_of_cities):
                neighbors[idx] = get_neighbor(solution, i, j)
                idx += 1
        return unique(neighbors)

    def prune_tabu_list(self):
        while len(self.tabu) > self.tabu_size:
            self.tabu.pop(0)

    def update_best_solution(self, solution, cost):
        self.best_solution = solution
        self.best_cost = cost

    def _report(self, n_iteration, time_elapsed):
        print "Iteration number", n_iteration
        print "\t * Current solution:", list(self.current_solution)
        print "\t * Current cost:", self.current_cost
        print "\t * Time elpased:", time_elapsed, 'seconds'
        print "\t * Tabu list length:", len(self.tabu)


