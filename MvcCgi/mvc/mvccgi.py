DEFAULT_ERROR = error = """<html>
    <head>
    <title>Error</title>
    <body>
        <p>Internal error - no handler for {} with method {}</p>
    </body>
    </html>"""

import json, platform
from os import path


# This is a very simple view class, allowing us to read
# a page off of the disk, and the insert parameters using
# standard python string formatting
class BaseViewer():
    def __init__(self, default):
        self.default = default

    def getDefaultPage(self, params):
        return self.getPage(self.default, params)


    # You can override this method to make sure all pages
    # have similar styling
    def getPage(self, template, params=None):
        with open(template, "rt") as f:
            result = f.read()
            if params == None:
                return result
            else:
                return result.format(**params)


# This is a very simple json based model class, allowing us
# to store arbitary data in a json file.
class BaseModel():
    # Call BaseModel with the name of a json file you'd like
    # to use as storage.  If the file doesn't exist, you must
    # provide a list of headers (columns) to use in the database.
    #
    # After that, it is no longer necessary to provide headers,
    # although you can as long as they match.  If the headers do not
    # match, an error will be thrown
    #
    # See the comments on individual functions for use
    def __init__(self, filename, headers=None):
        self.filename = filename
        self.dirty = False
        if not path.exists(filename) and headers == None:
            raise ValueError("No headers specified and database does not exists")
        elif path.exists(filename):
            self.reload()
            if headers != None and self.storage['headers'] != headers:
                raise ValueError("Provided headers do not match those in dbfile")
        else:
            self.storage = {"headers": headers, "data": [[] for x in headers]}
            self.dirty = True
            self.flush()

    # Search the database
    #   query: a dictionary that is used to find the row you want to update.
    #          Fields in the query dictionary will be matched to corresponding
    #          columns in the database.  If all fields in the query string match
    #          a row, that row will be returned.
    #
    #          Rows are returned as a list of dictionaries, with fields corresponding
    #          to the header of the database
    #
    def find(self, query=None):
        self.flush()
        result = []
        indices = []
        if query == None:
            indices = range(self.numRecords())
        else:
            indices = self.findIndices(query)

        return ([self.getAtIndex(i) for i in indices])


    # Update the database
    #   query: a dictionary that is used to find the row you want to update.
    #           All rows matching all fields in the query will be updated
    #   update: a dictionary specifying the fields you want to update
    def update(self, query, update):
        indices = self.findIndices(query)
        for i in indices:
            self.updateAtIndex(i, update)
        self.flush()
        return len(indices)

    # Add a row to the database
    #   row: a dictionary containing the data you want to add. All fields must
    #       be specified, or else an error will be thrown
    def add(self, row):
        self.checkColumns(row.keys(), False)
        headers = self.storage['headers']
        for i in range(len(headers)):
            self.storage['data'][i].append(row[headers[i]])
        self.dirty = True
        self.flush()

    # Update or add row to the database
    #   query: as with the update function, a dictionary used to find the row you want to update.
    #           All rows matching all fields in the query will be updated.  However, if no rows
    #           match, these fields will be used to create a new row
    #   update: a dictionary specifying the fields you want to update
    def updateOrAdd(self, query, update):
        if self.update(query, update) == 0:
            self.add({**query, **update})

    # Delete row(s) in the database
    #   query: A dictionary used to find the row(s) you want to delete.
    #           All rows matching all fields in the query will be deleted.
    def delete(self, query):
        for i in sorted(self.findIndices(query), reverse=True):
            self.deleteAtIndex(i)
        self.flush()

    # Delete all rows in the database.  Doesn't change the headers.
    def clear(self):
        headers = self.storage['headers']
        self.storage['data'] = [[] for x in headers]
        self.dirty = True
        self.flush()

    #  Get a the list of headers in the database
    def headers(self):
        return self.storage['headers']

    # The following functions are for more advanced usage

    def flush(self):
        if not self.dirty:
            return
        with open(self.filename, "wt+") as f:
            f.write(json.dumps(self.storage))
            self.dirty = False

    def reload(self):
        with open(self.filename, "rt") as f:
            self.storage = json.loads(f.read())

    def checkColumns(self, fields, partial=True):
        subset = set(fields).issubset(set(self.storage['headers']))
        if subset and (partial or (len(fields) == len(self.storage['headers']))):
            return True
        else:
            raise ValueError("Invalid columns: " + str(fields))

    def numRecords(self):
        return (len(self.storage['data'][0]))

    def findIndices(self, query):
        result = []
        self.checkColumns(list(query.keys()), True)
        x = self.numRecords()
        headers = self.storage['headers']
        for i in range(x):
            match = True
            for j in range(len(headers)):
                if headers[j] in query:
                    if query[headers[j]] != self.storage['data'][j][i]:
                        match = False
                        break
            if match:
                result.append(i)
        return (result)

    def getAtIndex(self, row):
        self.flush()
        return ({self.storage['headers'][i]: self.storage['data'][i][row] for i in range(len(self.storage['headers']))})


    def updateAtIndex(self, row, update):
        headers = self.storage['headers']
        for j in range(len(headers)):
            if headers[j] in update:
                self.storage['data'][j][row] = update[headers[j]]
        self.dirty = True

    def deleteAtIndex(self, row):
        for i in range(len(self.storage['headers'])):
            del self.storage['data'][i][row]
        self.dirty = True

    def reinitialize(self, headers):
        self.storage = {"headers": headers, "data": [[] for x in headers]}
        self.dirty = True
        self.flush()

# This is a very simple controller class, based loosely on the MVC pattern
# By default, this class will attempt to handle any request by looking for a
# method named [path]_[method], where [path] is the full path from the root of the
# server, and [method] is the http method used.  Slashes are replaced with underscores.
#
# For example, if the server is running on local host, and a GET request is made to:
#
#       http://localhost:8080/test/mypage.html
#
# The controller with look for a method called test_mypage_GET.  If one is not found,
# the server will look for a file on disk matching that path.  If no such file is found,
# the server will return a default error page
class BaseController():




    def __init__(self, viewer):
        self.viewer = viewer

    # Return a string for a default header.  If you want to send
    # other headers, send them before this one
    def getStandardHeader(self, type="text/html"):
        return ("Content-type:" + type)

    def sanitizeUrl(self, original):
        if original.startswith("/"):
            original = original[1:]
        if original.endswith(".html"):
            original = original[:-5]
        return original.replace("/", "_")

    def senderror(self, original, method):
        return(DEFAULT_ERROR.format(original, method))

    # This simply returns the string that will make up the body of the
    # response.  You will need to return a header followed by a newline for
    # the script to work properly
    def handle(self, params, method):
        name = self.sanitizeUrl(params['_orig_url'].value)
        name += "_" + method

        try:
            tocall = getattr(self, name)
        except AttributeError:

            try:
                return(self.viewer.getPage(params['_orig_url'].value[1:]))

            except FileNotFoundError:
                return (self.senderror(params['_orig_url'].value, method))

        return tocall(params)

    def respond(self, params, method, type="text/html"):
        result = self.handle(params,method)
        print(self.getStandardHeader(type=type))
        print()
        print(result)