from dataclasses import dataclass
from flask import Flask, jsonify, abort
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import requests
import flask

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

#OpenCensus
from opencensus.trace.tracer import Tracer
from opencensus.trace import time_event as time_event_module
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace import config_integration
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.attributes_helper import COMMON_ATTRIBUTES
#from opencensus.trace.samplers import always_off
from opencensus.trace import (
    attributes_helper,
    execution_context,
    print_exporter,
    samplers,
)
########################################################################################
zipkins_host=""
admin_host=""
# Manual Instrumentation Initialization
ze = ZipkinExporter(service_name="test_main-api-tracing_manual_instrumentation",
                                host_name=zipkins_host,
                                port=9411,
                                endpoint='/api/v2/spans')
# 1b. Set the tracer to use the exporter
# 2. Configure 100% sample rate, otherwise, few traces will be sampled.
# 3. Get the global singleton Tracer object
#tracer = Tracer(exporter=ze, sampler=AlwaysOnSampler())
#



########################################################################################################
CONFIG = {"version": "v0.1.2", "config": "staging"}
MAIN = Blueprint("main", __name__)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:MyRootPass1@@db/main'
CORS(app)

#Automatic Instumentation
#Integrations for SQLalchemy and Requests
INTEGRATIONS = ['mysql', 'sqlalchemy', 'requests']
#
middleware = FlaskMiddleware(app, exporter = ZipkinExporter(service_name="test_main-api-tracing-automatic-instrumentation",host_name=zipkins_host, port=9411, endpoint='/api/v2/spans'),  sampler=AlwaysOnSampler(),)
config_integration.trace_integrations(INTEGRATIONS)
#opencenesus Manual attribute helpers
HTTP_HOST = attributes_helper.COMMON_ATTRIBUTES['HTTP_HOST']
HTTP_METHOD = attributes_helper.COMMON_ATTRIBUTES['HTTP_METHOD']
HTTP_PATH = attributes_helper.COMMON_ATTRIBUTES['HTTP_PATH']
HTTP_ROUTE = attributes_helper.COMMON_ATTRIBUTES['HTTP_ROUTE']
HTTP_URL = attributes_helper.COMMON_ATTRIBUTES['HTTP_URL']
HTTP_STATUS_CODE = attributes_helper.COMMON_ATTRIBUTES['HTTP_STATUS_CODE']

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
    #COmment the following line for auto_instrumentation
    tracer = Tracer(exporter=ze, sampler=AlwaysOnSampler())
    with tracer.span(name="get_products") as span:
        tracer.add_attribute_to_current_span(HTTP_HOST, flask.request.host)
        tracer.add_attribute_to_current_span(HTTP_METHOD, flask.request.method)
        tracer.add_attribute_to_current_span(HTTP_PATH, flask.request.path)
        tracer.add_attribute_to_current_span(HTTP_URL, str(flask.request.url))
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
    #COmment the following line for auto_instrumentation
    tracer = Tracer(exporter=ze, sampler=AlwaysOnSampler())
    with tracer.span(name="inside_like") as span:
        tracer.add_attribute_to_current_span(HTTP_HOST, flask.request.host)
        tracer.add_attribute_to_current_span(HTTP_METHOD, flask.request.method)
        tracer.add_attribute_to_current_span(HTTP_PATH, flask.request.path)
        tracer.add_attribute_to_current_span(HTTP_URL, str(flask.request.url))
        with tracer.span(name="calling_admin_for_user") as span:
            req = requests.get('http://'+admin_host+'/api/user')
            json = req.json()
        with tracer.span(name="updating_like") as span:
            try:
                with tracer.span(name="search_product_user_db") as span:
                    productUser = ProductUser(user_id=json['id'], product_id=id)
                    
                    with tracer.span(name="db_add_productuser") as span:
                        db.session.add(productUser)
                        
                        with tracer.span(name="db_add_product_user_commit") as span:
                            db.session.commit()

                with tracer.span(name="publish_like") as span:
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
