/**
 * 锚点对象，用于链接两个对象
 * @param id: 锚点ID
 * @param model: 所属模型
 * @param x_offset: 当前锚点在模型的中心点的x偏移值
 * @param y_offset: 当前锚点在模型的中心点的y偏移值
 * @param style: 当前锚点的风格定义结构
 * */
let JAnchor = function (id, model, x_offset, y_offset, style) {
    this.id = id;
    this.model = model;

    if ( style === undefined ) style = {};
    if ( style.name === undefined ) style.name = 'default';

    model.anchors[style.name] = this;

    this.x_offset = x_offset;
    this.y_offset = y_offset;
    this.height = 6;
    this.width = 6;
    this.style = style;

    this.x = model.x_offset + this.x_offset - this.width/2;
    this.y = model.y_offset + this.y_offset - this.height/2;

    return this;
};
/**
 * 渲染函数
 * */
JAnchor.prototype.render = function (ctx) {
};


/**
 * 生成保存锚点对象
 * */
JAnchor.prototype.save = function () {
    return {
        id: this.id,
        model: this.model.id,
        name: this.name,
        x_offset: this.x_offset,
        y_offset: this.y_offset,
        style: this.style
    }
};
