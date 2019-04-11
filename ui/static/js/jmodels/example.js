/**
 * example.html
 *
 * <html>
 *     <body>
 *         <canvas id="paint"></canvas>
 *     </body>
 * </html>
 *
 * */

var data = {
    models: [],
    links: [],
    anchors: []
};

/**
 * 'paint' canvas dom id
 * 1000: canvas width in pixel
 * 600: canvas height in pixel
 * data: canvas models/links/anchors data
 * */
var painter = new JPaintbord('paint', 1000, 600, data);
painter.begin();
painter.render();
painter.update();

/*
* 索引模型操作
* */
var model = painter.search_model_by_id(10);
//    or
var model = painter.search_model_by_name('model name');


/**
 * 隐藏模型内容
 * */
model.hide();
painter.commit();

/**
 * 显示模型内容
 * */
model.show();
painter.commit();

/**
 * 闪烁模型内容
 * painter.HZ_5: 闪烁频率, 5HZ
 * 支持的频率
 * HZ_10, HZ_8, HZ_5, HZ_4, HZ_3, HZ_2, HZ_1, HZ_0
 * 其中HZ_0 表示停止闪烁
 * */
model.blink(painter.HZ_5);

