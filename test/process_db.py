import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.processing.main import ArticleProcessingTool
import src.infrastructure.utils.PathUtil as DirUtil
from dotenv import load_dotenv
load_dotenv()

tool = ArticleProcessingTool()
output_path = tool.process_with_database(
    config_name="db_file_import",
    input_path=str(DirUtil.concat_path(DirUtil.get_project_base_dir(),"result/Huggingface/Blog/Trending/test"))
)
print(output_path)
