
import sys
import time
import socket
try:
    import ussl as ssl
except:
    import ssl
import binascii
import re

"""Open an arbitrary URL
Adapted for Micropython by Alex Cowan <acowan@gmail.com>
Works in a similar way to python-requests http://docs.python-requests.org/en/latest/
"""

def getTime():
    UTC_5=5*3600
    attempts=0

    while True and attempts < 5:
        try:
            timesock=socket.socket()
        except OSError:
            if timesock:
                timesock.close()
                del timesock
            else:
                time.sleep(1)
                pass
        if timesock:
            timesock.connect(socket.getaddrinfo("time.nist.gov",13)[0][4])
            CurrentTime=timesock.recv(1024)
            if CurrentTime:
                break
            else:
                timesock.close()
                del timesock
                time.sleep(1)
                attempts += 1

    print(CurrentTime)
    #Date=re.search("\d{2}-\d{2}-\d{2}",CurrentTime).group(0)
    Date=re.search("[0-9]+-[0-9]+-[0-9]+",CurrentTime).group(0)
    Time=re.search("[0-9]+:[0-9]+:([0-9]+.[0-9]+)", CurrentTime).group(0)
    tm_year=int(Date.split("-")[0]) + 100 #should be number of years since 1900
    tm_yday=int(Date.split("-")[2]) - 1 #number of day since Jan 1 of that year
    tm_hour=int(Time.split(":")[0])
    tm_min=int(Time.split(":")[1]) + 1 #Nist time seems to be around a min behind and 15 secs
    tm_sec=int(Time.split(":")[2].split(" ")[0])
    
    print(tm_hour, tm_yday, tm_min , tm_sec)
    epoch = int((tm_min*60) + (tm_hour*3600) + (tm_yday*86400) + ((tm_year-70)*31536000) + (((tm_year-69)/4)*86400) - (((tm_year-1)/100)*86400) + (((tm_year+299)/400)*86400))
    epoch+=tm_sec
    print(epoch, time.time())
    timesock.close()
    print(epoch)
    del timesock
    return epoch

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
                print(result+"\n"+"Noah")
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
            print(s)
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
        #print(recv)
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

def post_data(sensor_id, sensor_value, gateway_id):
	#httpSAS="SharedAccessSignature sr=https%3a%2f%2feappiotsens.servicebus.windows.net%2f4c6b45a4-8b35-4a10-9080-abd9b912f409&sig=u6sP5%2fUEpVMIoUtGxkIFdHQwaMa33M54a0LGGwlP140%3d&se=4634217147&skn=ListenAccessPolicy"
    httpSAS = "SharedAccessSignature sr=https%3a%2f%2feappiotsens.servicebus.windows.net%2fdatacollectoroutbox%2fpublishers%2f4c6b45a4-8b35-4a10-9080-abd9b912f409%2fmessages&sig=6fijY7s%2bgSdiXaffEffhfUx0BWperwSxI0zGHZzNzy4%3d&se=4634217147&skn=SendAccessPolicy"
    #time_now = int(1484682032447 + time.time()*1000.0)
    time_now=getTime() * 1000
    print(time_now)
    sensor_data = '[{"id":"%s","v":[{"m":[%s],"t":%d}]}]' % (sensor_id, sensor_value, time_now)

    headers={'Authorization': httpSAS,
	        'DataCollectorId': gateway_id,
	        'PayloadType': 'Measurements',
	        'Timestamp': str(time_now),
	        'Cache-Control': 'no-cache',
	        'Content-Length': str(len(sensor_data)) }
    print(headers,sensor_data)
    return(headers,sensor_data)

def DataPost(Data):
    gateway_id="4c6b45a4-8b35-4a10-9080-abd9b912f409"
    #url='https://eappiot.sensbysigma.com/#/datacollector/%s' % (gateway_id)
    url='https://eappiotsens.servicebus.windows.net/datacollectoroutbox/publishers/%s/messages' % (gateway_id)

    sensors={"Temperature":"8b2a21e0-0159-447a-9587-cca30a7bd176"}

    sensor_inputs={"Temperature":Data}

    for Key in sensors:
        sensor_value = sensor_inputs[Key]
        sensor_name=sensors[Key]
        sensor_id=sensors[Key]
        #print(sensor_value)
        (header_data, sensor_data) = post_data(sensor_id, sensor_value, gateway_id)
        response = post(url, data=sensor_data, headers=header_data)
        print(response)
        if str(response.status_code) != "201":
            print("Error: Post Response: "+ str(response.status_code))
            sys.exit(1)
        print ("Posted %s: %s" % (sensor_name, sensor_data))
        print ("Post Response Status: " + str(response.status_code))

