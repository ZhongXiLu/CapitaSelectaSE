# base image
FROM postgres:11.1-alpine

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d

CMD ["postgres", "-c", "max_connections=350", "-c" ,"shared_buffers=256MB"]