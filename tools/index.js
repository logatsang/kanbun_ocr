const buttonGroup = document.getElementById("char-buttons");
const textField = document.getElementById("text-field");
const pageDisplay = document.getElementById("page-display");
const pageNumberDisplay = document.getElementById("page-number");

const pageMin = 100, pageMax = 200;
var segments, segmentCount, curIndex = 0, pageIndex = pageMin;

function pageChange(value) {
    pageIndex += value;
    pageIndex = Math.max(Math.min(pageIndex, pageMax), pageMin);
    pageUpdate();
}

function pageUpdate() {
    const pageNumber = String(pageIndex);
    pageNumberDisplay.innerHTML = pageNumber;
    pageDisplay.src = `img/${pageNumber.padStart(4, '0')}.jpg`
}

function insertAtCursor(myField, myValue) {
    // https://stackoverflow.com/questions/11076975/how-to-insert-text-into-the-textarea-at-the-current-cursor-position
    const newIndex = myField.selectionStart + 1;

    //IE support
    if (document.selection) {
        myField.focus();
        sel = document.selection.createRange();
        sel.text = myValue;
    }
    //MOZILLA and others
    else if (myField.selectionStart || myField.selectionStart == '0') {
        var startPos = myField.selectionStart;
        var endPos = myField.selectionEnd;
        myField.value = myField.value.substring(0, startPos)
            + myValue
            + myField.value.substring(endPos, myField.value.length);
    } else {
        myField.value += myValue;
    }
    
    textField.focus();
    textField.setSelectionRange(newIndex, newIndex);
}

function writeChar(charIndex) {
    const char = segments[curIndex][charIndex];
    
    insertAtCursor(textField, char);
}

function indexChange(value) {
    curIndex += value;
    curIndex = Math.max(Math.min(curIndex, segmentCount - 1), 0);
    update();
}

function indexSet(value) {
    curIndex = value;
    update();
}

function update() {
    console.log(curIndex);

    const currentSegment = segments[curIndex];
    var result = "";

    Array.from(currentSegment).forEach((value, index) => {
        result += `<button type="button" class="btn btn-primary" onclick="writeChar(${index})">${value}</button>`;
    })
    buttonGroup.innerHTML = result;
}

function initialize() {
    pageChange(0);

    document.addEventListener("keydown", (event) => {
        if (textField === document.activeElement) return;

        if (event.key == "ArrowLeft") pageChange(-1);
        else if (event.key == "ArrowRight") pageChange(+1); 
    });

    // Load text
    fetch("verify.txt")
    .then((res) => res.text())
    .then((text) => {
        segments = text.split(/[。，、「」『』？！：；\n\r]+/);
        segmentCount = segments.length;
    })
    .then(update)
    .catch((e) => console.error(e));
}

initialize();
