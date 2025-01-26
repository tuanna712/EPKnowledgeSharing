function processFile(fileId) {
    var processLink = document.getElementById(fileId).href + '?file=' + fileId;
    document.getElementById(fileId).href = processLink;
}

async function deleteFile(fileId) {
    try {
        const csrftoken = getCookie('csrftoken');
        const data = {
            'id': fileId,
            'type': 'file'
        };

        const request = new Request (
            "/process/delete/",
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
        const a = document.getElementById("button-" + data['id'])
        a.style.color = "red";
        a.textContent = "Deleted";
        a.style.fontStyle = "italic";

    } catch (error) {
        console.error('Error:', error.message);
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