from astrbot.api import Star, Context, AstrBotMessageEvent
import json
import os
from datetime import datetime

class TimeTracker(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "record.json")
        self.load_data()

    def load_data(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save_data(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_today_str(self):
        return datetime.now().strftime("%Y-%m-%d")

    @Star.command("/log")
    async def log_record(self, event: AstrBotMessageEvent, category: str, value: float):
        """
        /log 学习 3.5
        /log 健身 0.8
        /log 睡眠 7.2
        """
        uid = event.sender.user_id
        today = self.get_today_str()
        allow_cat = ["学习", "健身", "睡眠"]
        if category not in allow_cat:
            return f"❌ 分类只支持：{','.join(allow_cat)}"
        if value <= 0:
            return "❌ 时长必须大于0"

        if uid not in self.data:
            self.data[uid] = {}
        if today not in self.data[uid]:
            self.data[uid][today] = {"学习":0, "健身":0, "睡眠":0}

        self.data[uid][today][category] = value
        self.save_data()
        return f"✅ 记录成功 | {today} {category}：{value}小时"

    @Star.command("/today")
    async def show_today(self, event: AstrBotMessageEvent):
        """查看今日记录 /today"""
        uid = event.sender.user_id
        today = self.get_today_str()
        empty = {"学习":0, "健身":0, "睡眠":0}
        rec = self.data.get(uid, {}).get(today, empty)
        msg = f"📅 {today} 打卡记录\n"
        msg += f"📖 学习：{rec['学习']} h\n"
        msg += f"🏃 健身：{rec['健身']} h\n"
        msg += f"😴 睡眠：{rec['睡眠']} h"
        return msg

    @Star.command("/week")
    async def stat_week(self, event: AstrBotMessageEvent):
        """本周统计 /week"""
        uid = event.sender.user_id
        if uid not in self.data:
            return "📊 暂无记录"
        now = datetime.now()
        total_study = 0.0
        total_fit = 0.0
        total_sleep = 0.0
        cnt = 0
        for date_str, item in self.data[uid].items():
            d = datetime.strptime(date_str, "%Y-%m-%d")
            delta = (now - d).days
            if 0 <= delta < 7:
                total_study += item["学习"]
                total_fit += item["健身"]
                total_sleep += item["睡眠"]
                cnt +=1
        if cnt ==0:
            return "📊 本周暂无记录"
        avg_sleep = round(total_sleep / cnt, 2)
        msg = "📊 本周汇总\n"
        msg += f"📖 学习总时长：{total_study:.2f} h\n"
        msg += f"🏃 健身总时长：{total_fit:.2f} h\n"
        msg += f"😴 睡眠总时长：{total_sleep:.2f} h，日均 {avg_sleep} h"
        return msg

    @Star.command("/month")
    async def stat_month(self, event: AstrBotMessageEvent):
        """本月统计 /month"""
        uid = event.sender.user_id
        if uid not in self.data:
            return "📊 暂无记录"
        now = datetime.now()
        target_month = now.month
        target_year = now.year
        total_study = 0.0
        total_fit = 0.0
        total_sleep = 0.0
        cnt = 0
        for date_str, item in self.data[uid].items():
            d = datetime.strptime(date_str, "%Y-%m-%d")
            if d.year == target_year and d.month == target_month:
                total_study += item["学习"]
                total_fit += item["健身"]
                total_sleep += item["睡眠"]
                cnt +=1
        if cnt ==0:
            return "📊 本月暂无记录"
        avg_sleep = round(total_sleep / cnt, 2)
        msg = "📊 本月汇总\n"
        msg += f"📖 学习总时长：{total_study:.2f} h\n"
        msg += f"🏃 健身总时长：{total_fit:.2f} h\n"
        msg += f"😴 睡眠总时长：{total_sleep:.2f} h，日均 {avg_sleep} h"
        return msg

    @Star.command("/export")
    async def export_data(self, event: AstrBotMessageEvent):
        """导出全部记录 /export"""
        uid = event.sender.user_id
        if uid not in self.data:
            return "📤 没有记录可导出"
        raw = json.dumps(self.data[uid], ensure_ascii=False, indent=2)
        return "📤 你的全部记录（可复制保存）：\n```json\n"+raw+"\n```"

    @Star.command("/trackhelp")
    async def help(self, event: AstrBotMessageEvent):
        help_text = """
⏰ 时长打卡插件指令：
/log 分类 时长      录入记录（单位：小时）
    例：/log 学习 3.5   /log 健身 0.75  /log 睡眠 7.5
/today              查看今日
/week               本周统计
/month              本月统计
/export             导出全部记录
/trackhelp          帮助
"""
        return help_text

