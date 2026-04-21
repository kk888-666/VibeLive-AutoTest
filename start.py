import pytest
import os

# 启动测试
if __name__ == '__main__':
    pytest.main()
    # 生成测试报告
    os.system("allure generate -o report -c temps")
