# Don't forget to change this file's name before submission.
import sys
import os
import enum
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
        """
        Convert the HTTP request/response
        to a valid HTTP string.
        As the protocol specifies:

        [request_line]\r\n
        [header]\r\n
        [headers..]\r\n
        \r\n

        (just join the already existing fields by \r\n)

        You still need to convert this string
        to byte array before sending it to the socket,
        keeping it as a string in this stage is to ease
        debugging and testing.
        """

        print("*" * 50)
        output_string = ""
        output_string = self.method +" "+ self.requested_path + " HTTP/1.0\r\n"
        for ls in self.headers:
            if ls[0] == "Host" and self.requested_port != 80:
                ls[1] = ls[1] + ":" + str(self.requested_port)
            output_string = output_string + ls[0]+ ": " + ls[1] +"\r\n"
        output_string = output_string + "\r\n"
        print("*" * 50)
        return output_string

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
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
        """ Same as above """
        pass

    def to_byte_array(self, http_string):
        """
        Converts an HTTP string to a byte array.
        """
        return bytes(http_string, "UTF-8")

    def display(self):
        print(self.to_http_string())


class HttpRequestState(enum.Enum):
    """
    The values here have nothing to do with
    response values i.e. 400, 502, ..etc.

    Leave this as is, feel free to add yours.
    """
    INVALID_INPUT = 0
    NOT_SUPPORTED = 1
    GOOD = 2
    PLACEHOLDER = -1


def entry_point(proxy_port_number):
    """
    Entry point, start your code here.

    Please don't delete this function,
    but feel free to modify the code
    inside it.
    """

    setup_sockets(proxy_port_number)
    print("*" * 50)
    print("[entry_point] Implement me!")
    print("*" * 50)
    return None


def setup_sockets(proxy_port_number):
    """
    Socket logic MUST NOT be written in the any
    class. Classes know nothing about the sockets.

    But feel free to add your own classes/functions.

    Feel free to delete this function.
    """
    print("Starting HTTP proxy on port:", proxy_port_number)

    # when calling socket.listen() pass a number
    # that's larger than 10 to avoid rejecting
    # connections automatically.
    print("*" * 50)
    print("[setup_sockets] Implement me!")
    print("*" * 50)
    return None


def do_socket_logic():
    """
    Example function for some helper logic, in case you
    want to be tidy and avoid stuffing the main function.

    Feel free to delete this function.
    """
    pass


def http_request_pipeline(source_addr, http_raw_data):
    """
    HTTP request processing pipeline.

    - Validates the given HTTP request and returns
      an error if an invalid request was given.
    - Parses it
    - Returns a sanitized HttpRequestInfo

    returns:
     HttpRequestInfo if the request was parsed correctly.
     HttpErrorResponse if the request was invalid.

    Please don't remove this function, but feel
    free to change its content
    """
    # Parse HTTP request
    validity = check_http_request_validity(http_raw_data)
    # Return error if needed, then:
    # parse_http_request()
    # sanitize_http_request()
    # Validate, sanitize, return Http object.
    print("*" * 50)
    print("[http_request_pipeline] Implement me!")
    print("*" * 50)
    return None

def parse_relative_url(host_path):
    words = host_path.split(':')
    if len(words) == 3: #port number is given
        port = words[2].strip()
    else:
        port = '80'
    host = words[1].strip()
    return host, port
def parse_absolute_url(url):
    parsed_url = urlparse(url)
    if parsed_url.port == None:
        port = '80'
    else:
        port = parsed_url.port
    host_name = parsed_url.hostname
    print("host name fatma : ", host_name)
    path = parsed_url.path
    return host_name, path, port




def parse_http_request(source_addr, http_raw_data):
    """
    This function parses a "valid" HTTP request into an HttpRequestInfo
    object.
    """
    header_list = []
    http_request_list = http_raw_data.split("\r\n")
    method = http_request_list[0].split()[0].strip()


    print("fatma ", http_raw_data)
    if http_request_list[1].split(':')[0].strip() == 'Host':
        relative_path = True
        print("in the true ")
    else:
        print("in the false",http_request_list[1].strip(":").lower() )
        relative_path = False
    if relative_path:
        host, port =parse_relative_url(http_request_list[1])
        path = urlparse(http_request_list[0].split()[1].strip()).path
        #http_request_list[0].split()[1].strip()
    else:
        http_check = http_request_list[0].split()[1].split('/').strip()
        if http_check != "http:":
            url = "http://" + http_request_list[0].split()[1].strip()
        else:
            url = http_request_list[0].split()[1].strip()
        host, path, port = parse_absolute_url( url)
    print("host is ", host,"path is ",path)
    for i in range(1, len(http_request_list)):
        if not http_request_list[i]:
            continue
        current_list = []
        splitting = http_request_list[i].split(':')
        if i == 1 and relative_path:
            current_list.append(splitting[0].strip())
            current_list.append(splitting[1].strip())
        else:
            current_list.append(splitting[0].strip())
            current_list.append(splitting[1].strip())
        print("fatma list ", current_list)
        header_list.append(current_list)

    print("*" * 50)
    print("[parse_http_request] Implement me!")
    print("*" * 50)
    # Replace this line with the correct values.
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
        i=1

    while i < len(http_request_list) and http_request_list[i]:
        if len(http_request_list[i].split(':')) != 2:
            return HttpRequestState.INVALID_INPUT
        i = i+1
    return HttpRequestState.GOOD




def check_http_request_validity(http_raw_data) -> HttpRequestState:
    """
    Checks if an HTTP request is valid

    returns:
    One of values in HttpRequestState
    """
    http_request_list = http_raw_data.split("\r\n")
    method = http_request_list[0].split()[0]
    res = HttpRequestState.GOOD
    if method == "GET" or method == "POST" or method == "HEAD" or method == "PUT":
        res = validate_http_request(http_request_list)
        if method != "GET" and res == HttpRequestState.GOOD:
            res = HttpRequestState.NOT_SUPPORTED
    else:
        print("else in original fn ")
        res = HttpRequestState.INVALID_INPUT

    print("*" * 50)
    print("[check_http_request_validity] Implement me!")
    print("*" * 50)
    # return HttpRequestState.GOOD (for example)
    return res


def sanitize_http_request(request_info: HttpRequestInfo):
    """
    Puts an HTTP request on the sanitized (standard) form
    by modifying the input request_info object.

    for example, expand a full URL to relative path + Host header.

    returns:
    nothing, but modifies the input object
    """
    print("*" * 50)
    list_headers = request_info.headers
    if list_headers[0][0].strip() == "Host":
        return
    host_header = []
    host_header.append("Host")
    host_header.append(request_info.requested_host)
    request_info.headers.insert(0, host_header)

    print("*" * 50)


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
    #proxy_port_number = get_arg(1, 18888)
    #entry_point(proxy_port_number)
    string = "/things"
    o = urlparse(string)
    print("prt ", o.port, " host ", o.hostname, "path ", o.path)



if __name__ == "__main__":
    main()
