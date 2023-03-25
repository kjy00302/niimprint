import requests


BASE_URL = 'https://print.niimbot.com/api'
GET_CLOUD_TEMPLATE_BY_ONE_CODE_URL = BASE_URL + '/template/getCloudTemplateByOneCode'

HEADERS = {
    'niimbot-user-agent': 'AppId/com.gengcon.jccloudprinter OS/Android AppVersionName/4.9.3 Model/Samsung S20 SystemVersion/10.0 DeviceId/456789 referer/CP001Mobile',
    'Content-Type': 'application/json',
}


def get_cloud_template_by_one_code(one_code):
    resp = requests.post(GET_CLOUD_TEMPLATE_BY_ONE_CODE_URL, headers=HEADERS)
    return resp.json()
