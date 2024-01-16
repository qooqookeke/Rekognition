import json
from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from flask_restful import Resource
from config import Config
from mysql.connector import Error
from PIL import Image, ImageDraw

from datetime import datetime
from io import BytesIO
import io
import boto3

class RecognizeFacesResource(Resource) :
    def post(self) :

        source_file = request.files.get('source_file')
        target_file = request.files.get('target_file')

        if source_file is None or target_file is None :
            return {"error" : '파일을 업로드 하세요'}, 400
        
        bucket = Config.S3_BUCKET
        region = 'ap-northeast-2'

        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':', '_') + '.jpg'

        source_file.filename = "source" + new_file_name
        target_file.filename = "source" + new_file_name

        s3 = boto3.client('s3', 
                     aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                     aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
        

        try :
            s3.upload_fileobj(source_file, 
                              Config.S3_BUCKET,
                              source_file.filename,
                              ExtraArgs = {'ACL' : 'public-read',
                                           'ContentType' : 'image/jpeg'})
        except Exception as e :
            print(e)

        BoundingBoxDataList = self.detect_faces(source_file.filename, bucket, region)


        return {'result' : 'success', 
                "items" : BoundingBoxDataList}, 200
    
    # 얼굴 인식
    def detect_faces(self, photo, bucket, region):

        client = boto3.client('rekognition',
                              region,
                              aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)

        response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                   Attributes=['ALL'])

        list = []
        for items in response['FaceDetails'] :
            list.append(items['BoundingBox'])
        return list