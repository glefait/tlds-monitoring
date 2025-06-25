import json
import os
import click
from tlds_monitoring.root import ROOT_TLD_DETAILS_FILE, ROOT_TLD_SIMPLIFIED_DETAILS_FILE


def simplify_root_tld(root_tlds_details):
    root_tlds_simplified = {}
    for tld, entity in root_tlds_details.items():
        simplified = {
            "unicodeName": (
                entity["unicodeName"] if "unicodeName" in entity else entity["ldhName"]
            ),
            "nameservers": {},
            "entities": {},
            "secureDNS": entity["secureDNS"],
            "status": entity["status"],
            "port43": entity["port43"] if "port43" in entity else None,
        }
        for ns in entity["nameservers"]:
            if ns["objectClassName"] == "nameserver":
                ns_name = ns["ldhName"]
                simplified["nameservers"][ns_name] = {}
                for z in ns["ipAddresses"]:
                    simplified["nameservers"][ns_name][z] = ns["ipAddresses"][z]
        roles = ["registrant", "technical", "administrative"]
        for e in entity["entities"]:
            for r in e["roles"]:
                assert r in roles
                assert r not in simplified["entities"], (
                    "this role was already assumed by another entity"
                )
                simplified["entities"][r] = {
                    "fn": None,
                    "org": None,
                    "adr": None,
                    "tel": None,
                    "email": None,
                }
                # vcardArray = ['vcard', {}]
                assert len(e["vcardArray"]) == 2, "vcardArray should have 2 elements"
                for vcard in e["vcardArray"][1]:
                    if vcard[0] == "adr":
                        if (
                            "label" in vcard[1] and len(vcard[1]["label"].strip()) > 0
                        ):  # cuba does not have a label
                            simplified["entities"][r][vcard[0]] = vcard[1][
                                "label"
                            ].strip()
                    elif vcard[0] in simplified["entities"][r]:
                        simplified["entities"][r][vcard[0]] = vcard[3].strip()
        root_tlds_simplified[tld] = simplified
    return root_tlds_simplified


@click.command()
@click.option(
    "--data-path", default="data", required=True, help="Directory to read / write data"
)
def main(data_path: str):
    # load existing root tlds
    with open(os.path.join(data_path, f"{ROOT_TLD_DETAILS_FILE}.json"), "r") as r:
        root_tlds_details = json.load(r)
        root_tlds_simplified = simplify_root_tld(root_tlds_details)
        # write the aggregated result
        with open(
            os.path.join(data_path, f"{ROOT_TLD_SIMPLIFIED_DETAILS_FILE}.json"), "w"
        ) as f:
            json.dump(root_tlds_simplified, indent=2, fp=f)


if __name__ == "__main__":
    main()
