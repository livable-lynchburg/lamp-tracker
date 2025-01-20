class Config(object):
    DEBUG = False
    TESTING = False
    FLASK_APP="run.py"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    POSTGRES_DB = "lamp-tracker_db"
    POSTGRES_URL = "localhost"
    POSTGRES_USER = "lamp-tracker"
    DEFAULT_LOCATION_EWKT = "SRID=4326;POINT(37.4011 -79.2379)"

    #Variable definitions passed from GitLab through Ansible args in .gitlab-ci.yml go after this line
    SECRET_KEY = "top-secret"
    MAPBOX_API_KEY = "so so secret"
    POSTGRES_PW = "password"
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
