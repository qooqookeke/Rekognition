from datetime import datetime
from flask import request
from flask_restful import Resource
from config import Config


from io import BytesIO
import boto3
from PIL import Image, ImageDraw, ImageFont

class CompareFacesResource(Resource) :
    def post(self) :               

        source_file = request.files.get('source_file')
        target_file = request.files.get('target_file')

        if source_file is None or target_file is None :
            return {"error" : '파일을 업로드 하세요'}, 400
                
        data = self.compare_faces(source_file.read(), target_file.read())

        face_matches = data['FaceMatches']
        face_unmatches = data['UnmatchedFaces']

        for faceMatch in data['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            similarity = str(faceMatch['Similarity'])
         

        # 얼굴 비교 표시하기
        image = Image.open(target_file)
        font = ImageFont.truetype('NanumGothic', size=30)
        draw = ImageDraw.Draw(image)
        w, h = image.size
        
        if {face_matches == True}:
            name = format(similarity, ".6s") + '%'
            x0 = int(position['Left'] * w)
            y0 = int(position['Top'] * h)
            x1 = x0 + int(position['Width'] * w)
            y1 = y0 + int(position['Height'] * h)
            draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=3)
            draw.text((x0, y1), name, font=font, fill=(255, 0, 0))

        for face_unmatches in data['UnmatchedFaces']:
            x0 = int(face_unmatches['BoundingBox']['Left'] * w)
            y0 = int(face_unmatches['BoundingBox']['Top'] * h)
            x1 = x0 + int(face_unmatches['BoundingBox']['Width'] * w)
            y1 = y0 + int(face_unmatches['BoundingBox']['Height'] * h)
            draw.rectangle([x0, y0, x1, y1], outline='yellow', width=2)
            
        
        # 사진 파일 저장
        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':', '_') + '.jpg'  
        
        image.save(new_file_name)
 
        return {'result' : 'success', 
                "matchItems" : face_matches,
                "unMatchItems" : face_unmatches
                }, 200
    

    # 얼굴 비교
    def compare_faces(self, sourceFile, targetFile):

        client = boto3.client('rekognition',
                              'ap-northeast-2',
                              aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)

        imageSource = BytesIO(sourceFile)
        imageTarget = BytesIO(targetFile)

        response = client.compare_faces(SimilarityThreshold=80,
                                        SourceImage={'Bytes': imageSource.read()},
                                        TargetImage={'Bytes': imageTarget.read()})

        for faceMatch in response['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            similarity = str(faceMatch['Similarity'])
            
            print('감지된 얼굴에서 ' +
                str(position['Left']) + ' ' +
                str(position['Top']) +
                ' 위치의 얼굴이 ' + similarity + '% 유사도')

        imageSource.close()
        imageTarget.close()

        return response
    
