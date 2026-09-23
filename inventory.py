import argparse
import json
import openstack


def get_instance_data(server, conn):
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
    return instance_data


def get_network_data(network, conn):
    network_data = {
        "id": network.id,
        "name": network.name,
        "connected_instances": []
    }
    ports = conn.network.ports(network_id=network.id, device_owner="compute:nova")
    for port in ports:
        network_data["connected_instances"].append(port.device_id)
    return network_data


def filter_by_status(servers, status):
    if not status:
        return list(servers)
    return [s for s in servers if s.status == status]


def build_report(conn, filter_status=None):
    report = {"instances": [], "networks": []}

    servers = filter_by_status(conn.compute.servers(), filter_status)
    for server in servers:
        report["instances"].append(get_instance_data(server, conn))

    for network in conn.network.networks():
        report["networks"].append(get_network_data(network, conn))

    return report


def main():
    parser = argparse.ArgumentParser(description="Mini Workload Inventory Tool")
    parser.add_argument("--filter-status", help="Filter instances by status (e.g. ACTIVE)")
    args = parser.parse_args()

    conn = openstack.connect()
    report = build_report(conn, args.filter_status)

    with open("workload_inventory.json", "w") as f:
        json.dump(report, f, indent=2)

    print("Report written to workload_inventory.json")


if __name__ == "__main__":
    main()
