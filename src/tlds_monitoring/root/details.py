import httpx
import json
import os
import click
import aiohttp
import asyncio


from tlds_monitoring.root import ROOT_TLD_FILE, DOMAIN_DIR_PATH, ROOT_TLD_DETAILS_FILE

MAX_RETRY = 5
RETRY_DELAY_SEC = 10
CRAWL_ASYNC_MAX_CONNEXION = 10
CRAWL_ASYNC_TIMEOUT = 30


def get_tld_details_through_rdap_files(root_tlds):
    # for each tld, get details
    root_tlds_details = {}
    with httpx.Client() as client:
        for tld in root_tlds:
            print(tld)
            req = client.get(f"https://rdap.iana.org/domain/{tld}")
            root_tlds_details[tld] = req.json()
    # TODO: slow. 02m 30s => async ?
    return root_tlds_details


async def fetch(session: aiohttp.ClientSession, sem, url, tld):
    for i in range(MAX_RETRY):
        async with sem:
            try:
                async with session.get(url) as response:
                    return tld, await response.json()
            except Exception as e:
                print(f"error {i}/{MAX_RETRY} for {tld}: {e}")
                asyncio.sleep(RETRY_DELAY_SEC)


async def async_get_tld_details_through_rdap_files(root_tlds):
    # for each tld, get details
    sem = asyncio.Semaphore(
        CRAWL_ASYNC_MAX_CONNEXION
    )  # let's be super nice (aiohttp default is 100)
    custom_timeout = aiohttp.ClientTimeout(
        total=0,
        sock_connect=CRAWL_ASYNC_TIMEOUT,
        sock_read=CRAWL_ASYNC_TIMEOUT,
        connect=CRAWL_ASYNC_TIMEOUT,
    )
    tasks = []
    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
        for tld in root_tlds:
            tasks.append(
                fetch(session, sem, f"https://rdap.iana.org/domain/{tld}", tld)
            )
        fetched = await asyncio.gather(*tasks)

    return {k: v for k, v in fetched}


@click.command()
@click.option(
    "--data-path", default="data", required=True, help="Directory to read / write data"
)
def main(data_path: str):
    # load existing root tlds
    with open(os.path.join(data_path, f"{ROOT_TLD_FILE}.json"), "r") as r:
        root_tlds = json.load(r)
        tld_details = asyncio.run(async_get_tld_details_through_rdap_files(root_tlds))
        # loop = asyncio.get_event_loop()
        # tld_details = loop.run_until_complete(
        #     async_get_tld_details_through_rdap_files(root_tlds)
        # )
        # tld_details = get_tld_details_through_rdap_files(root_tlds)

        # write the individual details
        domain_path = os.path.join(data_path, DOMAIN_DIR_PATH)
        os.makedirs(domain_path, exist_ok=True)
        for tld, tld_detail in tld_details.items():
            with open(os.path.join(domain_path, f"{tld}.json"), "w") as f:
                json.dump(tld_detail, indent=2, fp=f)

        # # write the aggregated result
        with open(os.path.join(data_path, f"{ROOT_TLD_DETAILS_FILE}.json"), "w") as f:
            json.dump(tld_details, indent=2, fp=f)


if __name__ == "__main__":
    main()
