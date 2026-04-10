from openai import OpenAI

# 👇 把引号里的内容替换成你自己的 API Key
client = OpenAI(
    api_key="sk-ff5dbe36db204dd38803f175ca0a02fa",  # 粘贴你复制的 Key
    base_url="https://api.deepseek.com"
)

class ChatAgent:
    def __init__(self):
        self.memory = []

    def remember(self, role, content):
        self.memory.append({"role": role, "content": content})

    def chat(self, user_input):
        self.remember("user", user_input)

        response = client.chat.completions.create(  #内部是如何打包数据、发送网络请求的？——暂时不用管。
            model="deepseek-chat",
            messages=self.memory,
            stream=False
        )

        reply = response.choices[0].message.content  #记住这是从返回包里把 AI 的话“掏出来”的固定写法。
        self.remember("assistant", reply)
        return reply

if __name__ == "__main__":
    agent = ChatAgent()
    print("🤖 你的真·AI助手已上线！输入 'q' 退出。\n")

    while True:
        msg = input("你： ")
        if msg.lower() in ["q", "quit", "exit"]:
            print("AI：再见！")
            break
        res = agent.chat(msg)
        print("AI：", res)