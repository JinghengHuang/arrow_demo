from lark import Lark, Transformer, v_args
from pyomo.environ import *

grammar = r"""
    ?start: sum_expr
          | expr
          | relation


    ?relation: expr "<=" expr "<=" expr    -> between
             | expr "<=" expr              -> le
             | expr ">=" expr              -> ge
             | expr "=" expr               -> eq
             
    ?sum_expr: "sum" "(" indexer ")" expr -> summation

    ?indexer: CNAME "in" CNAME      -> indexer

    ?expr: expr "+" term            -> add
         | expr "-" term            -> sub
         | term

    ?term: term "*" factor          -> mul
         | term "/" factor          -> div
         | factor

    ?factor: "-" factor             -> neg
           | atom

    ?atom: CNAME "[" CNAME "]"      -> indexed
         | CNAME                    -> var
         | NUMBER                   -> number
         | "(" expr ")"

    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""


@v_args(inline=True)
class PyomoTransformer(Transformer):
    def __init__(self, model, local_vars=None):
        self.model = model
        self.local_vars = local_vars or {}
        self.index_val_list = []
        self.curr_idx = 0

    def number(self, token): return float(token)
    def var(self, name): 
        return self._resolve(str(name))
    def indexer(self, name, *indices):
        # Reset the curr index
        self.curr_idx = 0
        name = str(indices[0])
        # Transform each index token
        index_vals = tuple(
            self._resolve(self.transform(index)) if hasattr(index, 'children') else self._resolve(index)
            for index in indices
        )
        print("Index value:", index_vals)

        if len(index_vals) == 1:
            index_vals = index_vals[0]

        component = getattr(self.model, name)
        self.index_val_list = component.value_list

    def indexed(self, name, *indices):
        print("Index value:", self.index_val_list)

        index_vals = self.index_val_list[self.curr_idx]

        self.curr_idx += 1
        component = getattr(self.model, name)
        return component[index_vals]

    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b
    def mul(self, a, b): return a * b
    def div(self, a, b): return a / b
    def neg(self, x): return -x

    def le(self, a, b): return a <= b
    def ge(self, a, b): return a >= b
    def eq(self, a, b): return a == b
    def between(self, lb, mid, ub): return inequality(lb, mid, ub)

    # TODO Solve the mystery of this thing
    def summation(self, index_var, set_name):
        set_obj = getattr(self.model, str(set_name))
        index_str = str(index_var)

        result = 0
        for idx in set_obj:
            sub_transformer = PyomoTransformer(self.model, {**self.local_vars, index_str: idx})
            result += sub_transformer
        return result

    def _resolve(self, token):
        token = str(token)
        if token in self.local_vars:
            return self.local_vars[token]
        elif hasattr(self.model, token):
            return getattr(self.model, token)
        else:
            return token

    # ------------ EXPRESSION PARSER ------------
def parse_expr(expr_str, model, local_vars=None):
    parser = Lark(grammar, parser="lalr", propagate_positions=False)
    tree = parser.parse(expr_str)
    return PyomoTransformer(model, local_vars).transform(tree)

# ------------ BUILD PYOMO MODEL FROM JSON IR ------------
def build_model_structure(ir):
    model = ConcreteModel()

    # Sets
    for sname in ir.get("sets", {}):
        setattr(model, sname, Set(initialize=[]))

    # Parameters
    for pname, pdef in ir.get("parameters", {}).items():
        sets = tuple(getattr(model, s) for s in pdef.get("index", []))
        setattr(model, pname, Param(*sets, mutable=True, default=0))

    # Variables
    for vname, vdef in ir.get("variables", {}).items():
        sets = tuple(getattr(model, s) for s in vdef.get("index", []))
        domain = {
            "Continuous": Reals,
            "NonNegative": NonNegativeReals,
            "Binary": Binary,
            "Integer": Integers
        }.get(vdef.get("type", "Continuous"), Reals)
        bounds = (
            vdef.get("bounds", {}).get("lb", None),
            vdef.get("bounds", {}).get("ub", None)
        )
        setattr(model, vname, Var(*sets, domain=domain, bounds=bounds))

    return model

def attach_constraints_and_objective(model, ir):
    # Objective
    if "objective" in ir:
        odef = ir["objective"]
        expr = parse_expr(odef["expression"], model)
        model.obj = Objective(expr=expr, sense=minimize if odef["sense"] == "minimize" else maximize)

    # Constraints
    for cname, cdef in ir.get("constraints", {}).items():
        if "index" in cdef:
            index_var, index_set = cdef["index"][0].split(" in ")
            index_set = getattr(model, index_set)

            def rule(m, i, expr_str=cdef["expression"], var=index_var):
                return parse_expr(expr_str, m, {var: i})

            setattr(model, cname, Constraint(index_set, rule=rule))
        else:
            expr = parse_expr(cdef["expression"], model)
            setattr(model, cname, Constraint(expr=expr))