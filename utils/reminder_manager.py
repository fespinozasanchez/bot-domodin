from datetime import datetime
from utils.data_manager import save_reminder, load_reminders, delete_reminder


class ReminderManager:
    def __init__(self):
        self.reminders = load_reminders()

    def add_reminder(self, reminder_datetime, message, channel_id):
        save_reminder(reminder_datetime, message, channel_id)
        self.reminders = load_reminders()

    def remove_reminder(self, reminder_id):
        delete_reminder(reminder_id)
        self.reminders = load_reminders()

    def get_reminders(self):
        return self.reminders

    async def check_reminders(self, bot):
        now = datetime.now()
        for reminder in self.reminders[:]:
            reminder_time = reminder['reminder_time']
            message = reminder['message']
            channel_id = reminder['channel_id']
            if now >= reminder_time:
                channel = bot.get_channel(channel_id)
                await channel.send(f"@everyone son las {reminder_time.strftime('%H:%M')} hora, es hora {message}")
                delete_reminder(reminder['id'])
                self.reminders = load_reminders()
