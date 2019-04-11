/***
 *  jmodels.js
 *  作者: 李杰
 *  报告漏洞: bedreamer@163.com
 *
 *  计划:
 *      第一阶段： jmodels.js 可以将canvas初始化为不同的大小尺寸
 *      第二阶段:  Paintboard可以将mdatabase中的模型渲染出来
 *      第三阶段: 丰富模型的风格
 *      第四阶段: 实现模型的在线编辑
 *   注意:
 *      加载顺序:
 *          model --> anchors --> link
 *      渲染顺序
 *          link  --> anchor --> model
 *
 *  版本记录
 *  v1.0
 *  解决页面动态模型的绘制问题，
 *  支持：
 *      1. 动态编辑
 *      2. 模块
 *      3. 连接点(锚点)
 *      4. 连接线(连线)
 *  设计思路：
 *     1. js 进行调用，初始化canvas为JPaintbord;
 *     2. js 调用时传入option参数指定模型数据库mdatabase
 *     3. Paintboard通过mdatabase将模型渲染在canvas上
 */
document.write("<script type='text/javascript' src='/static/js/jmodels/jmodels.basic.library.js'></script>");
document.write("<script type='text/javascript' src='/static/js/jmodels/jmodels.basic.link.js'></script>");
document.write("<script type='text/javascript' src='/static/js/jmodels/jmodels.basic.anchor.js'></script>");
document.write("<script type='text/javascript' src='/static/js/jmodels/jmodels.basic.model.js'></script>");
document.write("<script type='text/javascript' src='/static/js/jmodels/jmodels.basic.paintboard.js'></script>");


