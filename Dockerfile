FROM python:3.12-alpine

RUN apk add --no-cache gcc musl-dev
RUN adduser -D myuser
USER myuser

WORKDIR /app
COPY --chown=myuser:myuser . .
RUN mkdir -p data

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
