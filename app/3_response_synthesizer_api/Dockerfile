FROM python:3.11

WORKDIR /app

# Install Doppler CLI
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg 

# Install Python dependencies
COPY ./requirements ./requirements
RUN pip3 install -r ./requirements/prod.txt
# Create non-root user to run as.
# RUN useradd -m app -u 1001
# Copy the dependencies
COPY ./src ./src
COPY ./gen_deps ./gen_deps

ENV PYTHONPATH=/app:/app/gen_deps:/app/src:/app/gen_deps/response_synthesizer_proto:/app/gen_deps/attachment_proto:/app/gen_deps/storage:/app/gen_deps/rabbitmq:/app/gen_deps/logger

# Start the executable
WORKDIR /app/src
EXPOSE 5050
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5050", "--timeout-keep-alive", "90"]
