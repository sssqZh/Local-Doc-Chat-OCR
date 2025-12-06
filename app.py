"""
Streamlit RAG 知识库问答系统前端

该模块实现了基于 Streamlit 的用户界面，包括：
- 侧边栏文件上传功能
- 主界面流式对话
- 知识库管理
"""

import streamlit as st
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

from rag_engine import RAGEngine

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="RAG 知识库问答系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .info-box {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_rag_engine() -> RAGEngine:
    """
    初始化 RAG 引擎（使用缓存避免重复初始化）

    Returns:
        RAGEngine 实例
    """
    try:
        return RAGEngine()
    except Exception as e:
        st.error(f"初始化 RAG 引擎失败: {str(e)}")
        st.stop()
        # 这行代码不会执行，因为 st.stop() 会停止执行
        # 但为了类型检查，我们需要返回一个值
        raise  # 重新抛出异常


def main():
    """主函数"""
    # 初始化 RAG 引擎
    if 'rag_engine' not in st.session_state:
        try:
            st.session_state.rag_engine = init_rag_engine()
        except Exception as e:
            st.error(f"初始化失败: {str(e)}")
            st.info("请检查 .env 文件中的配置是否正确，特别是 DEEPSEEK_API_KEY")
            st.stop()

    rag_engine = st.session_state.rag_engine

    # 标题
    st.markdown('<p class="main-header">📚 RAG 知识库问答系统</p>', unsafe_allow_html=True)

    # 侧边栏
    with st.sidebar:
        st.markdown('<p class="sidebar-header">📁 文档管理</p>', unsafe_allow_html=True)

        # 文件上传
        uploaded_files = st.file_uploader(
            "上传文档",
            type=['pdf', 'md', 'txt', 'markdown'],
            accept_multiple_files=True,
            help="支持 PDF、Markdown 和文本文件"
        )

        # 上传按钮
        if st.button("📤 添加到知识库", type="primary", use_container_width=True):
            if uploaded_files:
                with st.spinner("正在处理文档..."):
                    for uploaded_file in uploaded_files:
                        file_content = uploaded_file.read()
                        result = rag_engine.add_document(file_content, uploaded_file.name)

                        if result["success"]:
                            st.success(f"✅ {result['message']} (分块数: {result['chunks_count']})")
                        else:
                            st.error(f"❌ {result['message']}")
            else:
                st.warning("请先选择要上传的文件")

        st.divider()

        # 知识库统计
        st.markdown('<p class="sidebar-header">📊 知识库统计</p>', unsafe_allow_html=True)
        stats = rag_engine.get_stats()
        st.metric("文档片段数", stats["total_chunks"])
        st.caption(f"集合名称: {stats['collection_name']}")

        st.divider()

        # 清空知识库
        st.markdown('<p class="sidebar-header">⚙️ 管理操作</p>', unsafe_allow_html=True)
        if st.button("🗑️ 清空知识库", use_container_width=True):
            if st.session_state.get('confirm_clear', False):
                rag_engine.clear_knowledge_base()
                st.success("知识库已清空")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("请再次点击确认清空")

        if st.session_state.get('confirm_clear', False):
            st.button("取消", on_click=lambda: st.session_state.update({'confirm_clear': False}))

        st.divider()

        # 使用说明
        with st.expander("📖 使用说明"):
            st.markdown("""
            **使用步骤：**
            1. 在侧边栏上传 PDF/MD/TXT 文件
            2. 点击"添加到知识库"按钮
            3. 在主界面输入问题开始对话
            4. 系统会基于上传的文档回答问题

            **支持格式：**
            - PDF 文档 (.pdf)
            - Markdown 文件 (.md, .markdown)
            - 文本文件 (.txt, .text)

            **注意事项：**
            - 确保 Ollama 服务正在运行（用于 Embedding）
            - 确保已配置 DeepSeek API Key
            - 首次使用需要下载 all-minilm 模型
            """)

    # 主界面
    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 生成回答
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # 流式生成回答
            try:
                for chunk in rag_engine.query(prompt, stream=True):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)
            except Exception as e:
                error_msg = f"生成回答时出错: {str(e)}"
                message_placeholder.error(error_msg)
                full_response = error_msg

        # 添加助手消息
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 底部信息
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("💡 提示：系统会基于您上传的文档回答问题")
    with col2:
        st.caption("🔍 支持流式对话，实时显示回答")
    with col3:
        st.caption("📚 知识库片段数: " + str(stats["total_chunks"]))


if __name__ == "__main__":
    main()

