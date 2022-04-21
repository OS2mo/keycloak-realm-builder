import sys 
import os
sys.path.append(os.path.abspath("../main.py"))

import pytest
from pydantic import ValidationError

from main import Settings


def test_unset():
    with pytest.raises(ValidationError):
        Settings()


def test_minimal_settings(monkeypatch):
    monkeypatch.setenv('keycloak_admin_password', 'hunter2')
    settings = Settings()
    assert settings.keycloak_admin_password == "hunter2"


def test_minimal_settings_tf_prefix(monkeypatch):
    monkeypatch.setenv('TF_VAR_keycloak_admin_password', 'hunter2')
    settings = Settings()
    assert settings.keycloak_admin_password == "hunter2"


def test_mixed_tf_var_settings(monkeypatch):
    monkeypatch.setenv('keycloak_admin_username', 'AzureDiamond')
    monkeypatch.setenv('TF_VAR_keycloak_admin_password', 'hunter2')
    settings = Settings()
    assert settings.keycloak_admin_username == "AzureDiamond"
    assert settings.keycloak_admin_password == "hunter2"
