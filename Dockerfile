FROM python:3.11-slim
WORKDIR /app
COPY server.py .
COPY public/ ./public/
ENV PORT=8000
EXPOSE 8000
CMD ["python", "server.py"]
