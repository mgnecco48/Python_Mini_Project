import numpy as np
from rich.console import Console

console = Console()


row1 = [1] * 3
row2 = [2] * 3
row3 = [3] * 3

array = np.array([row1, row2, row3])
console.clear()
console.print()
console.print(len(array), justify="center")
console.print()
console.print(len(array[0]), justify="center")


diag = []
for i, row in enumerate(array):
    diag.append(row[i])

console.print("-" * 5, justify="center")
console.print(diag, justify="center")

diag = []
for i, row in enumerate(array):
    diag.append(row[-(i + 1)])

console.print("-" * 5, justify="center")
console.print(diag, justify="center")
