# Use an official lightweight Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables with default values
ENV GEMINI_AI_API_KEY=""
ENV PERIODIC_CLEAN_TIME_SECS=7200
ENV FLASK_PORT=5000

# Expose the Flask port (default is 5000)
EXPOSE ${FLASK_PORT}

# Command to run the Flask app
CMD ["sh", "-c", "FLASK_PORT=${FLASK_PORT} python api.py --host=0.0.0.0"]
