FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install the gcloud CLI per https://cloud.google.com/sdk/docs/install
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list  \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && apt-get update -y \
    && apt-get install google-cloud-sdk -y

# Install terraform per https://developer.hashicorp.com/terraform/downloads
RUN wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg  \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list \
    && sudo apt update && sudo apt install terraform

# Install postgres client
RUN apt-get -y install --no-install-recommends postgresql-client

# Install the Doppler CLI
# Install pre-reqs
RUN sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl gnupg
# Add Doppler's GPG key
RUN curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | sudo apt-key add -
# Add Doppler's apt repo
RUN echo "deb https://packages.doppler.com/public/cli/deb/debian any-version main" | sudo tee /etc/apt/sources.list.d/doppler-cli.list
# Fetch and install latest doppler cli
RUN sudo apt-get update && sudo apt-get install -y doppler

## Install Dagger
RUN cd /usr/local && curl -L https://dl.dagger.io/dagger/install.sh | sh

## Install Envoy Proxy
RUN sudo apt-get update && \
sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl lsb-release && \
curl -sL 'https://deb.dl.getenvoy.io/public/gpg.8115BA8E629CC074.key' | sudo gpg --dearmor -o /usr/share/keyrings/getenvoy-keyring.gpg && \
echo a077cb587a1b622e03aa4bf2f3689de14658a9497a9af2c427bba5f4cc3c4723 /usr/share/keyrings/getenvoy-keyring.gpg | sha256sum --check && \
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/getenvoy-keyring.gpg] https://deb.dl.getenvoy.io/public/deb/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/getenvoy.list && \
sudo apt-get update && sudo apt-get install -y getenvoy-envoy

# Install HashiCorp Nomad & Consul
RUN sudo apt-get update && sudo apt-get install wget gpg coreutils
RUN curl -sL 'https://apt.releases.hashicorp.com/gpg' | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
RUN sudo apt-get update && sudo apt-get install -y nomad
RUN sudo apt-get update && sudo apt-get install -y consul 
RUN sudo apt-get update && sudo apt-get install -y iptables

# Install CNI Plugins
RUN curl -L -o cni-plugins.tgz "https://github.com/containernetworking/plugins/releases/download/v1.0.0/cni-plugins-linux-$( [ $(uname -m) = aarch64 ] && echo arm64 || echo amd64)"-v1.0.0.tgz && \
  sudo mkdir -p /opt/cni/bin && \
  sudo tar -C /opt/cni/bin -xzf cni-plugins.tgz

# Allow iptables usage in bridge networking
# RUN echo 1 | sudo tee /proc/sys/net/bridge/bridge-nf-call-arptables && \
#   echo 1 | sudo tee /proc/sys/net/bridge/bridge-nf-call-ip6tables && \
#   echo 1 | sudo tee /proc/sys/net/bridge/bridge-nf-call-iptables

COPY .devcontainer/iptables.conf /etc/sysctl.d/iptables.conf

# Install the gcloud docker registry helper
RUN VERSION=2.1.14 && \
OS=linux && \
ARCH=amd64 && \
curl -fsSL "https://github.com/GoogleCloudPlatform/docker-credential-gcr/releases/download/v${VERSION}/docker-credential-gcr_${OS}_${ARCH}-${VERSION}.tar.gz" \
| tar xz docker-credential-gcr \
&& chmod +x docker-credential-gcr && sudo mv docker-credential-gcr /usr/bin/

# TODO: Parameterize this for dev and prod.
# Note: Github Codespaces seems to override this, so make this in postcreate commands.
# Then create a credential file like: gcloud auth application-default login
# Test with: echo "https://us-docker.pkg.dev" | docker-credential-gcr get

# Install tailscale
RUN curl -fsSL https://tailscale.com/install.sh | sh

# Make nomad and consul services executable
# Make the scripts executable
COPY .devcontainer/conf/service/nomad /etc/init.d/nomad
COPY .devcontainer/conf/service/consul /etc/init.d/consul
RUN sudo chmod +x /etc/init.d/nomad 
RUN sudo chmod +x /etc/init.d/consul
