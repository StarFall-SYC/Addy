"""日历工具

提供日程管理、提醒设置、日期查询等功能。
"""

import json
import os
from datetime import datetime, timedelta, date
from typing import Dict, Any, List
from .base_tool import BaseTool

class CalendarTool(BaseTool):
    """日历工具类"""
    
    def __init__(self, config=None, logger=None, speak_func=None):
        super().__init__(config, logger)
        self.speak = speak_func or (lambda x: print(f"[CalendarTool] {x}"))
        
        # 日历数据文件路径
        self.calendar_file = os.path.join(os.getcwd(), 'data', 'calendar.json')
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.calendar_file), exist_ok=True)
        
        # 初始化日历数据
        self.calendar_data = self._load_calendar_data()
        
    def get_name(self) -> str:
        return "日历工具"
        
    def get_description(self) -> str:
        return "提供日程管理、提醒设置、日期查询等功能"
        
    def get_supported_intents(self) -> List[str]:
        return [
            'add_event',
            'get_events',
            'delete_event',
            'update_event',
            'get_today_events',
            'get_week_events',
            'get_month_events',
            'set_reminder',
            'get_reminders',
            'check_availability',
            'get_date_info',
            'calculate_date_diff',
            'find_next_weekday',
            'get_holidays',
            'create_recurring_event'
        ]
        
    def execute(self, intent: str, entities: Dict[str, Any], original_text: str) -> str:
        """执行日历操作"""
        try:
            if intent == 'add_event':
                return self._add_event(entities)
            elif intent == 'get_events':
                return self._get_events(entities)
            elif intent == 'delete_event':
                return self._delete_event(entities)
            elif intent == 'update_event':
                return self._update_event(entities)
            elif intent == 'get_today_events':
                return self._get_today_events(entities)
            elif intent == 'get_week_events':
                return self._get_week_events(entities)
            elif intent == 'get_month_events':
                return self._get_month_events(entities)
            elif intent == 'set_reminder':
                return self._set_reminder(entities)
            elif intent == 'get_reminders':
                return self._get_reminders(entities)
            elif intent == 'check_availability':
                return self._check_availability(entities)
            elif intent == 'get_date_info':
                return self._get_date_info(entities)
            elif intent == 'calculate_date_diff':
                return self._calculate_date_diff(entities)
            elif intent == 'find_next_weekday':
                return self._find_next_weekday(entities)
            elif intent == 'get_holidays':
                return self._get_holidays(entities)
            elif intent == 'create_recurring_event':
                return self._create_recurring_event(entities)
            else:
                return f"不支持的日历操作: {intent}"
                
        except Exception as e:
            error_msg = f"日历操作失败: {str(e)}"
            self.speak(error_msg)
            self.logger.error(error_msg)
            return f"error: {str(e)}"
            
    def _load_calendar_data(self) -> Dict:
        """加载日历数据"""
        if os.path.exists(self.calendar_file):
            try:
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载日历数据失败: {e}")
                
        # 返回默认结构
        return {
            'events': [],
            'reminders': [],
            'settings': {
                'default_reminder_minutes': 15,
                'timezone': 'Asia/Shanghai'
            }
        }
        
    def _save_calendar_data(self) -> bool:
        """保存日历数据"""
        try:
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump(self.calendar_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"保存日历数据失败: {e}")
            return False
            
    def _add_event(self, entities: Dict[str, Any]) -> str:
        """添加日程事件"""
        title = entities.get('title')
        date_str = entities.get('date')
        time_str = entities.get('time')
        duration = entities.get('duration', 60)  # 默认60分钟
        description = entities.get('description', '')
        location = entities.get('location', '')
        
        if not title:
            self.speak("请提供事件标题")
            return "error: missing_title"
            
        if not date_str:
            self.speak("请提供事件日期")
            return "error: missing_date"
            
        try:
            # 解析日期和时间
            event_datetime = self._parse_datetime(date_str, time_str)
            if not event_datetime:
                self.speak("日期或时间格式错误")
                return "error: invalid_datetime"
                
            # 创建事件
            event = {
                'id': self._generate_event_id(),
                'title': title,
                'datetime': event_datetime.isoformat(),
                'duration_minutes': duration,
                'description': description,
                'location': location,
                'created_at': datetime.now().isoformat(),
                'reminder_set': False
            }
            
            # 添加到日历
            self.calendar_data['events'].append(event)
            
            # 保存数据
            if self._save_calendar_data():
                success_msg = f"事件 '{title}' 已添加到 {event_datetime.strftime('%Y年%m月%d日 %H:%M')}"
                self.speak(success_msg)
                return f"event_added: {event['id']}"
            else:
                self.speak("保存事件失败")
                return "error: save_failed"
                
        except Exception as e:
            error_msg = f"添加事件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _get_events(self, entities: Dict[str, Any]) -> str:
        """获取指定日期的事件"""
        date_str = entities.get('date')
        
        if not date_str:
            # 如果没有指定日期，显示今天的事件
            return self._get_today_events(entities)
            
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # 查找指定日期的事件
            events = []
            for event in self.calendar_data['events']:
                event_date = datetime.fromisoformat(event['datetime']).date()
                if event_date == target_date:
                    events.append(event)
                    
            # 按时间排序
            events.sort(key=lambda x: x['datetime'])
            
            if events:
                info = f"{target_date.strftime('%Y年%m月%d日')}的日程:\n"
                for i, event in enumerate(events, 1):
                    event_time = datetime.fromisoformat(event['datetime'])
                    info += f"{i}. {event['title']} - {event_time.strftime('%H:%M')}\n"
                    if event['location']:
                        info += f"   地点: {event['location']}\n"
                    if event['description']:
                        info += f"   描述: {event['description']}\n"
                        
                self.speak(info)
                return f"events_found: {len(events)}"
            else:
                self.speak(f"{target_date.strftime('%Y年%m月%d日')}没有安排日程")
                return "no_events_found"
                
        except ValueError:
            self.speak("日期格式错误，请使用YYYY-MM-DD格式")
            return "error: invalid_date_format"
            
    def _get_today_events(self, entities: Dict[str, Any]) -> str:
        """获取今天的事件"""
        today = date.today()
        
        # 查找今天的事件
        events = []
        for event in self.calendar_data['events']:
            event_date = datetime.fromisoformat(event['datetime']).date()
            if event_date == today:
                events.append(event)
                
        # 按时间排序
        events.sort(key=lambda x: x['datetime'])
        
        if events:
            info = f"今天({today.strftime('%Y年%m月%d日')})的日程:\n"
            for i, event in enumerate(events, 1):
                event_time = datetime.fromisoformat(event['datetime'])
                info += f"{i}. {event['title']} - {event_time.strftime('%H:%M')}\n"
                if event['location']:
                    info += f"   地点: {event['location']}\n"
                    
            self.speak(info)
            return f"today_events_found: {len(events)}"
        else:
            self.speak("今天没有安排日程")
            return "no_today_events"
            
    def _get_week_events(self, entities: Dict[str, Any]) -> str:
        """获取本周的事件"""
        today = date.today()
        # 计算本周的开始和结束日期（周一到周日）
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # 查找本周的事件
        events = []
        for event in self.calendar_data['events']:
            event_date = datetime.fromisoformat(event['datetime']).date()
            if start_of_week <= event_date <= end_of_week:
                events.append(event)
                
        # 按日期和时间排序
        events.sort(key=lambda x: x['datetime'])
        
        if events:
            info = f"本周({start_of_week.strftime('%m月%d日')} - {end_of_week.strftime('%m月%d日')})的日程:\n"
            
            # 按日期分组显示
            current_date = None
            for event in events:
                event_datetime = datetime.fromisoformat(event['datetime'])
                event_date = event_datetime.date()
                
                if event_date != current_date:
                    current_date = event_date
                    weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][event_date.weekday()]
                    info += f"\n{event_date.strftime('%m月%d日')} {weekday}:\n"
                    
                info += f"  • {event['title']} - {event_datetime.strftime('%H:%M')}\n"
                
            self.speak(info)
            return f"week_events_found: {len(events)}"
        else:
            self.speak("本周没有安排日程")
            return "no_week_events"
            
    def _get_month_events(self, entities: Dict[str, Any]) -> str:
        """获取本月的事件"""
        today = date.today()
        # 计算本月的开始和结束日期
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            
        # 查找本月的事件
        events = []
        for event in self.calendar_data['events']:
            event_date = datetime.fromisoformat(event['datetime']).date()
            if start_of_month <= event_date <= end_of_month:
                events.append(event)
                
        # 按日期和时间排序
        events.sort(key=lambda x: x['datetime'])
        
        if events:
            info = f"本月({start_of_month.strftime('%Y年%m月')})的日程概览:\n"
            info += f"共有 {len(events)} 个事件\n\n"
            
            # 显示前10个事件
            for i, event in enumerate(events[:10], 1):
                event_datetime = datetime.fromisoformat(event['datetime'])
                info += f"{i}. {event['title']} - {event_datetime.strftime('%m月%d日 %H:%M')}\n"
                
            if len(events) > 10:
                info += f"\n还有 {len(events) - 10} 个事件...\n"
                
            self.speak(info)
            return f"month_events_found: {len(events)}"
        else:
            self.speak("本月没有安排日程")
            return "no_month_events"
            
    def _set_reminder(self, entities: Dict[str, Any]) -> str:
        """设置提醒"""
        title = entities.get('title')
        datetime_str = entities.get('datetime')
        message = entities.get('message', '')
        
        if not title:
            self.speak("请提供提醒标题")
            return "error: missing_title"
            
        if not datetime_str:
            self.speak("请提供提醒时间")
            return "error: missing_datetime"
            
        try:
            # 解析提醒时间
            reminder_datetime = datetime.fromisoformat(datetime_str)
            
            # 创建提醒
            reminder = {
                'id': self._generate_event_id(),
                'title': title,
                'datetime': reminder_datetime.isoformat(),
                'message': message,
                'created_at': datetime.now().isoformat(),
                'completed': False
            }
            
            # 添加到提醒列表
            self.calendar_data['reminders'].append(reminder)
            
            # 保存数据
            if self._save_calendar_data():
                success_msg = f"提醒 '{title}' 已设置到 {reminder_datetime.strftime('%Y年%m月%d日 %H:%M')}"
                self.speak(success_msg)
                return f"reminder_set: {reminder['id']}"
            else:
                self.speak("保存提醒失败")
                return "error: save_failed"
                
        except ValueError:
            self.speak("时间格式错误")
            return "error: invalid_datetime"
            
    def _get_reminders(self, entities: Dict[str, Any]) -> str:
        """获取提醒列表"""
        active_reminders = [r for r in self.calendar_data['reminders'] if not r['completed']]
        
        if active_reminders:
            # 按时间排序
            active_reminders.sort(key=lambda x: x['datetime'])
            
            info = f"您有 {len(active_reminders)} 个活跃提醒:\n"
            for i, reminder in enumerate(active_reminders, 1):
                reminder_time = datetime.fromisoformat(reminder['datetime'])
                info += f"{i}. {reminder['title']} - {reminder_time.strftime('%m月%d日 %H:%M')}\n"
                if reminder['message']:
                    info += f"   备注: {reminder['message']}\n"
                    
            self.speak(info)
            return f"reminders_found: {len(active_reminders)}"
        else:
            self.speak("没有活跃的提醒")
            return "no_active_reminders"
            
    def _check_availability(self, entities: Dict[str, Any]) -> str:
        """检查时间段可用性"""
        date_str = entities.get('date')
        start_time = entities.get('start_time')
        end_time = entities.get('end_time')
        
        if not all([date_str, start_time, end_time]):
            self.speak("请提供完整的日期和时间段信息")
            return "error: missing_time_info"
            
        try:
            # 解析时间段
            check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_datetime = datetime.combine(check_date, datetime.strptime(start_time, '%H:%M').time())
            end_datetime = datetime.combine(check_date, datetime.strptime(end_time, '%H:%M').time())
            
            # 检查冲突
            conflicts = []
            for event in self.calendar_data['events']:
                event_datetime = datetime.fromisoformat(event['datetime'])
                event_end = event_datetime + timedelta(minutes=event['duration_minutes'])
                
                # 检查时间重叠
                if (start_datetime < event_end and end_datetime > event_datetime):
                    conflicts.append(event)
                    
            if conflicts:
                info = f"{check_date.strftime('%Y年%m月%d日')} {start_time}-{end_time} 时间段有冲突:\n"
                for conflict in conflicts:
                    conflict_time = datetime.fromisoformat(conflict['datetime'])
                    info += f"• {conflict['title']} - {conflict_time.strftime('%H:%M')}\n"
                    
                self.speak(info)
                return f"time_conflicts_found: {len(conflicts)}"
            else:
                self.speak(f"{check_date.strftime('%Y年%m月%d日')} {start_time}-{end_time} 时间段可用")
                return "time_available"
                
        except ValueError:
            self.speak("日期或时间格式错误")
            return "error: invalid_format"
            
    def _get_date_info(self, entities: Dict[str, Any]) -> str:
        """获取日期信息"""
        date_str = entities.get('date')
        
        if not date_str:
            # 如果没有指定日期，使用今天
            target_date = date.today()
        else:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.speak("日期格式错误，请使用YYYY-MM-DD格式")
                return "error: invalid_date_format"
                
        # 计算日期信息
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday = weekday_names[target_date.weekday()]
        
        # 计算是一年中的第几天
        day_of_year = target_date.timetuple().tm_yday
        
        # 计算距离今天的天数
        today = date.today()
        days_diff = (target_date - today).days
        
        info = f"{target_date.strftime('%Y年%m月%d日')} 日期信息:\n"
        info += f"星期: {weekday}\n"
        info += f"一年中的第 {day_of_year} 天\n"
        
        if days_diff == 0:
            info += "就是今天\n"
        elif days_diff > 0:
            info += f"距离今天还有 {days_diff} 天\n"
        else:
            info += f"距离今天已过去 {abs(days_diff)} 天\n"
            
        self.speak(info)
        return f"date_info_retrieved: {target_date.isoformat()}"
        
    def _calculate_date_diff(self, entities: Dict[str, Any]) -> str:
        """计算日期差"""
        start_date_str = entities.get('start_date')
        end_date_str = entities.get('end_date')
        
        if not all([start_date_str, end_date_str]):
            self.speak("请提供开始日期和结束日期")
            return "error: missing_dates"
            
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # 计算差值
            diff = end_date - start_date
            days = diff.days
            
            if days == 0:
                info = "两个日期是同一天"
            elif days > 0:
                weeks = days // 7
                remaining_days = days % 7
                info = f"从 {start_date.strftime('%Y年%m月%d日')} 到 {end_date.strftime('%Y年%m月%d日')}\n"
                info += f"相差 {days} 天"
                if weeks > 0:
                    info += f" ({weeks} 周 {remaining_days} 天)"
            else:
                info = f"结束日期早于开始日期 {abs(days)} 天"
                
            self.speak(info)
            return f"date_diff_calculated: {days} days"
            
        except ValueError:
            self.speak("日期格式错误，请使用YYYY-MM-DD格式")
            return "error: invalid_date_format"
            
    def _find_next_weekday(self, entities: Dict[str, Any]) -> str:
        """查找下一个指定星期几"""
        weekday_name = entities.get('weekday')
        
        if not weekday_name:
            self.speak("请指定星期几")
            return "error: missing_weekday"
            
        # 星期几映射
        weekday_map = {
            '周一': 0, '星期一': 0, '周二': 1, '星期二': 1,
            '周三': 2, '星期三': 2, '周四': 3, '星期四': 3,
            '周五': 4, '星期五': 4, '周六': 5, '星期六': 5,
            '周日': 6, '星期日': 6, '周天': 6, '星期天': 6
        }
        
        target_weekday = weekday_map.get(weekday_name)
        if target_weekday is None:
            self.speak("无法识别的星期几")
            return "error: invalid_weekday"
            
        # 计算下一个指定星期几
        today = date.today()
        days_ahead = target_weekday - today.weekday()
        
        if days_ahead <= 0:  # 如果是今天或已过去，则找下周的
            days_ahead += 7
            
        next_date = today + timedelta(days=days_ahead)
        
        info = f"下一个{weekday_name}是 {next_date.strftime('%Y年%m月%d日')} (还有{days_ahead}天)"
        self.speak(info)
        return f"next_weekday_found: {next_date.isoformat()}"
        
    def _get_holidays(self, entities: Dict[str, Any]) -> str:
        """获取节假日信息"""
        year = entities.get('year', date.today().year)
        
        # 简单的中国节假日列表（实际应用中可以使用更完整的节假日API）
        holidays = {
            f"{year}-01-01": "元旦",
            f"{year}-02-14": "情人节",
            f"{year}-03-08": "妇女节",
            f"{year}-05-01": "劳动节",
            f"{year}-06-01": "儿童节",
            f"{year}-10-01": "国庆节",
            f"{year}-12-25": "圣诞节"
        }
        
        # 农历节日（简化版本，实际需要农历转换）
        lunar_holidays = {
            "春节": "农历正月初一",
            "元宵节": "农历正月十五",
            "端午节": "农历五月初五",
            "中秋节": "农历八月十五"
        }
        
        info = f"{year}年主要节假日:\n\n公历节日:\n"
        for date_str, holiday_name in holidays.items():
            holiday_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][holiday_date.weekday()]
            info += f"• {holiday_name}: {holiday_date.strftime('%m月%d日')} {weekday}\n"
            
        info += "\n农历节日:\n"
        for holiday_name, lunar_date in lunar_holidays.items():
            info += f"• {holiday_name}: {lunar_date}\n"
            
        self.speak(info)
        return f"holidays_retrieved: {year}"
        
    def _create_recurring_event(self, entities: Dict[str, Any]) -> str:
        """创建重复事件"""
        title = entities.get('title')
        start_date_str = entities.get('start_date')
        time_str = entities.get('time')
        recurrence_type = entities.get('recurrence_type', 'weekly')  # daily, weekly, monthly
        recurrence_count = entities.get('recurrence_count', 4)  # 重复次数
        
        if not all([title, start_date_str]):
            self.speak("请提供事件标题和开始日期")
            return "error: missing_required_info"
            
        try:
            # 解析开始日期和时间
            start_datetime = self._parse_datetime(start_date_str, time_str)
            if not start_datetime:
                self.speak("日期或时间格式错误")
                return "error: invalid_datetime"
                
            # 计算重复间隔
            if recurrence_type == 'daily':
                delta = timedelta(days=1)
            elif recurrence_type == 'weekly':
                delta = timedelta(weeks=1)
            elif recurrence_type == 'monthly':
                delta = timedelta(days=30)  # 简化处理
            else:
                self.speak("不支持的重复类型")
                return "error: invalid_recurrence_type"
                
            # 创建重复事件
            created_events = []
            for i in range(recurrence_count):
                event_datetime = start_datetime + (delta * i)
                
                event = {
                    'id': self._generate_event_id(),
                    'title': f"{title} ({i+1}/{recurrence_count})",
                    'datetime': event_datetime.isoformat(),
                    'duration_minutes': entities.get('duration', 60),
                    'description': entities.get('description', ''),
                    'location': entities.get('location', ''),
                    'created_at': datetime.now().isoformat(),
                    'recurring': True,
                    'recurrence_type': recurrence_type
                }
                
                self.calendar_data['events'].append(event)
                created_events.append(event)
                
            # 保存数据
            if self._save_calendar_data():
                success_msg = f"已创建 {len(created_events)} 个重复事件: {title}"
                self.speak(success_msg)
                return f"recurring_events_created: {len(created_events)}"
            else:
                self.speak("保存重复事件失败")
                return "error: save_failed"
                
        except Exception as e:
            error_msg = f"创建重复事件失败: {str(e)}"
            self.speak(error_msg)
            return f"error: {str(e)}"
            
    def _delete_event(self, entities: Dict[str, Any]) -> str:
        """删除事件"""
        event_id = entities.get('event_id')
        title = entities.get('title')
        
        if not event_id and not title:
            self.speak("请提供事件ID或标题")
            return "error: missing_identifier"
            
        # 查找要删除的事件
        events_to_remove = []
        for event in self.calendar_data['events']:
            if (event_id and event['id'] == event_id) or (title and title in event['title']):
                events_to_remove.append(event)
                
        if events_to_remove:
            # 删除事件
            for event in events_to_remove:
                self.calendar_data['events'].remove(event)
                
            # 保存数据
            if self._save_calendar_data():
                success_msg = f"已删除 {len(events_to_remove)} 个事件"
                self.speak(success_msg)
                return f"events_deleted: {len(events_to_remove)}"
            else:
                self.speak("保存删除操作失败")
                return "error: save_failed"
        else:
            self.speak("未找到匹配的事件")
            return "error: event_not_found"
            
    def _update_event(self, entities: Dict[str, Any]) -> str:
        """更新事件"""
        # 这个功能需要更复杂的实现来处理部分更新
        self.speak("事件更新功能需要进一步实现")
        return "feature_under_development"
        
    def _parse_datetime(self, date_str: str, time_str: str = None) -> datetime:
        """解析日期时间字符串"""
        try:
            # 解析日期
            if date_str.lower() == 'today' or date_str == '今天':
                target_date = date.today()
            elif date_str.lower() == 'tomorrow' or date_str == '明天':
                target_date = date.today() + timedelta(days=1)
            else:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
            # 解析时间
            if time_str:
                target_time = datetime.strptime(time_str, '%H:%M').time()
            else:
                target_time = datetime.now().time().replace(second=0, microsecond=0)
                
            return datetime.combine(target_date, target_time)
            
        except ValueError:
            return None
            
    def _generate_event_id(self) -> str:
        """生成事件ID"""
        import uuid
        return str(uuid.uuid4())[:8]