client {
  enabled = true
}

plugin "docker" {
  config {
    endpoint = "unix:///var/run/docker.sock"
    auth {
      config = "/etc/docker/config.json"
    }
  }
}
