FROM python:3.11-slim

WORKDIR /session11

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "langgraph/youtubeshortscreator.py"]
