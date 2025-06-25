import hashlib
import httpx
import json
import os
import click

from tlds_monitoring.root import ROOT_TLD_FILE


def get_root_tlds():
    # get root TLDs
    req = httpx.get("https://data.iana.org/TLD/tlds-alpha-by-domain.txt")
    tlds_alpha_by_domain_md5sum = hashlib.md5(req.content).hexdigest()

    # check md5sum
    req_md5sum = httpx.get("https://data.iana.org/TLD/tlds-alpha-by-domain.txt.md5")
    tlds_alpha_by_domain_md5sum_offered = req_md5sum.text.split(" ")[0]
    assert tlds_alpha_by_domain_md5sum == tlds_alpha_by_domain_md5sum_offered

    # generate tlds
    root_tlds = []
    for line in req.text.split("\n"):
        line = line.strip()
        if line.startswith("#") or len(line) == 0:
            continue
        tld = line.lower()
        root_tlds.append(tld)
    return root_tlds


@click.command()
@click.option(
    "--data-path", default="data", required=True, help="Directory to write data"
)
def main(data_path: str):
    root_tlds = get_root_tlds()
    os.makedirs(data_path, exist_ok=True)
    # write root TLDs
    with open(os.path.join(data_path, f"{ROOT_TLD_FILE}.json"), "w") as f:
        json.dump(root_tlds, indent=2, fp=f)


if __name__ == "__main__":
    main()
