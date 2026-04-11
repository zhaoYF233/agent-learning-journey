import streamlit as st

st.set_page_config(page_title="🤖 天气智能助手",page_icon="☀️")#这是 Streamlit 的要求——页面配置必须在任何其他 Streamlit 命令之前调用。

from day5_agent_real import ChatAgent

# --- 页面配置 --

st.title("🤖 你的真·AI助手")

if "agent" not in st.session_state:
    st.session_state.agent = ChatAgent()

# --- 初始化聊天历史（如果 session_state 中没有，就创建一个）---
if "messages" not in st.session_state:
    # 预设一条欢迎消息
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是你的天气助手。你可以问我任何城市的天气，或者和我聊天。我叫什么名字取决于你告诉我什么 😊"}
    ]

# --- 显示所有历史消息 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# --- 接收用户输入 ---
if prompt := st.chat_input("输入你的问题..."):
    # 1. 把用户消息存入 session_state 并立即显示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 显示一个临时回复（先占位，后面会替换为真实 Agent 回复）
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            response = st.session_state.agent.chat(prompt)
        st.markdown(response)

        # 3. 把临时回复也存入历史（等接入 Agent 后，这里会变成真实回复）
        st.session_state.messages.append({"role": "assistant", "content": "这是一个测试回复，后续会接入真实 Agent。"})


















