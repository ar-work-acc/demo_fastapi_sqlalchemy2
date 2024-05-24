FROM python:3.11

WORKDIR /code

# set environment variables for production
ENV ENVIRONMENT="prod"
ENV DB_DATABASE="prod"
ENV DB_USER="postgres"
ENV DB_PASSWORD="pw2023"
ENV ADMIN_USERNAME="admin@meowfish.org"
ENV ADMIN_PASSWORD="pw2023"
ENV USER_USERNAME="alice@meowfish.org"
ENV USER_PASSWORD="maxwell"
ENV CORS_ORIGINS="http://localhost,http://meowfish.org,https://meowfish.org"
ENV JWT_SECRET_KEY="A90ElQhCem1ZVAdNCmAnH6fNjXe148HgnDa/vvnjTEI="
ENV REDIS_USERNAME="admin"
ENV REDIS_PASSWORD="pw2024"
ENV REDIS_DB_BROKER=2
ENV REDIS_DB_RESULT_BACKEND=3

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./src /code

# Behind a TLS Termination Proxy (load balancer) like Traefik, add the option --proxy-headers
# CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
