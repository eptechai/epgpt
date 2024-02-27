format:
	nomad fmt main.hcl
# Runs using the local configuration.
deploy/local:
	nomad job run -var-file=".local.secrets.vars" -var-file="dev.vars" main.hcl

stop/local:
	nomad job stop -purge idso2305llms-app-dev

# Runs using the dev configuration.
deploy/dev:
	nomad job run -var-file=".local.secrets.vars" -var-file="dev.vars" -address=http://100.102.201.162:4646 main.hcl

stop/dev:
	nomad job stop -purge -address=http://100.102.201.162:4646 idso2305llms-app-dev
