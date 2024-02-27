import { Container, Client, connect } from "@dagger.io/dagger";
import { excludes, publish } from "../dagger_helpers.js";
import { Command } from "commander";

const container = async (client: Client): Promise<Container> => {
    return await client
    .container()
    .from("python:3.11")
    .withFile("install_doppler.sh",client.host().file("/workspace/build_scripts/install_doppler.sh"))
    .withDirectory("/module/requirements", client.host().directory("./requirements"))
    .withWorkdir("/module")
    .withExec(["pip", "install", "-r", "requirements/prod.txt"])
    .withDirectory("/module", client.host().directory("."),{exclude: excludes})
    .withExposedPort(5003)
    .withExec(["useradd", "-m", "app", "-u", "1001"])
    .withUser("1001")
    .withEnvVariable("PYTHONPATH", "/module/gen_deps:/module/src:/module/gen_deps/conversation_index_proto:/module/gen_deps/attachment_proto:/module/gen_deps/storage:/module/gen_deps/rabbitmq")
    .withWorkdir("/module/src")
    .withEntrypoint(["python", "-u", "app.py"])
}

connect(
    async (client: Client ) => {

    const program = new Command();
    const vars = program
    .requiredOption("-d, --destination <destination>", "Destination to build to. One of: local, or an image registry url.")
    .requiredOption("-t, --tag <tag>", "name of the branch to build")
    .parse()
    .opts()

    const c = await container(client)

    if (vars.destination === "local") {
        (await container(client)).export("./gen_dist/image.tgz")
    } else {
        publish(client, vars.destination, c, "3_conversation_index", vars.tag)
    }
    },
    { LogOutput: process.stdout }
);


// FROM python:3.11

// WORKDIR /app

// # Install Doppler CLI
// RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg && \
//     curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | gpg --dearmor -o /usr/share/keyrings/doppler-archive-keyring.gpg && \
//     echo "deb [signed-by=/usr/share/keyrings/doppler-archive-keyring.gpg] https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
//     apt-get update && \
//     apt-get -y install doppler

// # Install Python dependencies
// COPY ./requirements ./requirements
// RUN pip3 install -r ./requirements/prod.txt

// # Copy the dependencies
// COPY ./Makefile ./Makefile
// COPY ./src ./src
// COPY ./gen_deps ./gen_deps
// WORKDIR /app
// # Start the executable
// EXPOSE 5003
// RUN useradd -m app -u 1001
// USER 1001
// CMD export PYTHONPATH=/app/gen_deps:/app/src:/app/gen_deps/conversation_index_proto:/app/gen_deps/attachment_proto:/app/gen_deps/storage:/app/gen_deps/rabbitmq && cd src && python -u app.py 
