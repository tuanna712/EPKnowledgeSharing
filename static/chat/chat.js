var preview = document.getElementById("preview");
var refNum = 3;
var searchNum = 1;

function openPreview(embedLink) {
    document.getElementById("preview").src = embedLink;
}

function handleKeyDown(event) {
    if (event.key === 'Enter') {
        // Prevent the default behavior of Enter key (e.g., new line)
        event.preventDefault();

        // Call sendMessage function when Enter key is pressed
        sendMessage();
    }
}

function createSummary(file) {
    var imageHtml = "";
    for (var i = 0; i < file.images.length; i++) {
        imageHtml += '<a style="height: 100%;" href=\'' + file.images[i] + '\' target="_blank"><img height="100%" width="auto" src=\'' + file.images[i] + '\' alt=""></a>'
    }
    const div = document.createElement('div');

    if (imageHtml.length == 0) {
        div.innerHTML = '<div class="p-2 d-flex justify-content-between" style="background-color: #DFF5FF;">' +
                                '<a target="_blank" href=\'' + file.file_redirect_url + '\' class="text-decoration-none fw-bold text-truncate" style="max-width: 80%;">' + file.file_name + '</a>' +
                                '<span class="text-secondary fst-italic">'+'Year: '+ file.year +' Page: ' + file.page_num + '</span>' +
                        '</div> '+
                        '<div class="p-2">' +
                            '<div class="fst-italic">Relevant information:</div>'+
                            '<div>\'' + file.text + '\'</div>' +
                            '<div class="fst-italic">No relevant images.</div>' +
                        '</div>';
    } else {
        div.innerHTML = '<div class="p-2 d-flex justify-content-between" style="background-color: #DFF5FF;">' +
        '<a target="_blank" href=\'' + file.file_redirect_url + '\' class="text-decoration-none fw-bold text-truncate" style="max-width: 80%;">' + file.file_name + '</a>' +
        '<span class="text-secondary fst-italic">'+'Year: '+ file.year +' Page: ' + file.page_num + '</span>' +
        '</div> '+
        '<div class="p-2">' +
        '<div class="fst-italic">Relevant information:</div>'+
        '<div>\'' + file.text + '\'</div>' +
        '<div class="fst-italic">Relevant images:</div>' +
        '<div class="hstack gap-1 overflow-x-auto" style="height: 30vh;">' +
        imageHtml
        '</div>' +
        '</div>';
    }

    return div;
}

async function sendMessage() {
    const inputBox = document.getElementById('inputBox');
    const message = inputBox.value;

    if (message.trim() !== '') {
        const chatbox = document.getElementById('chatbox');
        const newDiv = document.createElement('div');

        // Create user div
        const youTitle = document.createElement('div');
        youTitle.classList.add('fw-bold');
        youTitle.textContent = "You";
        newDiv.appendChild(youTitle);

        const newMessage = document.createElement('div');
        newMessage.textContent = message;
        newDiv.appendChild(newMessage);
        chatbox.appendChild(newDiv);


        // Clear the input box after sending a message
        inputBox.value = '';

        // Create chatbot div
        const chatbotDiv = document.createElement('div');

        const botTitle = document.createElement('div');
        botTitle.classList.add('fw-bold', 'text-info');
        botTitle.textContent = "AI Assistant";
        chatbotDiv.appendChild(botTitle);

        const replyStatus = document.createElement('div');
        replyStatus.classList.add('text-secondary', 'fst-italic', 'ms-3');
        const replyWait = document.createElement('div');
        const spinner = document.createElement('span');
        spinner.classList.add('spinner-border', 'spinner-border-sm', 'me-2');
        replyWait.appendChild(spinner);
        const replyWaitText = document.createElement('span');
        replyWaitText.textContent = "Generating response ..."
        replyWait.appendChild(replyWaitText);
        replyStatus.appendChild(replyWait);
        chatbotDiv.appendChild(replyStatus);
        chatbox.appendChild(chatbotDiv);
        chatbox.scrollTop = chatbox.scrollHeight;

        var summaryTab = document.getElementById('summary-tab');
        summaryTab.classList.add('d-flex', 'justify-content-center', 'align-items-center');
        summaryTab.innerHTML = 
        '<div><center><div class="spinner-grow spinner-grow-sm" role="status"></div></center><div class = "text-secondary">Fetching your results ...</div></div>'

        try {
            // Use `await` directly on the fetch call
            const data = await deliver(message);
            const reply = document.createElement('div');
            reply.textContent = data.reply;

            replyWait.removeChild(spinner);
            replyWait.removeChild(replyWaitText);
            chatbotDiv.appendChild(reply);

            // const learnMore = document.createElement('div');
            // const learnMoreText = document.createElement('span');
            // learnMoreText.classList.add('fw-bold');
            // learnMoreText.textContent = "Learn more:";
            // learnMore.appendChild(learnMoreText);
            // chatbotDiv.appendChild(learnMore);
            

            // const name = data.files[i].file_name;
            // const page = data.files[i].page_num;
            // const file_link = data.files[i].file_redirect_url;
            // html = '<a href="#" onclick="openPreview(\'' + file_link + '\')">' + name + '</a>'
            // + '<span class="ms-1 text-secondary fst-italic">pg.' + page + '</span>';
            // const ref = document.createElement('span');
            // ref.classList.add('badge', 'border', 'text-bg-light', 'text-decoration-none', 'fw-normal', 'ms-1');
            // ref.innerHTML = html;
            // learnMore.appendChild(ref);
            

            // Scroll to the bottom of the chatbox to show the latest message
            chatbox.scrollTop = chatbox.scrollHeight;
        } catch (error) {
            console.error('Error delivering message:', error.message);
        }
    }
}

async function getReferences(message) {
    var jsonSettings = {};
    jsonSettings['numRef'] = settings.numRef;
    jsonSettings['searchCoef'] = settings.searchCoef;
    jsonSettings['sortDescending'] = settings.sortDescending;
    jsonSettings['message'] = message;
    jsonSettings['list_files'] = getFileList();

    const csrftoken = getCookie('csrftoken');

    const refs = await fetch("refs/", {
        method: "POST",
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',
        body: JSON.stringify(jsonSettings),  // Wrap the message in an object
    });

    if (!refs.ok) {
        throw new Error('Network response was not ok');
    }
    // console.log(refs);
    const data = await refs.json();
    // console.log(data);
    return data;  // Return the parsed JSON response
}

async function deliver(message) {
    const csrftoken = getCookie('csrftoken');
    const refs = await getReferences(message);
    console.log(refs.refNum);

    var summaryTab = document.getElementById('summary-tab');
    summaryTab.classList.remove('d-flex', 'justify-content-center', 'align-items-center');
    summaryTab.innerHTML = "";

    //Check if refs.files is empty array
    const refNum = document.getElementById('refs-num').value;
    if (refNum > 0) {
        for (var i = 0; i < refNum; i++) { //refs.files.length <<== ERROR with .length function
            summaryTab.appendChild(createSummary(refs.files[i]));
        }
    }

    // Update list of filter files
    const unique_refs = Array.from(new Set(
        refs.files
            .filter(({ file_id, file_name }) => file_id && file_name)
            .map(({ file_id, file_name }) => JSON.stringify({ file_id, file_name }))
    )).map(JSON.parse);
    const fileListContainer = document.getElementById('files-filter');
    const files_ul = document.getElementById('file-list-ul');
    fileListContainer.removeChild(files_ul);
    showFileFilter(unique_refs);

    // Get final Chat response
    jsonInput = {
        'message': message,
        'refs': refs,
    }

    const response = await fetch("reply/", {
        method: "POST",
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',
        body: JSON.stringify(jsonInput),  // Wrap the message in an object
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return data;  // Return the parsed JSON response
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
const settings = {
    numRef: 10,
    searchCoef: 0.5,
    sortDescending: true,
}


function changeSettings() {
    const refNum = document.getElementById('refs-num').value;
    const searchCoefs = document.getElementById('search-coefs').value;
    const sortRefs = document.getElementById('sort-refs');

    if (refNum > 20) {
        alert("Maximum number of references is 20.")
        return;
    }
    if (searchNum < 0 || searchNum > 1) {
        alert("Must be in range 0 - 1.")
        return;
    }
    settings.numRef = refNum;
    settings.searchCoef = searchCoefs;
    if (sortRefs.checked) {
        settings.sortDescending = true;
    } else {
        settings.sortDescending = false;
    }
    console.log(settings);
    alert("Change successfully!")
}



function getFileList() {
    var file_ids = [];
    var checkboxes = document.querySelectorAll('input[type=checkbox]:checked');
    checkboxes.forEach(function (checkbox) {
        file_ids.push(checkbox.value);
    });
    console.log(file_ids);
    return file_ids;
}


async function getFileFilter() {
    const csrftoken = getCookie('csrftoken');

    const files = await fetch("files/", {
        method: "POST",
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        mode: 'same-origin',
    });

    if (!files.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await files.json();
    console.log("File ID sample: ",data.files[0].file_id);
    
    await showFileFilter(data.files);
    return data.files;  // Return the parsed JSON response
}

async function showFileFilter(files) {
    const fileListContainer = document.getElementById('files-filter');

    const fileListUl = document.createElement('ul');
    fileListUl.setAttribute('id', 'file-list-ul');
    fileListUl.classList.add('list-group', 'overflow-x-hidden');
    fileListUl.style.overflowY = 'auto';
    fileListUl.style.height = 'calc(100vh - 120px)';
    fileListContainer.appendChild(fileListUl);

    files.forEach(file => {
        const fileListLi = document.createElement('li');
        fileListLi.classList.add('list-group-item', 'd-flex', 'list-group-hover');

        const fileCheckbox = document.createElement('input');
        fileCheckbox.classList.add('form-check-input', 'me-2');
        fileCheckbox.type = 'checkbox';
        fileCheckbox.value = file.file_id;
        fileCheckbox.id = 'tick-' + file.file_id;
        fileCheckbox.addEventListener('change', getFileList);
        fileListLi.appendChild(fileCheckbox);

        const fileLabel = document.createElement('label');
        fileLabel.classList.add('form-check-label', 'fw-light');
        fileLabel.setAttribute('for', 'tick-' + file.file_id);
        fileLabel.style.fontSize = 'small';
        fileLabel.textContent = file.file_name;
        fileListLi.appendChild(fileLabel);

        fileListUl.appendChild(fileListLi);
    });
}