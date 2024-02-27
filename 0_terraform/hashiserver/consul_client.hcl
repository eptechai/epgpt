datacenter = "idso2305llms-app-dev"
data_dir = "/opt/consul"
encrypt = "THE KEY FROM THE KEYGEN"
tls {
   defaults {
      ca_file = "/etc/consul.d/certs/consul-agent-ca.pem"

      verify_incoming = true
      verify_outgoing = true
   }
   internal_rpc {
      verify_server_hostname = true
   }
}

auto_encrypt {
  tls = true
}

retry_join = ["STATIC INTERNAL IP OF THE THREE SERVERS"]

acl {
  enabled = false
  default_policy = "allow"
  enable_token_persistence = true
}

bind_addr = <VM Local ADDR>

addresses {
   grpc = "127.0.0.1"
  grpc_tls = "127.0.0.1"
}

ports {
   grpc = 8502
  grpc_tls  = 8503
}