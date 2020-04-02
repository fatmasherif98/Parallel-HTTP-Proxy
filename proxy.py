# Don't forget to change this file's name before submission.
import sys
import os
import enum
import threading
import socket
from urllib.parse import urlparse


class HttpRequestInfo(object):
    """
    Represents a HTTP request information

    Since you'll need to standardize all requests you get
    as specified by the document, after you parse the
    request from the TCP packet put the information you
    get in this object.

    To send the request to the remote server, call to_http_string
    on this object, convert that string to bytes then send it in
    the socket.

    client_address_info: address of the client;
    the client of the proxy, which sent the HTTP request.

    requested_host: the requested website, the remote website
    we want to visit.

    requested_port: port of the webserver we want to visit.

    requested_path: path of the requested resource, without
    including the website name.

    NOTE: you need to implement to_http_string() for this class.
    """

    def __init__(self, client_info, method: str, requested_host: str,
                 requested_port: int,
                 requested_path: str,
                 headers: list):
        self.method = method
        self.client_address_info = client_info
        self.requested_host = requested_host
        self.requested_port = requested_port
        self.requested_path = requested_path
        # Headers will be represented as a list of lists
        # for example ["Host", "www.google.com"]
        # if you get a header as:
        # "Host: www.google.com:80"
        # convert it to ["Host", "www.google.com"] note that the
        # port is removed (because it goes into the request_port variable)
        self.headers = headers

    def to_http_string(self):

        print("*" * 50)
        output_string = ""
        output_string = self.method +" "+ self.requested_path + " HTTP/1.0\r\n"

        for ls in self.headers:
            output_string = output_string + ls[0]+ ": " + ls[1] +"\r\n"

        output_string = output_string + "\r\n"
        print("*" * 50)
        return output_string

    def to_byte_array(self, http_string):
        return bytes(http_string, "UTF-8")

    def display(self):
        print(f"Client:", self.client_address_info)
        print(f"Method:", self.method)
        print(f"Host:", self.requested_host)
        print(f"Port:", self.requested_port)
        stringified = [": ".join([k, v]) for (k, v) in self.headers]
        print("Headers:\n", "\n".join(stringified))


class HttpErrorResponse(object):
    """
    Represents a proxy-error-response.
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def to_http_string(self):
        output_string = str(self.code) +" " + self.message +"\r\n"
        return output_string

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(self.to_http_string())


class HttpRequestState(enum.Enum):
    INVALID_INPUT = 0
    NOT_SUPPORTED = 1
    GOOD = 2
    PLACEHOLDER = -1


class HttpErrorCodes(enum.Enum):

    #enum to hold error codes for HTTP/1.0

    BAD_REQUEST = 400
    NOT_IMPLEMENTED = 501



def entry_point(proxy_port_number):
    socket_client,socket_server = setup_sockets(proxy_port_number)
    cache = dict()
    threads=[]
    for i in range(30):
        t = threading.Thread(target=do_socket_logic, args=(socket_client, socket_server,cache,))
        t.start()
        threads.append(t)
    for i in threads:
        i.join()

    print("*" * 50)
    return None


def setup_sockets(proxy_port_number):
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_address = ("127.0.0.1", proxy_port_number)
    socket_client.bind(proxy_address)
    socket_client.listen(30)
    print("Starting HTTP proxy on port:", proxy_port_number)
    print("*" * 50)
    return socket_client ,socket_server


def do_socket_logic(socket_client: socket,socket_server: socket,cache: dict):

    (conn, address) = socket_client.accept()
    msg = ''
    while True:
        packet=conn.recv(500)
        if packet ==b'\r\n':
            break
        msg = msg + packet.decode('utf-8')
    print(msg)
    response = http_request_pipeline(address,msg)
    if isinstance(response,HttpErrorResponse):
        print('Error')
        packet = response.to_byte_array(response.to_http_string())
        socket_client.sendto(packet,address)
    else: #good
        url=response.requested_host+response.requested_path
        if url in cache:
            packet=cache[url]
            socket_client.sendto(packet,address)
        else:
            packet = response.to_byte_array(response.to_http_string())
            server_address=(response.requested_host,response.requested_port)

            socket_server.connect(server_address)
            socket_server.send(packet)

            (server_conn, server_address) = socket_server.accept()
            response_packet = server_conn.recv(1000000)

            cache[url]=response_packet
            socket_client.sendto(response_packet,address)
    pass

def http_request_pipeline(source_addr, http_raw_data):
    # Parse HTTP request
    print("*" * 50)

    validity = check_http_request_validity(http_raw_data)

    if validity == HttpRequestState.GOOD:
        request_info = parse_http_request(source_addr, http_raw_data)
        sanitize_http_request(request_info)
        return request_info

    elif validity == HttpRequestState.NOT_SUPPORTED:
        error_response = HttpErrorResponse(HttpErrorCodes.NOT_IMPLEMENTED, "Not Implemented")
        return error_response

    elif validity == HttpRequestState.INVALID_INPUT:
        error_response = HttpErrorResponse(HttpErrorCodes.BAD_REQUEST, "Bad Request")
        return error_response

    print("*" * 50)
    return None


def parse_relative_url(host_path):

    words = host_path.split(':')
    if len(words) == 3: #port number is given
        port = words[2].strip()
    else:
        port = 80
    host = words[1].strip()
    return host, port


def parse_absolute_url(url):
    url_split = url.split(':')
    if len(url_split) > 1 and url_split[0].lower() != "http":
        url = "http://" + url + "/"
    parsed_url = urlparse(url)
    if parsed_url.port == None:
        port = 80
    else:
        port = parsed_url.port
    host_name = parsed_url.hostname
    path = parsed_url.path
    if not host_name:
        host_name = path
    print( "Host :", host_name, "path: ", path, "Port: ", port )
    return host_name, path, port


def parse_http_request(source_addr, http_raw_data):
    header_list = []
    http_request_list = http_raw_data.split("\r\n")
    method = http_request_list[0].split()[0].strip()

    if len( http_request_list) > 1 and http_request_list[1].split(':')[0].strip().lower() == 'host':
        relative_path = True
    else:
        relative_path = False

    if relative_path:
        host, port = parse_relative_url(http_request_list[1])
        path = http_request_list[0].split()[1].strip()

    else:
        url = http_request_list[0].split()[1].strip()
        host, path, port = parse_absolute_url(url)
        if not host:
            host = path

    for i in range(1, len(http_request_list)):
        if not http_request_list[i]:
            continue
        current_list = []
        splitting = http_request_list[i].split(':')
        current_list.append(splitting[0].strip())
        current_list.append(splitting[1].strip())
        header_list.append(current_list)

    print("*" * 50)
    ret = HttpRequestInfo( source_addr, method, host, port, path, header_list)
    return ret


def validate_http_request(http_request_list):
    #checking that all 3 required sections are available

    if len(http_request_list[0].split()) != 3:
        return HttpRequestState.INVALID_INPUT

    method = http_request_list[0].split()[0]
    url = http_request_list[0].split()[1]
    http_version = http_request_list[0].split()[2]
    check_host_header = False

    #checking which form relative or absolute
    if url[0] == '/':
        check_host_header = True

    if http_version.lower() != "http/1.0":
        return HttpRequestState.INVALID_INPUT

    if check_host_header:
        host_header_line = http_request_list[1].split(':')
        if host_header_line[0].lower() != 'host':
            return HttpRequestState.INVALID_INPUT
        elif not host_header_line[1]:
            return HttpRequestState.INVALID_INPUT

    #checking headers format
    if check_host_header:
        i = 2
    else:
        i = 1

    while i < len(http_request_list) and http_request_list[i]:
        if len(http_request_list[i].split(':')) != 2:
            return HttpRequestState.INVALID_INPUT
        i = i+1
    return HttpRequestState.GOOD


def check_http_request_validity(http_raw_data) -> HttpRequestState:
    print("*" * 50)
    http_request_list = http_raw_data.split("\r\n")
    method = http_request_list[0].split()[0]
    res = HttpRequestState.GOOD
    if method == "GET" or method == "POST" or method == "HEAD" or method == "PUT":
        res = validate_http_request(http_request_list)
        if method != "GET" and res == HttpRequestState.GOOD:
            res = HttpRequestState.NOT_SUPPORTED
    else:
        res = HttpRequestState.INVALID_INPUT
    print("*" * 50)

    return res


def sanitize_http_request(request_info: HttpRequestInfo):

    if not request_info.requested_path:
        host, path, port = parse_absolute_url(request_info.requested_host)
        request_info.requested_host = host
        request_info.requested_path = path
        request_info.requested_port = port

    list_headers = request_info.headers
    if len(list_headers) > 1 and list_headers[0][0].strip() == "Host": #first list in header_list, first item in this list
        return
    host_header = ["Host", request_info.requested_host]
    request_info.headers.insert(0, host_header)

    return




#######################################
# Leave the code below as is.
#######################################


def get_arg(param_index, default=None):
    """
        Gets a command line argument by index (note: index starts from 1)
        If the argument is not supplies, it tries to use a default value.

        If a default value isn't supplied, an error message is printed
        and terminates the program.
    """
    try:
        return sys.argv[param_index]
    except IndexError as e:
        if default:
            return default
        else:
            print(e)
            print(
                f"[FATAL] The comand-line argument #[{param_index}] is missing")
            exit(-1)    # Program execution failed.


def check_file_name():
    """
    Checks if this file has a valid name for *submission*

    leave this function and as and don't use it. it's just
    to notify you if you're submitting a file with a correct
    name.
    """
    script_name = os.path.basename(__file__)
    import re
    matches = re.findall(r"(\d{4}_){,2}lab2\.py", script_name)
    if not matches:
        print(f"[WARN] File name is invalid [{script_name}]")
    else:
        print(f"[LOG] File name is correct.")


def main():
    """
    Please leave the code in this function as is.

    To add code that uses sockets, feel free to add functions
    above main and outside the classes.
    """
    print("\n\n")
    print("*" * 50)
    print(f"[LOG] Printing command line arguments [{', '.join(sys.argv)}]")
    check_file_name()
    print("*" * 50)

    # This argument is optional, defaults to 18888
    proxy_port_number = get_arg(1, 18888)
    entry_point(proxy_port_number)
    #parse_absolute_url("http://www.google.com:58/")
    #string = "http://www.google.com/"
    #o = urlparse(string)
    #print("prt ", o.port, " host ", o.hostname, "path ", o.path)
    #parse_http_request( ['127.0.0.1', '80'], string)



if __name__ == "__main__":
    main()
