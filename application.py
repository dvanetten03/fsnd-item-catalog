from flask import Flask
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

@app.route('/')
@app.route('/hardware')
def showHardware():
	return "This page will show all network hardware"

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)