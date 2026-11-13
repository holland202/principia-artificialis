"""Frozen finite arithmetic corpus for PA-CHOICE-001 (standard library only)."""
import hashlib
import json

OPTIONS = "ABCD"
PER_TEMPLATE = 16
TEMPLATES = {
    "development": {
        "add-product": ("{a} + {b} * {c} + {d}", lambda a, b, c, d, e: a + b*c + d),
        "difference-product": ("({a} - {b}) * {c} + {d}", lambda a, b, c, d, e: (a-b)*c + d),
        "product-sum": ("{a} * ({b} + {c}) + {d}", lambda a, b, c, d, e: a*(b+c) + d),
        "sum-then-product": ("({a} + {b}) * {c} - {d}", lambda a, b, c, d, e: (a+b)*c - d),
        "two-products-add": ("{a} * {b} + {c} * {d}", lambda a, b, c, d, e: a*b + c*d),
        "two-sums-product": ("({a} + {b}) * ({c} + {d})", lambda a, b, c, d, e: (a+b)*(c+d)),
        "product-of-difference": ("{a} + {b} * ({c} - {d})", lambda a, b, c, d, e: a + b*(c-d)),
        "subtract-product-add": ("{a} - {b} * {c} + {d}", lambda a, b, c, d, e: a - b*c + d),
    },
    "holdout": {
        "nested-product": ("({a} + {b} * {c}) * {d}", lambda a, b, c, d, e: (a+b*c)*d),
        "subtract-group-product": ("{a} - ({b} + {c}) * {d}", lambda a, b, c, d, e: a - (b+c)*d),
        "two-products-subtract": ("{a} * {b} - {c} * {d}", lambda a, b, c, d, e: a*b - c*d),
        "two-differences-product": ("({a} - {b}) * ({c} - {d})", lambda a, b, c, d, e: (a-b)*(c-d)),
        "product-difference-subtract": ("{a} * ({b} - {c}) - {d}", lambda a, b, c, d, e: a*(b-c)-d),
        "product-minus-difference": ("{a} * {b} - ({c} - {d})", lambda a, b, c, d, e: a*b-(c-d)),
        "group-and-product": ("({a} + {b}) * {c} + {d} * {e}", lambda a, b, c, d, e: (a+b)*c+d*e),
        "nested-two-products": ("{a} * ({b} + {c} * {d}) - {e}", lambda a, b, c, d, e: a*(b+c*d)-e),
    },
}


def cases():
    out = []
    for split, templates in TEMPLATES.items():
        for name, (expression, solve) in templates.items():
            for index in range(PER_TEMPLATE):
                case_id = f"{name}:{index:02d}"
                entropy = hashlib.sha256(f"PA-CHOICE-001/v1/{case_id}".encode()).digest()
                a, b, c, d, e = (11 + entropy[0] % 32, 5 + entropy[1] % 15, 3 + entropy[2] % 12,
                                 2 + entropy[3] % 13, 3 + entropy[4] % 11)
                expr = expression.format(a=a, b=b, c=c, d=d, e=e)
                answer = solve(a, b, c, d, e)
                correct_position, numeric_rank = index % 4, index // 4
                steps = (1 + (a + 2*b + index) % 7, 1 + (2*b + c + 2*index) % 9,
                         1 + (3*c + d + 5*index) % 11)
                offsets = (0, steps[0], sum(steps[:2]), sum(steps))
                distractors = [rank for rank in range(4) if rank != numeric_rank]
                distractors.sort(key=lambda rank: (entropy[5+rank], rank))
                distractors.insert(correct_position, numeric_rank)
                options = [answer + offsets[rank] - offsets[numeric_rank] for rank in distractors]
                out.append({"id": case_id, "split": split, "template": name, "expression": expr,
                            "options": options, "answer": answer, "correct_index": correct_position})
    return out


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def corpus_sha(data):
    return hashlib.sha256(canonical(data)).hexdigest()
