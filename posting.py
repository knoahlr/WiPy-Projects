
import sys
import time
import socket
try:
    import ussl as ssl
except:
    import ssl
import binascii
import re
import gc

"""Open an arbitrary URL
Adapted for Micropython by Alex Cowan <acowan@gmail.com>
Works in a similar way to python-requests http://docs.python-requests.org/en/latest/
"""


def urlparse(url):
    scheme = url.split('://')[0].lower()
    url = url.split('://')[1]
    host = url.split('/')[0]
    path = '/'
    data = ""
    port = 80
    if scheme == 'https':
        port = 443
    if host != url:
        path = '/'+''.join(url.split('/',1)[1:])
        if path.count('?'):
            if path.count('?') > 1:
                raise Exception('URL malformed, too many ?')
            [path, data] = path.split('?')
    if host.count(':'):
        [host, port] = host.split(':')
    if path[0] != '/':
        path = '/'+path
    return [scheme, host, port, path, data]

def get(url, params={}, **kwargs):
    return urlopen(url, "GET", params = params, **kwargs)

def post(url, data={}, **kwargs):
    return urlopen(url, "POST", data = data, **kwargs)

def put(url, data={}, **kwargs):
    return urlopen(url, "PUT", data = data, **kwargs)

def delete(url, **kwargs):
    return urlopen(url, "DELETE", **kwargs)

def head(url, **kwargs):
    return urlopen(url, "HEAD", **kwargs)

def options(url, **kwargs):
    return urlopen(url, "OPTIONS", **kwargs)

def urlopen(url, method, params = {}, data = {}, headers = {}, cookies = {}, auth = (), timeout = 5, **kwargs):
    orig_url = url
    attempts = 0
    result = URLOpener(url, method, params, data, headers, cookies, auth, timeout)
    print(result.status_code)
    ## Maximum of 4 redirects
    while attempts < 4:
        attempts += 1
        if result.status_code in (301, 302):
            url = result.headers.get('Location', '')
            if not url.count('://'):
                [scheme, host, port, path, data] = urlparse(orig_url)
                url = '%s://%s%s' % (scheme, host, url)
            if url:
                result = URLOpener(url)
            else:
                raise Exception('URL returned a redirect but one was not found')
        else:
            return result
    return result

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')

def quote(s):
    res = []
    replacements = {}
    for c in s:
        if c in always_safe:
            res.append(c)
            continue
        res.append('%%%x' % ord(c))
    return ''.join(res)

def quote_plus(s):
    if ' ' in s:
        s = s.replace(' ', '+')
    return quote(s)

def unquote(s):
    """Kindly rewritten by Damien from Micropython"""
    """No longer uses caching because of memory limitations"""
    res = s.split('%')
    for i in xrange(1, len(res)):
        item = res[i]
        try:
            res[i] = chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            res[i] = '%' + item
    return "".join(res)

def unquote_plus(s):
    """unquote('%7e/abc+def') -> '~/abc def'"""
    s = s.replace('+', ' ')
    return unquote(s)

def urlencode(query):
    if isinstance(query, dict):
        query = query.items()
    l = []
    for k, v in query:
        if not isinstance(v, list):
            v = [v]
        for value in v:
            k = quote_plus(str(k))
            v = quote_plus(str(value))
            l.append(k + '=' + v)
    return '&'.join(l)

def b64encode(s, altchars=None):
    """Reproduced from micropython base64"""
    if not isinstance(s, (bytes, bytearray)):
        raise TypeError("expected bytes, not %s" % s.__class__.__name__)
    # Strip off the trailing newline
    encoded = binascii.b2a_base64(s)[:-1]
    if altchars is not None:
        if not isinstance(altchars, bytes_types):
            raise TypeError("expected bytes, not %s"
                            % altchars.__class__.__name__)
        assert len(altchars) == 2, repr(altchars)
        return encoded.translate(bytes.maketrans(b'+/', altchars))
    return encoded
	
class URLOpener:
    def __init__ (self, url, method, params={}, data={}, headers = {}, cookies = {}, auth = (), timeout = 5):
        self.status_code = 0
        self.headers = {}
        self.text = ""
        self.url = url
        [scheme, host, port, path, query_string] = urlparse(self.url)
        #print([scheme, host, port, path, query_string])
        if auth and isinstance(auth, tuple) and len(auth) == 2:
            headers['Authorization'] = 'Basic %s' % (b64encode('%s:%s' % (auth[0], auth[1])))
        if scheme == 'http':
            addr = socket.getaddrinfo(host, int(port))[0][-1]
            s = socket.socket()
            s.settimeout(5)
            s.connect(addr)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            s = ssl.wrap_socket(sock)
            # s=sock
            try:
                s.connect(socket.getaddrinfo(host, port)[0][-1])
            except OSError:
                print(socket.getaddrinfo(host, port)[0][-1])
        if params:
            enc_params = urlencode(params)
            path = path + '?' + enc_params.strip()
        header_string = 'Host: %s\r\n' % host
        if headers:
            for k, v in headers.items():
                header_string += '%s: %s\r\n' % (k, v)
        if cookies:
            for k, v in cookies.items():
                header_string += 'Cookie: %s=%s\r\n' % (k, quote_plus(v))
        request = '%s %s HTTP/1.0\r\n%s' % (method, path, header_string)
        if data:
            if isinstance(data, dict):
                enc_data = urlencode(data)
                if not headers.get('Content-Type'):
                    request += 'Content-Type: application/x-www-form-urlencoded\r\n'
                request += 'Content-Length: %s\r\n\r\n%s\r\n' % (len(enc_data), enc_data)
            else:
                request += 'Content-Length: %s\r\n\r\n%s\r\n' % (len(data), data)
        request += '\r\n'
        s.send(request.encode())
        while 1:
            recv = s.recv(1024)
            print(recv)
            if len(recv) == 0: break
            self.text += recv.decode()
        s.close()
        self._parse_result()

    def read(self):
        return self.text

    def _parse_result(self):
        self.text = self.text.split('\r\n')
        while self.text:
            line = self.text.pop(0).strip()
            if line == '':
                break
            if line[0:4] == 'HTTP':
                data = line.split(' ')
                self.status_code = int(data[1])
                continue
            if len(line.split(':')) >= 2:
                data = line.split(':')
                self.headers[data[0]] = (':'.join(data[1:])).strip()
                continue
        self.text = '\r\n'.join(self.text)
        return

    #Contact GitHub API Training Shop Blog About 

###################################################################################################
##                                        Post Function                                          ##
###################################################################################################

def post_data(sensor_id, sensor_value, gateway_id, httpSAS):

	#httpSAS="SharedAccessSignature sr=https%3a%2f%2feappiotsens.servicebus.windows.net%2f4c6b45a4-8b35-4a10-9080-abd9b912f409&sig=u6sP5%2fUEpVMIoUtGxkIFdHQwaMa33M54a0LGGwlP140%3d&se=4634217147&skn=ListenAccessPolicy"
    #time_now = int(1484682032447 + time.time()*1000.0)
    time_now=time.time() * 1000
    print(time_now)
    sensor_data = '[{"id":"%s","v":[{"m":[%s],"t":%d}]}]' % (sensor_id, sensor_value, time_now)

    headers={'Authorization': httpSAS,
	        'DataCollectorId': gateway_id,
	        'PayloadType': 'Measurements',
	        'Timestamp': str(time_now),
	        'Cache-Control': 'no-cache',
	        'Content-Length': str(len(sensor_data)) }
    #print(headers,sensor_data)
    return(headers,sensor_data)

def DataPost(SensorInfo, httpSAS, gateway_id):
    #url='https://eappiot.sensbysigma.com/#/datacollector/%s' % (gateway_id)
    url='https://eappiotsens.servicebus.windows.net/datacollectoroutbox/publishers/%s/messages' % (gateway_id)

    SensorTypes={"Temperature":"da4a54fe-3d80-4542-a592-42aa89c97fd3", "Distance":"43abb163-44e2-40c9-81e0-9ac4cfa8ccc7"}

    for Sensors in SensorInfo:
        Sensor_Value = Sensors[1]
        Sensor_Name=Sensors[0]
        print(Sensors[0],Sensors[1])
        Sensor_Id=SensorTypes[Sensor_Name]
        #print(sensor_value)
        (Header_Data, Sensor_Data) = post_data(Sensor_Id, Sensor_Value, gateway_id, httpSAS)
        response = post(url, data=Sensor_Data, headers=Header_Data)
        #print(response)
        if str(response.status_code) != "201":
            print("Error: Post Response: "+ str(response.status_code))
            sys.exit(1)
        print ("Posted %s: %s" % (Sensor_Name, Sensor_Data))
        print ("Post Response Status: " + str(response.status_code))

