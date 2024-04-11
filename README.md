

## Project Setup

1. Install all the python requirements using `make setup`


#### Database Setup

1. Provision the schema setup using `cd 2_database && prisma migrate dev`

#### Backend Setup

> Note that this command generates the dependencies across all the folders

1. Generate gRPC, model-related and common libraries' dependencies using `cd 1_backend && make generate_deps`
2. Run the backend using `make run/local`


### RAG Enhancements:
1. Index Builder: `cd 3_index_builder && make run`
2. Query Engine: `cd 3_query_engine && make run`
3. Response Synthesizer: `cd 3_response_synthesizer && make run`


