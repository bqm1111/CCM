import asyncio
import subprocess
import csv
async def ping(ip):
    proc = await asyncio.create_subprocess_exec(
        'ping', '-c', '1', ip,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    await proc.communicate()
    return proc.returncode == 0

async def main():
    ips = []
    with open("coordinator/camera.csv", "r") as f:
        data = csv.reader(f)
        for row in data:
            ips.append(row[1])
    results = await asyncio.gather(*(ping(ip) for ip in ips))
    reachable = []
    for ip, result in zip(ips, results):
        if result:
            reachable.append(ip)
    with open("reachable.csv", "w") as f:
        writer = csv.writer(f)
        for r in reachable:
            writer.writerow([r])
asyncio.run(main())
