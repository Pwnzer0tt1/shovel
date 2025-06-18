FROM debian

RUN apt update && apt upgrade -y
RUN apt install -y tshark dnsutils

COPY ./init.sh /bin/docker-entrypoint.sh
RUN chmod +x /bin/docker-entrypoint.sh
