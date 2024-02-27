FROM envoyproxy/envoy:v1.27-latest

# Install Doppler CLI
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install doppler

# Install python3
RUN apt-get update && apt-get install -y python3 python3-pip
COPY requirements.txt /home/envoy/requirements.txt
RUN pip3 install -r /home/envoy/requirements.txt
# Copy Envoy configuration in
COPY envoy.yaml.template /home/envoy/envoy.yaml.template
# Copy startup script in
COPY startup.sh /home/envoy/startup.sh
# Copy the python script in
COPY script.py /home/envoy/script.py
# Make it executable
RUN chmod +x /home/envoy/startup.sh
# Run the startup script
CMD /home/envoy/startup.sh