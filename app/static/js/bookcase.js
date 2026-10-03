class Bookcase {
    constructor(targetContainer, config) {
        this.config = config || [];
        this.targetContainer = targetContainer;
        this.selectedCount = 0;
        this.listeners = {};
    }

    addEventListener(method, callback) {
        this.listeners[method] = callback;
    }

    emit(method, payload) {
        const callback = this.listeners[method];
        if (typeof callback == "function") {
            callback(this, payload);
        }
    }

    updateRowsCols(rows, cols) {
        const config = [];
        for (var r = 0; r < rows; r++) {
            var row = [];
            for (var c = 0; c < cols; c++) {
                row.push({
                    id: null,
                    row: r,
                    col: c,
                    rowspan: 1,
                    colspan: 1,
                    selected: false,
                });
            }
            config.push(row);
        }
        this.config = config;
        this.draw();
    }

    getCell(row, col) {
        for (const _row of this.config) {
            for (const cell of _row) {
                if (cell.row == row && cell.col == col) {
                    return cell;
                }
            }
        }
    }

    mergeSelected() {
        const toBeMerged = [];
        for (const row of this.config) {
            for (const col of row) {
                if (col.selected) {
                    toBeMerged.push(col);
                }
            }
        }

        if (toBeMerged.length < 2) return;

        const toKeep = toBeMerged.shift();
        let rowspan = toKeep.rowspan;
        let colspan = toKeep.colspan;

        for (const item of toBeMerged) {
            if (item.row !== toKeep.row && item.col === toKeep.col) {
                rowspan += item.rowspan;
            }
            if (item.col !== toKeep.col && item.row === toKeep.row) {
                colspan += item.colspan;
            }
        }

        toKeep.rowspan = rowspan;
        toKeep.colspan = colspan;

        const newConfig = [];
        for (const row of this.config) {
            const newRow = [];
            for (const cell of row) {
                if (!toBeMerged.includes(cell)) {
                    cell.selected = false;
                    newRow.push(cell);
                }
            }

            newConfig.push(newRow);
        }
        this.config = newConfig;
        this.selectedCount = 0;
        this.draw();
    }

    clearSelections() {
        for (const row of this.config) {
            for (const cell of row) {
                cell.selected = false;
            }
        }
        this.draw();
    }

    draw() {
        const table = document.createElement("table");
        table.classList.add("bookcaseTable");

        for (const row of this.config) {
            const tr = table.insertRow();
            for (const cell of row) {
                const td = tr.insertCell();

                td.setAttribute("rowSpan", cell.rowspan);
                td.setAttribute("colSpan", cell.colspan);

                td.dataset.row = cell.row;
                td.dataset.col = cell.col;
                if (cell.selected) {
                    td.dataset.selected = true;
                }
                if (cell.location) {
                    td.innerText = cell.location;
                }
            }
        }

        this.targetContainer.replaceChildren(table);
        table.addEventListener("click", (event) => this.onClick(event));
        this.emit("updated");
    }
    onClick(event) {
        const td = event.target.closest("td");
        const cell = this.getCell(td.dataset.row, td.dataset.col);
        cell.selected = !cell.selected;
        this.draw();
        this.selectedCount += cell.selected ? 1 : -1;
        this.emit("selected", { bookcase: this, cell: cell });
    }
}

class ShelfSelector {
    constructor(prefix, selectionCallback, clearCallback) {
        this.button = document.getElementById(`${prefix}-btn`);
        this.another = document.getElementById(`${prefix}-another`);
        this.clear  = document.getElementById(`${prefix}-clear`);
        this.dialog = document.getElementById(`${prefix}-dialog`);
        const cancelButton = this.dialog.getElementsByClassName("cancel")[0];
        this.listingButton = this.dialog.getElementsByClassName("listing")[0];
        this.overlay = document.getElementById(`${prefix}-overlay`);
        this.search = document.getElementById(`${prefix}-bookcase-search`);
        this.results = this.dialog.getElementsByClassName("results")[0];
        this.latestResults = [];

        this.selectionCallback = selectionCallback;
        this.clearCallback = clearCallback;

        this.bookcaseName = "";

        this.button.addEventListener("click", (e) => {
            e.preventDefault();
            this.openDialog();
        });

        this.another.addEventListener("click", (e) => {
            e.preventDefault();
            this.openDialog();
        });

        this.clear.addEventListener("click", (e) => {
            e.preventDefault();
            this.bookcaseName = "";
            this.clearCallback();
        });

        this.dialog.addEventListener("close", (e) => {
            this.overlay.classList.remove("active");
        });


        this.search.addEventListener("input", (e) => {
            this.handleSearch(this.search.value);
        });

        cancelButton.addEventListener("click", (e) => {
            e.preventDefault();
            this.closeDialog();
        });

        this.listingButton.addEventListener("click", (e) => {
            e.preventDefault();
            this.createResultsList(this.latestResults);
        });

        this.overlay.addEventListener("click", (e) => {
            this.closeDialog();
        });


        const recent = document.getElementById("recent-bookcases");
        if(recent) {
            try {
                this.createResultsList({"results": JSON.parse(recent.textContent)});
            } catch(error) {
                alert(error);
            }
        }
    }

    async handleSearch(value) {
        try {
            const response = await fetch(
                "/api/v1/autocomplete/?model=bookcase&q=" + value,
            );
            if (!response.ok)
                throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            this.createResultsList(data);
        } catch (error) {
            alert(error);
        }
    }

    openDialog() {
        this.dialog.showModal();
        this.overlay.classList.add("active");
    }

    closeDialog() {
        this.dialog.close();
    }

    createResultsList(data) {
        const element = document.createElement("div");
        element.classList.add("scroll");

        if (data.results.length > 0) {
            const ul = document.createElement("ul");
            ul.classList.add("list", "border");
            for (const result of data.results) {
                const li = document.createElement("li");

                const icon = document.createElement("i");
                icon.textContent = "shelves";

                li.append(icon, result.name);
                li.dataset.id = result.id;
                li.dataset.name = result.name;
                li.dataset.config = JSON.stringify(result.shelves_config);

                li.addEventListener("click", (event) => {
                    this.onResultClick(event);
                });

                ul.appendChild(li);
            }
            element.appendChild(ul);
        } else {
            element.appendChild(document.createTextNode("No results"));
        }

        this.results.replaceChildren(element);
        this.latestResults = data;
        this.listingButton.setAttribute("hidden", "");
    }

    onResultClick(event) {
        this.bookcaseName = event.target.dataset.name;
        const bookcase = new Bookcase(
            this.results,
            JSON.parse(event.target.dataset.config),
        );
        bookcase.addEventListener("selected", (_, payload) =>
            this.onShelfClick(payload),
        );
        bookcase.draw();
        this.listingButton.removeAttribute("hidden");
    }

    onShelfClick(payload) {
        this.selectionCallback(this.bookcaseName, payload.cell);
        payload.bookcase.clearSelections();
        this.dialog.close();
    }
}
