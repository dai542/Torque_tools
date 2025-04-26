#!/usr/bin/env python3
# Author: DJ

import re
import sys
import subprocess

def parse_qstat_output(output):
    result = {
        "Job_Id": None,
        "Job_Name": None,
        "Job_Owner": None,
        "Queue": None,
        "Nodes": None,
        "Submit_Time": None,
        "Run_Status": None,
        "Work_Directory": None,
        "Submit_Directory": None,
        "Submit_Arguments": None
    }

    patterns = {
        "Job_Id": r"Job Id:\s+(.+)",
        "Job_Name": r"Job_Name\s*=\s*(.+)",
        "Job_Owner": r"Job_Owner\s*=\s*(.+)",
        "Queue": r"queue\s*=\s*(.+)",
        "Nodes": r"exec_vnode\s*=\s*$(.+)$",
        "Submit_Time": r"ctime\s*=\s*(.+)",
        "Run_Status": r"job_state\s*=\s*(.+)",
        "Work_Directory": r"PBS_O_WORKDIR\s*=\s*(.+)",
        "Submit_Directory": r"jobdir\s*=\s*(.+)",
        "Submit_Arguments": r"Submit_arguments\s*=\s*([^\s]+)"
    }

    lines = output.splitlines()
    for i, line in enumerate(lines):
        for key, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                value = match.group(1).strip()
                if key in ["Submit_Arguments"]:
                    while i + 1 < len(lines) and not value.endswith(".sh"):
                        i += 1
                        next_line = lines[i].strip()
                        value += next_line.strip()
                result[key] = value

    if not result["Nodes"]:
        match = re.search(r"exec_host\s*=\s*(.+)", output)
        if match:
            result["Nodes"] = match.group(1).strip()

    return result


def main(job_id):
    try:
        qstat_output = subprocess.check_output(["qstat", "-xf", job_id], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Unable to retrieve information for job {job_id}. Please check if the job ID is correct.")
        sys.exit(1)

    parsed_data = parse_qstat_output(qstat_output)

    print("Job ID:", parsed_data["Job_Id"])
    print("Job Name:", parsed_data["Job_Name"])
    print("User Name:", parsed_data["Job_Owner"])
    print("Queue:", parsed_data["Queue"])
    print("Nodes:", parsed_data["Nodes"])
    print("Submit Time:", parsed_data["Submit_Time"])
    print("Run Status:", parsed_data["Run_Status"])
    print("Work Directory:", parsed_data["Work_Directory"])
    print("Submit Directory:", parsed_data["Submit_Directory"])
    print("Submit Arguments:", parsed_data["Submit_Arguments"])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 2.py <JOB_ID>")
        sys.exit(1)

    job_id = sys.argv[1]

    main(job_id)
