class Bookcase {
    constructor(targetContainer, mergeButton, configInput, config) {
        this.config = config || [];
        this.targetContainer = targetContainer;
        this.mergeButton = mergeButton;
        this.configInput = configInput;
        this.table = null;
        this.selectedCount = 0;

        mergeButton.addEventListener("click", (event) => this.mergeSelected());
    };

    updateRowsCols(rows, cols) {
        const config = [];
        for(var r=0; r<rows; r++) {
            var row = [];
            for(var c=0; c<cols; c++) {
                row.push(
                    {
                        "row": r,
                        "col": c,
                        "rowspan": 1,
                        "colspan": 1,
                        "selected": false,
                    }
                );
            }
            config.push(row);
        }
        this.config = config;
        this.draw();
    }

    updateMergeButton() {
        this.mergeButton.disabled = this.selectedCount < 2;
    }

    getCell(row, col) {
        for(const _row of this.config) {
            for(const cell of _row) {
                if(cell.row == row && cell.col == col) {
                    return cell;
                }
            }
        }
    }

    mergeSelected() {
        const toBeMerged = [];
        for(const row of this.config) {
            for(const col of row) {
                if(col.selected) {
                    toBeMerged.push(col);
                }

            }
        }

        if (toBeMerged.length < 2) return;

        const toKeep = toBeMerged.shift();
        let rowspan = toKeep.rowspan;
        let colspan = toKeep.colspan;

        for(const item of toBeMerged) {
            if(item.row !== toKeep.row && item.col === toKeep.col) {
                rowspan += item.rowspan;
            }
            if(item.col !== toKeep.col && item.row === toKeep.row) {
                colspan += item.colspan;
            }
        }

        toKeep.rowspan = rowspan;
        toKeep.colspan = colspan;

        const newConfig = [];
        for(const row of this.config) {
            const newRow = [];
            for(const cell of row) {
                if(!toBeMerged.includes(cell)) {
                    cell.selected = false;
                    newRow.push(cell);
                }
            }

            newConfig.push(newRow);
        }
        this.config = newConfig;
        this.selectedCount = 0;
        this.updateMergeButton();
        this.draw();
    }

    draw() {
        const table = document.createElement("table");
        table.classList.add("bookcaseTable");

        for(const row of this.config) {
            const tr = table.insertRow();
            for(const cell of row) {
                const td = tr.insertCell()

                td.setAttribute("rowSpan", cell.rowspan);
                td.setAttribute("colSpan", cell.colspan);

                td.dataset.row = cell.row;
                td.dataset.col = cell.col;
                if(cell.selected) {
                    td.dataset.selected = true;
                };
            }
        }


        if(this.table) { this.table.remove(); }

        this.table = table;
        this.targetContainer.appendChild(table);
        this.table.addEventListener("click", (event) => this.onClick(event));
        this.configInput.value = JSON.stringify(this.config);
    };
    onClick(event) {
        const td = event.target.closest("td");
        const cell = this.getCell(td.dataset.row, td.dataset.col);
        cell.selected = !cell.selected;
        this.draw();
        this.selectedCount += 1;
        this.updateMergeButton();
    }
};
