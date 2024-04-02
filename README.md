# SubSeeker: Subdomain Discovery Tool

SubSeeker is a Python tool designed for discovering subdomains of a target domain and resolving their IP addresses. By leveraging public SSL certificate logs, such as crt.sh, it gathers all possible subdomains for a domain and identifies which ones are active.


Features:

1- Extracts subdomain information from SSL certificates.

2- Resolves IP addresses of subdomains.

3- Lists active subdomains along with their corresponding IP addresses.

4- Outputs results as a list of URLs or a list of IPs compatible with masscan.



How to Use:

 1. Clone the Repository:

        https://github.com/omersayak/SubSeeker.git

 2. Navigate to the Directory:

         cd SubSeeker
    
 3. Install Dependencies:

         pip install -r requirements.txt

 4. Run the Scripts:

         python SubSeeker.py -d <target_domain> [options]






A. <target_domain>: The domain name you want to perform discovery on (e.g., example.com).
   
B. [options]: Optional arguments for different output formats and additional options. For details, use the -h option to access the help menu.



Options:

    -u, --urls: Outputs the resolved subdomains as URLs starting with https://.
    -m, --masscan: Lists resolved IP addresses, one per line, suitable for input into Masscan with the -iL option.
    -o, --output: Specifies the file path to write the results to. If not provided, outputs will be printed to standard output (the screen).

Example Usage:

1. To perform subdomain discovery for a domain and write the results to a file:

       python SubSeeker.py -d example.com -o output.txt
   
2. To get a list of URLs for active subdomains:

       python SubSeeker.py -d example.com -u
   
3. To create a list of IP addresses compatible with Masscan:

       python SubSeeker.py -d example.com -m -o ip_list.txt



