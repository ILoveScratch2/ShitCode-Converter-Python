import ast
import random
import string

# 用于生成随机函数名称和库别名
def random_function_name():
    return ''.join(random.choices(string.ascii_lowercase, k=8))

def random_lib_name():
    return ''.join(random.choices(string.ascii_lowercase, k=6))

# 用于生成随机的 Python 内置库
builtin_libraries = [
    'os', 'sys', 'math', 'time', 'random', 'collections', 'functools', 'itertools', 'pickle', 'socket'
]

class ShitCodeTransformer(ast.NodeTransformer):
    def __init__(self):
        self.imports = []  # 存储修改后的导入语句

    def visit_Import(self, node):
        # 只修改别名部分，而不修改库名
        for alias in node.names:
            if alias.asname:
                alias.asname = random_lib_name()  # 修改别名
        return node

    def visit_ImportFrom(self, node):
        # 对from ... import ... 语句做同样处理，只修改别名部分
        for alias in node.names:
            if alias.asname:
                alias.asname = random_lib_name()  # 修改别名
        return node

    def visit_FunctionDef(self, node):
        # 修改函数名称为随机的无意义名称
        old_name = node.name
        node.name = random_function_name()

        # 添加无意义的循环或者冗余代码，使得函数内容不再清晰
        for _ in range(random.randint(0, 2)):  # 添加随机数量的无效循环
            new_node = ast.For(
                target=ast.Name(id='i', ctx=ast.Store()),
                iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()), args=[ast.Constant(value=10)], keywords=[]),
                body=[ast.Pass()],
                orelse=[]
            )
            node.body.append(new_node)

        # 修改函数调用时的名称为新的随机名称
        self.replace_function_calls(old_name, node.name)

        return node

    def visit_Call(self, node):
        # 遍历函数调用，将函数名称替换为新名称
        if isinstance(node.func, ast.Name):
            node.func.id = random_function_name()
        return node

    def visit_Assign(self, node):
        # 替换变量名称为无意义的名称
        if isinstance(node.targets[0], ast.Name):
            node.targets[0].id = random.choice(['qwerty', 'abcd', 'zxcvbnm', 'asdfgh', 'randomname'])
        return node

    def visit_Expr(self, node):
        # 如果存在print等表达式，替换为一个无关的函数调用
        if isinstance(node.value, ast.Call):
            node.value.func = ast.Name(id=random_function_name(), ctx=ast.Load())
        return node

    def replace_function_calls(self, old_name, new_name):
        # 遍历AST树中的所有节点，替换函数调用
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == old_name:
                node.func.id = new_name

    def add_random_imports(self):
        # 随机选择并导入一些内置库（未使用）
        for _ in range(random.randint(1, 3)):
            lib = random.choice(builtin_libraries)
            alias = random_lib_name()
            import_node = ast.Import(names=[ast.alias(name=lib, asname=alias)])
            self.imports.append(import_node)

    def visit_Module(self, node):
        # 首先添加随机导入
        self.add_random_imports()

        # 将所有的导入语句添加到模块体的开头
        node.body = self.imports + node.body

        # 然后继续处理AST
        for stmt in node.body:
            self.visit(stmt)

        return node


def generate_shitcode(code):
    tree = ast.parse(code)
    transformer = ShitCodeTransformer()
    transformer.tree = tree  # 给转换器提供完整的AST树，以便替换函数调用
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    return transformed_tree


def unparse_ast(tree):
    try:
        # 尝试使用 ast.unparse (适用于 Python 3.9 及以上版本)
        return ast.unparse(tree)
    except AttributeError:
        # 对于旧版本 Python（低于 3.9），使用 astor
        import astor
        return astor.to_source(tree)


# 原始干净的 Python 代码
original_code = """
import math
import random

def add(a, b):
    return a + b

def main():
    x = 5
    y = 10
    result = add(x, y)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""

# 生成 Shitcode
transformed_tree = generate_shitcode(original_code)

# 将 AST 转换回代码并输出
shity_code = unparse_ast(transformed_tree)
print(shity_code)
