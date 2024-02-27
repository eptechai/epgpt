import { Container, Client, connect } from "@dagger.io/dagger";
import { ensureHostDir, excludes, gen_dist_path } from "../dagger_helpers";

export const build = async (client: Client, modify_host = true): Promise<Container> => {
    return await client
    .container()
    .from("python:3.11")
    .withFile("requirements.txt", client.host().file("./2_svc_vectordb_proto/requirements.txt"))
    .withExec(["pip", "install", "-r", "requirements.txt"])
    .withDirectory("/module", client.host().directory("./2_svc_vectordb_proto"),{exclude: excludes})
    .withWorkdir("/module")
    .withExec(["mkdir", "-p", "/module/gen_dist"])
    .withExec([
        "python", 
        "-m", 
        "grpc_tools.protoc", 
        "-I./src", 
        `--python_out=${gen_dist_path}`, 
        `--pyi_out=${gen_dist_path}`, 
        `--grpc_python_out=${gen_dist_path}`,
        "/src/vectordb.proto"
    ])
    .with(modify_host ? ensureHostDir("/module/generated","./2_svc_vectordb_proto/generated") : (c: Container) => c)
}

connect(
    async (client: Client ) => {
       await build(client)
    },
);
