import shutil
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 数据库文件夹路径
db_path = os.path.join(current_dir, 'chroma_db')

print(f"正在寻找数据库: {db_path}")

if os.path.exists(db_path):
    try:
        # 强制删除整个文件夹
        shutil.rmtree(db_path)
        print("✅ 成功删除旧的数据库文件夹！")
        print("现在你可以重新运行 streamlit，系统会自动创建一个适配 all-minilm 的新库。")
    except Exception as e:
        print(f"❌ 删除失败，请手动删除文件夹。错误: {e}")
        print("提示：请先关闭正在运行的 streamlit 终端，否则文件被占用删不掉。")
else:
    print("✅ 没有发现旧数据库，你可以直接开始使用。")