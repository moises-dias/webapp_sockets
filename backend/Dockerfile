# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the app when the container launches
CMD ["python", "app.py"]
# CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:5000"]
# CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]