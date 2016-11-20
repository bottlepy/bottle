from bottle import Bottle, static_file, view

main = Bottle()

# Declare our static file path
@main.route ('/static/<filename:path>')
def static_files(filename):
	return static_file(filename, root='static')

@main.route('/')
@view('index')
def index():
    message = "Hello World"
    return dict(message=message)

if __name__ == "__main__":
    main.run(host='0.0.0.0', port=8080, reloader=True, debug=True)