// YouTube Player API
let player;
let isHost = true; // For MVP, assume this client is the host. 

function onYouTubeIframeAPIReady() {
    player = new YT.Player('youtube-player', {
        height: '100%',
        width: '100%',
        videoId: '',
        playerVars: {
            'playsinline': 1,
            'controls': 1
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

function onPlayerReady(event) {
    console.log("Player Ready");
    fetchState();
}

function onPlayerStateChange(event) {
    // 0 = ENDED
    if (event.data === YT.PlayerState.ENDED) {
        playNext();
    }
}

// API Interaction
const API_BASE = "http://localhost:8000/api";

async function fetchState() {
    try {
        const response = await fetch(`${API_BASE}/state`);
        const data = await response.json();
        renderState(data);
    } catch (e) {
        console.error("Error fetching state:", e);
    }
}

async function suggestSong() {
    const input = document.getElementById('suggestion-input');
    const query = input.value.trim();
    if (!query) return;

    input.value = "Thinking...";
    input.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/suggest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });

        if (res.ok) {
            input.value = "";
            fetchState();
        } else {
            alert("Failed to find song.");
            input.value = query;
        }
    } catch (e) {
        console.error(e);
        input.value = query;
    } finally {
        input.disabled = false;
    }
}

async function vote(songId, type) {
    try {
        await fetch(`${API_BASE}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ song_id: songId, vote_type: type })
        });
        // In a real app, optimistic UI update
        // For now, just toast?
        console.log(`Voted ${type} for ${songId}`);
    } catch (e) {
        console.error(e);
    }
}

async function playNext() {
    try {
        const res = await fetch(`${API_BASE}/next`, { method: 'POST' });
        const song = await res.json();

        if (song && song.youtube_id && player) {
            player.loadVideoById(song.youtube_id);
            fetchState();
        }
    } catch (e) {
        console.error("Error playing next:", e);
    }
}

// Rendering
function renderState(data) {
    // Now Playing
    if (data.now_playing) {
        const song = data.now_playing;
        document.getElementById('np-title').innerText = song.title;
        document.getElementById('np-artist').innerText = song.artist;
        document.getElementById('np-art').src = song.thumbnail_url;

        // If player is idle/unstarted, maybe start it? (Auto-play logic needs care)
        if (player && player.getPlayerState() !== 1 && player.getPlayerState() !== 3) {
            // Check if the current loaded video is different
            const currentUrl = player.getVideoUrl();
            if (!currentUrl.includes(song.youtube_id)) {
                player.loadVideoById(song.youtube_id);
            }
        }
    } else {
        document.getElementById('np-title').innerText = "Nothing Playing";
        document.getElementById('np-artist').innerText = "Add a song or wait for AI...";
    }

    // Queue
    const list = document.getElementById('queue-list');
    list.innerHTML = '';

    data.queue.forEach(song => {
        const item = document.createElement('div');
        item.className = 'queue-item';
        item.innerHTML = `
            <img src="${song.thumbnail_url}" alt="art">
            <div class="queue-info">
                <span class="queue-title">${song.title}</span>
                <span class="queue-artist">${song.artist}</span>
            </div>
            <div class="vote-controls">
                <button class="btn-vote" onclick="vote(${song.id}, 'up')">▲</button>
                <button class="btn-vote" onclick="vote(${song.id}, 'down')">▼</button>
            </div>
        `;
        list.appendChild(item);
    });
}

// Polling
setInterval(fetchState, 5000);
