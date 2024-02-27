FROM python:3.10

WORKDIR /app

# Install Doppler CLI
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/miniconda && \
    rm miniconda.sh

# Add Conda to PATH
ENV PATH=/opt/miniconda/bin:${PATH}

COPY ./requirements ./requirements

RUN pip3 install -r ./requirements/prod.txt
RUN conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch-nightly -c nvidia

ENV PYTHONPATH=/gen_deps:/gen_deps/model_proto:/app
ENV HOST=localhost
# Start the executable
COPY ./src .
COPY ./gen_deps /gen_deps
RUN chmod u+x startup.sh

EXPOSE 5001
CMD [ "doppler","run","--", "/bin/bash", "startup.sh"]