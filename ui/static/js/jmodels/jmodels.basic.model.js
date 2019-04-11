/**
 * 模型对象
 * */
let JModel = function (id, painter, name, x_offset, y_offset, width, height, style) {
    this.id = id;

    this.painter = painter;
    this.x_offset = x_offset;
    this.y_offset = y_offset;
    this.x = Math.round(this.x_offset - width/2);
    this.y = Math.round(this.y_offset - height/2);
    this.width = width;
    this.height = height;
    this.name = name;

    if ( style === undefined ) style = {};
    this.style = style;
    if ( this.style.showed === undefined )
        this.style.showed = true;

    if ( this.style.row === undefined )
        this.style.row = 0;

    if ( this.style.column === undefined )
        this.style.column = 0;

    if ( this.style.show_boarder === undefined )
        this.style.show_boarder = true;

    // 模型上绑定的图片列表，可以通过image_switch函数切换
    this.images_list = {};

    if ( this.style.library ) {
        this.library = this.painter.search_image_library(this.style.library);
    } else {
        this.library = this.painter.search_image_library_by_name("Jmodel");
    }

    // 所有的锚点都需要注册在这里
    this.anchors = {};

    // 绑定的事件函数
    // 尺寸变化回调
    this._onresize = undefined;
    this.onresize = function (callback) {this._onresize = callback;};

    // 位置变化回调
    this._onrelocation = undefined;
    this.onrelocation = function (callback) {this._onrelocation = callback;};

    // 光标悬停回调
    this._onhover = undefined;
    this.onhover = function (callback) {this._onhover = callback;};

    // 光标进入回调
    this._onmousein = undefined;
    this.onmousein = function (callback) {this._onmousein = callback;};

    // 光标退出回调
    this._onmouseout = undefined;
    this.onmouseout = function (callback) {this._onmouseout = callback;};

    // 左键单击回调
    this._onclick = undefined;
    this.onclick = function (callback) {this._onclick = callback;};

    // 左键双击回调
    this._ondbclick = undefined;
    this.ondbclick = function (callback) {this._ondbclick = callback;};

    return this;
};

/**
 * 渲染函数
 * */
JModel.prototype.render = function (ctx) {
    // 控制外框显示
    if ( this.style.show_boarder ) {
        ctx.strokeRect(this.x, this.y, this.width, this.height);
    }

    if ( this.library && this.library.image.complete ) {
        ctx.save();
        // 将坐标转移到中心点上
        ctx.translate(this.x_offset, this.y_offset);

        if ( this.style && this.style.degree ) {
            // 旋转指定角度
            ctx.rotate(Math.PI * 2 * this.style.degree / 360);
        }

        let h_scale = 1,v_scale = 1;
        if ( this.style && this.style.h_scale ) {
            h_scale = this.style.h_scale;
        }
        if ( this.style && this.style.v_scale ) {
            v_scale = this.style.v_scale;
        }
        if ( h_scale + v_scale < 2 ) {
            ctx.scale(h_scale, v_scale);
        }

        let sy = this.style.row * this.library.unit_height;
        let sx = this.style.column * this.library.unit_width;

        ctx.drawImage(this.library.image, sx, sy, this.library.unit_width, this.library.unit_height, -this.width/2, -this.height/2, this.width, this.height);

        ctx.restore();
    }
};

/**
 * 生成保存锚点对象
 * */
JModel.prototype.save = function () {
    return {
        id: this.id,
        name: this.name,
        painter: this.painter.id,
        x_offset: Math.round(this.x_offset),
        y_offset: Math.round(this.y_offset),
        width: Math.round(this.width),
        height: Math.round(this.height),
        style: this.style
    }
};

/**
 * 显示模型
 * */
JModel.prototype.hide = function () {
    this.style.showed = false;
};
JModel.prototype.hidden = JModel.prototype.hide;

JModel.prototype.show = function () {
    this.style.showed = true;
};

JModel.prototype.toggle = function () {
    this.style.showed = this.style.showed === false;
};

JModel.prototype.blink = function (hz) {
};