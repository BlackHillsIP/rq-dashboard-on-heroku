import os
from flask import Flask, redirect
import rq_dashboard
from rq_dashboard.cli import add_basic_auth


def setup_rq_connection(current_app):
    # we need to do It here instead of cli, since It may be embeded
    rq_dashboard.web.upgrade_config(current_app)
    # Getting Redis connection parameters for RQ
    redis_url = current_app.config.get("RQ_DASHBOARD_REDIS_URL")
    if isinstance(redis_url, rq_dashboard.web.string_types):
        current_app.config["RQ_DASHBOARD_REDIS_URL"] = (redis_url,)
        _, current_app.redis_conn = rq_dashboard.web.from_url(
            (redis_url,)[0], client_options={"ssl_cert_reqs": None}
        )
    elif isinstance(redis_url, (tuple, list)):
        _, current_app.redis_conn = rq_dashboard.web.from_url(
            redis_url[0], client_options={"ssl_cert_reqs": None}
        )
    else:
        raise RuntimeError("No Redis configuration!")


app = Flask(__name__)
app.config.from_object(rq_dashboard.default_settings)
app.config["RQ_DASHBOARD_REDIS_URL"] = os.environ.get("RQ_DASHBOARD_REDIS_URL")

setup_rq_connection(app)

add_basic_auth(
    blueprint=rq_dashboard.blueprint,
    username=os.environ.get("RQ_DASHBOARD_USERNAME"),
    password=os.environ.get("RQ_DASHBOARD_PASSWORD"),
)

app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")


@app.route("/")
def root():
    return redirect("/rq", code=302)


if __name__ == "__main__":
    app.run()
