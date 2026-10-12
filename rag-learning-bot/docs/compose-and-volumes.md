# Docker Compose and Volumes

Docker Compose lets you define and run multi-container applications using a single YAML
file. Instead of running many separate docker run commands, you describe every service
once and start them all with docker compose up.

Service discovery is automatic in Compose. Every service gets a hostname equal to its
service name. If your compose file defines a service called chroma, any other container
in that project can reach it at the address http://chroma:8000. You never need to know
or hardcode IP addresses.

Published ports and internal ports are different things. The line "8001:8000" means
port 8000 inside the container is published as port 8001 on your host machine. Other
containers still talk to the internal port 8000, because they are already inside the
network. Only traffic coming from outside uses the published port.

Volumes provide persistent storage. Containers are disposable and lose everything written
to their filesystem when removed. A volume lives outside the container lifecycle, so data
survives docker compose down and reappears when you bring the services back up. Running
docker compose down -v deletes the volumes too, which permanently destroys that data.

Environment variables are how secrets reach a container at runtime. Never bake an API key
into an image with an ENV instruction, because anyone can extract it using docker history.
Use an env_file or the environment block in compose instead.
