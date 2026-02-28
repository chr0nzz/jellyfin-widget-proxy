  # 🎬 jellyfin-widget-proxy
  ---
  jellyfin-widget-proxy is a custom integration for the [Homepage](https://gethomepage.dev) dashboard that displays a beautiful, interactive poster grid of recently added movies and TV shows from your Jellyfin server via a lightweight proxy.
  ---

  ## ✨ Features

  * **Dynamic Poster Grid**: Automatically fetches and displays the latest high-quality media art.
  * **📱 Responsive Design**: Adaptable layout optimized for both desktop and mobile views.
  * **🔗 Direct Linking**: Click any poster to jump straight to that title in your Jellyfin web UI.
  * **🛠️ Lightweight Proxy**: Python-based backend that handles API security and cross-origin requests.
  * **🎨 Custom Styling**: Seamlessly integrates with Homepage's theme using custom CSS.

  ---

  ## 🖼️ Example of the Homepage widget in action.

  <p align="center">
    <img src="/images/widget.png?text=Jellyfin+Widget+Preview" alt="Widget Preview" width="35%">
  </p>

  ---

  # 🚀 Installation & Setup

  ## 1. Deploy the Proxy (Docker)
  The proxy securely communicates with the Jellyfin API and serves the data to the widget.

  #### Option A: Docker Compose (Recommended)
  Create a `docker-compose.yml` file:

  ```yaml
  services:
    jellyfin-widget-proxy:
      image: ghcr.io/chr0nzz/jellyfin-widget-proxy:latest
      container_name: jellyfin-widget-proxy
      restart: unless-stopped
      ports:
        - "5000:5000"
      environment:
        - JELLYFIN_URL=https://jellyfin.yourdomain.com
        - JELLYFIN_API_KEY=your_api_key_here
        - JELLYFIN_USER_ID=your_user_hex_id_here
        - LIMIT=6
  ```

  #### Option B: Docker Run
  ```bash
  docker run -d \
    --name jellyfin-widget-proxy \
    -p 5000:5000 \
    -e JELLYFIN_URL="https://jellyfin.yourdomain.com" \
    -e JELLYFIN_API_KEY="your_api_key_here" \
    -e JELLYFIN_USER_ID="your_user_hex_id_here" \
    -e LIMIT="6" \
    ghcr.io/chr0nzz/jellyfin-widget-proxy:latest
  ```

  ---

  ## 🛠 Build from Source
  If you want to build the image yourself instead of pulling from a registry:

  1. **Clone the repository**:
     ```bash
     git clone https://github.com/chr0nzz/jellyfin-widget-proxy.git
     cd jellyfin-widget-proxy
     ```

  2. **Build the Docker image**:
     ```bash
     docker build -t jellyfin-widget-proxy:local .
     ```

  3. **Run your local build**:
     ```bash
     docker run -d \
         --name jellyfin-widget-proxy \
         -p 5000:5000 \
         -e JELLYFIN_URL="https://jellyfin.yourdomain.com" \
         -e JELLYFIN_API_KEY="your_api_key_here" \
         -e JELLYFIN_USER_ID="your_user_hex_id_here" \
         -e LIMIT="6" \
         jellyfin-widget-proxy:local
     ```

  ---

  ## 🏠 Homepage Widget Configuration
  Add the following to your `services.yaml` file in Homepage. The `id` is required for the script to target this card.

  ```yaml
  - Media:
      - Latest Movies & Shows:
          id: jellyfin-recently-added
          #href: https://jellyfin.yourdomain.com
          #icon: sh-jellyfin
  ```

  ### Custom Scripts & Styles
  1. Copy the contents of [custom.js](/custom.js) into your Homepage `config/custom.js`.
  2. Copy the styles from [custom.css](/custom.css) into your Homepage `config/custom.css`.

  > [!IMPORTANT]
  > Ensure you update the `proxyApiUrl` variable in `custom.js` to point to your proxy container's IP (e.g., `http://192.168.1.100:5000/recent`).

  ---

  ## ⚙️ Environment Variables

  | Variable | Description | Example |
  | :--- | :--- | :--- |
  | `JELLYFIN_URL` | Full URL of your Jellyfin instance | `https://jellyfin.domain.com` |
  | `JELLYFIN_API_KEY` | Admin API Key (Dashboard > API Keys) | `7a8b9c0d...` |
  | `JELLYFIN_USER_ID` | The User ID to fetch recent items for | `00a11b22...` |
  | `LIMIT` | Number of posters to display | `6` |

  ---

  ## 🤝 Contributing
  Issues and pull requests are welcome! Feel free to open a ticket if you have suggestions for new features.

  ## 📄 License

  This project is licensed under the **GNU General Public License v3.0**.
  Copyright (C) 2026 chronzz (<https://github.com/chr0nzz>)
