"""SDO AIA sender."""

import datetime
import time

from .common import load_config, send_group_file, send_group_msg, text

SDO_VIDEOS = [
    {
        "name": "SDO AIA 193",
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/mpeg/latest_1024_0193.mp4",
        "description": """Where: Corona and hot flare plasma
Wavelength: 193 angstroms (0.0000000193 m) = Extreme Ultraviolet
Primary ions seen: 11 times ionized iron (Fe XII)
Characteristic temperature: 1.25 million K (2.25 million F)""",
    },
    {
        "name": "SDO AIA 304",
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/mpeg/latest_1024_0304.mp4",
        "description": """Where: Upper chromosphere and lower transition region
Wavelength: 304 angstroms (0.0000000304 m) = Extreme Ultraviolet
Primary ions seen: singly ionized helium (He II)
Characteristic temperature: 50,000 K (90,000 F)""",
    },
    {
        "name": "SDO AIA 171",
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/mpeg/latest_1024_0171.mp4",
        "description": """Where: Quiet corona and upper transition region
Wavelength: 171 angstroms (0.0000000171 m) = Extreme Ultraviolet
Primary ions seen: 8 times ionized iron (Fe IX)
Characteristic temperature: 1 million K (1.8 million F)""",
    },
    {
        "name": "SDO AIA 211",
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/mpeg/latest_1024_0211.mp4",
        "description": """Where: Active regions of the corona
Wavelength: 211 angstroms (0.0000000211 m) = Extreme Ultraviolet
Primary ions seen: 13 times ionized iron (Fe XIV)
Characteristic temperature: 2 million K (3.6 million F)""",
    },
    {
        "name": "SDO AIA 131",
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/mpeg/latest_1024_0131.mp4",
        "description": """Where: Flaring regions of the corona
Wavelength: 131 angstroms (0.0000000131 m) = Extreme Ultraviolet
Primary ions seen: 20 and 7 times ionized iron (Fe VIII, Fe XXI)
Characteristic temperatures: 10 million K (18 million F)""",
    },
    {
        "name": "SDO AIA 335",
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/mpeg/latest_1024_0335.mp4",
        "description": """Where: Active regions of the corona
Wavelength: 335 angstroms (0.0000000335 m) = Extreme Ultraviolet
Primary ions seen: 15 times ionized iron (Fe XVI)
Characteristic temperature: 2.8 million K (5 million F)""",
    },
    {
        "name": "SDO AIA 094",
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/mpeg/latest_1024_0094.mp4",
        "description": """Where: Flaring regions of the corona
Wavelength: 94 angstroms (0.0000000094 m) = Extreme Ultraviolet/soft X-rays
Primary ions seen: 17 times ionized iron (Fe XVIII)
Characteristic temperature: 6 million K (10.8 million F)""",
    },
    {
        "name": "SDO AIA 1600",
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/mpeg/latest_1024_1600.mp4",
        "description": """Where: Transition region and upper photosphere
Wavelength: 1600 angstroms (0.00000016 m) = Far Ultraviolet
Primary ions seen: thrice ionized carbon (C IV) and Continuum
Characteristic temperatures: 6,000 K (11,000 F), and 100,000 K (180,000 F)""",
    },
    {
        "name": "SDO AIA 1700",
        "url": "https://sdo.gsfc.nasa.gov/assets/img/latest/mpeg/latest_1024_1700.mp4",
        "description": """Where: Temperature minimum and photosphere
Wavelength: 1700 angstroms (0.00000017 m) = Far Ultraviolet
Primary ions seen: Continuum
Characteristic temperature: 6,000 K (11,000 F)""",
    },
]

SLOT_SECONDS = 6 * 60 * 60


def get_sdo():
    # Rotate through wavelengths by 6-hour slot so one-shot runs need no state
    slot = int(time.time()) // SLOT_SECONDS
    return SDO_VIDEOS[slot % len(SDO_VIDEOS)]


def send_sdo():
    config = load_config()
    sdo = get_sdo()
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = sdo["name"].replace(" ", "-") + "_" + timestamp + ".mp4"
    send_group_file(config["GROUP"], sdo["url"], file_name)
    send_group_msg(
        config["GROUP"], text("Sun in the past 48 hours from " + sdo["name"])
    )
    send_group_msg(config["GROUP"], text(sdo["description"]))
