FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip using the recommended method
RUN python -m pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright browsers
RUN playwright install --with-deps

# Copy the rest of the application code
COPY . .

# ssh
# ENV SSH_PASSWD "root:Docker!"
# RUN apt-get update \
#         && apt-get install -y --no-install-recommends dialog \
#         && apt-get update \
#  && apt-get install -y --no-install-recommends openssh-server \
#  && echo "$SSH_PASSWD" | chpasswd 

# COPY sshd_config /etc/ssh/
# COPY init.sh /usr/local/bin/

# Create directory for Chroma DB
#RUN mkdir -p chroma_store

# RUN chmod u+x /usr/local/bin/init.sh
# Expose the application port
# EXPOSE 80 2222
EXPOSE 80

# Command to run the application
CMD ["python", "main.py"]

# ENTRYPOINT ["init.sh"]