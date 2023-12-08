# BP Live - Backend

## Local development

> Do not forget to copy `.env.example` to `.env` and fill out all the enviroment variables.

Build container:

```
docker build -t bplive .
```

Run container with auto-reload:

```
docker run -p 127.0.0.1:8000:8000 -it -v .:/app bplive
```

Create migrations:

```
docker exec -it <container-id> aerich migrate
```

Run migrations:

```
docker exec -it <container-id> aerich upgrade
```
