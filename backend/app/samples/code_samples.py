"""
Pre-loaded code samples and error demonstration programs for all supported languages.
"""
from typing import Dict, Any, List

CODE_SAMPLES: List[Dict[str, Any]] = [
    {
        "id": "c-prompt-demo",
        "name": "C: Semicolon Error Demo (Prompt Example)",
        "language": "c",
        "target_default": "python",
        "description": "Standard prompt demonstration: C program with missing semicolons in variable assignment and printf.",
        "has_errors": True,
        "code": """#include <stdio.h>

int main() {
    int a = 10
    int b = 20;

    printf("%d", a + b)

    return 0;
}"""
    },
    {
        "id": "c-fibonacci",
        "name": "C: Fibonacci Sequence Loop",
        "language": "c",
        "target_default": "python",
        "description": "Clean C loop calculating first 8 Fibonacci numbers.",
        "has_errors": False,
        "code": """#include <stdio.h>

int main() {
    int n = 8;
    int t1 = 0;
    int t2 = 1;
    int i = 1;
    
    while (i <= n) {
        printf("%d ", t1);
        int nextTerm = t1 + t2;
        t1 = t2;
        t2 = nextTerm;
        i = i + 1;
    }
    return 0;
}"""
    },
    {
        "id": "py-vertical-slice",
        "name": "Python: Vertical Slice (Functions & Conditionals)",
        "language": "python",
        "target_default": "javascript",
        "description": "Computes max of two numbers with arithmetic and conditional branching.",
        "has_errors": False,
        "code": """def max_value(a, b):
    if a > b:
        return a
    else:
        return b

def main():
    x = 42
    y = 88
    result = max_value(x, y)
    print(result)

if __name__ == "__main__":
    main()"""
    },
    {
        "id": "py-syntax-errors",
        "name": "Python: Missing Colons & Delimiters",
        "language": "python",
        "target_default": "javascript",
        "description": "Demonstrates missing colons after function header and if conditional.",
        "has_errors": True,
        "code": """def calculate_total(price, tax)
    if price > 100
        discount = 10
    else
        discount = 0
    return price + tax - discount

def main():
    total = calculate_total(150, 15)
    print(total)

if __name__ == "__main__":
    main()"""
    },
    {
        "id": "js-arithmetic-loop",
        "name": "JavaScript: Sum of Numbers Loop",
        "language": "javascript",
        "target_default": "python",
        "description": "Modern JS script using let and while loop to accumulate sum.",
        "has_errors": False,
        "code": """function calculateSum(limit) {
  let sum = 0;
  let i = 1;
  while (i <= limit) {
    sum += i;
    i++;
  }
  return sum;
}

function main() {
  let total = calculateSum(10);
  console.log(total);
}

main();"""
    },
    {
        "id": "cpp-cout-demo",
        "name": "C++: Stream Output & Logic",
        "language": "cpp",
        "target_default": "python",
        "description": "C++ program using cout and arithmetic calculations.",
        "has_errors": False,
        "code": """#include <iostream>
using namespace std;

int main() {
    int base = 5;
    int height = 10;
    int area = (base * height) / 2;
    cout << area << endl;
    return 0;
}"""
    },
    {
        "id": "java-class-demo",
        "name": "Java: Class & Main Method",
        "language": "java",
        "target_default": "python",
        "description": "Standard Java program with class Main and System.out.println.",
        "has_errors": False,
        "code": """public class Main {
    public static void main(String[] args) {
        int a = 15;
        int b = 25;
        int sum = a + b;
        System.out.println(sum);
    }
}"""
    }
]

def get_samples() -> List[Dict[str, Any]]:
    return CODE_SAMPLES
