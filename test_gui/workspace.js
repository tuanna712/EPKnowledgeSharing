function changeChoice(checkedList, checkbox) {
    document.getElementById(checkedList);
    const checkedBoxes = document.getElementById(checkbox).children;
    var list = [];
    
    for (var i = 0; i < checkedBoxes.length; i++) {
        if (checkedBoxes[i].childNodes[1].checked) {
            console.log(checkedBoxes[i].childNodes[3].textContent);
            list.push(checkedBoxes[i].childNodes[3].textContent);
        }
    }

    list = list.join(", ");
    document.getElementById(checkedList).textContent = list;
}