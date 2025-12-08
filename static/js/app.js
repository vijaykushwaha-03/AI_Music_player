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
            'controls': 1,
            'autoplay': 1,  // Enable autoplay
            'mute': 0,      // Start unmuted
            'enablejsapi': 1
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

function onPlayerReady(event) {
    console.log("Player Ready");

    // FINAL AGGRESSIVE AUDIO FIX
    player.unMute();
    player.setVolume(100);

    fetchState();

    // Setup ALL interaction listeners for audio
    setupAudioEnablement();
}

function onPlayerStateChange(event) {
    const playIcon = document.getElementById('play-icon');

    // Update play/pause icon based on state
    if (event.data === YT.PlayerState.PLAYING) {
        if (playIcon) playIcon.textContent = '⏸️';
        startProgressUpdates();
    } else if (event.data === YT.PlayerState.PAUSED) {
        if (playIcon) playIcon.textContent = '▶️';
        stopProgressUpdates();
    } else if (event.data === YT.PlayerState.ENDED) {
        if (playIcon) playIcon.textContent = '▶️';
        stopProgressUpdates();
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
let currentPlayingId = null; // Track what's actually playing
let audioEnabled = false; // Track if user has interacted

function renderState(data) {
    // Now Playing
    if (data.now_playing) {
        const song = data.now_playing;
        document.getElementById('np-title').innerText = song.title;
        document.getElementById('np-artist').innerText = song.artist;
        document.getElementById('np-art').src = song.thumbnail_url;

        // Auto-play logic: If we have a new song in now_playing, start it!
        if (player && song.youtube_id && currentPlayingId !== song.youtube_id) {
            console.log(`Loading new song: ${song.title} (${song.youtube_id})`);
            player.loadVideoById(song.youtube_id);
            currentPlayingId = song.youtube_id;

            // AGGRESSIVE: Try to play immediately
            setTimeout(() => {
                forcePlay();
            }, 500);
        }
    } else {
        document.getElementById('np-title').innerText = "Nothing Playing";
        document.getElementById('np-artist').innerText = "Add a song or wait for AI...";
        currentPlayingId = null;
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
                <button class="btn-vote" onclick="toggleFavorite(${song.id})" style="color: ${song.is_favorite ? 'red' : 'inherit'}">❤</button>
            </div>
        `;
        list.appendChild(item);
    });

    // Update Heart on Now Playing
    const heartBtn = document.getElementById('np-heart');
    if (data.now_playing) {
        heartBtn.innerText = data.now_playing.is_favorite ? '❤️' : '🤍';
        currentPlayingId = data.now_playing.id; // Ensure ID is set for toggle
    }
}

async function toggleFavorite(songId) {
    if (!songId) return;
    try {
        await fetch(`${API_BASE}/favorite/${songId}`, { method: 'POST' });
        fetchState(); // Refresh UI
    } catch (e) {
        console.error("Error toggling favorite:", e);
    }
}

async function createPlaylist() {
    const name = prompt("Enter playlist name:");
    if (!name) return;
    try {
        await fetch(`${API_BASE}/playlists`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name })
        });
        fetchPlaylists();
    } catch (e) {
        console.error("Error creating playlist:", e);
    }
}

async function fetchPlaylists() {
    try {
        const res = await fetch(`${API_BASE}/playlists`);
        const playlists = await res.json();
        const list = document.getElementById('playlist-list');
        list.innerHTML = '';
        playlists.forEach(pl => {
            const li = document.createElement('li');
            li.style.padding = '5px 0';
            li.style.cursor = 'pointer';
            li.innerText = `🎵 ${pl.name}`;
            list.appendChild(li);
        });
    } catch (e) {
        console.error("Error fetching playlists:", e);
    }
}

async function fetchRecommendations() {
    try {
        const res = await fetch(`${API_BASE}/recommendations`);
        const songs = await res.json();
        const list = document.getElementById('recommendations-list');
        list.innerHTML = '';
        songs.forEach(song => {
            const item = document.createElement('div');
            item.className = 'recommendation-item';
            item.style.minWidth = '150px';
            item.style.cursor = 'pointer';
            item.onclick = () => suggestSong(song.title + " " + song.artist); // Hacky way to queue
            item.innerHTML = `
                <img src="${song.thumbnail_url}" style="width: 100%; border-radius: 10px; margin-bottom: 5px;">
                <div style="font-size: 0.9rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${song.title}</div>
                <div style="font-size: 0.8rem; color: gray;">${song.artist}</div>
            `;
            list.appendChild(item);
        });
    } catch (e) {
        console.error("Error fetching recommendations:", e);
    }
}

// Initial fetches
fetchPlaylists();
fetchRecommendations();

// Polling
setInterval(fetchState, 5000);

// ============ PLAYBACK CONTROLS ============

let progressUpdateInterval = null;

// Play/Pause Toggle
function togglePlayPause() {
    if (!player) return;

    const state = player.getPlayerState();
    const playIcon = document.getElementById('play-icon');

    if (state === YT.PlayerState.PLAYING) {
        player.pauseVideo();
        playIcon.textContent = '▶️';
        stopProgressUpdates();
    } else {
        player.playVideo();
        playIcon.textContent = '⏸️';
        startProgressUpdates();
    }
}

// Play Next Song
function playNextSong() {
    playNext(); // Uses existing function
}

// Play Previous Song (Mockup for now)
function playPreviousSong() {
    if (player && player.getCurrentTime() > 3) {
        player.seekTo(0);
    } else {
        // In a real app, fetch previous from history
        console.log("Previous song requested (not implemented in backend yet)");
        player.seekTo(0);
    }
}

// Toggle Shuffle
let isShuffle = false;
function toggleShuffle() {
    isShuffle = !isShuffle;
    const btn = document.getElementById('shuffle-btn');
    if (isShuffle) {
        btn.classList.add('active');
    } else {
        btn.classList.remove('active');
    }
    console.log("Shuffle:", isShuffle);
}

// Toggle Repeat
let isRepeat = false;
function toggleRepeat() {
    isRepeat = !isRepeat;
    const btn = document.getElementById('repeat-btn');
    if (isRepeat) {
        btn.classList.add('active');
        // If repeat is on, we might want to loop the video
        if (player) player.setLoop(true);
    } else {
        btn.classList.remove('active');
        if (player) player.setLoop(false);
    }
    console.log("Repeat:", isRepeat);
}

// Format seconds to MM:SS
function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Update Progress Bar
function updateProgress() {
    if (!player || !player.getDuration) return;

    try {
        const currentTime = player.getCurrentTime();
        const duration = player.getDuration();

        if (duration > 0) {
            const progress = (currentTime / duration) * 100;
            document.getElementById('progress-bar').value = progress;
            document.getElementById('current-time').textContent = formatTime(currentTime);
            document.getElementById('total-time').textContent = formatTime(duration);
        }
    } catch (e) {
        console.error('Error updating progress:', e);
    }
}

// Start Progress Updates
function startProgressUpdates() {
    stopProgressUpdates(); // Clear any existing interval
    progressUpdateInterval = setInterval(updateProgress, 1000);
}

// Stop Progress Updates
function stopProgressUpdates() {
    if (progressUpdateInterval) {
        clearInterval(progressUpdateInterval);
        progressUpdateInterval = null;
    }
}

// Event Listeners for Controls
document.addEventListener('DOMContentLoaded', function () {
    const progressBar = document.getElementById('progress-bar');
    const volumeSlider = document.getElementById('volume-slider');
    const volumeIcon = document.getElementById('volume-icon');

    // Progress bar seek
    if (progressBar) {
        progressBar.addEventListener('input', function () {
            if (!player || !player.getDuration) return;

            try {
                const duration = player.getDuration();
                const seekTime = (this.value / 100) * duration;
                player.seekTo(seekTime, true);
            } catch (e) {
                console.error('Error seeking:', e);
            }
        });
    }

    // Volume control
    if (volumeSlider) {
        volumeSlider.addEventListener('input', function () {
            if (!player) return;

            try {
                const volume = parseInt(this.value);
                player.setVolume(volume);

                // Update volume icon
                if (volume === 0) {
                    volumeIcon.textContent = '🔇';
                } else if (volume < 50) {
                    volumeIcon.textContent = '🔉';
                } else {
                    volumeIcon.textContent = '🔊';
                }
            } catch (e) {
                console.error('Error setting volume:', e);
            }
        });
    }

    // Volume icon click to mute/unmute (works with both regular and modern class names)
    if (volumeIcon) {
        volumeIcon.addEventListener('click', function () {
            if (!player) return;

            try {
                if (player.isMuted()) {
                    player.unMute();
                    const volume = player.getVolume();
                    if (volumeSlider) volumeSlider.value = volume;
                    volumeIcon.textContent = volume < 50 ? '🔉' : '🔊';
                } else {
                    player.mute();
                    volumeIcon.textContent = '🔇';
                }
            } catch (e) {
                console.error('Error toggling mute:', e);
            }
        });
    }

    // Search input Enter key listener
    const suggestionInput = document.getElementById('suggestion-input');
    if (suggestionInput) {
        suggestionInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                suggestSong();
            }
        });
    }
});

// ============ AGGRESSIVE AUTOPLAY FIX ============

// Force play with retry mechanism
function forcePlay(retryCount = 0) {
    if (!player) return;

    try {
        const state = player.getPlayerState();
        console.log(`Force play attempt ${retryCount + 1}, state: ${state}`);

        // Unmute and set volume
        player.unMute();
        player.setVolume(100);

        // Try to play
        player.playVideo();

        // Update UI
        const playIcon = document.getElementById('play-icon');
        if (playIcon) playIcon.textContent = '⏸️';

        // Verify playback started
        setTimeout(() => {
            const newState = player.getPlayerState();
            if (newState !== YT.PlayerState.PLAYING && retryCount < 5) {
                console.log(`Playback not started (state: ${newState}), retrying...`);
                forcePlay(retryCount + 1);
            } else if (newState === YT.PlayerState.PLAYING) {
                console.log('✅ Playback successfully started!');
                audioEnabled = true;
                startProgressUpdates();
            }
        }, 1000);
    } catch (e) {
        console.error('Error forcing play:', e);
        if (retryCount < 5) {
            setTimeout(() => forcePlay(retryCount + 1), 1000);
        }
    }
}

// Add listener to enable audio on first user interaction
function addAudioEnableListener() {
    const enableAudio = () => {
        if (!audioEnabled && player) {
            console.log('User interaction detected - enabling audio');
            forcePlay();
            audioEnabled = true;
        }
    };

    // Listen for any user interaction
    ['click', 'touchstart', 'keydown'].forEach(event => {
        document.addEventListener(event, enableAudio, { once: true });
    });

    // Also add visual prompt
    showAudioPrompt();
}

// Show visual prompt to click for audio
function showAudioPrompt() {
    const prompt = document.createElement('div');
    prompt.id = 'audio-prompt';
    prompt.innerHTML = '🔊 Click anywhere to enable audio';
    prompt.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 50px;
        font-weight: 600;
        z-index: 10000;
        cursor: pointer;
        animation: pulse 2s infinite;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    `;

    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0%, 100% { transform: translateX(-50%) scale(1); }
            50% { transform: translateX(-50%) scale(1.05); }
        }
    `;
    document.head.appendChild(style);

    prompt.addEventListener('click', () => {
        forcePlay();
        prompt.remove();
    });

    document.body.appendChild(prompt);

    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (prompt.parentNode) {
            prompt.remove();
        }
    }, 10000);
}

// Setup audio enablement on player ready
function setupAudioEnablement() {
    addAudioEnableListener();
}
