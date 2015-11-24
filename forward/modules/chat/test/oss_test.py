from oss.oss_api import *
endpoint = "oss.aliyuncs.com"
accessKeyId,accessKeySecret = "9fk40TQfvrRJwFLt", "v22JLrA9vOvdB0Vq5tXU0cgjmj82jU"
oss = OssAPI(endpoint, accessKeyId, accessKeySecret)

'''
bucket = "mmx-img"
res = oss.create_bucket(bucket, "private")
'''
bucket = "mmx-img-public"
res = oss.create_bucket(bucket, "public-read")
#res = oss.delete_bucket("mmx-img-test")

res = oss.put_object_from_file('mmx-img-public', "with_content_type.png", 
        "/usr/share/nginx/html/mmx_mt_cli/3c7aa6eac67bc7189971255b2aa9a739.png",
        content_type='image/png')

print res.status,res.read()
