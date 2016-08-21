import sys
reload(sys)
sys.setdefaultencoding('utf8')


from flask import Blueprint


main = Blueprint('main',__name__)


from . import views,errors
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)