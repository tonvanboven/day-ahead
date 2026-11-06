import logging
import os
from pathlib import Path

from flask import redirect, url_for

from dao.prog.config.loader import ConfigurationLoader

from . import app

app_datapath = os.environ.get("DAO_WEB_DATA_DIR", "app/static/data").rstrip("/") + "/"


@app.route("/", methods=["GET"])
def index():
    try:
        config = ConfigurationLoader(
            Path(app_datapath + "options.json")
        ).load_and_validate()
    except (ValueError, RuntimeError) as ex:
        logging.error("Unable to load dashboard configuration: %s", ex)
        config = None

    if config is not None and config.dashboard.ui_version == "v2":
        return redirect(url_for("v2.chart"))
    return redirect(url_for("v1.menu"))


@app.route("/legacy", methods=["GET", "POST"])
def legacy():
    return redirect(url_for("v1.menu"))
