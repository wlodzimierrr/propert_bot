FROM python:3.9-slim

# Set working directory
WORKDIR /property_bot

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install compatible versions of numpy and pandas first
RUN pip install --no-cache-dir numpy==1.24.3 pandas==2.1.0

# Install the rest of the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data logs

# Set the timezone to UK time
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Run the bot
CMD ["python", "main.py"]
