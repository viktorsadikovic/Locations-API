from consul import Consul, Check
import socket

CONSUL_PORT = 8500
SERVICE_NAME = 'locations'
SERVICE_PORT = 5000


def get_host_name_IP():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    return local_ip


def register_to_consul():
    consul = Consul(host="consul", port=CONSUL_PORT)

    agent = consul.agent

    service = agent.service

    ip = get_host_name_IP()

    check = Check.http(f"http://{ip}:{SERVICE_PORT}/api/{SERVICE_NAME}/ui", interval="10s", timeout="5s",
                       deregister="1s")

    service.register(name=SERVICE_NAME, service_id=SERVICE_NAME, address=ip, port=SERVICE_PORT, check=check)


def get_consul_service(service_id):
    consul = Consul(host="consul", port=CONSUL_PORT)

    agent = consul.agent

    service_list = agent.services()

    service_info = service_list[service_id]

    return service_info['Address'], service_info['Port']
