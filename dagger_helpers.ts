import { Client, Container, Directory } from "@dagger.io/dagger";
import { promises as fs } from "fs";

/**
 * Common excluded filepaths for all containers. These filepaths represent generated code, not source code. 
 */
export const excludes = ["**node_modules/**", "**.git/**", "**__pycache__/**", "**generated/**", "**gen_deps/**", "**gen_dist/**"]

export const gen_dist_path = "/module/gen_dist"
export const gen_deps_path = "/module/gen_deps"

/**
 * Ensures that a host directory is the same as a given container directory.
 * @param container_path Path within the container
 * @param host_path 
 * @returns Functor that sets ensures the host directory is the same as the container directory.
 */
export const ensureHostDir = <T extends Container | Directory>(container_path: string, host_path: string): ((c: T) => T) => {
    return (c: T): T => {
      if (!fs.access(host_path).then(() => true).catch(() => false)) fs.rm(host_path, {recursive: true});
      fs.mkdir(host_path, {recursive: true});
      c.directory(container_path)
      .export(host_path)
      return c
    }
  }

export const publish = (client: Client, image_registry_url: string, container: Container, image_name: string, tag: string) => {
    const GCP_SVC_CICD_KEY_B64 = client.setSecret("GCP_SVC_CICD_KEY_B64", btoa(process.env["GCP_SVC_CICD_KEY"]))
      container.withRegistryAuth("https://us-docker.pkg.dev", "_json_key_base64", GCP_SVC_CICD_KEY_B64)
      .publish(`${image_registry_url}/${image_name}:${tag}`) 
}