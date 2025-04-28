#!/usr/bin/env python3
# Author: DJ

import re
import sys
import subprocess
from datetime import datetime
import argparse  # 导入 argparse 模块用于解析命令行参数

def parse_time_field(value):
    """Parse time field and convert it to a readable format."""
    try:
        # 如果是 "Mon Apr 28 08:58:54 2025" 这样的格式
        dt = datetime.strptime(value, '%a %b %d %H:%M:%S %Y')
        return dt.strftime('%Y.%m.%d %H:%M:%S')
    except ValueError:
        pass

    try:
        # 如果是秒数（Epoch 时间戳）
        if value.isdigit():
            timestamp = int(value)
            return datetime.fromtimestamp(timestamp).strftime('%Y.%m.%d %H:%M:%S')
    except ValueError:
        pass

    try:
        # 如果是 "[[CC]YY]MMDDhhmm[.ss]" 格式
        for fmt in ('%Y%m%d%H%M%S', '%Y%m%d%H%M', '%Y%m%d%H'):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime('%Y.%m.%d %H:%M:%S')
            except ValueError:
                continue
    except Exception:
        pass

    # 如果无法解析，返回原始值
    return value


def parse_qstat_output(output):
    result = {
        "Job_Id": None,
        "Job_Name": None,
        "Job_Owner": None,
        "Queue": None,
        "Nodes": None,
        "Run_Status": None,
        "Error_Path": None,
        "Output_Path": None,
        "Memory_Used_GB": None,
        "CPU_Cores_Used": None,
        "Submit_Directory": None,
        "Submit_Arguments": None,
        "ctime": "N/A",          # 默认值
        "etime": "N/A",          # 默认值
        "mtime": "N/A",          # 默认值
        "qtime": "N/A",          # 默认值
        "stime": "N/A"           # 默认值
    }

    patterns = {
        "Job_Id": r"Job Id:\s+(.+)",
        "Job_Name": r"Job_Name\s*=\s*(.+)",
        "Job_Owner": r"Job_Owner\s*=\s*(.+)",
        "Queue": r"queue\s*=\s*(.+)",
        "Nodes": r"exec_host\s*=\s*(.+)",
        "Run_Status": r"job_state\s*=\s*(.+)",
        "Error_Path": r"Error_Path\s*=\s*(.+)",
        "Output_Path": r"Output_Path\s*=\s*(.+)",
        "Memory_Used": r"resources_used\.mem\s*=\s*([\d]+)kb",
        "CPU_Cores_Used": r"resources_used\.ncpus\s*=\s*([\d]+)",
        "Submit_Directory": r"jobdir\s*=\s*(.+)",
        "Submit_Arguments": r"Submit_arguments\s*=\s*(.+)",
        "ctime": r"ctime\s*=\s*(.+)",
        "etime": r"etime\s*=\s*(.+)",
        "mtime": r"mtime\s*=\s*(.+)",
        "qtime": r"qtime\s*=\s*(.+)",
        "stime": r"stime\s*=\s*(.+)"
    }

    lines = output.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        for key, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                value = match.group(1).strip()
                # 如果是 Error_Path、Output_Path 或 Submit_Arguments，处理多行情况
                if key in ["Error_Path", "Output_Path", "Submit_Arguments"]:
                    while i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if not re.match(r"^(exec_host|mtime|Priority|qtime|Rerunable|Resource_List|schedselect|stime|session_id|jobdir|substate|Variable_List|comment|etime|run_count|eligible_time|accrue_type|Submit_arguments)", next_line):
                            if key == "Submit_Arguments" and value.strip().endswith(".sh"):
                                break
                            i += 1
                            value += next_line.replace(" ", "")
                        else:
                            break
                # 解析并格式化时间字段
                if key in ["ctime", "etime", "mtime", "qtime", "stime"]:
                    value = parse_time_field(value)
                result[key] = value
        i += 1

    # 将内存从 KB 转换为 GB
    if "Memory_Used" in result:
        memory_kb = int(result.pop("Memory_Used"))
        result["Memory_Used_GB"] = f"{memory_kb / (1024 ** 2):.2f} GB"

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
    print("Run Status:", parsed_data["Run_Status"])
    print("CPU Cores Used:", parsed_data["CPU_Cores_Used"])
    print("Memory Used:", parsed_data["Memory_Used_GB"])
    print("Submit Directory:", parsed_data["Submit_Directory"])
    print("Error Path:", parsed_data["Error_Path"])
    print("Output Path:", parsed_data["Output_Path"])
    print("Submit Arguments:", parsed_data["Submit_Arguments"])
    print("Creation Time (ctime):", parsed_data["ctime"])
    print("Queue Entry Time (qtime):", parsed_data["qtime"])
    print("Eligibility Time (etime):", parsed_data["etime"])
    print("Start Time (stime):", parsed_data["stime"])
    print("Modification Time (mtime):", parsed_data["mtime"])


if __name__ == "__main__":
    # 创建 ArgumentParser 对象
    parser = argparse.ArgumentParser(description="Retrieve and display PBS job information.")

    # 添加参数
    parser.add_argument(
        "job_id",
        nargs="?",  # 可选参数
        help="The PBS job ID to query."
    )

    # 解析参数
    args = parser.parse_args()

    # 如果没有提供 job_id，则显示帮助信息
    if not args.job_id:
        parser.print_help()
        sys.exit(1)

    # 调用主函数
    main(args.job_id)
