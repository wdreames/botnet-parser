# botnet-parser
This program was made to parse through data on https://osint.bambenekconsulting.com/feeds/ and output relevant information. This website contains intel feeds for what appear to be various botnets. Each individual botnet gets their own set of files that contain information about the domains, IP Addresses that are produced from the domains, Domain Name Service (DNS) Hosts that the IPs use to connect to a new set of IPs, and IPs produced by the DNS Hosts. It is possible that the IPs produced by the DNS Host are the IPs of C&C Servers in an IRC botnet, or another bot in a P2P botnet. All of this information is contained inside the "master" file, which is the file my program is primarily concerned with. My program parses through all the information and pieces together potential pieces of important information by using the domains, IP Addresses, and IPs produced by the DNS Hosts of each individual bot in the botnet. 

When parsing through the master files, my program looks for 3 main things to output. Firstly, it looks to see how many IP Addresses repeat with a different domain. ***I'm not entirely sure what this indicates, but I found it interesting.*** Secondly, it finds how many different IPs point to the same IP created by the DNS Host. Depending on what botnet is being parsed, it could either be a P2P botnet, or a botnet similar in structure to an IRC botnet in which there is a central C&C server. In the P2P system, seeing multiple IPs being diricted to a single IP could indicate that the IP created by the DNS Host is actually another bot inside the botnet. As for an IRC system, or similar, this could indicate that the IP created by the DNS Host is one of the C&C servers, as there are multiple bots in the botnet that are accessing it. Through the knowledge of this information, we may be able to 

Outline:
- What the data means
- What it is doing / why it is important
- How to use it
- Problems with the geolocator library
- Line 10 problem

