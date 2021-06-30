
from flask import Flask, jsonify, abort#, 
from flask import request as flask_req
from flask.helpers import stream_with_context
from flask.wrappers import Response
from werkzeug.wrappers import request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import UniqueConstraint
from dataclasses import dataclass
import requests
from producer import publish

from prometheus_flask_exporter import PrometheusMetrics
import prometheus_client
from prometheus_client.core import CollectorRegistry
from prometheus_client import Summary, Counter, Histogram, Gauge
import time

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:MyRootPass1@@db/main'
CORS(app)
# metrics = PrometheusMetrics(app)
# metrics.info('app_info', 'Application info', version='1.0.3')
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




# @app.route('/')
# def main():
#     pass  # requests tracked by default

# @app.route('/skip')
# @metrics.do_not_track()
# def skip():
#     pass  # default metrics are not collected

# @app.route('/<item_type>')
# @metrics.do_not_track()
# @metrics.counter('invocation_by_type', 'Number of invocations by type',
#          labels={'item_type': lambda: flask_req.view_args['type']})
# def by_type(item_type):
#     pass  # only the counter is collected, not the default metrics

# @app.route('/long-running')
# @metrics.gauge('in_progress', 'Long running requests in progress')
# def long_running():
#     pass

# @app.route('/status/<int:status>')
# @metrics.do_not_track()
# @metrics.summary('requests_by_status', 'Request latencies by status',
#                  labels={'status': lambda r: r.status_code})
# @metrics.histogram('requests_by_status_and_path', 'Request latencies by status and path',
#                    labels={'status': lambda r: r.status_code, 'path': lambda: flask_req.path})
# def echo_status(status):
#     return 'Status: %s' % status, status



# by_path_counter = metrics.counter(
#     'by_path_counter', 'Request count by request paths',
#     labels={'path': lambda: flask_req.path}
# )

# @app.route('/simple')
# @by_path_counter
# def simple_get():
#     pass
    
# @app.route('/plain')
# @by_path_counter
# def plain():
#     pass
    
# @app.route('/not/tracked/by/path')
# def not_tracked_by_path():
#     pass


# PrometheusMetrics(app, group_by='path')         # the default
# PrometheusMetrics(app, group_by='endpoint')     # by endpoint
# PrometheusMetrics(app, group_by='url_rule')     # by URL rule

# def custom_rule(req):  # the Flask request object
#     """ The name of the function becomes the label name. """
#     return '%s::%s' % (req.method, req.path)

# PrometheusMetrics(app, group_by=custom_rule)    # by a function



_INF = float("inf")
graphs = {}
graphs['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
graphs['h'] = Histogram('python_request_duration_seconds', 'Histogram for the duration in seconds.', buckets=(1,2,5,6,10,_INF))
graphs['like_count'] = Counter('like_count', 'The number of likes')
graphs['response_time_productget'] = Histogram('product_get_response', 'Histogram for the duration in seconds.', buckets=(1,2,5,6,10,_INF))
graphs['response_time_likes'] = Histogram('like_response', 'Histogram for the duration in seconds.', buckets=(1,2,5,6,10,_INF))
graphs['product_get_count'] = Counter('product_get_count', 'The number of get requests for Products')

@app.route('/')
def hello():
    start = time.time()
    graphs['c'].inc()
    time.sleep(0.600)
    end=time.time()
    graphs['h'].observe(end-start)
    return "Hello!"

@app.route("/metrics")
def requests_count():
    res = []
    for k,v in graphs.items():
        res.append(prometheus_client.generate_latest(v))
    return Response(res, mimetype="text/plain")


@app.route('/api/products')
def index():
    start = time.time()
    # time.sleep(2)
    r = jsonify(Product.query.all())
    graphs['product_get_count'].inc()
    end = time.time()
    graphs['response_time_productget'].observe(end-start)
    return r


@app.route('/api/products/<int:id>/like', methods=['POST'])
def like(id):
    start = time.time()
    graphs['like_count'].inc()
    req=requests.get('http://172.18.0.1:8000/api/user')
    json = req.json()

    try:
        productUser = ProductUser(user_id=json['id'], product_id=id)
        db.session.add(productUser)
        db.session.commit()

        publish('product_liked',id)
    except:
        abort(400, 'You already liked this product')
    
    end = time.time()
    graphs['response_time_likes'].observe(end-start)
    return jsonify({
        'message': 'success',
        'id': json['id']
    })



if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')













# from dataclasses import dataclass
# from flask import Flask, jsonify, abort
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import UniqueConstraint
# import requests

# from producer import publish

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:MyRootPass1@@db/main'
# CORS(app)

# db = SQLAlchemy(app)


# @dataclass
# class Product(db.Model):
#     id: int
#     title: str
#     image: str

#     id = db.Column(db.Integer, primary_key=True, autoincrement=False)
#     title = db.Column(db.String(200))
#     image = db.Column(db.String(200))


# @dataclass
# class ProductUser(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer)
#     product_id = db.Column(db.Integer)

#     UniqueConstraint('user_id', 'product_id', name='user_product_unique')


# @app.route('/api/products')
# def index():
#     return jsonify(Product.query.all())


# @app.route('/api/products/<int:id>/like', methods=['POST'])
# def like(id):
#     req = requests.get('http://18.220.178.130:8000/api/user')
#     json = req.json()

#     try:
#         productUser = ProductUser(user_id=json['id'], product_id=id)
#         db.session.add(productUser)
#         db.session.commit()

#         publish('product_liked', id)
#     except:
#         abort(400, 'You already liked this product')

#     return jsonify({
#         'message': 'success'
#     })


# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')
