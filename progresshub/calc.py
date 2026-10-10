import ast
import math
import operator

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

BUILTINS = {
    "sqrt": math.sqrt, "abs": abs, "round": round, "floor": math.floor,
    "ceil": math.ceil, "log": math.log10, "ln": math.log, "sin": math.sin,
    "cos": math.cos, "tan": math.tan, "pi": math.pi, "e": math.e,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fn = BUILTINS.get(node.func.id)
        if fn is None:
            raise ValueError(f"Unknown function: {node.func.id}")
        return fn(*(_eval(a) for a in node.args))
    if isinstance(node, ast.Name) and node.id in BUILTINS:
        return BUILTINS[node.id]
    raise ValueError("Unsupported expression")


def evaluate(expr):
    expr = (expr or "").replace("^", "**")
    if not expr.strip():
        raise ValueError("Empty")
    tree = ast.parse(expr, mode="eval")
    return _eval(tree.body)


# --- calories needed (Mifflin-St Jeor with activity factor) ----------------

ACTIVITY = {"sedentary": 1.2, "light": 1.375, "active": 1.55, "very": 1.725}

def calories_needed(weight_kg, height_cm, age, male, activity="light"):
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if male else -161)
    return bmr * ACTIVITY.get(activity, 1.375)


# --- fitness ------------------------------------------------------------------

def one_rep_max(weight, reps):
    if reps >= 1:
        return weight * (1 + reps / 30)
    return 0


# --- trading --------------------------------------------------------------------

def risk_size(account, risk_pct, entry, stop):
    risk_pct = risk_pct / 100.0
    risk_per_share = abs(entry - stop)
    if risk_per_share <= 0:
        raise ValueError("Entry and stop can't be equal.")
    return (account * risk_pct) / risk_per_share


def pnl(direction, entry, exit_p, qty):
    return (exit_p - entry) * qty if direction == "long" else (entry - exit_p) * qty


def bmi(weight_kg, height_cm):
    m = height_cm / 100
    return weight_kg / (m * m)