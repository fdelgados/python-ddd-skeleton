from flask import Flask
from flask_restx import Api

from shared.domain.errors.errors import ApplicationError
from shared.infrastructure.flask.api.basecontroller import BaseController
from shared.application.bootstrap import Bootstrap

bootstrap = Bootstrap()

app = Flask(__name__)
app.config.from_mapping(bootstrap.settings.flask_config())

bootstrap.logger.info("Bootstrapping API")
api = Api(
    app,
    doc=bootstrap.settings.api_doc_path(),
    title=bootstrap.settings.api_title(),
    version=bootstrap.settings.api_version_str(),
)


@api.errorhandler(ApplicationError)
def handle_application_error(error):
    return BaseController.api_error(error)


@api.errorhandler(Exception)
def handle_generic_error(error):
    return BaseController.api_generic_error(error)

