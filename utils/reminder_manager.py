from datetime import datetime, timedelta


class ReminderManager:
    def __init__(self):
        self.reminders = []

    def add_reminder(self, reminder_datetime, message, channel_id):
        self.reminders.append((reminder_datetime, message, channel_id))

    def remove_reminder(self, index):
        if 0 <= index < len(self.reminders):
            return self.reminders.pop(index)
        else:
            return None

    def get_reminders(self):
        return self.reminders

    async def check_reminders(self, bot):
        now = datetime.now()
        for reminder in self.reminders[:]:
            reminder_time, message, channel_id = reminder
            if now >= reminder_time:
                channel = bot.get_channel(channel_id)
                for i in range(10):
                    await channel.send(f"@everyone son las {reminder_time.strftime('%H:%M')} hora, es hora {message}")
                self.reminders.remove(reminder)
