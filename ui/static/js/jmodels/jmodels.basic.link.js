/**
 * 连接线对象
 * @param id: 连接线ID
 * @param begin: 起点锚点
 * @param end: 终点锚点
 * @param style: 连接线风格
 * */
var JLink = function (id, begin, end, style) {
    this.id = id;
    this.begin = begin;
    this.end = end;
    this.style = style;

    this.idx_x = 0;
    return this;
};


/**
 * 生成保存锚点对象
 * */
JLink.prototype.save = function () {
    return {
        id: this.id,
        begin: this.begin.id,
        end: this.end.id,
        style: this.style
    }
};


JLink.prototype.render = function (ctx) {
    let delta_x = (this.end.x + this.end.width/2) - (this.begin.x + this.begin.width/2);
    let delta_y = (this.end.y + this.end.height/2) - (this.begin.y + this.begin.height/2);

    ctx.save();

    ctx.translate(this.begin.x + this.begin.width/2, this.begin.y + this.begin.height/2);
    ctx.moveTo(0, 0);
    ctx.setLineDash([5, 5]);

    let abs_delta_x = Math.abs(delta_x);
    let abs_delta_y = Math.abs(delta_y);

    if (abs_delta_x >= abs_delta_y && abs_delta_x > this.end.widget / 2) {
        ctx.lineTo(delta_x, 0);
    } else if (abs_delta_y > this.end.height / 2) {
        ctx.lineTo(0, delta_y);
    }

    ctx.lineTo(delta_x, delta_y);
    ctx.stroke();

    ctx.restore();

    /*
    ctx.beginPath();
    ctx.moveTo(this.begin.x + this.begin.width/2, this.begin.y + this.begin.height/2);
    ctx.lineTo(this.end.x + this.end.width/2, this.end.y + this.end.height/2);
    ctx.stroke();
    */
};


/**
 * 渲染函数
 * */
JLink.prototype.render2 = function (ctx) {
    /*
     ctx.beginPath();
     ctx.moveTo(this.begin.x + this.begin.width/2, this.begin.y + this.begin.height/2);
     ctx.lineTo(this.end.x + this.end.width/2, this.end.y + this.end.height/2);
     ctx.stroke();
     */
    ctx.save();
    var delta_x = (this.end.x + this.end.width/2) - (this.begin.x + this.begin.width/2);
    var delta_y = (this.end.y + this.end.height/2) - (this.begin.y + this.begin.height/2);

    // 首先转换坐标系到起点位置
    ctx.translate(this.begin.x + this.begin.width/2, this.begin.y + this.begin.height/2);
    // 计算目标点在默认坐标系中的弧度
    var ar = Math.atan2(delta_y, delta_x);
    ctx.rotate(ar);
    var len = Math.sqrt(delta_x * delta_x + delta_y * delta_y);
    //console.log("delta x:", delta_x, "delta y:", delta_y, "degree:", ar, "len:", len);

    // 创建固定绘制区域, 使有效绘制区域限制在固定范围内
    ctx.beginPath();
    ctx.lineTo(0, 5);
    ctx.lineTo(len, 5);
    ctx.lineTo(len, -5);
    ctx.lineTo(0, -5);
    ctx.closePath();
    ctx.clip();

    ctx.font = "12px serif";
    let text = "Hello world";
    let x = len / 2;
    if ( ar >= 0 ) {
        ctx.fillText(text, x, -5);
    } else {
        ctx.fillText(text, x, 5);
    }

    ctx.fillStyle = 'red';
    ctx.strokeStyle = 'red';
    for (let i = 0, x = this.idx_x; x * 5 + 10 < len + 5; x += 3, i++ ) {
        if ( i % 2 ) {
            ctx.fillStyle = 'red';
            ctx.strokeStyle = 'red';
        } else {
            ctx.fillStyle = 'black';
            ctx.strokeStyle = 'black';
        }
        ctx.beginPath();
        ctx.moveTo(x * 5 + 5, 0);
        ctx.lineTo(x * 5, 3);
        ctx.lineTo(x * 5 + 10, 3);
        ctx.lineTo(x * 5 + 15, 0);
        ctx.lineTo(x * 5 + 10, -3);
        ctx.lineTo(x * 5, -3);
        ctx.lineTo(x * 5 + 5, 0);
        ctx.fill();
    }

    this.idx_x += 1;
    if ( this.idx_x > 0 ) {
        this.idx_x = begin_index;
    }
    ctx.restore();
};
