import requests
import json
from datetime import datetime
from astrbot.api.event.filter import command
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register

@register("astrbot_plugin_horoscope", "zhx", "星座运势插件", "1.0.0", "https://github.com/zhx8702/astrbot_plugin_fate")
class HoroscopePlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.api_url = "https://api.tianapi.com/star/index"
        self.api_key = config.get('api_key')  # 在配置中提供您的API密钥
        self.cache = {}  # 用于存储缓存
        self.sign_translation = {
            'aries': '白羊座', 'taurus': '金牛座', 'gemini': '双子座', 'cancer': '巨蟹座',
            'leo': '狮子座', 'virgo': '处女座', 'libra': '天秤座', 'scorpio': '天蝎座',
            'sagittarius': '射手座', 'capricorn': '摩羯座', 'aquarius': '水瓶座', 'pisces': '双鱼座'
        }

    def get_today_date(self):
        '''返回今天的日期，格式：YYYY-MM-DD'''
        return datetime.today().strftime('%Y-%m-%d')

    def clear_old_cache(self):
        '''清除过期的缓存（非今天的缓存）'''
        today = self.get_today_date()
        self.cache = {key: value for key, value in self.cache.items() if value['date'] == today}

    def normalize_sign(self, sign: str):
        '''将星座名称标准化为中文形式'''
        sign = sign.strip().lower()
        if sign in self.sign_translation:
            return self.sign_translation[sign]
        return sign  # 如果无法识别，则原样返回

    @command("horoscope")
    async def handle_horoscope(self, event: AstrMessageEvent, sign: str = ""):
        '''horoscope 命令处理

        Args:
            sign (string): 星座名称，例如 "白羊座", "金牛座"
        '''
        if not sign:
            yield event.plain_result("用法: /horoscope [星座]，例如 /horoscope 金牛座")
            return

        # 规范化星座名称
        sign = self.normalize_sign(sign)

        # 清理过期缓存
        self.clear_old_cache()

        # 获取今天的日期
        today = self.get_today_date()

        # 检查是否已有缓存
        if sign in self.cache and self.cache[sign]['date'] == today:
            cached_data = self.cache[sign]['data']
            result = (f"🌟 今日 {sign} 运势 🌟\n"
                      f"📊 综合指数: {cached_data.get('综合指数', 'N/A')}\n"
                      f"❤️ 爱情指数: {cached_data.get('爱情指数', 'N/A')}\n"
                      f"💼 工作指数: {cached_data.get('工作指数', 'N/A')}\n"
                      f"💰 财运指数: {cached_data.get('财运指数', 'N/A')}\n"
                      f"🩺 健康指数: {cached_data.get('健康指数', 'N/A')}\n"
                      f"🎨 幸运颜色: {cached_data.get('幸运颜色', 'N/A')}\n"
                      f"🔢 幸运数字: {cached_data.get('幸运数字', 'N/A')}\n"
                      f"👫 贵人星座: {cached_data.get('贵人星座', 'N/A')}\n"
                      f"📖 今日概述: {cached_data.get('今日概述', '暂无概述')}\n")
            yield event.plain_result(result)
            return

        # 如果没有缓存，发起API请求
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
                # 缓存今天的运势数据
                self.cache[sign] = {'date': today, 'data': horoscope_data}
                yield event.plain_result(result)
            else:
                yield event.plain_result(f"查询失败：{data['msg']}")
        else:
            yield event.plain_result("查询失败，请稍后再试！")