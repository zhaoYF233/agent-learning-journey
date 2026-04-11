import requests
import os

def get_weather(city):
    """
    通过和风天气API查询真实天气
    """
    original_city = city  # 👈 新增：保存原始输入的中文城市名
    # 👇 新增：中文城市名 → LocationID 映射表
    city_map = {
        "北京": "101010100",
        "上海": "101020100",
        "广州": "101280101",
        "深圳": "101280601",
        "洛阳": "101180901"
    }
    # 把中文城市名转换成数字ID，如果不在字典里则保持原样（兼容直接传ID的情况）
    city = city_map.get(city, city)  # 第一个 city：是你传入函数的原始参数，比如 "北京"。它作为 “键” 去字典里查找
                                    #第二个 city：是 “默认值”。如果字典里找不到第一个 city，就原样返回第二个 city。
    api_key = os.getenv("QWEATHER_API_KEY")

    url = "https://m93aaqv98d.re.qweatherapi.com/v7/weather/now"
    params = {           #这是你给服务器的“菜单选项”。你告诉它：
        "location":city, #location：我想查哪个城市（比如 "北京"）
        "key":api_key    #key：这是我的钥匙，请验证。
    }

    try:  #真正打电话给服务器。把 url 和 params 打包发出去，最多等 10 秒
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url,params=params,headers=headers,timeout=10)
        response.raise_for_status() #检查一下“电话有没有接通”。如果网络断了、服务器崩了、网址写错了，这一行会主动报错，让程序跳到 except 处理。
        data = response.json()  #把一长串 JSON 字符串翻译成 Python 字典

        if data["code"] == "200": #检查服务器返回的状态码，"200" 是和风天气规定的“成功”标志。
            now = data["now"] #返回的数据字典里，"now" 里面装着实时天气的详细信息
            return f"{original_city}的实时天气：{now['text']},气温{now['temp']}℃。"
                                    #天气状况（text）     温度（temp）
        else:
            # 把服务器返回的错误码和消息打印出来，方便调试
            error_msg = data.get("msg", "未知错误")
            return f"抱歉，未能查询到{original_city}的天气信息。错误码：{data['code']}，原因：{error_msg}"

    except Exception as e:  #Exception：一个大类，代表了程序运行时可能出现的所有错误类型
                       # e 它是一个具体的变量名，用来抓住刚刚发生的那个具体错误对象。
        error_detail = "无详细信息"
        if 'response' in locals():
            error_detail = response.text
        return f"天气查询失败：{str(e)}。服务器返回详情：{error_detail}"

if __name__ =="__main__":
    print(get_weather("北京"))
