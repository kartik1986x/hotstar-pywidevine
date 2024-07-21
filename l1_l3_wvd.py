import logging
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
import httpx

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

WVD_PATH = "PATH_TO_THE_WVD_FILE"
from headers import headers

def get_key(pssh, license_url):
    logger.debug("Loading device...")
    device = Device.load(WVD_PATH)
    cdm = Cdm.from_device(device)
    session_id = cdm.open()
    logger.debug("Session opened...")

    challenge = cdm.get_license_challenge(session_id, PSSH(pssh))
    response = httpx.post(license_url, data=challenge, headers=headers)
    cdm.parse_license(session_id, response.content)

    keys = []
    logger.debug("Retrieving keys...")
    for key in cdm.get_keys(session_id):
        logger.debug(f"Key found: {key.kid.hex}:{key.key.hex()}, Type: {key.type}")
        if key.type == 'CONTENT':
            keys.append(f"--key {key.kid.hex}:{key.key.hex()}")

    cdm.close(session_id)
    logger.debug("Session closed...")
    return "\n".join(keys)

if __name__ == "__main__":
    pssh_str = input("PSSH? ")
    lic_url = input("License URL? ")
    result = get_key(pssh_str, lic_url)
    logger.debug("Result:")
    print(result)  
