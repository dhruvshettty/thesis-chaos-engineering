#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a general helper function used to along with the other scripts part
of the load generator for the Chaos Engineering experiments. This helper file
has very generalized code and skips certain confidential methods.

Author: dhruvshetty213@gmail.com
"""
from faker import Faker

def generate_user_data(update=False) -> dict:
    """
    Generate a fake user with necessary attributes or update the user's profile.

    Returns:
        dict: A dictionary with the user data.
    """
    fake = Faker()

    if update:
        return update_user_data()

    identifier = fake.uuid4()
    name = fake.name()
    email = fake.email()

    user_data = {
        "identifier": identifier,
        "currency": "XYZ",
        "name": name,
        "email": email,
        "auth_ref": None,
    }

    return user_data

def update_user_data():
    """Generate updated user data with name and email."""
    fake = Faker()

    updated_data = {
        "name": fake.name(),
        "email": fake.email()
    }

    return updated_data

def generate_payment_payload(transfer=False) -> dict:
    """
    Generate a payload for payment. If transfer is True, add a generic receiver_id.

    Returns:
        dict: A dictionary with the payment payload.
    """
    payload = {
        "amount": 3
    }

    if transfer:
        payload["receiver_id"] = "GENERATE_OR_PROVIDE_A_RECEIVER_ID"

    return payload

generic_test_card = {
    "card[number]": "YOUR_TEST_CARD_NUMBER",
    "card[exp_month]": 9,
    "card[exp_year]": 9999,
    "card[cvc]": 123,
    "type": "card"
}
