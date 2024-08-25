FROM python:3.11

# Set the working directory
WORKDIR /code

# Copy the requirements file and install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Create log file for cron
RUN touch /var/log/cron.log

# Copy the rest of the application code
COPY . /code/

# Copy and set up cron jobs
COPY cronjobs /etc/cron.d/cronjobs
RUN chmod 0644 /etc/cron.d/cronjobs && crontab /etc/cron.d/cronjobs

# Copy the wait-for-it script
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expose the port
EXPOSE 8000

# Command to run cron and the server
CMD ["sh", "-c", "cron && tail -f /var/log/cron.log & ./wait-for-it.sh db:5432 -- sh -c 'python manage.py migrate && python manage.py runserver 0.0.0.0:8000'"]
