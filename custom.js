/**
 * Jellyfin Recently Added Widget for Homepage
 */

function injectJellyfinPosters() {
    const targetCard = document.getElementById('jellyfin-recently-added');
    
    if (targetCard && !targetCard.dataset.loading && !targetCard.querySelector('.jellyfin-recent-grid')) {
        
        targetCard.dataset.loading = "true";
        
        console.log("Jellyfin Widget: Target found, fetching data...");

        const proxyApiUrl = "https://<JELLYFIN_PROXY_IP>:5000/recent";  /* Replace with Jellyfin Proxy Widget IP and Port */

        fetch(proxyApiUrl)
            .then(r => r.json())
            .then(data => {
                if (data.error || !Array.isArray(data)) {
                    console.error("Jellyfin Widget API Error:", data.error);
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
                    grid.appendChild(linkWrap);
                });

                const targetContainer = targetCard.querySelector('.flex.flex-col') || targetCard;
                targetContainer.appendChild(grid);
                
                console.log("Jellyfin Widget: Grid injected successfully.");
                delete targetCard.dataset.loading;
            })
            .catch(err => {
                console.error("Jellyfin Widget: Fetch failed:", err);
                delete targetCard.dataset.loading;
            });
    }
}

injectJellyfinPosters();

const observer = new MutationObserver(() => {
    injectJellyfinPosters();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
