import { promises as fs } from "fs";
import { Container, Directory, connect } from "@dagger.io/dagger";
import { Client } from "@dagger.io/dagger/dist";
import { Command } from "commander";

const name = "idso2305llms-chatapp";
const excludes = [
  "**node_modules/**/*",
  "**.git/**/*",
  "**__pycache__/**/*",
  "**generated/**/*",
  "**gen_deps/**/*",
  "**gen_dist/**/*",
  "**.pytest_cache/**/*",
  "**.mypy_cache/**/*",
];

//// Helper Functions

// Sets a directory on the host to be equal to that of a directory in the container, removing it if it already exists.
const setHostDir = <T extends Container | Directory>(
  container_path: string,
  host_path: string,
): ((c: T) => T) => {
  return (c: T): T => {
    if (
      !fs
        .access(host_path)
        .then(() => true)
        .catch(() => false)
    )
      fs.rm(host_path, { recursive: true });
    fs.mkdir(host_path, { recursive: true });
    c.directory(container_path).export(host_path);
    return c;
  };
};

// initialize Dagger client
connect(
  async (client: Client) => {
    // Get command line arguments.
    const program = new Command();
    const vars = program
      .requiredOption("-t, --tag <tag>", "name of the branch to build")
      .option(
        "--export-artifacts",
        "Whether or not to export build artifacts (gen_deps, gen_dist) to the host",
      )
      .option("--publish-local", "Whether or not to publish to a local registry on port 5000.")
      .option("--deploy-local", "Whether to deploy to local.")
      .option("--publish", "Whether to publish to online image registry.")
      .option("--deploy", "Whether to deploy to servers.")
      .parse(process.argv)
      .opts();

    // Declaration of secrets that are used in the pipeline
    const TF_API_TOKEN = client.setSecret("TF_API_TOKEN", process.env["TF_API_TOKEN"]);
    const DOPPLER_TOKEN = client.setSecret("DOPPLER_TOKEN", process.env["DOPPLER_TOKEN"]);
    const GCP_SVC_CICD_KEY_B64 = client.setSecret(
      "GCP_SVC_CICD_KEY_B64",
      btoa(process.env["GCP_SVC_CICD_KEY"]),
    );
    const DATABASE_NAME = client.setSecret("DATABASE_NAME", btoa(process.env["DATABASE_NAME"]));
    const DATABASE_USER_PASSWORD = client.setSecret(
      "DATABASE_USER_PASSWORD",
      btoa(process.env["DATABASE_USER_PASSWORD"]),
    );
    // Cache for Python Packages
    const pip_cache = client.cacheVolume("pip");

    // Common Folder path
    const common_folder_path = "./0_common";

    // Apply Terraform
    const stg_terraform = client
      .container()
      .from("hashicorp/terraform:latest")
      .withSecretVariable("TF_TOKEN_app_terraform_io", TF_API_TOKEN)
      .withDirectory(`/repo/0_terraform`, client.host().directory(`./0_terraform/`), {
        exclude: excludes,
      })
      .withWorkdir(`/repo/0_terraform/${vars.tag}`)
      .withExec(["init"]) // Initialize Terraform
      .withExec(["apply", "--auto-approve"]); // Builds Terraform Infrastructure

    const artifact_registry_url = await stg_terraform
      .withEntrypoint(["sh", "-c"])
      .withExec(["$(echo /bin/terraform output -raw artifact_registry_url)"])
      .stdout();
    console.debug(`Got this artifact registry url from Terraform: ${artifact_registry_url}`)

    const DATABASE_URL: () => Promise<string> = async () => {
      const postgres_ip_address = await stg_terraform
        .withEntrypoint(["sh", "-c"])
        .withExec(["$(echo /bin/terraform output -raw postgres_db_ip)"])
        .stdout();
      return `postgres://ci-user:${DATABASE_USER_PASSWORD}@${postgres_ip_address}:5432/${DATABASE_NAME}`;
    };

    //// Build OAuth2 Proxy
    const oauth2proxy = client
      .container()
      .from("quay.io/oauth2-proxy/oauth2-proxy:latest")
      .withDirectory("/templates", client.host().directory("./.devcontainer/conf/oauth2-proxy/templates"));

    //// Build Attachment Protobuf
    const attachment_proto = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withFile("requirements.txt", client.host().file("./1_attachment_proto/requirements.txt"))
      .withExec(["pip", "install", "-r", "requirements.txt"])
      .withDirectory("/module", client.host().directory("./1_attachment_proto"), { exclude: excludes })
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    const database = client
      .container()
      .from("python:3.11")
      .withFile("requirements.txt", client.host().file("./2_database/requirements.txt"))
      .withExec(["pip", "install", "-r", "requirements.txt"])
      .withDirectory("/module", client.host().directory("./2_database"), { exclude: excludes })
      .withWorkdir("/module")
      .withEnvVariable("DATABASE_URL", await DATABASE_URL())
      .withExec(["make", "all"]);

    //// Build VectorDB
    // Protobuf File
    const vectordb_global_proto = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withFile("requirements.txt", client.host().file("./2_svc_vectordb_proto/requirements.txt"))
      .withExec(["pip", "install", "-r", "requirements.txt"])
      .withDirectory("/module", client.host().directory("./2_svc_vectordb_proto"), { exclude: excludes })
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    const svc_vectordb_global_host_path = "./2_svc_vectordb";
    // Huggingface Model
    const svc_vectordb_global_embedding_model = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withExec(["pip", "install", "huggingface_hub"])
      .withDirectory("/module", client.host().directory(svc_vectordb_global_host_path), {
        include: ["lfs/", "Makefile"],
      })
      .withWorkdir("/module")
      .withExec(["make", "all"]);
    // Main Service
    const svc_vectordb_global = client
      .host()
      .directory(svc_vectordb_global_host_path, { exclude: excludes })
      .withDirectory("/gen_deps", svc_vectordb_global_embedding_model.directory("/module/gen_deps"))
      .withDirectory("/gen_deps/svc_vectordb_proto", vectordb_global_proto.directory("/module/gen_dist"))
      .withDirectory("/gen_deps/logger", client.host().directory(common_folder_path + "/logger"), {
        exclude: excludes,
      })
      .dockerBuild();

    //// Build Model
    // Protobuf File
    const model_proto = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withMountedFile("requirements.txt", client.host().file("./3_model_proto/requirements.txt"))
      .withExec(["pip", "install", "-r", "requirements.txt"])
      .withDirectory("/module", client.host().directory("./3_model_proto"), { exclude: excludes })
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    // Main Model
    const svc_model_host_path = "./3_model";
    const svc_model = client
      .host()
      .directory(svc_model_host_path, { exclude: excludes })
      .withDirectory("/gen_deps/storage", client.host().directory(common_folder_path + "/storage"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/model_proto", model_proto.directory("/module/gen_dist"))
      .dockerBuild();

    //// Build Conversation Index
    // Protobuf File
    const convo_index_proto = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withFile("requirements.txt", client.host().file("./3_conversation_index_proto/requirements.txt"))
      .withExec(["pip", "install", "-r", "requirements.txt"])
      .withDirectory("/module", client.host().directory("./3_conversation_index_proto"), {
        exclude: excludes,
      })
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    const svc_vectordb_convo_host_path = "./3_conversation_index";
    // Embedding model
    const embedding_model = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withExec(["pip", "install", "huggingface_hub"])
      .withDirectory(
        "/module",
        client.host().directory(svc_vectordb_convo_host_path, { include: ["Makefile"] }),
        {
          include: ["lfs/", "Makefile"],
        },
      )
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    // Main Model
    const svc_vectordb_convo = client
      .host()
      .directory(svc_vectordb_convo_host_path, { exclude: excludes })
      .withDirectory("/gen_deps", embedding_model.directory("/module/gen_deps"))
      .withDirectory("/gen_deps/rabbitmq", client.host().directory(common_folder_path + "/rabbitmq"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/storage", client.host().directory(common_folder_path + "/storage"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/logger", client.host().directory(common_folder_path + "/logger"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/conversation_index_proto", convo_index_proto.directory("/module/gen_dist")) // Pushes generated files from stage 0 to stage 1.
      .withDirectory("/gen_deps/attachment_proto", attachment_proto.directory("/module/gen_dist"))
      .dockerBuild();

    //// Build Index Builder
    // Protobuf File
    const index_builder_proto = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withFile("requirements.txt", client.host().file("./3_index_builder_proto/requirements.txt"))
      .withExec(["pip", "install", "-r", "requirements.txt"])
      .withDirectory("/module", client.host().directory("./3_index_builder_proto"), {
        exclude: excludes,
      })
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    const index_builder_host_path = "./3_index_builder";
    // Embedding model
    const ib_embedding_model = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withExec(["pip", "install", "huggingface_hub"])
      .withDirectory(
        "/module",
        client.host().directory(index_builder_host_path, { include: ["Makefile"] }),
        {
          include: ["lfs/", "Makefile"],
        },
      )
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    // Main Model
    const index_builder = client
      .host()
      .directory(index_builder_host_path, { exclude: excludes })
      .withDirectory("/gen_deps", ib_embedding_model.directory("/module/gen_deps"))
      .withDirectory("/gen_deps/rabbitmq", client.host().directory(common_folder_path + "/rabbitmq"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/storage", client.host().directory(common_folder_path + "/storage"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/logger", client.host().directory(common_folder_path + "/logger"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/db", database.directory("/module/gen_dist"))
      .withFile("/gen_deps/db/schema.prisma", database.file("/module/schema.prisma"))
      .withDirectory("/gen_deps/index_builder_proto", index_builder_proto.directory("/module/gen_dist"))
      .withDirectory("/gen_deps/attachment_proto", attachment_proto.directory("/module/gen_dist"))
      .dockerBuild();

    //// Build Query Engine
    // Protobuf File
    const query_engine_proto = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withFile("requirements.txt", client.host().file("./3_query_engine_proto/requirements.txt"))
      .withExec(["pip", "install", "-r", "requirements.txt"])
      .withDirectory("/module", client.host().directory("./3_query_engine_proto"), {
        exclude: excludes,
      })
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    const query_engine_host_path = "./3_query_engine";
    // Embedding model
    const qe_embedding_model = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withExec(["pip", "install", "huggingface_hub"])
      .withDirectory(
        "/module",
        client.host().directory(query_engine_host_path, { include: ["Makefile"] }),
        {
          include: ["lfs/", "Makefile"],
        },
      )
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    // Main Model
    const query_engine = client
      .host()
      .directory(query_engine_host_path, { exclude: excludes })
      .withDirectory("/gen_deps", qe_embedding_model.directory("/module/gen_deps"))
      .withDirectory("/gen_deps/query_engine_proto", query_engine_proto.directory("/module/gen_dist"))
      .withDirectory("/gen_deps/rabbitmq", client.host().directory(common_folder_path + "/rabbitmq"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/storage", client.host().directory(common_folder_path + "/storage"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/logger", client.host().directory(common_folder_path + "/logger"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/attachment_proto", attachment_proto.directory("/module/gen_dist"))
      .dockerBuild();

    //// Build Response Synthesizer
    // Protobuf File
    const response_synthesizer_proto = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withFile("requirements.txt", client.host().file("./3_response_synthesizer_proto/requirements.txt"))
      .withExec(["pip", "install", "-r", "requirements.txt"])
      .withDirectory("/module", client.host().directory("./3_response_synthesizer_proto"), {
        exclude: excludes,
      })
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    const response_synthesizer_host_path = "./3_response_synthesizer";
    // Embedding model
    const rs_embedding_model = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withExec(["pip", "install", "huggingface_hub"])
      .withDirectory(
        "/module",
        client.host().directory(response_synthesizer_host_path, { include: ["Makefile"] }),
        {
          include: ["lfs/", "Makefile"],
        },
      )
      .withWorkdir("/module")
      .withExec(["make", "all"]);

    // Main Model
    const response_synthesizer = client
      .host()
      .directory(response_synthesizer_host_path, { exclude: excludes })
      .withDirectory("/gen_deps", rs_embedding_model.directory("/module/gen_deps"))
      .withDirectory("/gen_deps/response_synthesizer_proto", response_synthesizer_proto.directory("/module/gen_dist"))
      .withDirectory("/gen_deps/rabbitmq", client.host().directory(common_folder_path + "/rabbitmq"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/storage", client.host().directory(common_folder_path + "/storage"), {
        exclude: excludes,
      })
      .withDirectory("/gen_deps/logger", client.host().directory(common_folder_path + "/logger"), {
        exclude: excludes,
      })
      .dockerBuild();

    //// Backend
    // Build the backend dependencies
    const backend_dist = client
      .container()
      .from("python:3.11")
      .withMountedCache("/root/.cache/pip", pip_cache)
      .withDirectory("requirements", client.host().directory("./1_backend/requirements"))
      .withExec(["pip", "install", "-r", "requirements/prod.txt"])
      .withDirectory("/module", client.host().directory("./1_backend"), {
        exclude: excludes,
      })
      .withDirectory("/module/gen_deps/rabbitmq", client.host().directory(common_folder_path + "/rabbitmq"), {
        exclude: excludes,
      })
      .withDirectory("/module/gen_deps/storage", client.host().directory(common_folder_path + "/storage"), {
        exclude: excludes,
      })
      .withDirectory("/module/gen_deps/logger", client.host().directory(common_folder_path + "/logger"), {
        exclude: excludes,
      })
      .withDirectory(
        "/module/gen_deps/conversation_index_proto",
        convo_index_proto.directory("/module/gen_dist"),
      )
      .withDirectory("/module/gen_deps/model_proto", model_proto.directory("/module/gen_dist"))
      .withDirectory(
        "/module/gen_deps/svc_vectordb_proto",
        vectordb_global_proto.directory("/module/gen_dist"),
      )
      .withDirectory(
        "/module/gen_deps/index_builder_proto",
        index_builder_proto.directory("/module/gen_dist"),
      )
      .withDirectory(
        "/module/gen_deps/query_engine_proto",
        query_engine_proto.directory("/module/gen_dist"),
      )
      .withDirectory(
        "/module/gen_deps/response_synthesizer_proto",
        response_synthesizer_proto.directory("/module/gen_dist"),
      )
      .withDirectory("/module/gen_deps/attachment_proto", attachment_proto.directory("/module/gen_dist"))
      .withDirectory("/module/gen_deps/db/client", database.directory("/module/gen_dist/client"))
      .withFile("/module/gen_deps/db/schema.prisma", database.file("/module/schema.prisma"))
      .withWorkdir("/module")
      .withExec(["make", "build"]);

    // Main Backend
    const backend_host_path = "./1_backend";
    const backend = client
      .host()
      .directory(backend_host_path, { exclude: excludes })
      .withDirectory("/gen_deps", backend_dist.directory("/module/gen_deps"))
      .dockerBuild();

    //// Build the GPU Gateway
    const gpu_gateway_host_path = "./4_gpu_gateway/src";
    const gpu_gateway = client.host().directory(gpu_gateway_host_path).dockerBuild();

    //// Frontend
    const frontend_host_path = "./1_frontend";
    const frontend = client
      .container()
      .from("node:18")
      .withDirectory("/module", client.host().directory(frontend_host_path))
      .withDirectory("/module/gen_deps", backend_dist.directory("/module/gen_dist"))
      .withWorkdir("/module")
      .withExec(["npm", "install", "-g", "pnpm"])
      .withExec(["pnpm", "install"])
      .withExec(["make", "generate_deps"])
      .directory(".")
      .dockerBuild();

    // Do our tasks
    const tasks = [];
    // Export build artifacts if specified.
    if (vars.exportArtifacts) {
      tasks.push(
        attachment_proto
          .with(setHostDir("/module/gen_dist", "./1_attachment_proto/gen_dist"))
      );
      tasks.push(
        attachment_proto
          .with(setHostDir("/module/gen_dist", "./2_database/gen_dist"))
      );
      tasks.push(
        vectordb_global_proto
          .with(setHostDir("/module/gen_dist", "./2_svc_vectordb_proto/gen_dist"))
      );
      tasks.push(
        svc_vectordb_global
          .with(setHostDir("/app/gen_deps", `${svc_vectordb_global_host_path}/gen_deps`)),
      );
      tasks.push(
        model_proto
          .with(setHostDir("/module/gen_dist", "./3_model_proto/gen_dist"))
      );
      tasks.push(
        svc_model
          .with(setHostDir("/gen_deps", `${svc_model_host_path}/gen_deps`)),
      );
      tasks.push(
        convo_index_proto
          .with(setHostDir("/module/gen_dist", "./3_conversation_index_proto/gen_dist"))
      );
      tasks.push(
        svc_vectordb_convo
          .with(setHostDir("/app/gen_deps", `${svc_vectordb_convo_host_path}/gen_deps`))
      );
      tasks.push(
        index_builder_proto
          .with(setHostDir("/module/gen_dist", "./3_index_builder_proto/gen_dist"))
      );
      tasks.push(
        index_builder
          .with(setHostDir("/app/gen_deps", "./3_index_builder/gen_deps"))
      );
      tasks.push(
        query_engine_proto
          .with(setHostDir("/module/gen_dist", "./3_query_engine_proto/gen_dist"))
      );
      tasks.push(
        query_engine
          .with(setHostDir("/app/gen_deps", "./3_query_engine/gen_deps"))
      );
      tasks.push(
        response_synthesizer_proto
          .with(setHostDir("/module/gen_dist", "./3_response_synthesizer_proto/gen_dist"))
      );
      tasks.push(
        response_synthesizer
          .with(setHostDir("/app/gen_deps", "./3_response_synthesizer/gen_deps"))
      );
      tasks.push(backend_dist.with(setHostDir("/module/gen_dist", "./1_backend/gen_dist")));
      tasks.push(backend.with(setHostDir("/app/gen_deps", "./1_backend/gen_deps")));
    }

    // Export to local directory if specified.
    if (vars.publishLocal) {
      tasks.push(oauth2proxy.publish("host.docker.internal:5000/oauth2proxy:local"));
      tasks.push(frontend.publish("host.docker.internal:5000/frontend:local"));
      tasks.push(backend.publish("host.docker.internal:5000/backend:local"));
      tasks.push(svc_model.publish("host.docker.internal:5000/svc_model:local"));
      tasks.push(svc_vectordb_convo.publish("host.docker.internal:5000/svc_vectordb_convo:local"));
      tasks.push(index_builder.publish("host.docker.internal:5000/index_builder:local"));
      tasks.push(query_engine.publish("host.docker.internal:5000/query_engine:local"));
      tasks.push(response_synthesizer.publish("host.docker.internal:5000/response_synthesizer:local"));
      await svc_vectordb_global.publish("host.docker.internal:5000/svc_vectordb_global:local");
      tasks.push(svc_vectordb_global.publish("host.docker.internal:5000/svc_vectordb_global:local"));
      tasks.push(gpu_gateway.publish("host.docker.internal:5000/gpu_gateway:local"));
    }

    // Export to registry if specified.
    if (vars.publish) {
      tasks.push(
        oauth2proxy
          .withRegistryAuth("https://us-docker.pkg.dev", "_json_key_base64", GCP_SVC_CICD_KEY_B64)
          .publish(`${artifact_registry_url}/oauth2proxy:${vars.tag}`),
      );
      tasks.push(
        frontend
          .withRegistryAuth("https://us-docker.pkg.dev", "_json_key_base64", GCP_SVC_CICD_KEY_B64)
          .publish(`${artifact_registry_url}/frontend:${vars.tag}`),
      );
      tasks.push(
        backend
          .withRegistryAuth("https://us-docker.pkg.dev", "_json_key_base64", GCP_SVC_CICD_KEY_B64)
          .publish(`${artifact_registry_url}/backend:${vars.tag}`),
      );
      tasks.push(svc_model.publish(`teragonia/idso2305llms-app-svc-model:${vars.tag}`));
      tasks.push(
        svc_vectordb_convo
          .withRegistryAuth("https://us-docker.pkg.dev", "_json_key_base64", GCP_SVC_CICD_KEY_B64)
          .publish(`${artifact_registry_url}/svc_vectordb_convo:${vars.tag}`),
      );
      tasks.push(
        svc_vectordb_global
          .withRegistryAuth("https://us-docker.pkg.dev", "_json_key_base64", GCP_SVC_CICD_KEY_B64)
          .publish(`${artifact_registry_url}/svc_vectordb_global:${vars.tag}`),
      );
      tasks.push(
        index_builder
          .withRegistryAuth("https://us-docker.pkg.dev", "_json_key_base64", GCP_SVC_CICD_KEY_B64)
          .publish(`${artifact_registry_url}/index_builder:${vars.tag}`),
      );
      tasks.push(index_builder.publish(`teragonia/idso2305llms-app-index-builder:${vars.tag}`));
      tasks.push(query_engine.publish(`teragonia/idso2305llms-app-query-engine:${vars.tag}`));
      tasks.push(response_synthesizer.publish(`teragonia/idso2305llms-app-response-synthesizer:${vars.tag}`));
      tasks.push(
        gpu_gateway
          .withRegistryAuth("https://us-docker.pkg.dev", "_json_key_base64", GCP_SVC_CICD_KEY_B64)
          .publish(`${artifact_registry_url}/gpu_gateway:${vars.tag}`),
      );
    }
    await Promise.allSettled(tasks).then((results) =>
      results.forEach((result) => {
        console.log(result.status);
      }),
    );

    // TODO: Condition on whether image builds succeeded.
    if (vars.deploy) {
      await client
        .container()
        .from("hashicorp/nomad")
        .withDirectory("/nomad", client.host().directory("./nomad"), { exclude: excludes })
        .withWorkdir("/nomad")
        .withExec([
          "job",
          "run",
          "-var-file=.local.secrets.vars",
          "-var-file=dev.vars",
          "-address=http://100.102.201.162:4646",
          "main.hcl",
        ])
        .stdout();
    }
    // TODO: Condition on whether image builds succeeded.
    if (vars.deployLocal) {
      await client
        .container()
        .from("hashicorp/nomad")
        .withDirectory("/nomad", client.host().directory("./nomad"), { exclude: excludes })
        .withWorkdir("/nomad")
        .withExec(["job", "run", "-var-file=.local.secrets.vars", "-var-file=local.vars", "main.hcl"])
        .stdout();
    }
  },
  { LogOutput: process.stdout },
);
