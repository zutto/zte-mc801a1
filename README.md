# ZTE Connection Recovery Program

This is a Python program for automatically recovering a dropped connection on a ZTE mc801av1 box.


* Note:
This has not been extensively tested, and may not help at all. What this does is attempts to trick the box into refreshing the uplink from the ZTE box to the ISP's tower.

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/zutto/zte-mc801a1.git
   cd zte-mc801a1
   ```

2. Update the `main.py` script with your ZTE device information.

3. Run the script using the following command:
   ```bash
   python3 main.py --zte-password <your_zte_password> --zte-host <your_zte_host> --zte-remote-host "google.com"
   ```

## Configuration

You can configure the following options in the `main.py` script:

- `zte-password`: Your ZTE device password.
- `zte-host`: The IP address or hostname of your ZTE device.
- `zte-remote-host`: The remote host to monitor connection to (default: google.com).
- - This remote host needs to be a host that accepts a tcp connection, prefer IP addresses for faster failover)
- `zte-remote-port`: The remote port to monitor connection to (default: 80).
- `pause-after-switch`: The duration to pause after switching bearer preference (default: 15 seconds).

## Features

- Monitors connection to a remote host and performs an auto-fix if connection is lost.

## Disclaimer

This script is provided as-is and is intended for educational and testing purposes only. Use at your own risk.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
