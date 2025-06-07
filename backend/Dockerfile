FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
 && apt-get install -y --no-install-recommends openssh-server \
 && echo "$SSH_PASSWD" | chpasswd 

COPY sshd_config /etc/ssh/
COPY init.sh /usr/local/bin/

# Create directory for Chroma DB
#RUN mkdir -p chroma_store

RUN chmod u+x /usr/local/bin/init.sh
# Expose the application port
EXPOSE 80 2222

# Command to run the application
#CMD ["python", "main.py"]

ENTRYPOINT ["init.sh"]