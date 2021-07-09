from dataclasses import dataclass
from flask import Flask, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import requests

from producer import publish

##prometheus
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_prometheus_metrics import register_metrics
from flask import Blueprint





##prometheus
import os
from datetime import datetime
import time
import sys

from opencensus.trace.tracer import Tracer
from opencensus.trace import time_event as time_event_module
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from opencensus.trace.samplers import AlwaysOnSampler


zipkins_host=""
admin_host=""
# 1a. Setup the exporter
ze = ZipkinExporter(service_name="test_main-api-tracing",
                                host_name=zipkins_host,
                                port=9411,
                                endpoint='/api/v2/spans')
# 1b. Set the tracer to use the exporter
# 2. Configure 100% sample rate, otherwise, few traces will be sampled.
# 3. Get the global singleton Tracer object
tracer = Tracer(exporter=ze, sampler=AlwaysOnSampler())
#
# Constants
#

CONFIG = {"version": "v0.1.2", "config": "staging"}
MAIN = Blueprint("main", __name__)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:MyRootPass1@@db/main'
CORS(app)

db = SQLAlchemy(app)

@dataclass
class Product(db.Model):
    id: int
    title: str
    image: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))


@dataclass
class ProductUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    UniqueConstraint('user_id', 'product_id', name='user_product_unique')


@MAIN.route('/api/products', methods=['GET'])
def index():
    with tracer.span(name="get_products") as span:
            return jsonify(Product.query.all())

@MAIN.route('/api/products', methods=['DELETE'])
def delete():
    db.session.query(Product).delete()
    db.session.commit()
    
    db.session.query(ProductUser).delete()
    db.session.commit()    

    return jsonify({
        'message': 'success'
    })
    
@MAIN.route('/api/products/<int:id>/like', methods=['POST'])
def like(id):
    with tracer.span(name="inside_like") as span:
        with tracer.span(name="calling_admin") as span:
            req = requests.get('http://172.21.0.1:8000/api/user')
            json = req.json()
    with tracer.span(name="updating_like") as span:
        try:

            productUser = ProductUser(user_id=json['id'], product_id=id)
            db.session.add(productUser)
            db.session.commit()

            publish('product_liked', id)
        except:

            abort(400, 'You already liked this product')

        return jsonify({
        'message': 'success'
        })


##prom



#
# Main app
#



def register_blueprints(app):
    """
    Register blueprints to the app
    """
    app.register_blueprint(MAIN)


def create_app(config):
    """
    Application factory
    """
    
    register_blueprints(app)
    register_metrics(app, app_version=config["version"], app_config=config["config"])
    return app


#
# Dispatcher
#


def create_dispatcher() -> DispatcherMiddleware:
    """
    App factory for dispatcher middleware managing multiple WSGI apps
    """
    main_app = create_app(config=CONFIG)
    return DispatcherMiddleware(main_app.wsgi_app, {"/metrics": make_wsgi_app()})


#
# Run
#

if __name__ == "__main__":
    run_simple(
        "0.0.0.0",
        8001,
        create_dispatcher(),
        use_reloader=True,
        use_debugger=True,
        use_evalex=True,
    )

##prom


#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0')
#    run_simple(hostname="0.0.0.0", port=5000, application=dispatcher)
