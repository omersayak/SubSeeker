#!/usr/bin/env python3

import requests
import argparse
from gevent import socket
from gevent.pool import Pool
from rich.console import Console
from rich.panel import Panel

console = Console()


def show_panel():
    panel = Panel("[bold cyan]SubSeeker[/bold cyan]\nSubdomain detection tool", subtitle="[yellow]Author: Ömer ŞAYAK[/yellow]")
    console.print(panel)


requests.packages.urllib3.disable_warnings()

def main(domain, output_masscan, output_urls, output_file_path):
    resolved_domains = {}
    unresolved_domains = {}

    if not output_masscan and not output_urls:
        print("[+]: Downloading domain list from crt.sh...")

    response = fetch_response(domain)

    if not output_masscan and not output_urls:
        print("[+]: Domain list download completed.")

    domains = parse_domain_data(response)

    if not output_masscan and not output_urls:
        print(f"[+]: Resolved {len(domains)} domains.")

    if len(domains) == 0:
        print("[!]: No domains found.")
        exit(1)

    pool = Pool(15)
    tasks = [pool.spawn(resolve_domain, domain) for domain in domains]

    pool.join(timeout=1)

    for task in tasks:
        result = task.value

        if result:
            ip_address = list(result.values())[0]
            if ip_address != 'none':
                resolved_domains.update(result)
            else:
                unresolved_domains.update(result)

    if output_file_path:
        with open(output_file_path, 'w') as file:
            if output_urls:
                print_urls_to_file(sorted(domains), file)

            if output_masscan:
                print_masscan_to_file(resolved_domains, file)

            if not output_masscan and not output_urls:
                print_domains_to_file(resolved_domains, file, "\n[+]: Found Domains:")
                print_domains_to_file(unresolved_domains, file, "\n[+]: Domains without DNS records:")
    else:
        if output_urls:
            print_urls(sorted(domains))

        if output_masscan:
            print_masscan(resolved_domains)

        if not output_masscan and not output_urls:
            print("\n[+]: Found Domains:")
            print_domains(resolved_domains)
            print("\n[+]: Domains without DNS records:")
            print_domains(unresolved_domains)

def resolve_domain(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        return {domain: ip_address}
    except:
        return {domain: "none"}

def print_domains(domains_dict):
    for domain in sorted(domains_dict):
        print(f"{domains_dict[domain]}\t{domain}")

def print_masscan(domains_dict):
    ip_addresses = set(domains_dict.values())
    for ip in sorted(ip_addresses):
        print(ip)

def print_urls(domains_list):
    for domain in domains_list:
        print(f"https://{domain}")

def print_domains_to_file(domains_dict, file, header):
    file.write(header + '\n')
    for domain in sorted(domains_dict):
        file.write(f"{domains_dict[domain]}\t{domain}\n")

def print_masscan_to_file(domains_dict, file):
    ip_addresses = set(domains_dict.values())
    for ip in sorted(ip_addresses):
        file.write(f"{ip}\n")

def print_urls_to_file(domains_list, file):
    for domain in domains_list:
        file.write(f"https://{domain}\n")

def fetch_response(domain):
    crt_sh_url = f'https://crt.sh/?q={domain}&output=json'
    try:
        response = requests.get(crt_sh_url, verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"[!]: HTTP error: {e}")
        exit(1)
    except Exception as e:
        print(f"[!]: Failed to connect to the server. Error: {e}")
        exit(1)

    try:
        return response.json()
    except ValueError:
        print(f"[!]: The server did not return a valid JSON response. Response: {response.text}")
        exit(1)

def parse_domain_data(response_data):
    domain_set = set()
    for entry in response_data:
        domain_set.add(entry['common_name'])
        additional_domains = entry['name_value'].split('\n')
        domain_set.update(additional_domains)
    return domain_set

if __name__ == '__main__':
    show_panel()
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain", type=str, required=True, help="Domain to query CT logs for, e.g., domain.com")
    parser.add_argument("-u", "--urls", action="store_true", help="Outputs resolved domains as URLs with https:// prefix.")
    parser.add_argument("-m", "--masscan", action="store_true", help="Outputs resolved IP addresses, one per line, suitable for Masscan's '-iL' option.")
    parser.add_argument("-o", "--output", type=str, help="File path to write the results.")
    args = parser.parse_args()

    main(args.domain, args.masscan, args.urls, args.output)
