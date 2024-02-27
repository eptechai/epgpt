datacenter = "idso2305llms-app-dev"
data_dir = "/opt/consul"
encrypt = "THE KEY FROM THE KEYGEN"
tls {
   defaults {
      ca_file = "/etc/consul.d/certs/consul-agent-ca.pem"
      cert_file = "/etc/consul.d/certs/idso2305llms-app-dev-server-consul-0.pem"
      key_file = "/etc/consul.d/certs/idso2305llms-app-dev-server-consul-0-key.pem"
      tls_min_version="TLSv1_3"
      verify_incoming = true
      verify_outgoing = true
   }
   internal_rpc {
      verify_server_hostname = true
   }
}

auto_encrypt {
  allow_tls = true
}

retry_join = ["provider=gce tag_value=hashistack-server"]

acl {
  enabled = false
  default_policy = "allow"
  enable_token_persistence = true
}