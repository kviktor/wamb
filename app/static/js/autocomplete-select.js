/* AutocompleteSelectMultiple widget: Choices.js styled as beercss chips and menu,
 * options are loaded from the autocomplete endpoint while typing */

// beercss menus need <menu> and <li> elements
function withTag(el, tag) {
    const newEl = document.createElement(tag);
    for (const attr of el.attributes) newEl.setAttribute(attr.name, attr.value);
    newEl.append(...el.childNodes);
    return newEl;
}

function initAutocompleteSelect(select) {
    const url = select.dataset.autocompleteUrl;
    const model = select.dataset.autocompleteModel;
    let query = "";
    let searchTimeout = null;

    const choices = new Choices(select, {
        removeItemButton: true,
        itemSelectText: "",
        placeholder: false,
        shouldSort: false,
        // don't offer options that are already selected
        duplicateItemsAllowed: false,
        // searching is done by the autocomplete endpoint
        searchChoices: false,
        // there are no options to choose from until something is searched
        noChoicesText: () => (query ? "No results found" : "Start typing to search"),
        classNames: {
            // beercss class for selected chips and the hovered menu option
            highlightedState: ["is-highlighted", "fill"],
        },
        callbackOnCreateTemplates: function () {
            const defaults = Choices.defaults.templates;
            return {
                choiceList: function (...args) {
                    const menu = withTag(defaults.choiceList.call(this, ...args), "menu");
                    menu.classList.add("active");
                    return menu;
                },
                choice: function (...args) {
                    return withTag(defaults.choice.call(this, ...args), "li");
                },
                notice: function (...args) {
                    return withTag(defaults.notice.call(this, ...args), "li");
                },
                // render selected items as beercss chips with a close icon
                item: function (config, choice, removeItemButton) {
                    const el = defaults.item.call(this, config, choice, removeItemButton);
                    el.classList.add("chip");
                    const button = el.querySelector("[data-button]");
                    if (button) {
                        const icon = document.createElement("i");
                        icon.textContent = "close";
                        icon.dataset.button = "";
                        icon.setAttribute("aria-label", button.getAttribute("aria-label"));
                        button.replaceWith(icon);
                    }
                    return el;
                },
            };
        },
    });

    select.addEventListener("search", (event) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            const params = new URLSearchParams({model: model, q: event.detail.value});
            const response = await fetch(url + "?" + params);
            const data = await response.json();
            // option values from the <select> are strings, ids must match them for duplicateItemsAllowed
            const options = data.results.map((r) => ({value: String(r.id), label: r.name}));
            choices.setChoices(options, "value", "label", true);
        }, 250);
    });

    function resetSearch() {
        query = "";
        clearTimeout(searchTimeout);
        choices.clearChoices();
    }

    choices.input.element.addEventListener("input", (event) => {
        query = event.target.value;
        if (query === "") resetSearch();
    });
    // Choices clears the input after picking an option without an input event
    select.addEventListener("addItem", resetSearch);
}

// runs for the initial page and for every piece of content htmx swaps in
htmx.onLoad((content) => {
    // Choices marks the selects it already took over with data-choice
    content
        .querySelectorAll("select[data-autocomplete-url]:not([data-choice])")
        .forEach(initAutocompleteSelect);
});
