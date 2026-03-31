import sys
print("Python版本:", sys.version)

try:
    from flask import Flask
    print("✓ Flask导入成")
except ImportError as e:
    print("✗ Flask导入失败:", e)

try:
    import numpy as np
    print("✓ NumPy导入成功")
except ImportError as e:
    print("✗ NumPy导入失败:", e)

try:
    import scipy
    print("✓ SciPy导入成功")
except ImportError as e:
    print("✗ SciPy导入失败:", e)

print("诊断完成")
input("按Enter键退出...")