version: '3.8'

services:
  postgres:
    image: postgres:17
    container_name: postgres_db
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mysecretpassword
      POSTGRES_DB: mydatabase
    volumes:
      - ./subscriber.sql:/docker-entrypoint-initdb.d/subscriber.sql
    ports:
      - "5432:5432"

  redis:
    image: redis
    container_name: redis_cache
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    ports:
      - "6379:6379"