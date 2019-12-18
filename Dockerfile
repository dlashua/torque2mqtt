FROM python:3.7-alpine

# Install dependencies
RUN apk add --no-cache gcc libffi-dev musl-dev \
    && pip3 install --no-cache-dir .

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "python", "./server.py", "-c", "/config"]
