FROM python:3.12-alpine

WORKDIR /app/

COPY src/ .

COPY requirement.txt .

RUN pip install -r requirement.txt

CMD ["python", "main.py"]