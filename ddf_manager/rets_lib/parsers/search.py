try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET
from .base import Base
from ..exceptions import RETSException, MaxrowException
import logging
import re


logger = logging.getLogger('rets')

from collections import defaultdict

def etree_to_dict(t):
    t.tag = re.sub(r'{.*}','',t.tag) #IH Added
    d = {t.tag: {} if t.attrib else None}
    #print(t.tag)
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        #print (t.tag)
        d[t.tag].update((k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

class OneXSearchCursor(Base):
    """Parses Search Result Data"""

    def __init__(self):
        self.parsed_rows = 0

    def generator_xml(self,response,resource):
        response.raw.decode_content = True

        response_dic = {"ReplyCode": '-1', "ReplyText": "No Query applied or Unknown Error occuried", "Count": '0', "Data": []}
        response_dic_err = {"ReplyCode": '-1', "ReplyText": "No Query applied or Unknown Error occuried", "Count": '0', "Data": []}
        server_response_raw = etree_to_dict(ET.fromstring(response.text))
        resource_details_tag = resource + "Details"

        if server_response_raw:
            server_response = server_response_raw["RETS"]
            if "ReplyCode" and "ReplyText" in server_response.keys():
                response_dic["ReplyCode"]= server_response["ReplyCode"]
                response_dic["ReplyText"]= server_response["ReplyText"]
                if "COUNT" in server_response.keys():
                    if "Records" in server_response["COUNT"]:
                        response_dic["Count"] = server_response["COUNT"]["Records"]
                else:
                    return response_dic
                if resource in server_response["RETS-RESPONSE"].keys():
                    response_dic["Data"] =server_response["RETS-RESPONSE"][resource]
                elif resource_details_tag in server_response["RETS-RESPONSE"].keys():
                    response_dic["Data"] = server_response["RETS-RESPONSE"][resource_details_tag]
            else:
                return response_dic
        else:
            return response_dic_err

        return response_dic

    def generator(self, response):
        """
        Takes a response socket connection and iteratively parses and yields the results as python dictionaries.
        :param response: a Requests response object with stream=True
        :return:
        """
        response_dic = {"ReplyCode":'-1',"ReplyText":"No Query applied","Count":'0',"Data":[]}
        delim = '\t'  # Default to tab delimited
        columns = []
        count=0
        response.raw.decode_content = True
        from io import StringIO
        events = ET.iterparse(StringIO(response.text))

        results = []
        for event, elem in events:
            # Analyze search record data
            if "DATA" == elem.tag:
                data_dict = {column: data for column, data in zip(columns, elem.text.split(delim)) if column != ''}
                self.parsed_rows += 1  # Rows parsed with all requests
                results.append(data_dict)
            elif "COUNT" ==elem.tag: #IH
                count=elem.get("Records")
                response_dic["Count"]= count
            # Handle reply code
            elif "RETS" == elem.tag:
                reply_code = elem.get('ReplyCode')
                reply_text = elem.get('ReplyText')

                response_dic["ReplyCode"]= reply_code
                response_dic["ReplyText"]= reply_text

                if reply_code == '20201':
                    # RETS Response 20201 - No Records Found
                    # Generator should continue and return nothing
                    continue
                elif reply_code != '0':
                    return response_dic
                    #msg = "RETS Error {0!s}: {1!s}".format(reply_code, reply_text)

                    #raise RETSException(msg)

            # Analyze delimiter
            elif "DELIMITER" == elem.tag:
                val = elem.get("value")
                delim = chr(int(val))

            # Analyze columns
            elif "COLUMNS" == elem.tag:
                columns = elem.text.split(delim)

            # handle max rows
            elif "MAXROWS" == elem.tag:
                continue
                #response_dic["Data"] = results
                #return response_dic
                #logger.debug("MAXROWS Tag reached in XML")
                #logger.debug("Received {0!s} results from this search".format(self.parsed_rows))
                #raise MaxrowException(results)

            else:
                # This is a tag we don't process (like COUNT)
                continue

            elem.clear()
        response_dic["Data"]=results
        return response_dic
