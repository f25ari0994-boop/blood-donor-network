"""Run scheduled donor reminders and overdue request notifications."""
from app import process_scheduled_notifications


if __name__ == "__main__":
    process_scheduled_notifications()
