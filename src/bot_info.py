# Used to store certain information regarding various IPs in a collective manner
class BotInfo:

    # Initialization method
    # Input: an IP Address and a list of DNS IP Addresses
    def __init__(self, current_ip, current_dns_hosts, current_dns_ips):
        self.ip = current_ip
        self.dns_hosts = set(current_dns_hosts)
        self.dns_ips = set(current_dns_ips)

    # Method used to compare the DNS Hosts between two BotInfo instances
    # Manipulates a given dictionary to contain information regarding how many C&C IPs use a single DNS Host
    # Input: BotInfo other, dictionary data
    def same_dns_hosts(self, other, data):
        if isinstance(type(other), BotInfo):  # Makes sure a BotInfo instance was passed in as other
            raise ValueError("Error: Required to pass in a BotInfo instance")
        else:
            # Compares each DNS IP in this instance with the other BotInfo's DNS IPs
            if self.ip != other.ip:
                for dns_host in self.dns_hosts:
                    if dns_host in other.dns_hosts:
                        # Adds to the dictionary
                        if dns_host not in data:
                            data[dns_host] = set()
                        data[dns_host].add(self.ip)
                        data[dns_host].add(other.ip)

    # Method used to compare the DNS IPs between two BotInfo instances
    # Manipulates a given dictionary to contain information regarding how many C&C IPs use a single DNS IP
    # Input: BotInfo other, dictionary data
    def same_dns_ips(self, other, data):
        if isinstance(type(other), BotInfo):  # Makes sure a BotInfo instance was passed in as other
            raise ValueError("Error: Required to pass in a BotInfo instance")
        else:
            # Compares each DNS IP in this instance with the other BotInfo's DNS IPs
            if self.ip != other.ip:
                for dns_ip in self.dns_ips:
                    if dns_ip in other.dns_ips:
                        # Adds to the dictionary
                        if dns_ip not in data:
                            data[dns_ip] = set()
                        data[dns_ip].add(self.ip)
                        data[dns_ip].add(other.ip)

    # str method used during development phase
    def __str__(self):
        return "IP: {}, dns IPs: {}".format(self.ip, self.dns_ips)
