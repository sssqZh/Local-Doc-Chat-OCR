import os
from dotenv import load_dotenv

# 1. 确定当前位置
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

print(f"📂 脚本所在目录: {current_dir}")
print(f"🔍 正在寻找文件: {env_path}")

# 2. 检查文件是否存在（以及是否名字叫 .env.txt）
print("\n--- 目录下的所有文件 (请仔细看有没有 .env.txt) ---")
files = os.listdir(current_dir)
found = False
for f in files:
    if f.startswith(".env"):
        print(f" -> 发现文件: [{f}] <--- 请确认这里是不是只有 .env")
        if f == ".env":
            found = True

if not found:
    print("\n❌ 错误：根本没找到名为 .env 的文件！")
    print("   可能原因：文件名其实是 .env.txt (Windows隐藏了后缀)")
else:
    print("\n✅ 文件存在检查通过。")

    # 3. 尝试读取内容
    print("\n--- 正在尝试读取内容 ---")
    load_dotenv(dotenv_path=env_path, override=True)
    
    key = os.getenv("DEEPSEEK_API_KEY")
    if key:
        print(f"✅ 读取成功！")
        print(f"   Key 的长度: {len(key)}")
        print(f"   Key 的开头: {key[:5]}...")
        # 检查是否有非法字符（比如括号）
        if "（" in key or "(" in key:
            print("⚠️ 警告：Key 里面好像包含了括号！请去掉！")
    else:
        print("❌ 读取失败：文件找到了，但没读到 DEEPSEEK_API_KEY。")
        print("   可能原因：.env 里变量名写错了，或者没保存。")

input("\n按回车键退出...")