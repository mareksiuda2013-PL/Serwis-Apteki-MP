from __future__ import annotations

from services.network import NetworkService, NetworkInfo


def test_network_service_can_be_created():
    service = NetworkService()

    assert isinstance(service, NetworkService)


def test_get_info_returns_network_info():
    service = NetworkService()

    result = service.get_info()

    assert isinstance(result, NetworkInfo)


def test_local_ip_is_string():
    service = NetworkService()

    result = service.get_info()

    assert isinstance(result.local_ip, str)


def test_gateway_is_string():
    service = NetworkService()

    result = service.get_info()

    assert isinstance(result.gateway, str)


def test_internet_is_boolean():
    service = NetworkService()

    result = service.get_info()

    assert isinstance(result.internet, bool)


def test_network_info_default_values():
    info = NetworkInfo()

    assert info.local_ip == ""
    assert info.gateway == ""
    assert info.internet is False


def test_get_info_can_be_called_twice():
    service = NetworkService()

    first = service.get_info()
    second = service.get_info()

    assert isinstance(first, NetworkInfo)
    assert isinstance(second, NetworkInfo)
