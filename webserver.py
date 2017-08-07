from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def send_response_header(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response_header()
                output = ""
                output += "<html><body>"
                output += "<h1>Hello!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response_header()
                output = ""
                output += "<html><body>"
                output += "<h1>&#161 Hola !</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/hola'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                self.send_response_header()
                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>Make a New Restaurant Here</a>"
                output += "</br></br>"
                for restaurant in session.query(Restaurant).all():
                    output += "<p>"
                    output += restaurant.name
                    output += "</br>"
                    output += "<a href='/restaurants/%s/edit'>Edit</a>" % restaurant.id
                    output += "</br>"
                    output += "<a href='/restaurants/%s/delete'>Delete</a>" % restaurant.id
                    output += "</br>"
                    output += "</p>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response_header()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
                                <input name="newRestaurantName" placeholder="New Restaurant Name" type="text" >
                                <input type="submit" value="Create"> 
                            </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                self.send_response_header()
                output = ""
                output += "<html><body>"
                output += session.query(Restaurant).filter_by(id=restaurantIDPath).one().name
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" %restaurantIDPath
                output += ''' <input name="RestaurantRename" placeholder="%s" type="text" >
                                <input type="submit" value="Rename"> 
                            </form>''' % session.query(Restaurant).filter_by(id=restaurantIDPath).one().name
                output += "</body></html>"
                self.wfile.write(output)

            if self.path.endswith("delete"):
                restaurantIDPath = self.path.split("/")[2]
                self.send_response_header()
                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete %s?" % session.query(Restaurant).filter_by(id=restaurantIDPath).one().name
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % restaurantIDPath
                output += "<input type='submit' value='Delete'>"
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output)


        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                    newRestaurant = Restaurant(name = messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            elif self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('RestaurantRename')
                    restaurantIDPath = self.path.split("/")[2]
                    renamedRestaurant = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                    renamedRestaurant.name = messagecontent[0]
                    session.add(renamedRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            elif self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    restaurantIDPath = self.path.split("/")[2]
                    deletedRestaurant = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                    session.delete(deletedRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            else:
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')
                    output = ""
                    output += "<html><body>"
                    output += " <h2> Okay, how about this: </h2>"
                    output += "<h1> %s </h1>" % messagecontent[0]
                    output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                    output += "</body></html>"
                    self.wfile.write(output)
                    print output
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()