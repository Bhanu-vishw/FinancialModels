import subprocess

VOLUME = "hw5_data"

def main():
    print(f"creating {VOLUME} volume")
    subprocess.run(
        ["docker", "volume", "create", VOLUME], check=True, capture_output=True
    )
    print("done 🙂")

if __name__ == "__main__":
    main()
