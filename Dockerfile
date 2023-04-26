FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir money_bot
COPY money_bot/ money_bot
COPY requirements.txt money_bot
RUN python3.11 -m pip install -r money_bot/requirements.txt
ENTRYPOINT ["python3.11", "money_bot/bot.py"]