# 1. Base image - a ready-made Python kitchen
FROM python:3.12-slim

# 2. Our work counter inside the container
WORKDIR /app

# 3. Copy ONLY the shopping list first, so pip install stays cached
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Now copy the application code and the docs
COPY . .

# 5. The window our API serves through
EXPOSE 8000

# 6. What runs when the container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
