import typing

from betterconf import Config, field
from betterconf.config import AbstractProvider

import logging
import requests
import json
import graphyte
from dateutil import parser
import time


logging.getLogger().setLevel(logging.INFO)


class JSONProvider(AbstractProvider):
    SETTINGS_JSON_FILE = "settings.json"

    def __init__(self):
        with open(self.SETTINGS_JSON_FILE, 'r') as f:
            self._settings = json.load(f)

    def get(self, name: str) -> typing.Any:
        return self._settings.get(name)


provider = JSONProvider()


class SettingsConfig(Config):
    api_token = field("api_token", provider=provider, default="demo")
    metrics = field("metrics", provider=provider)
    graphite_host = field("graphite", provider=provider, default="graphite")
    base_url = field("base_url", provider=provider, default="https://www.alphavantage.co/query?function"
                                                            "=CURRENCY_EXCHANGE_RATE")


cfg = SettingsConfig()
response_keys = {
    "1. From_Currency Code": "from_currency",
    "3. To_Currency Code": "to_currency",
    "5. Exchange Rate": "price",
    "6. Last Refreshed": "time",
    "7. Time Zone": "timezone"
}


def request_currency_metric(from_currency, to_currency):
    request_url = cfg.base_url + \
                  "&from_currency=" + from_currency + \
                  "&to_currency=" + to_currency + \
                  "&apikey=" + cfg.api_token
    metric_response = requests.get(request_url)
    metric_json = metric_response.json()["Realtime Currency Exchange Rate"]

    logging.info("Received metrics %s .. ", str(metric_json))

    result = {}
    for key in response_keys:
        result[response_keys[key]] = metric_json[key]
    result['price'] = float(result['price'])

    return result


def get_currency_metrics(metrics):
    currency_metrics = []
    for from_currency in metrics:
        for to_currency in metrics[from_currency]:
            currency_metrics.append(request_currency_metric(from_currency, to_currency))

    return currency_metrics


def send_metrics(currency_metrics):
    sender = graphyte.Sender(cfg.graphite_host, prefix='currencies')
    for metric in currency_metrics:
        sender.send(
            metric["from_currency"] + ':' + metric["to_currency"],
            metric["price"],
            timestamp=parser.parse(metric["time"] + ' ' + metric["timezone"]).timestamp()
        )


def main():
    metrics = get_currency_metrics(cfg.metrics)
    logging.info("Accessed %s ..", cfg.base_url)
    send_metrics(metrics)
    logging.info("Sent metrics ..")


if __name__ == '__main__':
    main()
