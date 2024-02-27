FROM python:3.11

WORKDIR /app

# Install Doppler CLI
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler

# Install Google cloud CLI
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list  \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && apt-get update -y \
    && apt-get install google-cloud-sdk -y

# Install Python dependencies
COPY ./requirements ./requirements
RUN pip3 install -r ./requirements/prod.txt
# Create non-root user to run as.
# RUN useradd -m app -u 1001
# Copy the dependencies
COPY ./Makefile ./Makefile
COPY ./src ./src
COPY ./gen_deps ./gen_deps

WORKDIR /app/gen_deps/db
RUN prisma generate --schema ./schema.prisma

ENV PYTHONPATH=/app/gen_deps:/app/src:/app/gen_deps/index_builder_proto:/app/gen_deps/attachment_proto:/app/gen_deps/storage:/app/gen_deps/rabbitmq

# Start the executable
WORKDIR /app/src
EXPOSE 5004
CMD ["/bin/bash", "startup.sh"]
