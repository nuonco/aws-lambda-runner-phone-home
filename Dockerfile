FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
COPY --from=ghcr.io/astral-sh/uv:0.5.29 /uv /uvx /bin/
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY phonehome.py .
CMD ["python", "phonehome.py"]