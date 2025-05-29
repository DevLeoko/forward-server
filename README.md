# URL Redirection Service

A minimal, production-ready Python (FastAPI) web service for managing URL redirects with optional expiration times.

## Features

- Simple API endpoints for creating and managing redirects
- SQLite database for persistent storage
- API key authentication for management endpoints
- Support for temporary and permanent redirects
- Dockerized for easy deployment

## Usage

### Running Locally

```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

### Docker

Pull from Docker Hub:

```bash
docker pull leokogar/forward-server:latest
```

Run container:

```bash
docker run -d --restart always -v ./redirects.db:/app/redirects.db -p 8000:8000 leokogar/forward-server:latest
```

## API Endpoints

### Create Redirect

```
POST /create
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
    "path": "example",
    "url": "https://example.com",
    "ttlSeconds": 3600  # -1 for no expiration
}
```

### Delete Redirect

```
POST /delete
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
    "path": "example"
}
```

### Access Redirect

```
GET /{path}
```

Example:

```
GET http://localhost:8000/example
```

## Environment Variables

- `API_KEY`: Required for authentication of management endpoints

## Docker Image

Available on Docker Hub:

- [leokogar/forward-server](https://hub.docker.com/repository/docker/leokogar/forward-server)

## License

MIT
