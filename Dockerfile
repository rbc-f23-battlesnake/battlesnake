FROM python:3.12-slim

# Install app
COPY . /usr/app
WORKDIR /usr/app

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run Battlesnake
CMD [ "python", "main.py" ]
