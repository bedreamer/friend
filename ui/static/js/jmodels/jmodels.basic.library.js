let JLibrary = function (id, name, src, row, column, unit_width, unit_height) {
    this.image = new Image();
    this.row = row;
    this.column = column;
    this.unit_width = unit_width;
    this.unit_height = unit_height;
    this.id = id;
    this.name = name;
    this.src = src;

    this.image.src = src;
    return this;
};

JLibrary.prototype.save = function () {
    return {
        row: this.row,
        column: this.column,
        unit_height: this.unit_height,
        unit_width: this.unit_width,
        id: this.id,
        name: this.name,
        src: this.src
    }
};