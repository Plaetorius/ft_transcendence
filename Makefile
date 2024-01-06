# Check if Pipfile exists
check_pipfile:
	@test -f Pipfile || (echo "Pipfile not found, please ensure Pipfile exists" && exit 1)

# Install or upgrade pip and pipenv
pip_dependencies: check_pipfile
	pip install --upgrade pip pipenv

# Lock the Pipfile
lock_pipfile: pip_dependencies
	pipenv lock

# Build services
build:
	docker-compose build

# Start services in the foreground
up:
	docker-compose up

# Start services in the background
up-detached:
	docker-compose up -d

# Stop services
stop:
	docker-compose stop

# Stop and remove containers, networks, volumes, and images created by 'up'
down:
	docker-compose down

# View logs
logs:
	docker-compose logs

# Prune system - removes stopped containers, unused networks, dangling images, and build cache
prune:
	docker system prune -f

# Prune system including unused containers and images
prune-all:
	docker system prune -a -f

# Prune volumes - removes unused volumes
prune-volumes:
	docker volume prune -f

# Execute a command in a running container
# Usage: make exec service=[service_name] cmd="[command]"
exec:
	docker-compose exec $(service) $(cmd)

.PHONY: build up up-detached down stop logs prune prune-all prune-volumes exec
