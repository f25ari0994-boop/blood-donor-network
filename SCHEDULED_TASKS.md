# Scheduled blood-request notifications

Donor reminders are due when 55% of the original request duration has elapsed,
leaving 45% of the duration before the deadline. Each active undonated match
receives at most one reminder. Incomplete requests also generate one overdue
notification after their deadline.

Configure a PythonAnywhere scheduled task with this command:

```bash
cd /home/ahmedrizwan/blood-donor-network && python tasks.py
```

Choose the shortest execution interval supported by the account so notifications
are processed close to their calculated due times. Due notifications are also
processed whenever the application's request-expiry workflow runs.
