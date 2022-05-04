from flask import Flask
from flask import jsonify
import requests
from flask_cors import CORS
import logging
from logging.handlers import SMTPHandler

app = Flask(__name__)

# logging setup
logger = logging.getLogger('frs')
logger.setLevel(logging.DEBUG)

log_format = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

mail_handler = SMTPHandler(
    mailhost='127.0.0.1',
    fromaddr='janskibf@gmail.com',
    toaddrs=['aaron_paetznick@fin-rec.com'],
    subject='Application Error'
)
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(log_format)

file_handler = logging.FileHandler('frs_takehome.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)

logger.addHandler(file_handler)

if not app.debug:
    logger.addHandler(mail_handler)
# end logging setup

CORS(app)

@app.route('/api/<what>/<query>', methods=['GET'])
def frs(what:str, query:str):
    """
    Returns a gender for a name, or place name for a zip code
    :param what: type of query ('place' or 'gender')
    :param query: zip or name to query
    :return: result json
    """
    try:
        # test name for gender
        if what == "gender":
            res = requests.get('https://api.genderize.io?name={}'.format(query)).json()
            value = res['gender']
        # test zip for place
        elif what == "place":
            res = requests.get('http://api.zippopotam.us/us/{}'.format(query)).json()
            value = res['places'][0]['place_name']
        else:
            logger.warning('bad %s', what)
            return {"usage": "/gender/<name> OR /place/<zip>"}, 400
        logger.info('success: %s %s', what, query)
        return {query: value}
    # value not returned from API
    except KeyError as e:
        logger.warning('not found %s %s', what, query)
        return {query: "not found"}, 404
    # application error
    except BaseException as e:
        logger.error('fail %s %s... %s', what, query, e)
        return {query: "application error"}, 500


if __name__ == '__main__':
    app.run()
