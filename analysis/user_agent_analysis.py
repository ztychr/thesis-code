import json
import sqlite3
import sys
from user_agents import parse
import requests
import dateutil.parser


def print_database_contents(database_path, group):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    uas = {}
    unique_vulnerabilities = {}
    total_vulnerabilities = {}
    processed_browsers = set()
    total_high_vulnerable_devices = 0
    total_critical_vulnerable_devices = 0
    total_low = 0
    total_medium = 0
    total_high = 0
    total_critical = 0
    total_unique_low = 0
    total_unique_medium = 0
    total_unique_high = 0
    total_unique_critical = 0
    total_cves_excluded = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    cve_to_severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    registered_cves = set()

    group_names = sys.argv[2:]
    for group_name in group_names:
        cursor.execute("SELECT * FROM json_data")
        rows = cursor.fetchall()
        cve_device_vulnerability = {}
        for row in rows:
            cve_2023_41061 = False
            cve_2023_41064 = False
            jd = json.loads(row[1])
            if jd["group"] == group_name:
                ua = jd["data"]["User-Agent"]

                # if jd["src"] == "qr":
                if jd["filename"] == "qr":

                    user_agent = parse(ua)
                    uas["total_os_families"] = uas.get("total_os_families", 0) + 1

                    # Increment count for specific OS family
                    if user_agent.os.family in uas:
                        uas[user_agent.os.family]["count"] = (
                            uas[user_agent.os.family].get("count", 0) + 1
                        )
                    else:
                        uas[user_agent.os.family] = {"count": 1}

                    # Increment count for specific browser family
                    if user_agent.browser.family in uas[user_agent.os.family]:
                        uas[user_agent.os.family][user_agent.browser.family][
                            "count"
                        ] = (
                            uas[user_agent.os.family][user_agent.browser.family].get(
                                "count", 0
                            )
                            + 1
                        )
                    else:
                        uas[user_agent.os.family][user_agent.browser.family] = {
                            "count": 1
                        }

                    # Increment count for specific browser version
                    if (
                        user_agent.browser.version_string
                        in uas[user_agent.os.family][user_agent.browser.family]
                    ):
                        uas[user_agent.os.family][user_agent.browser.family][
                            user_agent.browser.version_string
                        ] += 1
                    else:
                        uas[user_agent.os.family][user_agent.browser.family][
                            user_agent.browser.version_string
                        ] = 1

                    if "Mobile Safari" in user_agent.browser.family:
                        browser_name = "safari"
                    else:
                        # print(user_agent.browser.family, "is not Safari - Skipping")
                        continue

                    vendor = user_agent.device.brand
                    browser_version = user_agent.browser.version_string
                    user_agent.device.family
                    headers = {"apiKey": "redacted"}
                    cpe_name = f"cpe:2.3:a:{vendor}:{browser_name}:*:*:*:*:*:*:*:*"

                    try:
                        browser_new_version = version_up(browser_version)
                    except:
                        print("DEBUG: ", ua)  # vendor, browser_name, browser_version)
                    url = (
                        "https://services.nvd.nist.gov/rest/json/cves/2.0?virtualMatchString="
                        + cpe_name.replace(" ", "%20").lower()
                        + f"&versionStart={browser_version}&versionStartType=including&versionEnd={browser_new_version}&versionEndType=excluding"
                    )

                    print("yo")
                    if browser_version not in processed_browsers or True:
                        response = requests.get(url, headers=headers)
                        if response.status_code == 200:
                            json_response = json.loads(response.text)
                            for vulnerability in json_response["vulnerabilities"]:
                                cve_id = vulnerability["cve"]["id"]
                                base_score = vulnerability["cve"]["metrics"][
                                    "cvssMetricV31"
                                ][0]["cvssData"]["baseScore"]
                                published = dateutil.parser.parse(
                                    vulnerability["cve"]["published"]
                                )

                                if group_name == "boeing0":
                                    date_limiter = dateutil.parser.parse(
                                        "2023-12-03T23:59:59.999"
                                    )  # TS0
                                if group_name == "boeing1":
                                    date_limiter = dateutil.parser.parse(
                                        "2023-12-11T23:59:59.999"
                                    )  # TS1
                                if group_name == "boeing2":
                                    date_limiter = dateutil.parser.parse(
                                        "2023-12-15T23:59:59.999"
                                    )  # TS2
                                if group_name == "boeing3":
                                    date_limiter = dateutil.parser.parse(
                                        "2023-12-11T23:59:59.999"
                                    )  # TS3
                                if group_name == "ufm":
                                    date_limiter = dateutil.parser.parse(
                                        "2024-01-17T23:59:59.999"
                                    )  # UFM
                                if group_name == "ms":
                                    date_limiter = dateutil.parser.parse(
                                        "2024-2-14T23:59:59.999"
                                    )  # MS
                                if group_name == "dtu1":
                                    date_limiter = dateutil.parser.parse(
                                        "2024-2-28T23:59:59.999"
                                    )  # DTU
                                if group_name == "dtu2":
                                    date_limiter = dateutil.parser.parse(
                                        "2024-2-28T23:59:59.999"
                                    )  # DTU

                                published - date_limiter
                                if (
                                    published < date_limiter
                                ):  # HVIS DEN ER FØR EXPERIMENT STOP
                                    if float(base_score) >= float(9.0):
                                        if cve_id not in cve_device_vulnerability:
                                            cve_device_vulnerability[cve_id] = {}

                                        if (
                                            browser_version
                                            not in cve_device_vulnerability[cve_id]
                                        ):
                                            cve_device_vulnerability[cve_id][
                                                browser_version
                                            ] = 1
                                        else:
                                            cve_device_vulnerability[cve_id][
                                                browser_version
                                            ] += 1

                                if (
                                    published < date_limiter
                                ):  # HVIS DEN ER FØR EXPERIMENT STOP
                                    if browser_version not in total_vulnerabilities:
                                        total_vulnerabilities[browser_version] = {
                                            "low": 0,
                                            "medium": 0,
                                            "high": 0,
                                            "critical": 0,
                                        }

                                    if float(0.1) <= float(base_score) <= float(3.9):
                                        total_vulnerabilities[browser_version][
                                            "low"
                                        ] += 1
                                    if float(4.0) <= float(base_score) <= float(6.9):
                                        total_vulnerabilities[browser_version][
                                            "medium"
                                        ] += 1
                                    if float(7.0) <= float(base_score) <= float(8.9):
                                        total_vulnerabilities[browser_version][
                                            "high"
                                        ] += 1
                                    if float(9.0) <= float(base_score) <= float(10.0):
                                        total_vulnerabilities[browser_version][
                                            "critical"
                                        ] += 1

                                if (
                                    published < date_limiter
                                ):  # HVIS DEN ER FØR EXPERIMENT STOP
                                    if browser_version not in unique_vulnerabilities:
                                        unique_vulnerabilities[browser_version] = {
                                            "seen_cves": [],
                                            "low": 0,
                                            "medium": 0,
                                            "high": 0,
                                            "critical": 0,
                                        }

                                    if (
                                        cve_id
                                        not in unique_vulnerabilities[browser_version][
                                            "seen_cves"
                                        ]
                                    ):
                                        if (
                                            float(0.1)
                                            <= float(base_score)
                                            <= float(3.9)
                                        ):
                                            unique_vulnerabilities[browser_version][
                                                "low"
                                            ] += 1

                                            if cve_id not in registered_cves:
                                                cve_to_severity["low"] += 1

                                        if (
                                            float(4.0)
                                            <= float(base_score)
                                            <= float(6.9)
                                        ):
                                            unique_vulnerabilities[browser_version][
                                                "medium"
                                            ] += 1
                                            if cve_id not in registered_cves:
                                                cve_to_severity["medium"] += 1
                                        if (
                                            float(7.0)
                                            <= float(base_score)
                                            <= float(8.9)
                                        ):
                                            unique_vulnerabilities[browser_version][
                                                "high"
                                            ] += 1
                                            if cve_id not in registered_cves:
                                                cve_to_severity["high"] += 1
                                        if (
                                            float(9.0)
                                            <= float(base_score)
                                            <= float(10.0)
                                        ):
                                            unique_vulnerabilities[browser_version][
                                                "critical"
                                            ] += 1
                                            if cve_id not in registered_cves:
                                                cve_to_severity["critical"] += 1
                                try:
                                    if (
                                        cve_id
                                        in unique_vulnerabilities[browser_version][
                                            "seen_cves"
                                        ]
                                    ):  # HVIS DEN ALLEREDE ER REGISTRERET
                                        continue
                                except:
                                    continue

                                if (
                                    published > date_limiter
                                    and cve_id not in registered_cves
                                ):  # HVIS DEN ER EFTER EXPERIMENT STOP
                                    if float(0.1) <= float(base_score) <= float(3.9):
                                        total_cves_excluded["low"] += 1
                                    if float(4.0) <= float(base_score) <= float(6.9):
                                        total_cves_excluded["medium"] += 1
                                    if float(7.0) <= float(base_score) <= float(8.9):
                                        total_cves_excluded["high"] += 1
                                    if float(9.0) <= float(base_score) <= float(10.0):
                                        total_cves_excluded["critical"] += 1

                                unique_vulnerabilities[browser_version][
                                    "seen_cves"
                                ].append(cve_id)
                                registered_cves.add(cve_id)

                            processed_browsers.add(browser_version)

        print(group_name, cve_device_vulnerability)
    if cve_2023_41061 == True:
        if cve_2023_41064 == True:
            print("BLASTPASS?????")

    print("##### Dictionaries: #####\n")
    print("UAS Dict Dump:\n", json.dumps(uas, indent=2))
    print(
        "Browser total total_vulnerabilities:\n",
        json.dumps(total_vulnerabilities, indent=2),
    )  # BRUGES TIL AT TÆLLE VULNS PER VERSION
    print(
        "Browser total unique_vulnerabilities:\n",
        json.dumps(unique_vulnerabilities, indent=2),
    )  # BRUGES KUN TIL TOTAL UNIQUE
    print("Total unique CVES:\n", json.dumps(cve_to_severity, indent=2))
    print("Total CVEs excluded:\n", json.dumps(total_cves_excluded, indent=2))
    print("")

    for os_family, os_data in uas.items():
        if os_family.startswith("total_"):
            continue

        for browser_family, browser_data in os_data.items():
            if browser_family == "count":
                continue
            if "Safari" not in browser_family:
                continue

            for browser_version, count in browser_data.items():
                if browser_version == "count":
                    continue
                if browser_version == "total_count":
                    continue
                if browser_version in total_vulnerabilities:
                    if total_vulnerabilities[browser_version]["high"] > 0:
                        total_high_vulnerable_devices += count
                    if total_vulnerabilities[browser_version]["critical"] > 0:
                        total_critical_vulnerable_devices += count

    for key, value in total_vulnerabilities.items():
        total_low += value["low"]
        total_medium += value["medium"]
        total_high += value["high"]
        total_critical += value["critical"]

    for key, value in unique_vulnerabilities.items():
        total_unique_low += value["low"]
        total_unique_medium += value["medium"]
        total_unique_high += value["high"]
        total_unique_critical += value["critical"]

    print("##### Summary: #####\n")
    print("Total Low:", total_low)
    print("Total Medium:", total_medium)
    print("Total High:", total_high)
    print("Total Critical:", total_critical, "\n")

    print("Total Unique Low:", total_unique_low)
    print("Total Unique Medium:", total_unique_medium)
    print("Total Unique High:", total_unique_high)
    print("Total Unique Critical:", total_unique_critical, "\n")

    print("Total devices with high vulnerabilities: ", total_high_vulnerable_devices)
    print(
        "Total devices with critical vulnerabilities: ",
        total_critical_vulnerable_devices,
        "\n",
    )
    print(
        "##### Browser total unique_vulnerabilities: #####\n",
        json.dumps(unique_vulnerabilities, indent=2),
    )  # Print total counts

    print("Total scans:", uas["total_os_families"])
    for os_family, os_data in uas.items():
        if os_family.startswith("total_"):
            continue
        print("OS family:", os_family, "(Total Count:", str(os_data["count"]) + ")")
        for browser_family, browser_data in os_data.items():
            if browser_family == "count":
                continue
            print(
                "\tBrowser family:",
                browser_family,
                "(Total Count:",
                str(browser_data["count"]) + ")",
            )
            for browser_version, count in browser_data.items():
                if browser_version == "count":
                    continue
                if browser_version == "total_count":
                    continue
                browser_version_str = (
                    str(browser_version)
                    if isinstance(browser_version, tuple)
                    else browser_version
                )
                print(
                    "\t\tBrowser version:", browser_version, "(Count:", str(count) + ")"
                )


"""    
def remove_versions(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if key == "count":
                new_data[key] = value
            else:
                new_data[key] = remove_versions(value)
        return new_data
    elif isinstance(data, list):
        return [remove_versions(item) for item in data]
    else:
        return data
"""


def version_up(version):
    parts = version.split(".")
    last_number = int(parts[-1]) + 1
    updated_text = ".".join(parts[:-1]) + "." + str(last_number)
    return updated_text


database_path = sys.argv[1]
group = sys.argv[2]
print_database_contents(database_path, group)
