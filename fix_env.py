import os

# --- 配置内容 ---
# 这里已经帮你把 OLLAMA_MODEL 改成了 'all-minilm'
# 其他配置保持标准默认值
content = """DEEPSEEK_API_KEY=sk-7af0e80749074a868cc12efa27ec7ab6
DEEPSEEK_BASE_URL=https://api.deepseek.com
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=all-minilm
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=knowledge_base
MAX_CHUNK_SIZE=500
CHUNK_OVERLAP=50"""

# MAX_CHUNK_SIZE 改成了 500 (原来是1000)，降低显存压力
# CHUNK_OVERLAP 改成了 50

# --- 写入逻辑 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

print(f"正在重写文件: {env_path}")

try:
    # 强制使用 utf-8 编码写入，确保无 BOM，无乱码
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ .env 文件已成功重写！")
    print("   -> 模型已设置为: all-minilm")
    print("   -> 分块大小已优化为: 500")
    
    # 验证读取
    from dotenv import load_dotenv
    load_dotenv(env_path, override=True)
    
    model = os.getenv("OLLAMA_MODEL")
    key = os.getenv("DEEPSEEK_API_KEY")
    
    if model == "all-minilm" and key:
        print(f"🎉 验证成功！配置已生效。")
    else:
        print("❌ 验证失败，请检查代码。")

except Exception as e:
    print(f"❌ 写入失败: {e}")