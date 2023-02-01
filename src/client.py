"""FastAPI Titanic model inference example"""

import argparse
import requests


def main():
    """Функция-пример работы клиента с запущенным сервером"""
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-host", "--host", required=True, type=str, help="server_ip")
    argparser.add_argument(
        "-port", "--port", required=True, type=str, help="server_port"
    )
    args = argparser.parse_args()
    url = f"http://{args.host}:{args.port}"

    response = requests.get(url + "/", timeout=30)
    print("status code: ", response.status_code)
    print("content: ", response.content)

    passenger = {
        "Name": "John",
        "Pclass": 1,
        "Sex": "male",
        "Age": 27,
        "Embarked": "S",
        "Fare": 100,
        "SibSp": 0,
        "Parch": 0,
        "Ticket": "C101",
        "Cabin": "ST",
    }
    response = requests.post(
        url + "/predict?passenger_id=1", json=passenger, timeout=30
    )
    print("status code: ", response.status_code)
    print("content: ", response.content)

    passengers = {
        "passengers": [
            {
                "Name": "John",
                "Pclass": 1,
                "Sex": "male",
                "Age": 27,
                "Embarked": "S",
                "Fare": 100,
                "SibSp": 0,
                "Parch": 0,
                "Ticket": "C101",
                "Cabin": "ST",
            },
            {
                "Name": "Anna",
                "Pclass": 1,
                "Sex": "female",
                "Age": 27,
                "Embarked": "S",
                "Fare": 100,
                "SibSp": 0,
                "Parch": 0,
                "Ticket": "C101",
                "Cabin": "ST",
            },
        ]
    }

    response = requests.post(url + "/predict_batch", json=passengers, timeout=30)
    #response = requests.post(url, json=passengers, timeout=30)
    print("status code: ", response.status_code)
    print("content: ", response.content)


if __name__ == "__main__":
    main()
