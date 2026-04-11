from openai import OpenAI
import json
import os

# 👇 把引号里的内容替换成你自己的 API Key
client = OpenAI(
    api_key="sk-ff5dbe36db204dd38803f175ca0a02fa",  # 粘贴你复制的 Key
    base_url="https://api.deepseek.com"
)
# --- 👇 新增：工具定义（告诉模型你有什么工具）---
tools = [
    {
        "type":"function",
        "function":{
            "name":"get_weather",
            "description":"查询指定的城市的天气情况",
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type":"string",
                        "description":"城市名称，例如：北京、上海"
                    }
                },
                "required":["city"]
            }
        }
    }
]

class ChatAgent:
    memory_file = "memory.json"
    max_memory_items = 10   # 保留最近10条消息

    def __init__(self):
        self.memory = []
        self.load_memory()   # 启动时加载

    def save_memory(self):
        """将当前记忆保存到文件"""
        try:
            with open(self.memory_file,"w",encoding="utf-8") as f:
                json.dump(self.memory,f,ensure_ascii=False,indent=2)
        except Exception as e:
            print(f"保存记忆失败：{e}")

    def load_memory(self):
        """从文件加载记忆"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file,"r",encoding="utf-8") as f:
                    self.memory = json.load(f)
            except Exception as e:
                print(f"加载记忆失败：{e}")
                self.memroy = []

    def remember(self, role, content,tool_call_id=None):
        #三个参数，若只有两个参数，最后一个默认为None
        """
        记忆存储（升级版：支持 tool 角色）。
        """
        msg = {"role":role,"content":content}
        if tool_call_id:   #第一次调用 self.remember 直接跳过
            msg["tool_call_id"]=tool_call_id
        self.memory.append(msg)

        # 裁剪记忆：保留 system 消息和最近 MAX_MEMORY_ITEMS 条
        self._trim_memory()
        self.save_memory()    # 每次记忆变化都保存

    def _trim_memory(self):
        """滑动窗口裁剪：保留 system 消息 + 最近 MAX_MEMORY_ITEMS 条其他消息"""
        # 先把所有消息统一转成字典格式（兼容对象）
        dict_memory = []
        for m in self.memory:
            if isinstance(m, dict):
                dict_memory.append(m)
            else:
                # 如果是 ChatCompletionMessage 对象，转换成字典
                dict_memory.append(m.model_dump(exclude_none=True))

        system_msgs = [m for m in dict_memory if m.get("role") == "system"]
        other_msgs = [m for m in dict_memory if m.get("role") != "system"]

        # 只保留最近 MAX_MEMORY_ITEMS 条非 system 消息
        if len(other_msgs) > self.max_memory_items:  #max_memory_items==10
            other_msgs = other_msgs[-self.max_memory_items:] #取后10条

        self.memory = system_msgs + other_msgs

    def chat(self, user_input):
        self.remember("user", user_input)

        response = client.chat.completions.create(  #内部是如何打包数据、发送网络请求的？——暂时不用管。
            model="deepseek-chat",
            messages=self.memory,
            tools=tools,         # 👈 新增   一开始的10行的那个架构
            tool_choice="auto",  # 👈 新增：让模型自己决定是否用工具
            stream=False
        )

        message = response.choices[0].message  # 固定搭配
        """
        reply = response.choices[0].message.content  #记住这是从返回包里把 AI 的话“掏出来”的固定写法。
        self.remember("assistant", reply)
        return reply
        """
        # --- 👇 新增：判断模型是否想调用工具 ---
        if message.tool_calls:  #-------------tool_calls是 DeepSeek API 返回的 JSON 数据中自带的一个字段
            # 取出第一个工具调用请求
            tool_call =message.tool_calls[0]
            func_name = tool_call.function.name  # tool_call和10行的那个不一样
            args = json.loads(tool_call.function.arguments)

            # 根据函数名调用对应的工具
            if func_name=="get_weather":
# 改这里把from tools import get_weather中的tools改为real_tools
                from real_tools import get_weather  # 👈 从 tools.py 导入函数
                city = args.get("city")
                tool_result = get_weather(city)

                # 把模型的工具调用请求存入记忆（role = "assistant"，但包含 tool_calls）
                self.memory.append(message)#------第二个存入memory列表的东西

                # 把工具执行结果存入记忆（role = "tool"）
                self.remember("tool",tool_result,tool_call_id=tool_call.id)#------第三个个存入memory列表的东西

                # 第二次调用 API，让模型基于工具结果生成最终回答
                second_response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=self.memory,
                    stream=False
                )
                reply = second_response.choices[0].message.content
            else:
                reply = "抱歉，我暂时不支持这个工具。"
        else:
            # 正常文本回复
            reply = message.content

        # 3. 记住 AI 的最终回复
        self.remember("assistant", reply)  ##------第四个个存入memory列表的东西
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