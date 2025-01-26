var preview = document.getElementById("preview");
const randomString = generateRandomString(32); // You can change the length to any desired value
// console.log("Random String: ", randomString);

setCookie('csrftoken', randomString, 1);

// console.log("Document Cookie: ", document.cookie);

function openPreview(embedLink) {
    document.getElementById("preview").src = embedLink;
}

function createQueryObject() {
    var data = {};
    const checkboxes = document.querySelectorAll('input[type=checkbox]');
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            const name = checkbox.name;
            if (name in data) {
                data[name].push(checkbox.id);
            } else {
                data[name] = [checkbox.id];
            }
        }
    })
    return data;
}

function submitFilter() {
    let csrftoken;
    try {
        csrftoken = getCookie('csrftoken');
        console.log("CSRF Token: ",csrftoken);
    } catch(err) {
        console.log(err);
    }

    const data = createQueryObject();

    deleteOldLinks();



    const request = new Request (
        "filter/", 
        {
            method: "POST",
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            mode: 'same-origin',
            body: JSON.stringify(data),
        }
    );

    fetch(request).then(function(response) {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // Set response type to 'text'
    }).then(data => {
        appendNewLinks(data);        
    });
}

function deleteOldLinks() {
    var result = document.getElementById('group-files');
    result.innerHTML = "";
}

function appendNewLinks(data) {
    console.log(data);
    var result = document.getElementById("group-files");
    data.forEach(item => createGroupList(item, result));
}

function createGroupList(item, result) {
    // Create button
    var button = document.createElement("button");
    button.classList.add("list-group-item", "list-group-item-action", "list-group-item-light");
    button.onclick = function() {
        openPreview(item.ServerRedirectedEmbedUri)
    };

    // Create div
    var div1 = document.createElement("div");
    div1.classList.add("ms-1", "me-auto", "d-flex", "justify-content-between");
    div1.id = "button-content";
    
    // Create link
    var a = document.createElement("a");
    a.classList.add("fw-semibold", "text-decoration-none");
    a.textContent = item.Name;
    div1.appendChild(a);

    // Create div2
    var div2 = document.createElement("div");
    div2.classList.add("ms-1", "me-auto", "text-secondary", "fst-italic");

    // Create spans
    var span1 = document.createElement("span");
    span1.classList.add("me-3");
    span1.textContent = "Block: " + item.Block;
    div2.appendChild(span1);

    var span2 = document.createElement("span");
    span2.classList.add("me-3");
    span2.textContent = "Well: " + item.WellName;
    div2.appendChild(span2);

    var span3 = document.createElement("span");
    span3.classList.add("me-3");
    span3.textContent = "Year: " + item.YearOfPublication;
    div2.appendChild(span3);


    button.appendChild(div1);
    button.appendChild(div2);
    result.appendChild(button);
}



function changeChoice(checkedList, checkbox) {
    document.getElementById(checkedList);
    const checkedBoxes = document.getElementById(checkbox).children;
    var list = [];
    
    for (var i = 0; i < checkedBoxes.length; i++) {
        if (checkedBoxes[i].childNodes[1].checked) {
            list.push(checkedBoxes[i].childNodes[3].textContent);
        }
    }

    list = list.join(", ");
    document.getElementById(checkedList).textContent = list;
    submitFilter();
}

function setCookie(name, value, hours) {
    const now = new Date();
    now.setTime(now.getTime() + (hours * 60 * 60 * 1000));
    const expires = "expires=" + now.toUTCString();
    document.cookie = name + "=" + value + ";" + expires + ";path=/";
    console.log(document.cookie);
}

function getCookie_backup(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function generateRandomString(length) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    const charactersLength = characters.length;
    
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * charactersLength);
        result += characters[randomIndex];
    }

    return result;
}

