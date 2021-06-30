//app.js
App({
  onLaunch: function () {
    var that = this;
    if (!wx.cloud) {
      console.error('请使用 2.2.3 或以上的基础库以使用云能力')
    } else {
      wx.cloud.init({
        env: 'test-jpqyt',
        traceUser: true,
      })
      wx.cloud.callFunction({
        name: "login",
        complete: res => {
          that.globalData.openid = res.result.openid;
          console.log(that.globalData.openid)
        }
      })
    }

    this.globalData = {
      openid: null,//手机端
      // openid: '0211',//本地
      evn: 'test',
      // address:'http://127.0.0.1:8080/',//本地
      address: 'http://101.226.18.132:8000/',//服务器
    }
  }
})
