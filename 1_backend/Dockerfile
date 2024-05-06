FROM python:3.11

WORKDIR /app

# Install Doppler CLI
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg

# Install Python dependencies
COPY ./requirements ./requirements
RUN pip3 install -r ./requirements/dev.txt

# Copy the dependencies
COPY ./Makefile ./Makefile
COPY ./src ./src
COPY ./config ./config
COPY ./gen_deps ./gen_deps

ENV PYTHONPATH=/app/gen_deps/conversation_index_proto:/app/gen_deps/model_proto:/app/gen_deps/svc_vectordb_proto:/app/gen_deps/attachment_proto:/app/src:/app/gen_deps:/app/config:/app/gen_deps/storage:/app/gen_deps/rabbitmq:/app/gen_deps/index_builder_proto:/app/gen_deps/query_engine_proto:/app/gen_deps/response_synthesizer_proto

RUN mkdir /app/attachments

# Start the executable
WORKDIR /app/src
EXPOSE 8000
RUN chmod u+x startup.sh
CMD ["/bin/bash", "startup.sh"]
