var currentFileId;

function setCurrentFileId(fileId) {
    var processLink = document.getElementById('process-link');
    processLink.style.display = 'block';
    currentFileId = fileId;
}

function processFile() {
    var processLink = document.getElementById('process-link').href + '?file=' + currentFileId;
    document.getElementById('process-link').href = processLink;
}

