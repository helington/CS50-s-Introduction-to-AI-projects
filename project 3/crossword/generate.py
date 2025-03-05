import sys

from crossword import *

from collections import deque


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Loop though all variables in domains
        for variable in self.domains:
            words_to_remove = set()
            
            # Loop though all words in domain of the variable
            for word in self.domains[variable]:

                # If unary constraint isn't satisfied
                if variable.length != len(word):

                    # Then, remove word from domain
                    words_to_remove.add(word)
            
            self.domains[variable] -= words_to_remove
            
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Initialize revised variable with assignment as False
        revised = False

        # Get the overlap between x and y variables, if there is
        overlap = self.crossword.overlaps[x, y]

        # If there is not overlap, we will not be able revise
        if overlap is None:
            return False
        
        x_index, y_index = overlap
        to_remove = set()

        # Loop though all values on X domain
        for X in self.domains[x]:
            # If any value in y doesn't satisfy the constraint with x, then add x to the set 'to_remove'
            if not any(X[x_index] == Y[y_index] for Y in self.domains[y]):
                to_remove.add(X)
        
        if to_remove:
            self.domains[x] -= to_remove
            revised = True
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = deque()
        
        # If arcs is None, begin with initial list of all arcs in the CSP
        if arcs is None:
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    if x != y:
                        queue.append((x, y))
        
        # Else, put the arcs on the queue
        else:
            queue.extend(arcs)

        # Enforce the AC3 algorithm
        while queue:

            # Dequeue an arc
            x, y = queue.popleft()

            # If there is alteration on X domain
            if self.revise(x, y):

                # If this happens, then there is no solution
                if len(self.domains[x]) == 0:
                    return False
                
                # Queue all neighbors (except Y), to ensure they still consistent
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        complete = True
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                complete = False
        
        return complete

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Set of all words assined in Crossword
        words = set()

        for variable in assignment:
            # Check if all words be distinct
            if assignment[variable] not in words:
                words.add(assignment[variable])

            else:
                return False
            
            # Check if all values have the correct length
            if len(assignment[variable]) != variable.length:
                return False
        
            # Check if there are no conflits between neighbors
            for neighbor in self.crossword.neighbors(variable):
                if neighbor in assignment:
                    x_index, y_index = self.crossword.overlaps[variable, neighbor]
                    if assignment[variable][x_index] != assignment[neighbor][y_index]:
                        return False
        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        constraint_values = dict()

        # Loop through all domains of the 'var'
        for domain in self.domains[var]:
            constraint_values[domain] = 0

            # Loop through all neighbors of the 'var'
            for neighbor in self.crossword.neighbors(var) - assignment.keys():

                # If the neighbor isn't assigned, then it will be computed
                if neighbor not in assignment.keys():
                    if domain in self.domains[neighbor]:
                        constraint_values[domain] += 1

        # Order the constraint values in ascending order
        ordered_domain_values = sorted(constraint_values, key=constraint_values.get)
        return ordered_domain_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get the unassigned variables
        unassigned_variables = {
            variable for variable in self.crossword.variables
            if variable not in assignment.keys()
        }

        # Find the variable with the minimum reaming value
        minimum_remaining_value_variables = set()
        minimum_remaining_value = float('inf')

        for variable in unassigned_variables:
            remaining_values = len(self.domains[variable])
            if minimum_remaining_value > remaining_values:
                minimum_remaining_value = remaining_values
                minimum_remaining_value_variables = {variable}
            
            elif remaining_values == minimum_remaining_value:
                minimum_remaining_value_variables.add(variable)

        # If there is not a tie between variables, return the variable
        if len(minimum_remaining_value_variables) == 1:
            return next(iter(minimum_remaining_value_variables))
    
        # Otherwise, resolve the tie , choosing the variable with the largest degree
        largest_degree = float('-inf')
        best_variable = None

        for variable in minimum_remaining_value_variables:
            degree = len(self.crossword.neighbors(variable))
            
            if degree > largest_degree:
                largest_degree = degree
                best_variable = variable

        return best_variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        variable = self.select_unassigned_variable(assignment)
        domain_values = self.order_domain_values(variable, assignment)

        for value in domain_values:
            assignment[variable] = value

            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            
            assignment.pop(variable)
        
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
