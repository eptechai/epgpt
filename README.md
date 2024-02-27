# Project Setup

## One-Time Commands for Each Codespace/Devcontainer

1. Login to doppler with `doppler login`
2. Setup the workspace with `doppler setup`
<!-- TODO: Automate injection of secrets into Nomad. -->
3. Create a .local.secrets.vars containing `doppler_token="DOPPLER_TOKEN"`, where `DOPPLER_TOKEN` comes from Doppler.
4. Run `gcloud auth application-default login` to authenticate to gcloud for image access.

## Commands to run each time you start the devcontainer.

<!-- TODO: Autostart the tailscale daemon and connection after initial login. -->

1. Start the tailscale daemon with `tailscaled --state=mem:`
2. Login to tailscale with `tailscale up`

## Project Setup

1. Install all the pnpm packages and also the python requirements using `make setup`

#### Frontend Setup

1. Generate the FAST API client to use with the frontend using `cd 1_frontend && make generate_deps`
2. Run the frontend using `make run`

#### Database Setup

1. Provision the schema setup using `cd 2_database && prisma migrate dev`

#### Backend Setup

> Note that this command generates the dependencies across all the folders

1. Generate gRPC, model-related and common libraries' dependencies using `cd 1_backend && make generate_deps`
2. Run the backend using `make run/local`
3. Run the background process using `make run/bg`

#### VectorDB Setup

1. Split/Create a new terminal
2. In the `1_backend` directory, run the vectordb using `make run/vectordb`

#### Conversation Index Service Setup

1. Split/Create a new terminal
2. In the `1_backend` directory, run the convo_index using `make run/convo_index`
3. Run the indexing process using `cd 3_conversation_index && make run/background`

#### Model Service Setup

1. Split/Create a new terminal
2. In the `1_backend` directory, run the model using `make run/model`

### RAG Enhancements:
1. Index Builder: `cd 3_index_builder && make run`
2. Query Engine: `cd 3_query_engine && make run`
3. Response Synthesizer: `cd 3_response_synthesizer && make run`

## Tailscale daemon run:

tailscaled --state=mem:
