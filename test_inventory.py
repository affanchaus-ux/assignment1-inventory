from unittest.mock import MagicMock
from inventory import get_instance_data, get_network_data, filter_by_status, build_report


def make_fake_server(id_, name, status, host):
    server = MagicMock()
    server.id = id_
    server.name = name
    server.status = status
    server.compute_host = host
    return server


def make_fake_attachment(volume_id, device):
    att = MagicMock()
    att.volume_id = volume_id
    att.device = device
    return att


def make_fake_network(id_, name):
    network = MagicMock()
    network.id = id_
    network.name = name
    return network


def make_fake_port(device_id):
    port = MagicMock()
    port.device_id = device_id
    return port


def test_get_instance_data_basic_fields():
    server = make_fake_server("id-1", "test-instance1", "ACTIVE", "controller")
    conn = MagicMock()
    conn.compute.volume_attachments.return_value = []

    result = get_instance_data(server, conn)

    assert result["id"] == "id-1"
    assert result["name"] == "test-instance1"
    assert result["status"] == "ACTIVE"
    assert result["host"] == "controller"
    assert result["volumes"] == []


def test_get_instance_data_with_volume():
    server = make_fake_server("id-1", "test-instance1", "ACTIVE", "controller")
    conn = MagicMock()
    conn.compute.volume_attachments.return_value = [
        make_fake_attachment("vol-1", "/dev/vdb")
    ]

    result = get_instance_data(server, conn)

    assert len(result["volumes"]) == 1
    assert result["volumes"][0]["volume_id"] == "vol-1"
    assert result["volumes"][0]["device"] == "/dev/vdb"


def test_get_network_data():
    network = make_fake_network("net-1", "selfservice")
    conn = MagicMock()
    conn.network.ports.return_value = [
        make_fake_port("instance-a"),
        make_fake_port("instance-b"),
    ]

    result = get_network_data(network, conn)

    assert result["id"] == "net-1"
    assert result["name"] == "selfservice"
    assert result["connected_instances"] == ["instance-a", "instance-b"]


def test_filter_by_status_matches():
    servers = [
        make_fake_server("1", "a", "ACTIVE", "h1"),
        make_fake_server("2", "b", "SHUTOFF", "h1"),
    ]
    result = filter_by_status(servers, "ACTIVE")
    assert len(result) == 1
    assert result[0].status == "ACTIVE"


def test_filter_by_status_no_match():
    servers = [
        make_fake_server("1", "a", "ACTIVE", "h1"),
    ]
    result = filter_by_status(servers, "SHUTOFF")
    assert result == []


def test_filter_by_status_no_filter_returns_all():
    servers = [
        make_fake_server("1", "a", "ACTIVE", "h1"),
        make_fake_server("2", "b", "SHUTOFF", "h1"),
    ]
    result = filter_by_status(servers, None)
    assert len(result) == 2


def test_build_report_structure():
    conn = MagicMock()
    conn.compute.servers.return_value = [
        make_fake_server("1", "test-instance1", "ACTIVE", "controller")
    ]
    conn.compute.volume_attachments.return_value = []
    conn.network.networks.return_value = [
        make_fake_network("net-1", "selfservice")
    ]
    conn.network.ports.return_value = []

    report = build_report(conn)

    assert "instances" in report
    assert "networks" in report
    assert len(report["instances"]) == 1
    assert len(report["networks"]) == 1
