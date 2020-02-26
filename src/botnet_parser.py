# Program made to parse through data on https://osint.bambenekconsulting.com/feeds/
# Created on 02/20/2020
# William Reames

import csv
import requests
import collections
# For certain IDEs, the following must be "from src.bot_info import BotInfo"
# For terminal use, however, the following must be "from bot_info import BotInfo"
from bot_info import BotInfo
from ip2geotools.databases.noncommercial import DbIpCity
from ip2geotools.errors import InvalidRequestError


# Gathers input from the user
def gather_input(original_url):
    print()
    print("-" * 50)
    print("\nThis program may be used to parse through and output relevant information from {}".format(original_url))
    print("You may choose to either parse through \"C2 IP Feed\", which contains a list of every IP from all of the\n"
          "given subsets, or parse through any of the master lists underneath Family-Specific Feeds on the website.")
    print("For example, an input may look like \"Bamital\", if you wished to parse through Bamital's master list,\n"
          "or \"Ramnit\", if you wished to parse through Ramnit's master list.")
    print("Enter \"exit\" to exit the program")
    test_input(input("Please enter what you would like to parse through: "), original_url)


# Tests to ensure the input from the user is valid then collects the appropriate data
def test_input(parse_this, original_url):
    print()
    name = parse_this.lower().strip()
    if parse_this.lower() != 'exit' and parse_this.lower() != 'quit':
        if parse_this.upper().strip() == "C2 IP FEED":
            run_c2_data(original_url)
        else:
            append = "{}-master.txt".format(name)
            web_url = original_url + append
            print("Accessing {}'s master feed ...\n".format(name.capitalize()))
            if requests.get(web_url):  # Tests if the given input exists
                run_master_data(web_url, name.capitalize())
            else:
                print("Invalid input. Please enter the name of a intel feed on the given website.")
        gather_input(original_url)


# Collects and outputs data from one of the master links
def run_master_data(web_url, name):
    parser = BotnetParser()
    parser.master_data_from_url(web_url)
    parser.find_similar_dns_ips()

    print("Parsing data for {}:\n".format(name))

    if parser.ips:  # Ensures data has been found before outputting data
        if parser.repeating_ips_count != {}:
            print("Systems with repeating IPs but different domains:")
            for ip in parser.repeating_ips_count:
                print(
                    "{:15} appeared {:2.0f} times under a different domain".format(ip, parser.repeating_ips_count[ip]))
            print()

        if parser.multiple_pointers != {}:
            print("List of all DNS IPs that have different IPs pointing to it:")
            for key in parser.multiple_pointers:
                print('{:15} is pointed to by {:2.0f} IPs: {}'.format(key, len(parser.multiple_pointers[key]),
                                                                      parser.multiple_pointers[key]))

        print()
        parser.find_countries()
        print()
        print("Amount of IPs originating from each country:")
        for key in parser.countries:
            if parser.countries[key] == 1:
                print('{} had  1 occurrence'.format(key))
            else:
                print('{} had {:2.0f} occurrences'.format(key, parser.countries[key]))
    else:
        print('{} has no data written in it'.format(name))


# Collects and outputs data from the C2 IP Feed
def run_c2_data(original_url):
    web_url = original_url + 'c2-ipmasterlist.txt'
    ips = {}
    response = requests.get(web_url)
    file = response.text.split('\n')
    csv_reader = csv.reader(file)
    for data in csv_reader:
        # Don't retrieve data from commented lines
        if len(data) > 0 and data[0][0] != '#':
            # Text is usually "IP used by (name) C&C". After being split the name will be at index 3
            name = data[1].split(' ')[3]
            # Adds to the dictionary
            if data[0] in ips:
                ips[data[0]].append(name)
            else:
                ips[data[0]] = [name]

    # Adds the repeating IPs to a separate dictionary
    repeating_ips = {}
    for ip in ips:
        if len(ips[ip]) > 1:
            repeating_ips[ip] = ips[ip]

    repeating_ips = collections.OrderedDict(repeating_ips)

    print("Parsing C2 IP Feed:\n")

    print("Total of {} repeating IPs.\n".format(len(repeating_ips)))
    print("All IPs that repeat across differing systems:")
    for ip in repeating_ips:
        print('{:15} was included in {}'.format(ip, repeating_ips[ip]))


# Class used to parse through and store data from the input urls
class BotnetParser:

    def __init__(self):
        # Using sets and dictionaries due to the fact that they are hashed and have O(1) containment
        self.domains = set()  # Contains a single entry of all domains
        self.bots = {}  # Dictionary that contains each IP and the information it points to as a BotInfo instance
        self.ips = []  # List containing all ips used to find specific keys quickly
        self.repeating_ips_count = {}  # Only contains the ips that occur more than once and the number of occurrences
        self.countries = {}  # Dictionary that contains country names and how many IPs are from that country
        self.multiple_pointers = {}  # Contains each dns_IP and a set containing each host IP that points to it
        self.can_find_locations = True  # Only allowed to find a certain amount of locations with the library I am using

    # Prepares a url for parsing by a csv
    def master_data_from_url(self, url):
        response = requests.get(url)
        file = response.text.split('\n')
        csv_reader = csv.reader(file)
        self.gather_master_data(csv_reader)

    # Only used during testing
    # Prepares a file for parsing by a csv
    def _master_data_from_file(self, file_path):
        with open(file_path) as file:
            csv_reader = csv.reader(file)
            self.gather_master_data(csv_reader)

    # Gathers data through the use of a csv
    def gather_master_data(self, csv_reader):
        for data in csv_reader:
            # Don't retrieve data from commented lines
            if len(data) > 0 and data[0][0] != '#':

                # Gathers the data
                current_domain = data[0]
                current_ips = data[1].split('|')
                # Don't use lines with missing data
                if current_ips[0] == '':
                    break
                current_dns_ips = data[3].split('|')

                # Stores the data
                for current_ip in current_ips:
                    # Adds ips that are the same but have different domains to the unique_ip_count dictionary
                    # Since ips are used as the key for bots, we can use that to test if the ip already exists
                    if current_domain not in self.domains and current_ip in self.bots:
                        if current_ip in self.repeating_ips_count:
                            self.repeating_ips_count[current_ip] += 1
                        else:
                            # Sets it equal to two in order to include the ip inside the set and the ip being compared
                            self.repeating_ips_count[current_ip] = 2
                    else:
                        self.ips.append(current_ip)
                        self.bots[current_ip] = BotInfo(current_ip, current_dns_ips)
                self.domains.add(current_domain)

    # Finds the location of each ip address that has been found
    # Because finding the location is so time consuming, it is done separately
    def find_countries(self):
        print("Finding the locations of all IPs ...")
        for i, ip in enumerate(self.bots):
            if self.can_find_locations:  # Makes sure we can find locations before calling the method
                percentage = int(i / len(self.bots) * 100)
                if percentage != 0 and percentage % 10 == 0:
                    print('{}% complete'.format(percentage))
                self._find_location(ip, self.countries)
            else:
                break
        print("Finished finding the locations of all IPs")

    # Method used to find the location (country) of a given IP Address
    # Method takes a long time to ping each address
    # The method can also have a limited number of queries per day which is problematic
    def _find_location(self, ip, countries):
        try:
            # Gathers info from the library and stores the country code
            response = DbIpCity.get(ip)
            current_country = response.country
            # Adds to the dictionary
            if current_country in self.countries:
                self.countries[current_country] += 1
            else:
                self.countries[current_country] = 1
        except KeyError:
            print("Error: \"{}\" could not be found".format(ip))
        except InvalidRequestError as e:
            print("Error: maximum number of queries per day exceeded")
            self.can_find_locations = False

    # Finds DNS IP Addresses that are found in multiple lines, as well as what original IP they are connected to
    def find_similar_dns_ips(self):
        # Loops through each combination of ip lists, then compares the DNS IPs using a method from BotInfo
        for i in range(0, len(self.ips) - 1):
            for j in range(i + 1, len(self.ips)):
                self.bots[self.ips[i]].same_dns_ips(self.bots[self.ips[j]], self.multiple_pointers)


if __name__ == '__main__':
    original_url = "https://osint.bambenekconsulting.com/feeds/"
    gather_input(original_url)
    print('Done.')
