const proxyApiUrl = "http://YOUR_PROXY_IP:5000/recent"; /* Update this with your proxy URL */

let fetchFailed = false;

function injectJellyfinPosters() {
    if (fetchFailed) return;

    const targetCard = document.getElementById('jellyfin-recently-added');

    if (!targetCard) return;
    if (targetCard.querySelector('.jellyfin-recent-grid')) return;
    if (targetCard.dataset.loading) return;

    targetCard.dataset.loading = "true";

    fetch(proxyApiUrl)
        .then(r => r.json())
        .then(data => {
            if (data.error || !Array.isArray(data)) {
                delete targetCard.dataset.loading;
                return;
            }

            const grid = document.createElement('div');
            grid.className = 'jellyfin-recent-grid';

            data.forEach(item => {
                const linkWrap = document.createElement('a');
                linkWrap.href = item.link;
                linkWrap.target = "_blank";
                linkWrap.className = 'jellyfin-recent-item';
                linkWrap.title = `${item.title} (${item.year})`;

                const img = document.createElement('img');
                img.src = item.poster;
                img.className = 'jellyfin-recent-poster';
                img.loading = "lazy";
                img.onerror = () => { img.src = 'https://via.placeholder.com/200x300?text=No+Poster'; };

                const badge = document.createElement('span');
                badge.className = 'jellyfin-recent-badge';
                badge.innerText = item.type === "TV" ? "TV" : "Movie";

                linkWrap.appendChild(img);
                linkWrap.appendChild(badge);

                if (item.type === "TV" && item.new_episodes > 1) {
                    const epBadge = document.createElement('span');
                    epBadge.className = 'jellyfin-recent-ep-badge';
                    epBadge.innerText = item.new_episodes;
                    linkWrap.appendChild(epBadge);
                }

                grid.appendChild(linkWrap);
            });

            const targetContainer = targetCard.querySelector('.flex.flex-col') || targetCard;
            targetContainer.appendChild(grid);

            delete targetCard.dataset.loading;
        })
        .catch(err => {
            fetchFailed = true;
            delete targetCard.dataset.loading;
        });
}

const observer = new MutationObserver(() => {
    const targetCard = document.getElementById('jellyfin-recently-added');
    if (!targetCard || !targetCard.querySelector('.jellyfin-recent-grid')) {
        fetchFailed = false;
    }
    injectJellyfinPosters();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

let pollCount = 0;
const poller = setInterval(() => {
    injectJellyfinPosters();
    pollCount++;
    if (pollCount >= 60) clearInterval(poller);
}, 500);
