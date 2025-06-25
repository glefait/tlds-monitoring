import httpx
import json
import os
import click

from tlds_monitoring.root import ROOT_TLD_FILE, DOMAIN_DIR_PATH, ROOT_TLD_DETAILS_FILE


def get_tld_details_through_rdap_files(root_tlds):
    # for each tld, get details
    root_tlds_details = {}
    with httpx.Client() as client:
        for tld in root_tlds:
            req = client.get(f"https://rdap.iana.org/domain/{tld}")
            root_tlds_details[tld] = req.json()
    # TODO: slow. 02m 30s => multithread ?
    return root_tlds_details


@click.command()
@click.option(
    "--data-path", default="data", required=True, help="Directory to read / write data"
)
def main(data_path: str):
    # load existing root tlds
    with open(os.path.join(data_path, f"{ROOT_TLD_FILE}.json"), "r") as r:
        root_tlds = json.load(r)
        tld_details = get_tld_details_through_rdap_files(root_tlds)
        # write the individual details
        domain_path = os.path.join(data_path, DOMAIN_DIR_PATH)
        os.makedirs(domain_path, exist_ok=True)
        for tld, tld_detail in tld_details.items():
            with open(os.path.join(domain_path, f"{tld}.json"), "w") as f:
                json.dump(tld_detail, indent=2, fp=f)
        # write the aggregated result
        with open(os.path.join(data_path, f"{ROOT_TLD_DETAILS_FILE}.json"), "w") as f:
            json.dump(tld_details, indent=2, fp=f)


if __name__ == "__main__":
    main()
