import base64
import json
import os
import requests

import functions_framework


# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def subscribe(cloud_event):
    data = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode())
    print("Jira at " + data.get("baseUrl", "???") + " sent request from the issue " + data.get("issueKey", "???") + "!")
    comment_issue(data.get("baseUrl", None), data.get("issueKey", None), "Test comment from Cloud Function!")


def comment_issue(base_url, issue_key, comment):
    if(not base_url):
        return
    url = f"{base_url}/rest/api/3/issue/{issue_key}/comment"
    data = {"body": { "type": "doc", "version": 1, "content": [
        { "type": "paragraph", "content": [
            { "text": comment, "type": "text" }
        ] }
    ]}}
    response = post(url, data)
    print('*** response: %s' % (json.dumps(response)))


def create_session():
    s = requests.Session()
    user = os.environ.get('JIRA_CZK_USER', '<user_not_found>')
    key = os.environ.get('JIRA_CZK_KEY', '<key_not_found>')
    s.auth = (user, key)
    s.headers.update({'Content-Type': 'application/json'})
    s.headers.update({'Accept': 'application/json'})
    return s


def post(url, data):
    print('*** POST: %s' % (url))
    print('*** data: %s' % (json.dumps(data)))
    s = create_session()
    try:
        response = s.post(url, json.dumps(data).encode('utf-8'), verify=False)
    except ConnectionError:
        response = s.post(url, json.dumps(data).encode('utf-8'), verify=False)
    return process_response(response)


SUCCESS_STATUS_CODES = [200, 201, 204]


def process_response(response):
    ''' trying to get json from response '''
    if response.ok:
        try:
            return format_response(response)
        except Exception:
            # intentionally left blank - error handling below
            pass
    elif response.status_code == 401:
        print('!!!\n!!! Not authorized - check login data.\n!!!')
        print('!!! response\n%s' % response.content)
        return None
        sys.exit()

    ''' if above failed - try to change control characters in contentType
        and only then try to convert to json by force '''
    result = {'ok': response.ok}
    try:
        content = response.text
        # content = re.sub(ILLEGAL_CHARS, "?", response.text)
        content = json.loads(content)
    except ValueError as e:
        if str(e) == 'No JSON object could be decoded':
            ''' if above also failed - chech if in deed there is no JSON object
                - then we assume there is some error message in content '''
            result['ok'] = False
        else:
            ''' if there is some another error message - raise an error '''
            print('!!!')
            print('!!! Error while encoding content data: \'%s\'' % str(e))
            print('!!!')
            raise

    result['status_code'] = response.status_code
    result['url'] = response.url
    result['content'] = content

    ''' finally - check result object and decide what to do with it '''
    resultdump = ''
    resultdump = {'status_code': result.get('status_code')}
    if(not result['ok'] and result['status_code'] not in SUCCESS_STATUS_CODES):
        print('\n!!! --- URL: %s\n!!! --- ERROR ---\n%s\n!!! --- ---\n' % (result['url'], resultdump))
        return result
    elif(not result['ok'] and result['status_code'] not in SUCCESS_STATUS_CODES):
        print('\n!!! --- URL: %s\n!!! --- ERROR ---\n%s\n!!! --- ---\n' % (result['url'], resultdump))
        return result
    elif 'content' in result:
        return result['content']
    else:
        return result


def format_response(response):
    # r = json.loads(json.dumps( response.json() ))
    r = response.json()
    # r = clean_empty(r)
    return r
