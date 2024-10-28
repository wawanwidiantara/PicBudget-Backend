from django.core.management.utils import get_random_secret_key

from picbudget.core.utils.criptography import generate_key_pair


def generate_account():
    key_pair = generate_key_pair()
    print(f"Signing Key: {key_pair.private}")
    print(f"Account Number{key_pair.public}")


def generate_secret_key():
    secret_key = get_random_secret_key()
    print(f"Secret Key: {secret_key}")


if __name__ == "__main__":
    print()
    generate_account()
    generate_secret_key()
