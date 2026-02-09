# Consider the following Counting game:
#
# A player draws 6 different numbers. The goal is to combine these numbers using the elementary arithmetic operations (+, -, *, /) to obtain a number as close as possible to a given goal. 
# Combining numbers means the following. First, the player chooses an initial number from the starting six numbers in their hand. Then, they choose a second number from their hand (different from the initial one), together with an operation, and compute the result of the operation. Now they choose a third number from their hand (different from the first and the second number), an operation, and compute the results. And so on.
#
# For example, if the user draws the numbers 1, 3, 5, 8, 10 e 50, and the goal number is 462, they can combine their numbers in the following way:
#
# 8 + 1 = 9
# 9 * 50 = 450
# 450 + 10 = 460
# 460 - 3 = 457
# 457 + 5 = 462
#
# Here, the player precisely reached the goal number. However, there are cases in which this is not possible. In such cases, the player has to aim to find the closest possible number to the goal.
# If it is possible to precisely reach the goal number, the players should try to minimize the numbers used. E.g., in the previous game, a better solution would have been:
#
# 50 - 3 = 47
# 47 * 10 = 470
# 470 - 8 = 462 
#
# which only uses 4 numbers instead of 6.
#
# Each number can only be used one time. 
#
# Your task is to implement a function CountingStrategy() that takes as input a list of 6 user numbers and 1 goal number, and returns the winning strategy. 
# The winning strategy should be printed in the following form:
#   Initial number: <n1>
#   Step 1: operation <operation> with number <n2> -> result <r2>
#   Step 2: operation <operation> with number <n3> -> result <r3>
#   ...
#   Final number: <final_result>
#   Distance from goal: <distance>
#
#
# E.g.:
# CountingStrategy([1, 3, 5, 8, 10, 50], 462) should output:
#   Initial number: 50
#   Step 1: operation - with number 3 -> result 47
#   Step 2: operation * with number 10 -> result 470
#   Step 3: operation - with number 8 -> result 462
#   Final number: 462
#   Distance from goal: 0
#

from z3 import *

def Abs(v):
    return If(v >= 0, v, -v)

def extract_solution(model, numbers, num_steps, num_idx, ops, result, Operation, goal):

    solution = {
        'num_steps': num_steps,
        'steps': []
    }
    
    # initial number 
    idx = model.eval(num_idx[0]).as_long()
    
    solution['initial_num'] = numbers[idx]
    
    # for each step get number and operation used and result 
    for i in range(1, num_steps):
        idx = model.eval(num_idx[i]).as_long()
        num_used = numbers[idx]

        op_val = model.eval(ops[i])

        if op_val == Operation.add:
            op_str = '+'
        elif op_val == Operation.sub:
            op_str = '-'
        elif op_val == Operation.mul:
            op_str = '*'
        elif op_val == Operation.div:
            op_str = '/'
        
        # get result at step i
        res = model.eval(result[i])
        
        # check if decimal or int and cast
        res_value = res.as_long() if res.is_int_value() else float(res.as_decimal(3))
        
        solution['steps'].append({
            'operation': op_str,
            'number': num_used,
            'result': res_value
        })
    
    # get final result
    res_final = model.eval(result[num_steps - 1]).as_long()

    solution['final_result'] = res_final

    # compute distance from goal
    solution['distance'] = abs(res_final - goal)
    
    return solution

def print_solution(solution):
    print(f"Initial number: {solution['initial_num']}")
    for i, step in enumerate(solution['steps']):
        print(f"Step {i+1}: operation {step['operation']} with number {step['number']} -> result {step['result']}")
    print(f"Final number: {solution['final_result']}")
    print(f"Distance from goal: {solution['distance']}")


def CountingStrategy(numbers, goal):
    
    print(f"Finding solution for numbers: {numbers} and goal: {goal}\n")

    MAX_STEPS = len(numbers)

    Operation = Datatype('Operation')
    Operation.declare('add')   
    Operation.declare('sub')   
    Operation.declare('mul')   
    Operation.declare('div')   
    Operation = Operation.create()
    
    best_solution = None
    best_distance = float('inf')
    best_num_steps = MAX_STEPS + 1
    
    for num_steps in range(1, MAX_STEPS + 1):
        
        s = Solver()
        
        # result at step i
        result = [Real(f'result_{i}') for i in range(num_steps)]
        
        # number used at step i
        num_idx = [Int(f'num_idx_{i}') for i in range(num_steps)]
        
        # operation at step i
        ops = [Const(f'op_{i}', Operation) for i in range(num_steps)]
            
        # constraint to use each number at most once
        s.add(Distinct(num_idx))
        
        # create constraints for choosing the initial values and the first step
        initial_value_constraints = [And(num_idx[0] == j, result[0] == n) for j, n in enumerate(numbers)]
        s.add(Or(initial_value_constraints))
        
        # create transitions for each step and for each number
        for i in range(1, num_steps):
            all_transitions = []
            for j, n in enumerate(numbers):
                add_trans = And(
                    num_idx[i] == j, # number at index j is used at step i
                    ops[i] == Operation.add, # update operation
                    result[i] == result[i-1] + n # update value
                )
                sub_trans = And(
                    num_idx[i] == j,
                    ops[i] == Operation.sub,
                    result[i] == result[i-1] - n
                )
                mul_trans = And(
                    num_idx[i] == j,
                    ops[i] == Operation.mul,
                    result[i] == result[i-1] * n
                )
                
                div_trans = And(
                    num_idx[i] == j,
                    ops[i] == Operation.div,
                    n != 0, # avoid division by zero
                    result[i] == result[i-1] / n
                )
                all_transitions.extend([add_trans, sub_trans, mul_trans, div_trans])

            s.add(Or(all_transitions))
        
        # variable and constraint for the distance from the goal
        distance = Real('distance')
        final_result = result[num_steps - 1]

        s.add(And(
                Or(final_result >= goal, final_result < goal),
                distance == Abs(final_result - goal))
        )
    
        # save state to find exact solution
        s.push()

        s.add(final_result == goal)
        
        if s.check() == sat:
            # found exact solution with minimum steps
            m = s.model()
            solution = extract_solution(m, numbers, num_steps, num_idx, ops, result, Operation, goal)
            
            best_solution = solution
            best_distance = solution['distance']
            best_num_steps = solution['num_steps']
            
            break
        
        # no exact match, find closest solution
        s.pop()
        
        opt = Optimize()

        # add all the constrains to the optimizer
        opt.add(s.assertions())
        
        # objective to minimize the distance from the goal
        opt.minimize(distance)
        
        if opt.check() == sat:
            m = opt.model()

            solution = extract_solution(m, numbers, num_steps, num_idx, ops, result, Operation, goal)

            # update closest solution if better
            if solution['distance'] < best_distance or \
               (solution['distance'] == best_distance and solution['num_steps'] < best_num_steps):
                best_solution = solution
                best_distance = solution['distance']
                best_num_steps = solution['num_steps']
            
    
    if best_solution:
        print_solution(best_solution)
    else:
        print("No solution found!")

if __name__ == "__main__":
    print("\n----------Example Test----------")
    CountingStrategy([1, 3, 5, 8, 10, 50], 462)
    print("-----------------------------------")
    print("\n-------------Test 1-------------")
    CountingStrategy([1, 2, 3, 4, 5, 6], 463)
    print("-----------------------------------")
    print("\n-------------Test 2-------------")
    CountingStrategy([1, 3, 5, 8, 10, 50], 94)
    print("-----------------------------------")
    print("\n-------------Test 3-------------")
    CountingStrategy([2, 4, 6, 8, 10, 12], 100)
    print("-----------------------------------")
    print("\n-------------Test 4-------------")
    CountingStrategy([8, 1, 7, 3, 9, 5], 900)
    print("-----------------------------------")

