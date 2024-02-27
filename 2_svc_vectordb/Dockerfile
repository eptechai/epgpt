FROM python:3.11

WORKDIR /app

# Install Doppler CLI
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler

# Install Python dependencies
COPY ./requirements ./requirements
RUN pip3 install -r ./requirements/prod.txt
# RUN useradd -m app -u 1001
# Copy the dependencies
COPY ./gen_deps ./gen_deps
COPY ./Makefile ./Makefile
COPY ./src ./src
WORKDIR /app
# Start the executable
EXPOSE 5002
ENV PYTHONPATH=/app/gen_deps:/app/src:/app/gen_deps/svc_vectordb_proto
# RUN chown -R 1001:1001 /app
WORKDIR /app/src
# USER 1001
CMD python -u app.py 
