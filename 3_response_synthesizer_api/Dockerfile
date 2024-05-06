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
COPY ./Makefile ./Makefile
COPY ./src ./src
COPY ./gen_deps ./gen_deps

ENV PYTHONPATH=/app/gen_deps:/app/src:/app/gen_deps/response_synthesizer_proto:/app/gen_deps/attachment_proto:/app/gen_deps/storage:/app/gen_deps/rabbitmq/app/gen_deps/cache

# Start the executable
WORKDIR /app
EXPOSE 5006
CMD ["/bin/bash", "src/startup.sh"]
