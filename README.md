# botnet-parser
**What my program is parsing:**

This program was made to parse through data on https://osint.bambenekconsulting.com/feeds/ and output relevant
information. This website contains intel feeds for what appear to be various botnets. Each individual botnet gets their
own set of files that contain information about the domains, IP Addresses created through the use of a Name Service
(NS) Server, the NS Host domain, and the NS IP Address. My program parses through all the data and pieces together
potential pieces of important information.

**What my program is finding:**

When parsing through the master files, my program looks for 3 main things to output. Firstly, it looks to see how many
IP Addresses repeat with a different domain. As these IPs are likely the IPs associated with a C&C server, this could
tell us which servers are being used more often than others, and which ones could potentially have a higher priority to
take down.
Secondly, it finds how many different C&Cs are using the same NS Server. This is split into two main parts, C&C servers
that share similar NS Host domains, and C&C Servers that share similar NS IP Addresses. This could help us understand
which NS Servers are being used more frequently than others, and would allow us to know where most of the C&C data is
being sent. Thirdly, my program finds the location of each C&C IP that is used inside the file. This can help to
understand where a majority of the servers are located, as well as tell us how widespread the botnet is.

Furthermore, my program also gives an option to parse through the website's "C2 IP Feed". This intel feed contains a
list of every IP that is used across all of the servers. Using this, my program finds how many times an IP repeats
between various servers, as well as which botnets are using the same IP for a server. This is interesting as it may
indicate that certain botnet systems may be working in tandem with each other, or that there is a single system that is
being used for multiple C&C servers at the same time.

**Using my program:**

My program is terminal based and should either be run using a terminal or ran through the use of an IDE. After running
the program, it will appear with a prompt to gather input from the user. Based off what the user wants, the user should
then enter "C2 IP Feed" if they wish to parse through the list of all IP Addresses, or enter the name of one of the
botnets listed on the website if they wish to parse its master list. After this, the program will output all relevant
information (described above) then ask the user for input again. This process will continue until the user enters
"Exit" or "Quit".

**Potential Errors:**

Depending on whether you are using a terminal or an IDE, line 10 of my program may cause you some problems:
Line 10: from bot_info import BotInfo
In a terminal this will work fine, but when using certain IDEs, or if you wish to run the test cases, line 10 will need
to be replaced with "from src.bot_info import BotInfo". By default it is set to "from bot_info import BotInfo" and will
need to be changed depending on the planned form of usage.
There are comments detailing this as well inside the program

The library used to find the geolocation of each IP Address does not have every IP in the database it uses, so on
occasion it cannot find an IP Address. This will appear during output as, "Error: "(insert IP)" could not be found",
and the program will continue to find the location of all other IP Addresses as usual.

Furthermore, the geolocator library only allows a certain number of "queries" per day. After this limit is exceeded,
the program will stop finding the locations of IP Addresses, and will instead output, "Error: maximum number of queries
per day exceeded". All other information, not including information regarding the locations of IP Addresses, will be
parsed out as usual.
