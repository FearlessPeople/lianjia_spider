# -*- coding: utf-8 -*-
from flask import jsonify
from flask import Blueprint, current_app

app = current_app
apis = Blueprint('apis', __name__)

@apis.route('/apis', methods=['GET'])
def get_example():
    routes = []
    for rule in app.url_map.iter_rules():
        route_info = {
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        }
        routes.append(route_info)
    return jsonify({'result': routes})
