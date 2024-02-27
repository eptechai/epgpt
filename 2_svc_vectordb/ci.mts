import { Client, connect } from "@dagger.io/dagger"

const name = "2_svc_vectordb"

export const format = async (client: Client) => {
    // Create a cache volume
    const cache = client.cacheVolume(name)
    // Mount source code in the container.
    const source = await client.container()
    .from("python:3.11-slim")
    .withDirectory('/requirements', client.host().directory('./src/requirements'))
    .withMountedCache("/usr/lib/python3/dist-packages/", cache)
    .withExec(["pip","install","black"]) // Install dependencies
    .withDirectory('/src', client.host().directory('./src'), { exclude: ["__pycache__/", "generated/", "requirements/"] })
    .withExec(["black", "/src"])
    .directory("/src")
    .export("./src")
    return source

}

// initialize Dagger client
connect(async (client) => {
    const source = await format(client)

    console.log(source)
  }, { LogOutput: process.stdout })