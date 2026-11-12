FROM python:3.12-slim

RUN pip install --no-cache-dir pillow numpy

# Scripts are mounted by docker-compose.yml, so editing them never needs a rebuild.
WORKDIR /app
ENTRYPOINT ["python", "generate_sprite.py"]
CMD ["--stage", "all"]
