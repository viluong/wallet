# Mini Wallet Exercise

## Requirement:
````
Docker, Docker-compose
````

## Install
1. Clone git source
2. Rename `.env-example` to `.env`.  
3. Run `docker-compose build`
4. Run `docker-compose up -d`


## Note:
- The domain API is localhost:8001. Please set `mw_base_url` on Postman Environments File is http://localhost:8001/
- If you want to run with http://localhost/. Please install nginx and setup `location` and `server_name` in config.
#### Example:
```text

upstream api_server {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name localhost;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/sammy/myproject;
    }

    location / {
        include proxy_params;
        proxy_pass http://api_server/;
    }
}

```