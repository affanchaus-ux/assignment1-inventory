import argparse
import json
import openstack

def main():
    parser = argparse.ArgumentParser(description="Mini Workload Inventory Tool")
    parser.add_argument("--filter-status", help="Filter instances by status (e.g. ACTIVE)")
    args = parser.parse_args()

    conn = openstack.connect()

    report = {"instances": [], "networks": []}

    for server in conn.compute.servers():
        if args.filter_status and server.status != args.filter_status:
            continue

        instance_data = {
            "id": server.id,
            "name": server.name,
            "status": server.status,
            "host": server.compute_host,
            "volumes": []
        }

        for att in conn.compute.volume_attachments(server):
            instance_data["volumes"].append({
                "volume_id": att.volume_id,
                "device": att.device
            })

        report["instances"].append(instance_data)

    for network in conn.network.networks():
        network_data = {
            "id": network.id,
            "name": network.name,
            "connected_instances": []
        }
        ports = conn.network.ports(network_id=network.id, device_owner="compute:nova")
        for port in ports:
            network_data["connected_instances"].append(port.device_id)
        report["networks"].append(network_data)

    with open("workload_inventory.json", "w") as f:
        json.dump(report, f, indent=2)

    print("Report written to workload_inventory.json")

if __name__ == "__main__":
    main()
