plugin "docker" {
  config {
    endpoint = "unix:///var/run/docker.sock"
    auth {
      config = "/root/.docker/config.json"
    }
  }
}
