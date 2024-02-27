import os
import re
from typing import List, TypedDict
import yaml
import argparse


class IPWithPort(TypedDict):
    ip: str
    port: int


def parse_ips(ip_string: str) -> List[IPWithPort]:
    # Regex pattern to match IP addresses with ports
    pattern = re.compile(
        r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):([0-9]{1,5})$"
    )

    # Splitting the string into a list using comma as the delimiter
    ip_port_pairs = ip_string.split(",")

    # Creating a list of dictionaries with keys "ip" and "port"
    ip_port_dicts = []
    for pair in ip_port_pairs:
        try:
            ip, port = pair.split(":")
            if pattern.match(pair):
                ip_port_dicts.append({"ip": ip, "port": int(port)})
            else: 
                raise ValueError
        except ValueError:
            raise ValueError(f"Invalid IP address and port pair: {pair} in {ip_string}")

    return ip_port_dicts


def main(yaml_file, ip_string):
    # Get the IP addresses
    ip_port_dicts = parse_ips(ip_string)
    # Load the Envoy configuration from the specified YAML file
    with open(yaml_file, "r") as file:
        envoy_config = yaml.safe_load(file)

    # Access the lb_endpoints list in the Envoy configuration
    lb_endpoints = envoy_config["static_resources"]["clusters"][0]["load_assignment"][
        "endpoints"
    ][0]["lb_endpoints"]

    # Clear the existing lb_endpoints
    lb_endpoints.clear()

    # Add each IP address as a new endpoint in the lb_endpoints list
    for ipwithport in ip_port_dicts:
        endpoint = {
            "endpoint": {
                "address": {
                    "socket_address": {
                        "address": ipwithport["ip"],
                        "port_value": ipwithport["port"],
                    }
                }
            }
        }
        lb_endpoints.append(endpoint)

    # Write the updated Envoy configuration back to the specified YAML file
    with open("envoy.yaml", "w") as file:
        yaml.safe_dump(envoy_config, file, default_flow_style=False)

    print(f"IP addresses have been updated in {yaml_file} with: {ip_port_dicts}")


# Create the parser to read command line arguments
parser = argparse.ArgumentParser(
    description="Update Envoy YAML configuration with IP addresses from an environment variable"
)
parser.add_argument(
    "yaml_file", type=str, help="The path to the Envoy YAML configuration file"
)
parser.add_argument(
    "ip_string",
    type=str,
    help="Comma-separated list of ip:port pairs. Example: '192.168.1.1:5001,192.168.1.2:5002'",
)

if __name__ == "__main__":
    # Parse the command line arguments
    args = parser.parse_args()
    # Call the main function with the command line arguments
    main(args.yaml_file, args.ip_string)
