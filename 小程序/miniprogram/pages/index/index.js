//index.js
const app = getApp()
const db = wx.cloud.database();
var that;
//多张图片上传
function uploadimg(data) {
  var that = this,
    i = data.i ? data.i : 0, //当前上传的哪张图片
    success = data.success ? data.success : 0, //上传成功的个数
    fail = data.fail ? data.fail : 0; //上传失败的个数
  wx.uploadFile({
    url: data.url,
    filePath: data.path[i],
    name: 'file', //这里根据自己的实际情况改
    formData: null, //这里是上传图片时一起上传的数据

    success: (resp) => {
      success++; //图片上传成功，图片上传成功的变量+1
      console.log(resp)
      // console.log(i);
    },
    fail: (res) => {
      fail++; //图片上传失败，图片上传失败的变量+1
      console.log('fail:' + i + "fail:" + fail);
    },
    complete: () => {
      // console.log(i);
      i++; //开始上传下一张
      if (i == data.path.length) { //当图片传完时，停止调用          
        console.log('执行完毕');
        console.log('成功：' + success + " 失败：" + fail);
        wx.showToast({
          title: '上传成功' + success,
          icon: 'success',
          duration: 2000
        })
      } else { //若图片还没有传完，则继续调用函数
        // console.log(i);
        data.i = i;
        data.success = success;
        data.fail = fail;
        uploadimg(data);
      }
    }
  });
}
Page({
  data: {
    imgurl: '', //模型预览的url
    modelurl: '', //模型下载链接
    filename: '131F12',
    imgs:[],
    model:[],
    f_length:[],
    flag: 0,
  },

  model_name_change(event){
    var that = this;
    console.log('model_name_change',event.currentTarget.dataset.id);
    that.data.model[event.currentTarget.dataset.id] = event.detail;
  },

  f_length_change(event) {
    var that = this;
    that.data.f_length[event.currentTarget.dataset.id] = event.detail;
  },


  // 选择图片
  chooseImg: function (e) {
    var that = this;
    var imgs = this.data.imgs;
    if (imgs.length >= 9) {
      this.setData({
        lenMore: 1
      });
      setTimeout(function () {
        that.setData({
          lenMore: 0
        });
      }, 2500);
      return false;
    }
    wx.chooseImage({
      // count: 1, // 默认9
      sizeType: ['original'], // 可以指定是原图还是压缩图，默认二者都有
      sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
      success: function (res) {
        // 返回选定照片的本地文件路径列表，tempFilePath可以作为img标签的src属性显示图片
        var tempFilePaths = res.tempFilePaths;
        var imgs = that.data.imgs;
        // console.log(tempFilePaths);
        for (var i = 0; i < tempFilePaths.length; i++) {
          if (imgs.length >= 9) {
            that.setData({
              imgs: imgs,
              // tempFilePaths: tempFilePaths
            });
            return false;
          } else {
            imgs.push(tempFilePaths[i]);
          }
        }
        // console.log(imgs);
        that.setData({
          imgs: imgs,
          flag:1,
          model:new Array(imgs.length),
          f_length: new Array(imgs.length),
        });
      }
    });
  },
  // 删除图片
  deleteImg: function (e) {
    var imgs = this.data.imgs;
    var index = e.currentTarget.dataset.index;
    imgs.splice(index, 1);
    this.setData({
      imgs: imgs
    });
  },
  // 预览图片
  previewImg: function (e) {
    //获取当前图片的下标
    var index = e.currentTarget.dataset.index;
    //所有图片
    var imgs = this.data.imgs;
    wx.previewImage({
      //当前显示图片
      current: imgs[index],
      //所有图片
      urls: imgs
    })
  },
  viewpre: function (e) {
    var that = this;
    wx.previewImage({
      urls: [that.data.imgurl]
    })
  },
  upload(e){
    var that = this;
    wx.showToast({
      icon: "loading",
      title: "正在上传"
    })
    console.log(that.data.model, that.data.f_length);
    uploadimg({
      url: app.globalData.address + 'uppic', //上传接口
      path: that.data.imgs, //图片的地址数组
    });
    that.setData({
    //   flag:0,
      imgs:[],
    })
    // wx.showToast({
    //   title: '上传成功',
    //   icon: 'success',
    //   duration: 2000
    // })

  },

  bindPickerChange(e) {
    console.log('picker发送选择改变，携带值为', e.detail.value)
    this.setData({
      index: e.detail.value
    })
  },
  clearFont() {
    this.setData({
      placeholder: ''
    })
  },

  bindRegionChange(e) {
    console.log('picker发送选择改变，携带值为', e.detail.value)
    this.setData({
      region: e.detail.value
    })
  },

  //重建
  reconstruct(e) {
    var that = this;
    that.setData({
      modelurl: '',
      imgurl: ''
    })
    var my_data = {
      id: app.globalData.openid,
      type: that.data.model,
      f_length: that.data.f_length,
      filename: that.data.filename
    };
    wx.showToast({
      icon: "loading",
      title: "请耐心等待结果"
    })
    wx.request({
      url: app.globalData.address + 'rectr', //服务器
      data: my_data,
      method: "POST",
      success: function (res) {
        console.log(res.data)
        that.setData({
          download_link: res.data
        })
      }
    })

  },
  check: function () { //从云数据库取结果
    that = this
    db.collection('test').where({
      id: app.globalData.openid
    })
      .get()
      .then(res => {
        // console.log(res);
        that.data.imgurl = res.data['0'].imgurl;
        that.data.modelurl = res.data['0'].address;

        that.setData({
          modelurl: that.data.modelurl,
          imgurl: that.data.imgurl
        })
      })
      .catch(res => {
        console.log(res);
        wx.showModal({
          title: '重建未完成',
        })
      })

  },
  rechoose(e) {
    var that = this;
    wx.request({
      url: app.globalData.address + 'clear', //接口
    })
    that.setData({
      modelurl: '',
      imgurl: '',
      flag: 0,
      imgs: [],
    });
  },
})
