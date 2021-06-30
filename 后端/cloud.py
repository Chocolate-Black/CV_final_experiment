import requests
import json

'''
实现小程序云数据库的
增 wxCloud.add_data(id,timeStamp,mood)
删 wxCloud.delete_data(id)
改 wxCloud.update_data(id,timeStamp,mood)
查 wxCloud.query_data(id)

使用:
import server
db=wxCloud(APP_ID,APP_SECRET,ENV)
db.add_data(
    id='001',
    timeStamp=[123, 456, 789],
    mood=[0, 2, 2]       
)
'''


class wxCloud:
    def __init__(self, APP_ID,APP_SECRET,ENV):

        self.WECHAT_URL='https://api.weixin.qq.com/'
        self.APP_ID=APP_ID
        self.APP_SECRET=APP_SECRET
        self.ENV=ENV
        self.token=self.get_access_token()
        self.collection=None

    def get_access_token(self):
        url='{0}cgi-bin/token?grant_type=client_credential&appid={1}&secret={2}'\
            .format(self.WECHAT_URL,self.APP_ID,self.APP_SECRET)
        response =requests.get(url)
        result=response.json()
        print(result)
        return result['access_token']

    '''
    新增数据
    '''
    def add_data(self,id,address,imgurl):
        url='{0}tcb/databaseadd?access_token={1}'.format(self.WECHAT_URL,self.token)
        query = '''
                db.collection("%s")
                .add({
                    data:{
                        id:'%s',
                        address:'%s',
                        imgurl:'%s'
                        }
                    })
                ''' % (self.collection,id, address,imgurl)
        data={
            "env":self.ENV,
            "query":query
        }
        response = requests.post(url,data=json.dumps(data))
        print('新增数据：'+response.text)

    '''
    查询数据
    '''
    def query_data(self,id):
        url='{0}tcb/databasequery?access_token={1}'.format(self.WECHAT_URL,self.token)
        query='''
        db.collection("%s").where({id:'%s'}).get()
        '''%(self.collection,id)

        data={
            "env":self.ENV,
            "query":query
        }
        response = requests.post(url,data=json.dumps(data))
        print('查询数据：'+response.text)
        result=response.json()
        return result['data']

    '''
    删除数据
    '''
    def delete_data(self,id):
        url='{0}tcb/databasedelete?access_token={1}'.format(self.WECHAT_URL,self.token)
        query = '''
                db.collection("%s").where({id:'%s'}).remove()
                ''' % (self.collection, id)

        data={
            "env":self.ENV,
            "query":query
        }
        response  = requests.post(url,data=json.dumps(data))
        print('删除数据：'+response.text)

    '''
    更新数据
    '''
    def update_data(self,id,address,imgurl):
        url = '{0}tcb/databaseupdate?access_token={1}'.format(self.WECHAT_URL, self.token)
        query='''
        db.collection("%s")
        .where({id:'%s'})
        .update({
            data:{
                address:'%s',
                imgurl:'%s'
                }
            })
        '''%(self.collection,id, address,imgurl)
        data = {
            "env": self.ENV,
            "query": query
        }
        response  = requests.post(url,data=json.dumps(data))
        print('更新数据：'+response.text)



if __name__ == '__main__':

    APP_ID = 'wxef5d34a20a297cb1'
    APP_SECRET = 'ebf23efa5a29b14a52cda982ee0c4244'
    ENV = 'test-jpqyt'

    db = wxCloud(APP_ID,APP_SECRET,ENV)
    db.collection='test'
    ID='004'
    filename='123'

    print(db.query_data(id='001'))  #先查询id是否存在，不存在返回空列表
    # if db.query_data(id=ID):
    #     print(1)
    #     db.update_data(     #存在则更新
    #         id=ID,
    #         address='http://127.0.0.1:8080/dld/'+filename
    #     )
    # else:
    #     print(0)
    #     db.add_data(        #不存在则添加
    #         id=ID,
    #         address='http://127.0.0.1:8080/dld/'+filename
    #     )
    # db.add_data(  # 不存在则添加
    #         id=ID,
    #         address='http://127.0.0.1:8080/dld/'+filename
    #     )

    # db.delete_data(id='001')    #删除
    # print('1',db.query_data(id='001'))

    # db.update_data(2,
    #                [1601731588, 1601731592, 1601731595, 1601731612],
    #                [0, 4, 1, 1])

