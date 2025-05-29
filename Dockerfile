FROM python:3.10-slim

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

RUN pip install -r requirements.txt


RUN pip install --find-links=/wheelhouse -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
