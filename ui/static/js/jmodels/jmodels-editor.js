let JEditor = function (painter) {
    this.painter = painter;
    this.painter.editor = this;

    // 光标在模型修改大小象限
    this.in_resize_model_arae = false;
    // 光标在模型移动位置象限
    this.in_move_model_arae = false;

    // 选择的模型
    this.model_selected = undefined;

    // 选择的锚点栈, 左键按下选择，左键弹起清空
    this.anchor_stack_selected = [];
    // 动态显示的锚点, 光标移动到锚点上时可以高亮显示，光标移入范围选择，移出范围清空
    this.hot_anchors_stack = [];
    // 跟随光标移动的线，选择锚点时激活，光标移动时更新，左键弹起时清空
    this.hotlines_stack = [];
    // 改变大小的对象选择栈，左键点击对象的第四象限时选择，光标移动时更新，左键弹起时清空
    this.resize_models_stack = [];
    // 改变位置的对象选择栈，左键点击对象的第一、二、三象限时选择，光标移动时更新，左键弹起时清空
    this.change_location_models_statck = [];
    // 选择的模型基本属性栈，选择时压入，左键弹起时清空
    this.attribute_of_selected_model_statck = {};
    // 光标移动的位置记录, 左键按下时记录，左键弹起时清空
    this.cursor_motion_stack = [];

    // 开始移动的点
    this.move_begin_point = undefined;

    // 可编辑的最小模型宽度
    this.model_min_width = 30;
    // 可编辑的最小模型高度
    this.model_min_height = 30;

    window.requestAnimationFrame(this.animation_render);
    window.editor = this;
    return this;
};


JEditor.prototype.animation_render = function() {
    console.log(this.editor);
};


/**
 * 绘制编辑模式下的连接线补充内容
 * */
JEditor.prototype.render_link = function(ctx, link) {
};


/**
 * 绘制编辑模式下的锚点补充内容
 * */
JEditor.prototype.render_anchor = function(ctx, anchor) {
    ctx.save();
    ctx.strokeRect(anchor.x, anchor.y, anchor.width, anchor.height);
    ctx.fillStyle = 'red';
    ctx.fillText(anchor.id, anchor.x, anchor.y);
    ctx.restore();
};


/**
 * 绘制编辑模式下的模型补充内容
 * */
JEditor.prototype.render_model = function(ctx, model) {
    // 绘制调整大小的把手
    let x = model.x_offset + model.width/2;
    let y = model.y_offset + model.height/2;

    ctx.save();

    ctx.beginPath();
    for ( let i = 1; i <= 4; i ++) {
        ctx.moveTo(x - 5 * i, y);
        ctx.lineTo(x, y - 5 * i);
    }
    ctx.stroke();
    ctx.restore();

    /*
    ctx.fillText("id:"+model.id, model.x_offset - 30, model.y_offset - 10);
    ctx.fillText("x:"+model.x, model.x_offset - 30, model.y_offset - 22);
    ctx.fillText("y:"+model.y, model.x_offset - 30, model.y_offset - 34);
    ctx.fillText("W:"+model.width, model.x_offset - 30, model.y_offset - 46);
    ctx.fillText("H:"+model.height, model.x_offset - 30, model.y_offset - 58);
    */
};


/**
 * 编辑器的绘制事件
 * */
JEditor.prototype.render = function(ctx) {
    ctx.save();

    let link_list = this.painter.links_list;
    for (let idx in link_list) {
        if ( ! link_list.hasOwnProperty(idx) ) {
            continue;
        }
        this.render_link(ctx, link_list[idx]);
    }

    let anchor_list = this.painter.anchors_list;
    for (let idx in anchor_list) {
        if ( ! anchor_list.hasOwnProperty(idx) ) {
            continue;
        }
        this.render_anchor(ctx, anchor_list[idx]);
    }

    let model_list = this.painter.models_list;
    for (let idx in model_list) {
        if ( ! model_list.hasOwnProperty(idx) ) {
            continue;
        }
        this.render_model(ctx, model_list[idx]);
    }

    // 绘制热锚点
    for ( let idx in this.hot_anchors_stack ) {
        if ( !this.hot_anchors_stack.hasOwnProperty(idx) ) {
            continue;
        }
        let anchor = this.hot_anchors_stack[idx];
        ctx.save();
        ctx.strokeStyle = 'blue';
        ctx.strokeRect(anchor.x - 3, anchor.y - 3, anchor.width + 3 * 2, anchor.height + 3 * 2);
        ctx.stroke();
        ctx.restore();
    }

    // 绘制热线
    for ( let idx in this.hotlines_stack ) {
        if ( !this.hotlines_stack.hasOwnProperty(idx) ) {
            continue;
        }
        let hot_line = this.hotlines_stack[idx];
        ctx.save();
        ctx.strokeStyle = 'blue';
        ctx.moveTo(hot_line.begin_x, hot_line.begin_y);
        ctx.lineTo(hot_line.end_x, hot_line.end_y);
        ctx.stroke();
        ctx.restore();
    }

    // 绘制选择的模型, 有改变模型位置的选择对象
    for(let i = 0, length = this.change_location_models_statck.length; i < length; i ++) {
        let model = this.change_location_models_statck[i];
        ctx.strokeStyle = 'red';
        ctx.strokeRect(model.x - 5, model.y - 5, model.width + 10, model.height + 10);
    }

    // 绘制选择的模型, 有改变模型大小的选择对象
    for(let i =0, length = this.resize_models_stack.length; i < length; i ++) {
        let model = this.resize_models_stack[i];
        ctx.strokeStyle = 'red';
        ctx.strokeRect(model.x - 5, model.y - 5, model.width + 10, model.height + 10);
    }

    ctx.restore();
};


/**
 * 更新绘制的内容到画板
 * */
JEditor.prototype.update = function () {
    this.painter.begin();
    this.painter.render();
    this.painter.update();
};


/**
 * 在当前的模型列表终新建一个模型
 * */
JEditor.prototype.create_link = function (begin, end, style) {
    let linked = this.painter.is_linked(begin, end);
    if ( linked ) {
        console.warn("锚点已经有过连接!");
        return undefined;
    }

    if ( begin === end ) {
        console.warn("不允许锚点连接自身！");
        return undefined;
    }

    if ( typeof begin != 'object' ) {
        let target = this.painter.search_anchor(begin);
        if ( ! target ) {
            console.error("没有找到锚点", begin);
            return undefined;
        }
        begin = target;
    }
    if ( typeof end != 'object' ) {
        let target = this.painter.search_anchor(end);
        if ( ! target ) {
            console.error("没有找到锚点", end);
            return undefined;
        }
        end = target;
    }

    if ( begin.model === end.model ) {
        console.warn("不允许模型自身的锚点连接！");
        return;
    }

    let id = ++ this.painter._id_pool;
    let link = new JLink(id, begin, end, style);
    this.painter.links_list[id] = link;
    return link;
};

/**
 * 在当前的模型列表终新建一个模型
 * */
JEditor.prototype.create_anchor = function (model, x_offset, y_offset, style) {
    let id = ++ this.painter._id_pool;
    if ( typeof model != 'object' ) {
        let target = this.painter.search_model(model);
        if ( ! target ) {
            console.error("没有找到模型", model);
            return undefined;
        }
        model = target;
    }
    let anchor = new JAnchor(id, model, x_offset, y_offset, style);
    this.painter.anchors_list[id] = anchor;
    return anchor;
};

/**
 * 在当前的模型列表终新建一个模型
 * */
JEditor.prototype.create_model = function(x_offset, y_offset, width, height, style) {
    let id = ++ this.painter._id_pool;
    let name = "model_" + id;
    let model = new JModel(id, this.painter, name, x_offset, y_offset, width, height, style);
    this.painter.models_list[id] = model;
    return model;
};

/**
 * 将画板中的对象保存起来
 * */
JEditor.prototype.save = function () {
    let models = [];
    let links = [];
    let anchors = [];
    let libraries = [];

    for (let i in this.painter.image_libraries_list) {
        if ( ! this.painter.image_libraries_list.hasOwnProperty(i) ) {
            continue;
        }
        libraries.push(this.painter.image_libraries_list[i].save())
    }

    for (let i in this.painter.links_list) {
        if ( ! this.painter.links_list.hasOwnProperty(i) ) {
            continue;
        }
        links.push(this.painter.links_list[i].save())
    }

    for (let i in this.painter.anchors_list) {
        if ( ! this.painter.anchors_list.hasOwnProperty(i) ) {
            continue;
        }
        anchors.push(this.painter.anchors_list[i].save())
    }

    for (let i in this.painter.models_list) {
        if ( ! this.painter.models_list.hasOwnProperty(i) ) {
            continue;
        }
        models.push(this.painter.models_list[i].save())
    }

    return {
        models: models,
        links: links,
        anchors: anchors,
        libraries: libraries,
        width: this.painter.width,
        height: this.painter.height
    };
};

/**
 * 从json对象加载到画板
 * */
JEditor.prototype.load = function (obj) {
    this.painter.load(obj.width, obj.height, obj.models, obj.anchors, obj.links, obj.libraries);
};


/**
 * 判断光标是否在改变大小的区域
 * */
JEditor.prototype.is_cursor_in_model_resize_area = function(model, ev) {
    if ( model.x > ev.offsetX ) {
        return false;
    }
    if ( model.x + model.width < ev.offsetX ) {
        return false;
    }
    if ( model.y > ev.offsetY ) {
        return false;
    }
    if ( model.y + model.height < ev.offsetY ) {
        return false;
    }

    return ev.offsetX > model.x_offset && ev.offsetY > model.y_offset;
};

/**
 * 判断光标是否在改变位置的区域内
 * */
JEditor.prototype.is_cursor_in_model_change_location_area = function(model, ev) {
    if ( model.x > ev.offsetX ) {
        return false;
    }
    if ( model.x + model.width < ev.offsetX ) {
        return false;
    }
    if ( model.y > ev.offsetY ) {
        return false;
    }
    if ( model.y + model.height < ev.offsetY ) {
        return false;
    }

    return !(ev.offsetX > model.x_offset && ev.offsetY > model.y_offset);
};


/**
 * 选择模型
 * */
JEditor.prototype.select_model = function (ev) {
    for ( let id in this.painter.models_list ) {
        if ( !this.painter.models_list.hasOwnProperty(id) ) {
            continue;
        }
        let model = this.painter.models_list[id];

        if ( model.x > ev.offsetX ) {
            continue;
        }
        if ( model.x + model.width < ev.offsetX ) {
            continue;
        }
        if ( model.y > ev.offsetY ) {
            continue;
        }
        if ( model.y + model.height < ev.offsetY ) {
            continue;
        }

        if ( ev.offsetX > model.x_offset && ev.offsetY > model.y_offset ) {
            this.in_resize_model_arae = true;
            this.in_move_model_arae = false;
        } else {
            this.in_resize_model_arae = false;
            this.in_move_model_arae = true;
        }

        return model;
    }
};


/**
 * 选择锚点
 * */
JEditor.prototype.select_anchor = function (ev) {
    for ( let id in this.painter.anchors_list ) {
        if ( !this.painter.anchors_list.hasOwnProperty(id) ) {
            continue;
        }
        let anchor = this.painter.anchors_list[id];

        if ( anchor.x > ev.offsetX ) {
            continue;
        }
        if ( anchor.x + anchor.width < ev.offsetX ) {
            continue;
        }
        if ( anchor.y > ev.offsetY ) {
            continue;
        }
        if ( anchor.y + anchor.height < ev.offsetY ) {
            continue;
        }

        return anchor;
    }
};


/**
 * 更新模型的位置
 **/
JEditor.prototype.update_model_location = function(model, new_x_offset, new_y_offset) {
    model.x_offset = new_x_offset;
    model.y_offset = new_y_offset;
    model.x = model.x_offset - model.width/2;
    model.y = model.y_offset - model.height/2;

    for (let name in model.anchors) {
        if ( model.anchors.hasOwnProperty(name) ) {
            let anchor = model.anchors[name];
            anchor.x = anchor.model.x_offset + anchor.x_offset - anchor.width / 2;
            anchor.y = anchor.model.y_offset + anchor.y_offset - anchor.height / 2;
        }
    }
};


/**
 * 更新模型的大小
 **/
JEditor.prototype.update_model_size = function(model, new_width, new_height) {
    model.width = new_width;
    model.height = new_height;

    // 固定中心点不变
    model.x = model.x_offset - model.width/2;
    model.y = model.y_offset - model.height/2;

    function relocation_anchor(model, anchor, x_offset, y_offset) {
        anchor.x_offset = x_offset;
        anchor.y_offset = y_offset;
        anchor.x = model.x_offset + anchor.x_offset - anchor.width/2;
        anchor.y = model.y_offset + anchor.y_offset - anchor.height/2;
    }

    // left anchor
    let anchor = model.anchors.left;
    anchor && relocation_anchor(model, anchor, - new_width / 2, 0);

    // top anchor
    anchor = model.anchors.top;
    anchor && relocation_anchor(model, anchor, 0, - new_height / 2);

    // right anchor
    anchor = model.anchors.right;
    anchor && relocation_anchor(model, anchor, new_width / 2, 0);

    // bottom anchor
    anchor = model.anchors.bottom;
    anchor && relocation_anchor(model, anchor, 0, new_height / 2);
};


/***
 *
 * 鼠标移动事件
 */
JEditor.prototype.onmousemove = function (ev) {
    let update_request = 0;

    // 跟踪热锚点位置, 光标移动至锚点上时用不同颜色的框描出边框
    let anchor = this.select_anchor(ev);
    if ( anchor && this.hot_anchors_stack.indexOf(anchor) < 0 ) {
        this.hot_anchors_stack.push(anchor);
        update_request ++;
    } else {
        this.hot_anchors_stack = [];
    }

    // 跟踪热线位置，随着光标的移动动态的绘制出连接线的位置
    if ( this.anchor_stack_selected.length > 0) {
        for (let idx in this.hotlines_stack) {
            if (!this.hotlines_stack.hasOwnProperty(idx)) {
                continue;
            }
            let hot_line = this.hotlines_stack[idx];
            hot_line.update_endpoint(ev.offsetX, ev.offsetY);
            update_request ++;
        }
    }

    let delta_x = 0, delta_y = 0;
    if ( this.cursor_motion_stack.length ) {
        delta_x = ev.offsetX - this.cursor_motion_stack[0].offsetX;
        delta_y = ev.offsetY - this.cursor_motion_stack[0].offsetY;
    }

    // 有位置变化时才进行更新操作，避免多次绘制
    if (delta_x || delta_y) {
        // 有改变模型位置的选择对象
        if (this.change_location_models_statck.length) {
            this.painter.dom.style.cursor = 'move';

            for(let i = 0, length = this.change_location_models_statck.length; i < length; i ++) {
                let model = this.change_location_models_statck[i];
                let attribute = this.attribute_of_selected_model_statck[model.id];

                let new_x_offset = attribute.x_offset + delta_x;
                let new_y_offset = attribute.y_offset + delta_y;
                this.update_model_location(model, new_x_offset, new_y_offset);
                update_request ++;
            }
        }
    }

    // 有位置变化时才进行更新操作，避免多次绘制
    if (delta_x || delta_y) {
        // 有改变模型大小的选择对象
        if (this.resize_models_stack.length) {
            this.painter.dom.style.cursor = 'nw-resize';

            for(let i =0, length = this.resize_models_stack.length; i < length; i ++) {
                let model = this.resize_models_stack[i];
                let attribute = this.attribute_of_selected_model_statck[model.id];
                let new_width = attribute.width + delta_x;
                if (new_width <= 20) {
                    new_width = 20;
                }
                let new_height = attribute.height + delta_y;
                if (new_height <= 20) {
                    new_height = 20;
                }
                this.update_model_size(model, new_width, new_height);
                update_request ++;
            }
        }
    }

    if ( update_request){
        console.log(update_request);
    }

    // 整体重绘一次，提高效率
    return update_request ? this.update() : undefined;
};

/**
 * 连接热线对象
 * */
let JHotline = function(begin_x, begin_y) {
    this.begin_x = begin_x;
    this.begin_y = begin_y;
    this.end_x = begin_x;
    this.end_y = begin_y;
};
JHotline.prototype.update_endpoint = function(end_x, end_y) {
    this.end_x = end_x;
    this.end_y = end_y;
};


/***
 *
 * 鼠标按下事件
 */
JEditor.prototype.onmousedown = function (ev) {
    let anchor = this.select_anchor(ev);

    // 只允许将锚点压栈一次
    if ( anchor && this.anchor_stack_selected.indexOf(anchor) < 0 ) {
        this.anchor_stack_selected.push(anchor);
        let hot_line = new JHotline(ev.offsetX, ev.offsetY);
        this.hotlines_stack.push(hot_line);
        return;
    }

    // 编辑模式下梳鼠标按下后应该优先选择锚点，然后选择模型
    let model = this.select_model(ev);
    if ( !model ) return;

    let attribute = {
        x_offset: model.x_offset,
        y_offset: model.y_offset,
        width: model.width,
        height: model.height
    };

    if (this.is_cursor_in_model_change_location_area(model, ev)) {
        if ( this.change_location_models_statck.indexOf(model) < 0 ) {
            this.change_location_models_statck.push(model);
        }
    } else { //if (this.is_cursor_in_model_resize_area(model, ev) ) {
        if ( this.resize_models_stack.indexOf(model) < 0 ) {
            this.resize_models_stack.push(model);
        }
    }

    this.attribute_of_selected_model_statck[model.id] = attribute;
    this.cursor_motion_stack.push(ev);

    /*
    if ( model ) {
        this.down_point_while_move = ev;
        this.model_selected = model;

        this.model_x_offset_while_mousedown = model.x_offset;
        this.model_y_offset_while_mousedown = model.y_offset;

        this.model_width_while_mousedown = model.width;
        this.model_height_while_mousedown = model.height;

        if ( this.in_move_model_arae ) {
            this.painter.dom.style.cursor = 'move';
        }

        if ( this.in_resize_model_arae ) {
            this.painter.dom.style.cursor = 'nw-resize';
        }
    }
    */
};

/***
 *
 * 鼠标弹起事件
 */
JEditor.prototype.onmouseup = function (ev) {
    let anchor = this.select_anchor(ev);

    if ( anchor && this.anchor_stack_selected.indexOf(anchor) < 0 ) {
        let begin_anchor = this.anchor_stack_selected.pop();

        // 现在已经有两个锚点了，判断一下：若还没有建立过连接，则新建一个连接
        let link = this.create_link(begin_anchor, anchor, {});
        console.log(link);
    }

    let model = this.select_model(ev);

    if ( this.model_selected !== undefined ) {
        this.update();
    }

    this.painter.dom.style.cursor = 'auto';
    this.model_selected = undefined;
    this.move_begin_point = undefined;

    // 清空锚点选择栈,左键按下时选择，左键弹起时清空
    this.anchor_stack_selected = [];
    // 动态显示的锚点, 光标移动到锚点上时可以高亮显示，光标移入范围选择，移出范围清空
    this.hot_anchors_stack = [];
    // 跟随光标移动的线，选择锚点时激活，光标移动时更新，左键弹起时清空
    this.hotlines_stack = [];
    // 改变大小的对象选择栈，左键点击对象的第四象限时选择，光标移动时更新，左键弹起时清空
    this.resize_models_stack = [];
    // 改变位置的对象选择栈，左键点击对象的第一、二、三象限时选择，光标移动时更新，左键弹起时清空
    this.change_location_models_statck = [];
    // 选择的模型基本属性栈，选择时压入，左键弹起时清空
    this.attribute_of_selected_model_statck = {};
    // 光标移动的位置记录, 左键按下压栈两次，光标移动时更新最后一个，左键弹起时清空
    this.cursor_motion_stack = [];
};

/***
 *
 * 鼠标单击事件
 */
JEditor.prototype.onclick = function (ev) {
    //let model = this.select_model(ev);
};

/***
 *
 * 鼠标双击事件
 */
JEditor.prototype.ondblclick = function (ev) {
    let model = this.select_model(ev);
    if ( model !== undefined ) {
        let href = '/model/' + model.id.toString() + '/change/';
        console.log(href);
        window.location.href = href;
    }
};
