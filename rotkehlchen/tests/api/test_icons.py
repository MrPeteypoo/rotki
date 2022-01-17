import filecmp
import os
import shutil
import urllib
from http import HTTPStatus
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import requests

from rotkehlchen.icons import ALLOWED_ICON_EXTENSIONS
from rotkehlchen.tests.utils.api import (
    api_url_for,
    assert_error_response,
    assert_proper_response_with_result,
)
from rotkehlchen.tests.utils.constants import A_GNO


@pytest.mark.parametrize('start_with_logged_in_user', [False])
@pytest.mark.parametrize('number_of_eth_accounts', [0])
@pytest.mark.parametrize('file_upload', [True, False])
@pytest.mark.parametrize('use_clean_caching_directory', [True])
def test_upload_custom_icon(rotkehlchen_api_server, file_upload, data_dir):
    """Test that uploading custom icon works"""
    root_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))  # noqa: E501
    filepath = root_path / 'frontend' / 'app' / 'src' / 'assets' / 'images' / 'kraken.png'
    asset_id_encoded = urllib.parse.quote(A_GNO.identifier, safe='')
    if file_upload:
        files = {'file': open(filepath, 'rb')}
        response = requests.post(
            api_url_for(
                rotkehlchen_api_server,
                'asseticonsresource',
                asset=asset_id_encoded,
            ),
            files=files,
        )
    else:
        json_data = {'file': str(filepath)}
        response = requests.put(
            api_url_for(
                rotkehlchen_api_server,
                'asseticonsresource',
                asset=asset_id_encoded,
            ), json=json_data,
        )

    result = assert_proper_response_with_result(response)
    assert result == {'identifier': A_GNO.identifier}
    uploaded_icon = data_dir / 'icons' / 'custom' / f'{asset_id_encoded}.png'
    assert uploaded_icon.is_file()
    assert filecmp.cmp(uploaded_icon, filepath)


@pytest.mark.parametrize('start_with_logged_in_user', [False])
@pytest.mark.parametrize('number_of_eth_accounts', [0])
@pytest.mark.parametrize('file_upload', [True, False])
@pytest.mark.parametrize('use_clean_caching_directory', [True])
def test_upload_custom_icon_errors(rotkehlchen_api_server, file_upload):
    """Test that common error handling for uploading custom icons"""
    root_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))  # noqa: E501
    filepath = root_path / 'frontend' / 'app' / 'src' / 'assets' / 'images' / 'kraken.png'
    asset_id_encoded = urllib.parse.quote(A_GNO.identifier, safe='')
    # Let's also try to upload a file without the csv prefix
    with TemporaryDirectory() as temp_directory:
        bad_filepath = Path(temp_directory) / 'somefile.bad'
        shutil.copyfile(filepath, bad_filepath)
        if file_upload:
            files = {'file': open(bad_filepath, 'rb')}
            response = requests.post(
                api_url_for(
                    rotkehlchen_api_server,
                    'asseticonsresource',
                    asset=asset_id_encoded,
                ),
                files=files,
            )
        else:
            json_data = {'file': str(bad_filepath)}
            response = requests.put(
                api_url_for(
                    rotkehlchen_api_server,
                    'asseticonsresource',
                    asset=asset_id_encoded,
                ), json=json_data,
            )

    assert_error_response(
        response=response,
        contained_in_msg=f'does not end in any of {",".join(ALLOWED_ICON_EXTENSIONS)}',
        status_code=HTTPStatus.BAD_REQUEST,
    )
