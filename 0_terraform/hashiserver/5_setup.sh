# Install GCP Ops Agent:
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh &&
sudo bash add-google-cloud-ops-agent-repo.sh --also-install

# Install docker
sudo apt-get update && /
sudo apt-get install -y ca-certificates curl gnupg && /
sudo install -m 0755 -d /etc/apt/keyrings && /
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg && /
sudo chmod a+r /etc/apt/keyrings/docker.gpg && /
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && \
sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Install consul & nomad
sudo apt-get update && sudo apt-get install wget gpg coreutils && \
curl -sL 'https://apt.releases.hashicorp.com/gpg' | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list && \
sudo apt-get update && sudo apt-get install -y nomad consul iptables

# Install CNI Plugins
curl -L -o cni-plugins.tgz "https://github.com/containernetworking/plugins/releases/download/v1.0.0/cni-plugins-linux-$( [ $(uname -m) = aarch64 ] && echo arm64 || echo amd64)"-v1.0.0.tgz && \
  sudo mkdir -p /opt/cni/bin && \
  sudo tar -C /opt/cni/bin -xzf cni-plugins.tgz

## Hashistack Servers Only:
# Install tailscale
curl -fsSL https://tailscale.com/install.sh | sh
## Activate tailscale
sudo tailscale up --advertise-tags=tag:hashistack-server --ssh
## End Hashistack Severs Only:

## Set up Consul

## BELOW ONLY NEEDS TO BE RUN FOR THE FIRST CONSUL INSTALLATION
consul keygen # Save the encryption key to 1Password
consul tls ca create
consul tls cert create -server -dc idso2305llms-app-dev -domain consul
## ABOVE ONLY NEEDS TO BE RUN FOR THE FIRST CONSUL INSTALLATION
# consul-agent-ca-pem goes to consul clients and servers.
# For below certs and keys, if the first server, use the ones made above. Else, download from the first server.
sudo mkdir --parents /etc/consul.d/certs
sudo cp consul-agent-ca.pem /etc/consul.d/certs/ # Clients & Servers
sudo cp idso2305llms-app-dev-server-consul-0-key.pem /etc/consul.d/certs/ # Servers only
sudo cp idso2305llms-app-dev-server-consul-0.pem /etc/consul.d/certs/ # Servers only
# consul-agent-ca-key, idso2305llms-app-dev-server... key and pem go to servers and clients.
sudo mkdir --parents /etc/consul.d
# To both servers and clients, copy 3a_consul.hcl into /etc/consul.d/consul.hcl
# Replace the 'encrypt' key with the one generated above.
# Comment out the retry_join for the first server.
sudo cp consul_<client/server>.hcl /etc/consul.d/consul.hcl
sudo chown --recursive consul:consul /etc/consul.d
sudo chmod 640 /etc/consul.d/consul.hcl
# To both servers only, copy 3b_server.hcl into /etc/consul.d/server.hcl
# Replace the bind_addr parameter with the VM's private IP address.
sudo cp consul_server.hcl /etc/consul.d/server.hcl
sudo chown --recursive consul:consul /etc/consul.d
sudo chmod 640 /etc/consul.d/server.hcl
# Validate consul configuration
sudo consul validate /etc/consul.d/
# Start consul
sudo systemctl enable consul
sudo systemctl start consul
sudo systemctl status consul

## Activate Nomad Server
sudo cp nomad.hcl /etc/nomad.d/nomad.hcl # Client and server
sudo cp nomad_client.hcl /etc/nomad.d/client.hcl # Client Only
# sudo cp nomad_server.hcl /etc/nomad.d/server.hcl # Server Only
sudo systemctl enable nomad
sudo systemctl start nomad
# Then for the second and third server, join to the first server. Not for clients.
nomad server join <known-address>

## For nomad clients, activate Docker GCR access:
VERSION=2.1.14 && \
OS=linux && \
ARCH=amd64 && \
curl -fsSL "https://github.com/GoogleCloudPlatform/docker-credential-gcr/releases/download/v${VERSION}/docker-credential-gcr_${OS}_${ARCH}-${VERSION}.tar.gz" \
| tar xz docker-credential-gcr \
&& chmod +x docker-credential-gcr && sudo mv docker-credential-gcr /usr/bin/

docker-credential-gcr configure-docker --registries=us-docker.pkg.dev
sudo cp ./.docker/config.json /etc/docker/config.json
sudo chmod a+r /etc/docker/config.json