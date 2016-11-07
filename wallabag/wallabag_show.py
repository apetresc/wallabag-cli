"""
Show a wallabag entry
"""
import formatter
import json
import os
from bs4 import BeautifulSoup
import api
import conf
import entry


def show(entry_id):
    """
    Main function for showing an entry.
    """
    conf.load()
    try:
        request = api.api_get_entry(entry_id)
        __handle_request_error(request)
        entr = entry.Entry(json.loads(request.response))
    except api.OAuthException as ex:
        print("Error: {0}".format(ex.text))
        print()
        exit(-1)

    output = html2text(entr.content)

    __print_formatted(output)


def html2text(html):
    soup = BeautifulSoup(html, "html.parser")

    # Replace images by information-texts
    for img in soup.findAll('img'):
        replace = soup.new_tag('p')
        try:
            alt = " \"{0}\"".format(img['alt'])
        except KeyError:
            alt = ""
        replace.string = "[IMAGE{0}]".format(alt)
        img.insert_after(replace)
        img.unwrap()

    return soup.text


def __print_formatted(text):
    maxcol = os.get_terminal_size().columns
    writer = formatter.DumbWriter(maxcol=maxcol)
    writer.send_flowing_data(text)


def __handle_request_error(request):
    if request.has_error():
        if request.error == api.Error.http_forbidden or request.error == api.Error.http_not_found:
            print("Error: Invalid entry id.")
            print()
            exit(-1)
        print("Error: {0} - {1}".format(request.error_text,
                                        request.error_description))
        exit(-1)
