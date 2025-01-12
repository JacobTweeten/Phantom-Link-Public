FROM python:3.11.6-slim

# Install PostgreSQL client and dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install nltk \
    && python -m nltk.downloader vader_lexicon

    # Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory to /app
COPY . .

# Set Flask environment to development
ENV FLASK_DEBUG=1
ENV FLASK_APP=server.py
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Expose the port the app will run on
EXPOSE 5000

# Specify the command to run your Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
