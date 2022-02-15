import atexit
import os

import beeline
from ariadne import graphql_sync, make_executable_schema
from ariadne.constants import PLAYGROUND_HTML
from beeline.middleware.flask import HoneyMiddleware
from flask import Flask, request, jsonify

from app.models import Base, engine, Post, db_session, Comment, Author, seed
from app.schema import type_defs, query

schema = make_executable_schema(type_defs, query)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
app = Flask(__name__)
HoneyMiddleware(app, db_events=True)

beeline.init(
    writekey=os.environ["HONEYCOMB_API_KEY"],
    dataset="graphql-tracing",
    service_name="sample",
)
atexit.register(beeline.close)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()

    with beeline.tracer("graphql_query"):
        beeline.add_trace_field("component", "graphql")
        success, result = graphql_sync(schema, data, context_value={}, debug=app.debug)

    status_code = 200 if success else 400
    return jsonify(result), status_code


seed()
