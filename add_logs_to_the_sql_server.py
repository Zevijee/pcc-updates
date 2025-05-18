import os
import re
import subprocess

def get_timestamp(filename):
    m = re.search(r'(\d{10})', filename)
    return int(m.group(1)) if m else 0

def add_logs():
    bak_path = r"C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\Backup\bak.bak"
    undo_path = r"C:\Program Files\Microsoft SQL Server\MSSQL15.MSSQLSERVER\MSSQL\Backup\rollback.bak"

    if os.path.exists(bak_path):
        os.remove(bak_path)

    entries = os.listdir('new_logs')
    sqb_files = [f for f in entries if f.lower().endswith('.sqb')]
    sqb_files.sort(key=get_timestamp)

    for fname in sqb_files:
        subprocess.run([
            r"C:\Program Files (x86)\Red Gate\SQL Backup 10\SQBConverter.exe",
            rf"C:\Users\zelli\Desktop\clearview-update-pcc-server\new_logs\{fname}",
            bak_path,
            "Pcc+bdrk=$uccess"
        ], check=True)

        cmd = [
            r"sqlcmd",
            "-S", "localhost",
            "-E",
            "-Q",
            f"RESTORE LOG us_bdrk_multi_replica "
            f"FROM DISK = N'{bak_path}' "
            f"WITH STANDBY = N'{undo_path}';"
        ]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running sqlcmd: {e}")
            exit(1)

        os.remove(bak_path)
        os.remove(f"C:\\Users\\zelli\\Desktop\\clearview-update-pcc-server\\new_logs\\{fname}")