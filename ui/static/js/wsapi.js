
function get_current_datetime() {
    var now = new Date();
    var year = now.getFullYear().toString();
    var month = now.getMonth().toString();
    var day = now.getDate().toString();
    var hour = now.getHours().toString();
    var minis = now.getMinutes().toString();
    var second = now.getSeconds().toString();
    var micros = now.getMilliseconds().toString();

    var p2 = ['', '0', ''];
    var p3 = ['', '00', '0', ''];

    //console.log(year, month, day, hour, minis, second, micros);
    var date = year + '-' + p2[month.length] + month + '-' + p2[day.length] + day + ' ';
    var time = p2[hour.length] + hour + ':' + p2[minis.length] + minis + ':' + p2[second.length] + second + '.' + p3[micros.length] + micros;
    return date + time;
}

var WsApi = function (ws_url, page_url) {
    return {
        ws: null,
        support_command_list: ['ping', 'init', 'print', 'push', 'query', 'rebase', 'debug', 'yt', 'yk', 'href'],
        support_status_list: ['ok', 'error'],

        // 请求发送后的等待队列
        my_request_list: [],
        get_my_request: function(response) {
            for ( var i = 0; i < this.my_request_list.length; i ++ ) {
                if ( this.my_request_list[i].rid !== response.rid ) {
                    continue;
                }
                return this.my_request_list.pop(this.my_request_list[i]);
            }
            return undefined;
        },

        // 请求id序列
        request_id_base: 81192,

        // 分配请求ID
        new_request_id: function() {
            if ( this.request_id_base > 99999 ) {
                this.request_id_base = 81192;
            }
            return this.request_id_base ++;
        },
        log: function() {
            var param_list = [];
            for ( var i = 0; i < arguments.length; i ++ ) {
                param_list.push(arguments[i].toString());
            }
            console.log('[' + get_current_datetime() + ']', param_list.join());
        },

        // 打开websocket通道
        open: function (url) {
            this.ws = new WebSocket('ws://' + window.location.host + '/ws/chat/xx/');
            this.ws.onmessage = this.on_message;
            this.ws.onclose = this.on_close;

            // 在onmessage和onclose函数中this对象是ws,
            // 为了能在on_message和on_close中使用WsAPi对象，需要在这里将对象本身this添加到ws对象中。
            this.ws.self = this;

            return this;
        },
        on_message: function(e) {
            var request_or_response = JSON.parse(e.data);

            if (request_or_response.status === undefined) {
                request_or_response.atsp = get_current_datetime();
                return this.self.on_ws_request(request_or_response);
            }

            var request = this.self.get_my_request(request_or_response);
            if ( request === undefined ) {
                return this.self.on_ws_crash("接收的应答包未找到对应的请求包, 应答包:" + JSON.stringify(request_or_response));
            }

            if ( request_or_response.status === 'ok' ) {
                return this.self.on_ws_response_without_error(request, request_or_response);
            } else if ( request_or_response.status === 'error' ) {
                return this.self.on_ws_response_with_error(request, request_or_response)
            } else {
                this.self.on_ws_crash("应答包状态异常，接受[ok, error], 给定:"+request_or_response.status);
            }
        },
        on_close: function(e) {
            console.log("closed.")
        },
        close: function (code) {
            this.ws.close(code);
        },

        // 制作请求包
        make_request_package: function(cmd, level, data) {
            return {
                cmd: cmd,
                rid: this.new_request_id(),
                level: level,
                data: data
            };
        },
        // 制作含错误应答包
        make_response_with_error_package: function(request, code, reason, data) {
            return {
                cmd: request.cmd,
                rid: request.rid,
                level: request.level,

                status: 'error',
                code: code,
                reason: reason,
                data: data
            };
        },
        // 制作无错误应打包
        make_response_without_error_package: function(request, data) {
            return {
                cmd: request.cmd,
                rid: request.rid,
                level: request.level,

                status: 'ok',
                code: 0,
                reason: 'no error',
                data: data
            };
        },
        // 将请求数据包发送出去
        do_request: function(request) {
            this.my_request_list.push(request);
            this.ws.send(JSON.stringify(request));

            request.success = function(callback) {this._success = callback; return this;};
            request.success(this.on_default_response_without_error);

            request.error = function(callback) {this._error = callback; return this;};
            request.error(this.on_default_response_with_error);

            request.abort = function(callback) {this._abort = callback; return this;};
            request.abort(this.on_default_abort);

            return request;
        },
        // 将答发送出去
        do_response: function(request, response) {
            response.atsp = request.atsp;
            response.btsp = get_current_datetime();
            return this.ws.send(JSON.stringify(response));
        },

        // 协议有问题
        on_ws_crash: function(reason) {
            console.error(reason);
            this.close(1000);
        },

        // 请求包
        on_ws_request: function(request) {
            if ( -1 === this.support_command_list.indexOf(request.cmd) ) {
                return this.on_ws_crash("接收到无效请求包（命令无效）包：" + JSON.stringify(request));
            }

            var response_callback = this['on_' + request.cmd + '_request'];
            response_callback = response_callback === undefined ? this.response_not_implement : response_callback;
            var response = response_callback(this, request);
            return this.do_response(request, response);
        },
        // 应答包
        on_ws_response_without_error: function(request, response) {
            request._success(this, request, response)
        },
        // 应答包
        on_ws_response_with_error: function(request, response) {
            request._error(this, request, response)
        },

        // 默认回调
        on_default_abort: function(self, request) {
            console.log("aborted", self, request);
        },
        // 默认故障回调
        on_default_response_without_error: function(self, request, response) {
            console.log("ok", self, request, response);
        },
        // 默认无故障回调
        on_default_response_with_error: function(self, request, response) {
            console.log("error", self, request, response);
        },

        // 异常应答
        // 未实现
        response_not_implement: function(self, request) {
            var reason = "command:" + request.cmd + ' not implement yet!';
            return self.make_response_with_error_package(request, 1000, reason, null);
        },
        // 协议内容
        init: function () {
        },

        // 网络、状态测试
        ping: function (data) {
            var request = this.make_request_package('ping', 5, data);
            return this.do_request(request).success(function (self, request, response) {
            }).error(function (self, request, response) {
            });
        },
        on_ping_request: function(self, request) {
            return self.make_response_without_error_package(request, request.data)
        },

        // 调试输出
        print: function (data) {
            var request = this.make_request_package('print', 99, data);
            return this.do_request(request);
        },
        on_print_request: function(self, request) {
            self.log(request.data);
            return self.make_response_without_error_package(request, null)
        },

        // 数据推送
        push: function (data) {
            var request = this.make_request_package('push', 7, data);
            return this.do_request(request);
        },
        on_push_request: function(self, request) {
            return self.make_response_without_error_package(request, 'copy');
        },

        // 数据查询
        query: function (data) {
            var request = this.make_request_package('query', 8, data);
            return this.do_request(request);
        },

        // 时间校准
        rebase: function (data) {
            var request = this.make_request_package('rebase', 6, data);
            return this.do_request(request);
        },
        on_rebase_request: function(self, request) {
            document.querySelector('#id_date_time').innerHTML = request.data;
            return self.make_response_without_error_package(request, get_current_datetime());
        },

        // 调试数据包
        debug: function (data) {
            var request = this.make_request_package('debug', 0, data);
            return this.do_request(request);
        },

        // 遥调
        yt: function (data) {
            var request = this.make_request_package('yt', 7, data);
            return this.do_request(request);
        },
        // 遥控
        yk: function (data) {
            var request = this.make_request_package('yk', 7, data);
            return this.do_request(request);
        },

        // 跳转
        on_href_request: function (self, request) {
            return self.make_response_without_error_package(request, null);
        }
    }.open(ws_url);
};
