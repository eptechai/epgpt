server = true
bootstrap_expect = 3
bind_addr = "10.0.33.37" # REPLACE WITH INTERNAL IP ADDRESS OF VM

connect {
  enabled = true
}

addresses {
  http    = "127.0.0.1" # REPLACE WITH TAILSCALE IP ADDRESS OF VM
  grpc_tls = "127.0.0.1"
}

ports {
  https     = 8500
  grpc_tls  = 8503
}

ui_config {
  enabled = true # Enable for just one of the three nodes.
}