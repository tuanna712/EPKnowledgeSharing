var currentDisplay = null;

function displayImage(imagePath, page, id) {
    const a = document.getElementById(id)
    document.getElementById('image-display').src = imagePath;
    document.getElementById('image-caption').textContent = a.textContent;
    document.getElementById('image-property-caption').textContent = a.textContent;
    document.getElementById('image-property-page').textContent = page;
    currentDisplay = {
        'type': 'image',
        'caption': a.textContent,
        'page': page,
        'id': id
    }
}

function displayTable(tablePath, page, id) {
    const a = document.getElementById(id)
    document.getElementById('table-display').src = tablePath;
    document.getElementById('table-caption').textContent = a.textContent;
    document.getElementById('table-property-caption').textContent = a.textContent;
    document.getElementById('table-property-page').textContent = page;
    currentDisplay = {
        'type': 'table',
        'caption': a.textContent,
        'page': page,
        'id': id
    }
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

var changes = false;

async function saveComponent() {
    if (!changes) {
        alert("You haven't made any changes!");
        return;
    }
    
    try {
        const csrftoken = getCookie('csrftoken');
        const data = currentDisplay;

        const request = new Request (
            "update/",
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

        const response = await fetch(request);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const responseData = await response.text();
        changes = false;
        alert(responseData);
        document.getElementById(data['id']).textContent = data['caption']

    } catch (error) {
        console.error('Error:', error.message);
    }
}


function editImage() {
    if (currentDisplay === null) {
        alert("You haven't chose any image or table");
        return;
    }
    var caption = document.getElementById('image-property-caption');
    caption.contentEditable = "true";
    document.getElementById('image-property-caption').style.border = '1px solid black';

    var imageToolbar = document.getElementById('image-toolbar');
    imageToolbar.className = imageToolbar.className.replace("d-flex", "d-none");
    var imageEditToolBar = document.getElementById('image-edit-toolbar');
    imageEditToolBar.className = imageEditToolBar.className.replace("d-none", "d-flex");
}

function cancelEditImage() {
    document.getElementById('image-caption').textContent = currentDisplay.caption;
    document.getElementById('image-property-caption').textContent = currentDisplay.caption;
    document.getElementById('image-property-caption').contentEditable = "false";
    document.getElementById('image-property-caption').style.border = 'none';

    var imageToolbar = document.getElementById('image-toolbar');
    imageToolbar.className = imageToolbar.className.replace("d-none", "d-flex");
    var imageEditToolBar = document.getElementById('image-edit-toolbar');
    imageEditToolBar.className = imageEditToolBar.className.replace("d-flex", "d-none");
    changes = false;
}

function doneEditImage() {
    const newCaption = document.getElementById('image-property-caption').textContent;
    const oldCaption = currentDisplay.caption;

    currentDisplay.caption = newCaption;

    document.getElementById('image-property-caption').contentEditable = "false";
    document.getElementById('image-property-caption').style.border = 'none';
    var imageToolbar = document.getElementById('image-toolbar');
    imageToolbar.className = imageToolbar.className.replace("d-none", "d-flex");
    var imageEditToolBar = document.getElementById('image-edit-toolbar');
    imageEditToolBar.className = imageEditToolBar.className.replace("d-flex", "d-none");
    if (oldCaption == newCaption) {
        changes = false;
    } else {
        changes = true;
        document.getElementById('image-caption').textContent = currentDisplay.caption;
        document.getElementById(currentDisplay.id).textContent = currentDisplay.caption;
    }
}

function editTable() {
    if (currentDisplay === null) {
        alert("You haven't chose any image or table");
        return;
    }
    var caption = document.getElementById('table-property-caption');
    caption.contentEditable = "true";
    document.getElementById('table-property-caption').style.border = '1px solid black';

    var imageToolbar = document.getElementById('table-toolbar');
    imageToolbar.className = imageToolbar.className.replace("d-flex", "d-none");
    var imageEditToolBar = document.getElementById('table-edit-toolbar');
    imageEditToolBar.className = imageEditToolBar.className.replace("d-none", "d-flex");
}

function cancelEditTable() {
    document.getElementById('table-caption').textContent = currentDisplay.caption;
    document.getElementById('table-property-caption').textContent = currentDisplay.caption;
    document.getElementById('table-property-caption').contentEditable = "false";
    document.getElementById('table-property-caption').style.border = 'none';

    var toolbar = document.getElementById('table-toolbar');
    toolbar.className = toolbar.className.replace("d-none", "d-flex");
    var editToolbar = document.getElementById('table-edit-toolbar');
    editToolbar.className = editToolbar.className.replace("d-flex", "d-none");
    changes = false;
}

function doneEditTable() {
    const newCaption = document.getElementById('table-property-caption').textContent;
    const oldCaption = currentDisplay.caption;

    currentDisplay.caption = newCaption;

    document.getElementById('table-property-caption').contentEditable = "false";
    document.getElementById('table-property-caption').style.border = 'none';
    var toolbar = document.getElementById('table-toolbar');
    toolbar.className = toolbar.className.replace("d-none", "d-flex");
    var editToolbar = document.getElementById('table-edit-toolbar');
    editToolbar.className = editToolbar.className.replace("d-flex", "d-none");
    if (oldCaption == newCaption) {
        changes = false;
    } else {
        changes = true;
        document.getElementById('table-caption').textContent = currentDisplay.caption;
        document.getElementById(currentDisplay.id).textContent = currentDisplay.caption;
    }
}

async function deleteComponent(fileId) {
    currentDisplay.id = fileId;
    try {
        const csrftoken = getCookie('csrftoken');
        const data = currentDisplay;

        const request = new Request (
            "delete/",
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

        const response = await fetch(request);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const responseData = await response.text();
        changes = false;
        alert(responseData);
        const a = document.getElementById(data['id']);
        a.style.color = "red";
        a.textContent = "Deleted";
        a.style.fontStyle = "italic";

    } catch (error) {
        console.error('Error:', error.message);
    }
}
