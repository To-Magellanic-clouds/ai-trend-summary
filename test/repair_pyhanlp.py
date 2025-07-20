import jpype
import os

# 硬编码所有必要路径
jpype_path = r"D:\code\ai-trend-summary\.venv\Lib\site-packages\org.jpype.jar"
hanlp_path = r"D:\code\ai-trend-summary\.venv\Lib\site-packages\pyhanlp\static\hanlp-1.8.6.jar"

# 确保文件存在
assert os.path.exists(jpype_path), f"JPype jar 不存在于 {jpype_path}"
assert os.path.exists(hanlp_path), f"HanLP jar 不存在于 {hanlp_path}"

# 启动JVM时强制指定classpath
jpype.startJVM(
    jpype.getDefaultJVMPath(),
    f"-Djava.class.path={jpype_path};{hanlp_path}",
    convertStrings=False  # 关键参数
)