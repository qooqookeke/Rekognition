from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from resources.CompareFacesResource import CompareFacesResource

# 로그아웃 관련된 임포트문
# from resources.user import jwt_blocklist

app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 매니저 초기화
jwt=JWTManager(app)

api = Api(app)

# 경로와 리소스를 연결한다.
api.add_resource(CompareFacesResource,'/upload')

# def handler(event, context) :
#     return serverless_wsgi.handle_request(app, event, context)

if __name__ == '__main__' :
    app.run()