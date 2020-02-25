# Program made to parse through data on https://osint.bambenekconsulting.com/feeds/
# Created on 02/20/2020
# William Reames

import csv
import requests
import collections
# For certain IDEs, the following must be "from src.bot_info import BotInfo"
# For terminal use, however, the following must be "from bot_info import BotInfo"
from src.bot_info import BotInfo
from ip2geotools.databases.noncommercial import DbIpCity
from ip2geotools.errors import InvalidRequestError


# TODO: Add a README
# TODO: Sort dictionaries

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
    print()  # Makes a space between input and output
    if parse_this.lower() == 'exit' or parse_this.lower() == 'quit':
        print('Done.')
        exit()
    elif parse_this.upper().strip() == "C2 IP FEED":
        run_c2_data(original_url)
    else:
        append = "{}-master.txt".format(parse_this.lower().strip())
        web_url = original_url + append
        if requests.get(web_url):  # Tests if the given input exists
            run_master_data(web_url, parse_this.lower().capitalize())
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
    # print(web_url, 'https://osint.bambenekconsulting.com/feeds/c2-ipmasterlist.txt')
    ips = {}
    response = requests.get(web_url)  # Connect to the url
    # print(response.text)
    file = response.text.split('\n')  # Split the text into separate lines
    csv_reader = csv.reader(file)  # Creates a csv
    for data in csv_reader:
        # If the line is commented out, do not attempt to retrieve data
        if len(data) > 0 and data[0][0] != '#':
            # Takes the name of the system out of the line.
            # Text is usually "IP used by (name) C&C" which means that if it is split by ' ',
            # the name will be at index 3
            name = data[1].split(' ')[3]
            # Adds to the dictionary
            if data[0] in ips:
                ips[data[0]].append(name)
            else:
                ips[data[0]] = [name]

    # Adds the repeating IPs to a separate dictionary
    repeating_ips = {}
    for ip in ips:
        if len(ips[ip]) > 1:  # Tests if there is more than one IP in the list (tests if it is repeating)
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
        response = requests.get(url)  # Connect to the url
        file = response.text.split('\n')  # Split the text into separate lines
        csv_reader = csv.reader(file)  # Creates a csv
        self.gather_master_data(csv_reader)  # Gathers the data

    # Only used during testing
    # Prepares a file for parsing by a csv
    def _master_data_from_file(self, file_path):
        with open(file_path) as file:  # Opens the file
            csv_reader = csv.reader(file)  # Creates a csv
            self.gather_master_data(csv_reader)  # Gathers the data

    # Gathers data through the use of a csv
    def gather_master_data(self, csv_reader):
        for data in csv_reader:
            # If the line is commented out, do not attempt to retrieve data
            if len(data) > 0 and data[0][0] != '#':
                # Gathers the data
                current_domain = data[0]
                current_ips = data[1].split('|')
                # For some reason some IPs can be left blank. Since these lines are missing data, we will not use them.
                if current_ips[0] == '':
                    break
                # I did not have a need for the DNS domains, so I did not use data[2]
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
                    # Otherwise it gets added to the list of ips and a new BotInfo instance is made
                    else:
                        # Adds the ip and info to the ips and bots set / dict
                        self.ips.append(current_ip)
                        self.bots[current_ip] = BotInfo(current_ip, current_dns_ips)

                # Adds the current domain to the set of all domains
                self.domains.add(current_domain)

    # Finds the location of each ip address that has been found
    # Because finding the location is so time consuming, it is done separately
    def find_countries(self):
        # Print statements added due to long amounts of time required to find the location of an IP
        print("Finding the locations of all IPs ...")
        for i, ip in enumerate(self.bots):
            if self.can_find_locations:  # Makes sure we can find locations before calling the method
                percentage = int(i / len(self.bots) * 100)
                if percentage != 0 and percentage % 10 == 0:
                    print('{}% complete'.format(percentage))  # Prints out the progress as a percentage
                self._find_location(ip, self.countries)  # Finds the location of the current IP
            else:
                break
        print("Finished finding the locations of all IPs")

    # Method takes a long time to ping each address
    # The method can also have a limited number of queries per day which is problematic
    # Input: an IP address as a string, and a dictionary to store the information
    # Output: The country name in abbreviated form returned as a two character string
    def _find_location(self, ip, countries):
        # The library used to find the locations sometimes does not have every IP in its database.
        # To work around this I've added a try catch.
        try:
            response = DbIpCity.get(ip)  # Gathers info from the library
            current_country = response.country  # Gets the country code
            # Adds to the dictionary
            if current_country in self.countries:
                self.countries[current_country] += 1
            else:
                self.countries[current_country] = 1
        except KeyError:  # Error that occurs when the IP cannot be found
            print("Error: \"{}\" could not be found".format(ip))
        except InvalidRequestError as e:  # Error that occurs when we cannot find locations of IPs
            print("Error: maximum number of queries per day exceeded")
            # After discovering we cannot find locations of IPs currently, can_find_locations is changed to False
            # So the method is not called again
            self.can_find_locations = False

    # Finds DNS IP Addresses that are found in multiple lines, as well as what original IP they are connected to
    def find_similar_dns_ips(self):
        # Loops through each combination of ip lists, then compares the DNS IPs using a method from BotInfo
        for i in range(0, len(self.ips) - 1):
            for j in range(i + 1, len(self.ips)):
                self.bots[self.ips[i]].same_dns_ips(self.bots[self.ips[j]], self.multiple_pointers)


if __name__ == '__main__':
    original_url = "https://osint.bambenekconsulting.com/feeds/"
    gather_input(original_url)  # Enters into the input loop, and outputs information until the user decides to stop
