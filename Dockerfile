# Step 1 - start from official Python image
FROM python:3.11

# Step 2 - set working directory inside container
WORKDIR /app

# Step 3 - copy requirements file first
COPY requirements.txt .

# Step 4 - install dependencies
RUN pip install -r requirements.txt

# Step 5 - copy all your code
COPY . .

# Step 6 - tell Docker which port your app uses
EXPOSE 8000

# Step 7 - command to start your app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]