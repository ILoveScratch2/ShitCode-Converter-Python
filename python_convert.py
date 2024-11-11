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

# 随机生成无意义的注释，确保不会嵌套引号
def random_comment():
    # 随机决定使用字符串字面量还是传统的 # 注释
    if random.choice([True, False]):
        # 字符串注释形式：确保注释不包含 ''' 或 """ 或单引号
        comment = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        while "'''" in comment or '"""' in comment or "'" in comment:
            comment = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        return f"''' {comment} '''"
    else:
        # # 注释形式：确保注释不包含单引号
        comment = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        while "'" in comment or '"' in comment:
            comment = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        return f"# {comment}"





class ShitCodeTransformer(ast.NodeTransformer):
    def __init__(self):
        self.imports = []  # 存储修改后的导入语句
        self.global_vars = set()  # 存储全局变量名称，避免冲突
        self.remove_comments = random.choice([True, False])  # 随机决定是否去除注释

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

        # 在函数体中使用全局变量替代局部变量
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        # 如果目标变量已经存在于全局变量中，跳过
                        if target.id not in self.global_vars:
                            target.id = random.choice(['global_' + ''.join(random.choices(string.ascii_lowercase, k=6)) for _ in range(3)])
                            self.global_vars.add(target.id)

        # 修改函数调用时的名称为新的随机名称
        self.replace_function_calls(old_name, node.name)

        # 添加无意义的注释
        node.body.insert(random.randint(0, len(node.body)), ast.Expr(value=ast.Str(s=random_comment())))

        return node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            # 确保不替换 print 函数
            if node.func.id != 'print':
                node.func.id = random_function_name()
        return node


    def visit_Assign(self, node):
        # 替换变量名称为全局变量，且不与现有全局变量冲突
        if isinstance(node.targets[0], ast.Name):
            new_name = random.choice(['global_' + ''.join(random.choices(string.ascii_lowercase, k=6)) for _ in range(3)])
            while new_name in self.global_vars:  # 确保新变量名不冲突
                new_name = random.choice(['global_' + ''.join(random.choices(string.ascii_lowercase, k=6)) for _ in range(3)])
            node.targets[0].id = new_name
            self.global_vars.add(new_name)

        # 添加无意义的注释
        node.value = ast.Call(func=ast.Name(id=random_function_name(), ctx=ast.Load()), args=[], keywords=[])
        node.value.lineno = node.lineno  # 保证注释不影响代码格式
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

        # 处理代码体中的所有节点
        for stmt in node.body:
            self.visit(stmt)

        # 如果需要去除注释，删除所有注释节点
        if self.remove_comments:
            node.body = [stmt for stmt in node.body if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Str)]
        else:
            # 否则，替换注释为随机注释
            for stmt in node.body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Str):
                    stmt.value.s = random_comment()  # 替换注释内容

        # 始终插入一些无意义的注释
        for i in range(random.randint(1, 3)):  # 随机添加1到3个无意义注释
            node.body.insert(random.randint(0, len(node.body)), ast.Expr(value=ast.Str(s=random_comment())))

        return node
def visit_BinOp(self, node):
    # 递归访问左右操作数
    self.generic_visit(node)

    # 随机生成空格
    left_spaces = ' ' * random.randint(0, 3)
    right_spaces = ' ' * random.randint(0, 3)

    # 创建新的操作符节点
    new_node = ast.BinOp(
        left=ast.BinOp(left=node.left, op=node.op, right=ast.Str(s=left_spaces)),
        op=node.op,
        right=ast.BinOp(left=ast.Str(s=right_spaces), op=node.op, right=node.right)
    )

    return new_node



        
    def visit(self, node):
        # 处理二元操作符
        if isinstance(node, ast.BinOp):
            return self.visit_BinOp(node)
        return self.generic_visit(node)


def generate_shitcode(code):
    tree = ast.parse(code)
    transformer = ShitCodeTransformer()
    transformer.tree = tree  # 给转换器提供完整的AST树，以便替换函数调用
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    return transformed_tree


def unparse_ast(tree):
    return ast.unparse(tree)


# 原始干净的 Python 代码
original_code = """
print("Hello, world!")
print(1124+1)
"""

# 生成 Shitcode
transformed_tree = generate_shitcode(original_code)

# 将 AST 转换回代码并输出
shity_code = unparse_ast(transformed_tree)
print(shity_code)
