# Counting Game Solver

This project implements an automatic strategy to solve the **Counting Game** using the **Z3** SMT solver.

Given a set of **6 distinct numbers** and a **target number (goal)**, the program searches for a sequence of arithmetic operations (`+`, `-`, `*`, `/`) that produces a result **as close as possible** to the goal.  
If the goal can be reached exactly, the solution that uses the **smallest number of values** is selected.

---

## 🧮 Counting Game Rules

- 6 initial numbers are available
- Each number can be used **only once**
- You start by choosing an initial number
- At each step:
  - choose a number that has not been used yet
  - apply one of the operations `+ - * /`
- The objective is:
  1. to minimize the distance from the goal  
  2. if the distance is 0, to minimize the number of steps

---

## ✨ Features

- Problem modeling using **SMT constraints**
- Incremental search over the minimum number of steps
- Use of `Optimize` to find the closest solution to the goal
- Clear and structured output of the winning strategy

### Output Format

```text
Initial number: <n1>
Step 1: operation <op> with number <n2> -> result <r2>
Step 2: operation <op> with number <n3> -> result <r3>
...
Final number: <final_result>
Distance from goal: <distance>
```

---

## 📦 Requirements

Python 3.8+

Z3 Solver

Z3 Installation:
```bash
pip install z3-solver
```

Execution:
```bash
python counting_game.py
