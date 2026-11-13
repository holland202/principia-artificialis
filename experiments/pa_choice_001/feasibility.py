"""Count frozen cases and check the generated keys without exposing individual items."""
import ast
from collections import Counter
import operator

from corpus import TEMPLATES, cases, corpus_sha


OPERATORS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul}


def arithmetic(node):
    if type(node) is ast.Constant and type(node.value) is int:
        return node.value
    if type(node) is ast.BinOp and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](arithmetic(node.left), arithmetic(node.right))
    raise ValueError("unexpected arithmetic syntax")


def main():
    rows = cases()
    unique = len({row["expression"] for row in rows})
    matches = sum(arithmetic(ast.parse(row["expression"], mode="eval").body) == row["answer"] for row in rows)
    if len({row["id"] for row in rows}) != len(rows) or unique != len(rows) or matches != len(rows):
        raise ValueError("duplicate case or arithmetic key mismatch")
    if any(len(set(row["options"])) != 4 or row["options"][row["correct_index"]] != row["answer"] for row in rows):
        raise ValueError("invalid answer set")
    print("cases", len(rows), "unique expressions", unique, "separate AST answer matches", matches)
    for split, templates in TEMPLATES.items():
        selected = [row for row in rows if row["split"] == split]
        positions = Counter(row["correct_index"] for row in selected)
        ranks = Counter(sorted(row["options"]).index(row["answer"]) for row in selected)
        signs = tuple(sum(test(row["answer"]) for row in selected)
                      for test in (lambda x: x < 0, lambda x: x == 0, lambda x: x > 0))
        print(split, "cases", len(selected), "templates", len(templates),
              "correct positions", sorted(positions.items()), "correct numeric ranks", sorted(ranks.items()),
              "negative/zero/positive", *signs, "sha256", corpus_sha(selected))
    print("full corpus sha256", corpus_sha(rows))


if __name__ == "__main__":
    main()
