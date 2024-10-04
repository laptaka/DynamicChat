const socket = io();
const messageBox = document.getElementById('chat');
const animationContainer = document.getElementById('animation-container');
const audioPlayer = document.getElementById('audioPlayer');
const spotify = document.getElementById('spotify');

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('ping', (callback) => {
    callback();
});

const emoteCache = new Map();

async function fetchEmoteInfo(emoteNames) {
    const uncachedEmotes = emoteNames.filter(name => !emoteCache.has(name));
    if (uncachedEmotes.length === 0) {
        return emoteNames.map(name => emoteCache.get(name));
    }

    const response = await fetch(`/emote-info?emotes=${uncachedEmotes.join(',')}`);
    if (response.ok) {
        const emoteInfo = await response.json();
        emoteInfo.forEach(info => {
            if (info) {
                emoteCache.set(info.name, info);
            }
        });
        return emoteNames.map(name => emoteCache.get(name));
    }
    return emoteNames.map(() => null);
}

function replaceEmotesWithImages(message) {
    const words = message.split(' ');
    const potentialEmotes = words.filter(word => word.length >= 2 && /^[a-zA-Z0-9]+$/.test(word));
    return fetchEmoteInfo(potentialEmotes).then(emoteInfos => {
        return words.map(word => {
            const emoteInfo = emoteInfos.find(info => info && info.name === word);
            if (emoteInfo && emoteInfo.url) {
                return `<img src="${emoteInfo.url}" alt="${word}" class="emote" title="${word}">`;
            }
            return word;
        }).join(' ');
    });
}

socket.on('message_update', async (data) => {
    const messageWithEmotes = await replaceEmotesWithImages(data.message);

    messageBox.innerHTML = `
        <div id="rectangle">
            <p class="username ${data.isDonation ? 'donation' : ''}" style="color: ${data.isDonation ? '#ff0000' : data.color}">
                ${data.username}${data.isDonation ? ` • ${data.amount}$` : ''}
            </p>
            <p class="message" style="font-weight: ${data.isDonation ? '600' : '400'}">${messageWithEmotes}</p>
        </div>
        `;
    if (data.isDonation) {
        animateBackgroundColor(data.audioDuration);
        if (data.audio) {
            playAudio(data.audio);
        }
    }
    adjustFontSize();
});

messageBox.addEventListener('click', () => {
    skipMessage();
});

spotify.addEventListener('click', () => {
    setDefaultSpotify();
});

function skipMessage() {
    animationContainer.innerHTML = '';
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    messageBox.innerHTML = `
        <div id="rectangle">
            <p class="message">Skipped...</p>
        </div>
        `;
    socket.emit('skip_message');
}

function playAudio(audioData) {
    const blob = new Blob([Uint8Array.from(audioData, c => c.charCodeAt(0))], { type: 'audio/mp3' });
    const url = URL.createObjectURL(blob);
    audioPlayer.src = url;
    audioPlayer.volume = 0.7;

    const staticAudio = new Audio('../static/d3.ogg');
    staticAudio.volume = 0.1;
    staticAudio.play();

    setTimeout(() => {
        fadeVolume(staticAudio, 0.05, 1000);
    }, 1000);

    setTimeout(() => {
        audioPlayer.play();
    }, 2000);
}

function fadeVolume(audioElement, targetVolume, duration) {
    const initialVolume = audioElement.volume;
    const volumeChange = targetVolume - initialVolume;
    const stepTime = 50;
    const steps = duration / stepTime;
    let currentStep = 0;

    const fadeInterval = setInterval(() => {
        currentStep++;
        audioElement.volume = initialVolume + (volumeChange * (currentStep / steps));
        if (currentStep >= steps) {
            clearInterval(fadeInterval);
        }
    }, stepTime);
}

function animateBackgroundColor(audioDuration) {
    const rectangle = document.getElementById('rectangle');

    setTimeout(() => {
        rectangle.style.transition = 'none';
        rectangle.offsetHeight;
        rectangle.style.transition = 'background-color 0.5s ease';
        rectangle.style.backgroundColor = 'rgba(54, 53, 55, 1)';
    }, 500);

    const endTime = Math.max(audioDuration);

    setTimeout(() => {
        rectangle.style.transition = 'background-color 2s ease';
        rectangle.style.backgroundColor = 'rgba(54, 53, 55, 0.9)';
    }, endTime * 1000 + 2);
}

function adjustFontSize() {
    const rectangle = document.getElementById('rectangle');
    const message = rectangle.querySelector('.message');
    const maxHeight = 60;
    let fontSize = 25;

    message.style.fontSize = `${fontSize}px`;

    while (message.scrollHeight > maxHeight && fontSize > 12) {
        fontSize--;
        message.style.fontSize = `${fontSize}px`;
    }

    if (message.scrollHeight > maxHeight) {
        message.style.textOverflow = 'ellipsis';
    } else {
        message.style.textOverflow = 'clip';
    }
}

function adjustSpotifyFontSize() {
    const trackName = document.getElementById('track-name');
    const artistName = document.getElementById('artist-name');
    const maxHeight = 30;
    let trackFontSize = 22;
    let artistFontSize = 18;

    trackName.style.fontSize = `${trackFontSize}px`;
    artistName.style.fontSize = `${artistFontSize}px`;

    while (trackName.scrollHeight > maxHeight && trackFontSize > 12) {
        trackFontSize--;
        trackName.style.fontSize = `${trackFontSize}px`;
    }

    while (artistName.scrollHeight > maxHeight && artistFontSize > 12) {
        artistFontSize--;
        artistName.style.fontSize = `${artistFontSize}px`;
    }
}

function updateSpotifyInfo(track) {
    const trackName = document.getElementById('track-name');
    const artistName = document.getElementById('artist-name');
    const albumCover = document.getElementById('album-cover');

    if (track == "paused") {
        trackName.style.color = 'lightgray';
        artistName.style.color = 'lightgray';
        albumCover.style.filter = 'grayscale(70%)';
    }

    if (track != "paused" && track) {
        trackName.style.color = 'white';
        artistName.style.color = 'white';
        albumCover.style.filter = 'grayscale(0%)';
        trackName.textContent = track.name;
        artistName.textContent = track.artist;
        if (track.album_cover != "None") {
            albumCover.src = track.album_cover;
        } else {
            albumCover.src = '../static/spotify.png';
        }
    } else if (track != "paused") {
        trackName.textContent = 'No track playing!';
        artistName.textContent = '';
        albumCover.src = '../static/spotify.png';
    }

    adjustSpotifyFontSize();
}

socket.on('spotify_update', (data) => {
    updateSpotifyInfo(data);
});

socket.on('paused', () => {
    updateSpotifyInfo("paused");
});

updateSpotifyInfo(null);

function setDefaultSpotify() {
    updateSpotifyInfo(null);
}
