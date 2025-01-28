// worker.js

onmessage = function (e) {
    if (e.data.command === 'start') {
        captureInterval = e.data.interval || captureInterval;
        startCapturing();
    } else if (e.data.command === 'stop') {
        clearInterval(captureTimer);
    }
};

let captureTimer;

function startCapturing() {
    captureTimer = setInterval(() => {
        postMessage('capture');
    }, captureInterval);
}
