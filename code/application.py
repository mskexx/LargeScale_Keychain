"""
User-level application (stub).

NB: Feel free to extend or modify.
"""

import argparse
from keychain import store
import time


def main(arguments):
    # Launch node
    # ----------------
    storage = allocate_application(arguments)
    # Adding a key-value pair to the storage.
    key = "info8002"
    value = "funFUNfun"
    callback = storage.put(key, value, block=False)
    # Depending on how fast your blockchain is,
    # this will return a proper result.
    print(">> Last value: ",storage.retrieve(key))

    # Using the callback object,
    # you can also wait for the operation to be completed.
    callback.wait()

    # Now the key should be available,
    # unless a different node `put` a new value.
    print(">> Last value after waiting", storage.retrieve(key))

    # Show all values of the key.
    print(">> History of values: ", ' <- '.join(storage.retrieve_all(key)))
    print("Finish application")


def allocate_application(arguments):
    application = store.Storage(
        port=arguments.port,
        bootstrap=arguments.bootstrap,
        miner=arguments.miner,
        difficulty=arguments.difficulty)

    return application


def parse_arguments():
    parser = argparse.ArgumentParser(
        "KeyChain - An overengineered key-value store "
        "with version control, powered by fancy linked-lists.")
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--miner", type=bool, default=False, nargs='?',
                        const=True, help="Starts the mining procedure.")
    parser.add_argument("--bootstrap", type=str, default=None,
                        help="Sets the address of the bootstrap node.")
    parser.add_argument("--difficulty", type=int, default=5,
                        help="Sets the difficulty of Proof of Work, only has "
                             "an effect with the `--miner` flag has been set.")
    arguments, _ = parser.parse_known_args()

    return arguments


if __name__ == "__main__":
    arguments = parse_arguments()
    main(arguments)
