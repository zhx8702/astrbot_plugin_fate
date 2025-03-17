import requests
from astrbot.api.event.filter import command
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register

@register("astrbot_plugin_horoscope", "YourName", "星座运势插件", "1.0.0", "https://github.com/YourRepo")
class HoroscopePlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.api_url = "https://api.tianapi.com/star/index"
        self.api_key = config.get('api_key')  # 在配置中提供您的API密钥

    @command("horoscope")
    async def handle_horoscope(self, event: AstrMessageEvent, sign: str = ""):
        '''horoscope 命令处理

        Args:
            sign (string): 星座名称，例如 "白羊座", "金牛座"
        '''
        if not sign:
            yield event.plain_result("用法: /horoscope [星座]，例如 /horoscope 金牛座")
            return

        params = {
            'key': self.api_key,
            'astro': sign
        }
        response = requests.get(self.api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                horoscope_data = {item['type']: item['content'] for item in data['newslist']}
                result = (f"🌟 今日 {sign} 运势 🌟\n"
                          f"📊 综合指数: {horoscope_data.get('综合指数', 'N/A')}\n"
                          f"❤️ 爱情指数: {horoscope_data.get('爱情指数', 'N/A')}\n"
                          f"💼 工作指数: {horoscope_data.get('工作指数', 'N/A')}\n"
                          f"💰 财运指数: {horoscope_data.get('财运指数', 'N/A')}\n"
                          f"🩺 健康指数: {horoscope_data.get('健康指数', 'N/A')}\n"
                          f"🎨 幸运颜色: {horoscope_data.get('幸运颜色', 'N/A')}\n"
                          f"🔢 幸运数字: {horoscope_data.get('幸运数字', 'N/A')}\n"
                          f"👫 贵人星座: {horoscope_data.get('贵人星座', 'N/A')}\n"
                          f"📖 今日概述: {horoscope_data.get('今日概述', '暂无概述')}\n")
                yield event.plain_result(result)
            else:
                yield event.plain_result(f"查询失败：{data['msg']}")
        else:
            yield event.plain_result("查询失败，请稍后再试！")