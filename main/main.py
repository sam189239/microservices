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
    
    

@app.route('/api/products', methods=['GET'])
def index():
    start = time.time()
    # time.sleep(2)
    r = jsonify(Product.query.all())
    graphs['product_get_count'].inc()
    end = time.time()
    graphs['response_time_productget'].observe(end-start)
    return r

@app.route('/api/products', methods=['DELETE'])
def delete():
    db.session.query(Product).delete()
    db.session.commit()
    
    db.session.query(ProductUser).delete()
    db.session.commit()    

    return jsonify({
        'message': 'success'
    })

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
    app.run(debug=True, host='0.0.0.0')
