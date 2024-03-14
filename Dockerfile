FROM python:3.11.4

WORKDIR /pickleball_bot

COPY . /pickleball_bot//

RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install necessary dependencies for Google Chrome
RUN apt-get update && \
    apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

CMD ["python", "main.py"]