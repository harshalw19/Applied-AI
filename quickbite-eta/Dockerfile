# 1. Base image = rent a ready-made kitchen (from Docker Hub)
FROM python:3.12-slim

# 2. Set up your counter inside that kitchen
WORKDIR /app

# 3. Copy ONLY the shopping list first (layer-caching trick)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. NOW copy the rest of the code
COPY . .

# 5. Train the model INSIDE the image (baked in at build time)
RUN python train.py

# 6. Declare which window the food comes out of
EXPOSE 8000

# 7. What runs the moment the container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
