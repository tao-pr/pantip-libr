"""
Terminal topic reaction prediction service

@starcolon projects
"""

from flask import Flask
from flask import request
import _v00
import json

SERVICE_NAME = "PANTIP-LIBR TERMINAL SERVICE"
app          = Flask(SERVICE_NAME)

@app.route("/")
def root():
	return SERVICE_NAME

@app.route('/topic/<version>/sentiment',methods=["POST","PUT"])
def check_topic_sentiment(version):
	topic = request.get_json(silent=True)
	if version=='00':
		return _v00.process(topic)
	else:
		return '{"error":true,"reason":"Unsupported version"}'


if __name__ == '__main__':
	app.run(debug=True,host="0.0.0.0",port=5858)