import os
import subprocess

CWD = os.getcwd()
VOLUME = "hw5_data"
TARBALL = f"{VOLUME}.tar.gz"

def main():
    subprocess.run(
        [
            "docker",
            "run",
            "-v",
            f"{VOLUME}:/data",
            "-v",
            f"{CWD}:/backup",
            "ubuntu",
            "tar",
            "czvfp",
            f"/backup/{TARBALL}",
            "/data/questdb",
        ],
        check=True,
    )
    print("done 🙂")


if __name__ == "__main__":
    main()
