import os
import time
import shutil
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from ruamel.yaml import YAML
from io import StringIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

CONFIG_PATH = '/app/config/dynamic.yml'
BACKUP_DIR = '/app/backups'
DEFAULT_RESOLVER = os.environ.get('CERT_RESOLVER', 'cloudflare')

DOMAINS_ENV = os.environ.get('DOMAINS', 'example.com')
AVAILABLE_DOMAINS = [d.strip() for d in DOMAINS_ENV.split(',') if d.strip()]
if not AVAILABLE_DOMAINS:
    AVAILABLE_DOMAINS = ['example.com']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 4096

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def create_backup():
    """Creates a timestamped backup of the dynamic.yml file."""
    ensure_backup_dir()
    if os.path.exists(CONFIG_PATH):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"dynamic.yml.{timestamp}.bak")
        shutil.copy2(CONFIG_PATH, backup_path)
        logger.info(f"Backup created: {backup_path}")
        return True
    return False

def load_config():
    """Loads the YAML config safely."""
    if not os.path.exists(CONFIG_PATH):
        return {"http": {"routers": {}, "services": {}, "middlewares": {}}}
    with open(CONFIG_PATH, 'r') as f:
        data = yaml.load(f)
        return data if data and isinstance(data, dict) else {"http": {"routers": {}, "services": {}, "middlewares": {}}}

def save_config(data):
    """Saves the YAML config."""
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(data, f)

@app.route('/')
def index():
    config = load_config()
    apps = []
    
    http_config = config.get('http', {})
    routers = http_config.get('routers', {})
    services = http_config.get('services', {})
    middlewares_dict = http_config.get('middlewares', {})
    
    for router_name, router_data in routers.items():
        service_name = router_data.get('service', '')
        
        target_url = "N/A"
        if service_name in services:
            servers = services[service_name].get('loadBalancer', {}).get('servers', [])
            if servers:
                target_url = servers[0].get('url', 'Unknown')

        apps.append({
            'id': router_name,
            'name': router_name,
            'rule': router_data.get('rule', ''),
            'service_name': service_name,
            'target': target_url,
            'middlewares': router_data.get('middlewares', []),
            'entryPoints': router_data.get('entryPoints', [])
        })

    middlewares = []
    for mw_name, mw_data in middlewares_dict.items():
        buf = StringIO()
        yaml.dump(mw_data, buf)
        middlewares.append({
            'name': mw_name,
            'yaml': buf.getvalue()
        })

    return render_template('index.html', apps=apps, domains=AVAILABLE_DOMAINS, middlewares=middlewares)

@app.route('/save', methods=['POST'])
def save_entry():
    try:
        svc_name = request.form.get('serviceName').strip()
        subdomain = request.form.get('subdomain', '').strip()
        domain = request.form.get('domain', AVAILABLE_DOMAINS[0]).strip()
        target_ip = request.form.get('targetIp').strip()
        target_port = request.form.get('targetPort').strip()
        middlewares_input = request.form.get('middlewares', '').strip()
        
        is_edit = request.form.get('isEdit') == 'true'
        original_id = request.form.get('originalId')

        router_name = svc_name
        service_name = f"{svc_name}-service"
        
        if '.' in subdomain:
            rule = f"Host(`{subdomain}`)"
        else:
            rule = f"Host(`{subdomain}.{domain}`)" if subdomain else f"Host(`{domain}`)"
            
        if not target_ip.startswith('http'):
            target_url = f"http://{target_ip}:{target_port}"
        else:
            target_url = f"{target_ip}:{target_port}"

        middlewares = [m.strip() for m in middlewares_input.split(',')] if middlewares_input else []

        create_backup()
        config = load_config()
        if 'http' not in config: config['http'] = {}
        if 'routers' not in config['http']: config['http']['routers'] = {}
        if 'services' not in config['http']: config['http']['services'] = {}

        if is_edit and original_id and original_id != router_name:
            if original_id in config['http']['routers']:
                del config['http']['routers'][original_id]
            old_svc_name = f"{original_id}-service"
            if old_svc_name in config['http']['services']:
                del config['http']['services'][old_svc_name]

        router_def = {
            'rule': rule,
            'entryPoints': ['https'],
            'tls': {'certResolver': DEFAULT_RESOLVER},
            'service': service_name
        }
        if middlewares:
            router_def['middlewares'] = middlewares
            
        config['http']['routers'][router_name] = router_def
        config['http']['services'][service_name] = {
            'loadBalancer': {'servers': [{'url': target_url}]}
        }

        save_config(config)
        flash(f"Successfully saved {svc_name}", "success")
    except Exception as e:
        logger.error(f"Error saving: {e}")
        flash(f"Error saving configuration: {e}", "error")

    return redirect(url_for('index'))

@app.route('/delete/<router_id>', methods=['POST'])
def delete_entry(router_id):
    try:
        create_backup()
        config = load_config()
        routers = config.get('http', {}).get('routers', {})
        services = config.get('http', {}).get('services', {})
        if router_id in routers:
            svc = routers[router_id].get('service')
            del routers[router_id]
            if svc in services: del services[svc]
            save_config(config)
            flash(f"Deleted {router_id}", "success")
    except Exception as e:
        logger.error(f"Delete error: {e}")
        flash(f"Error deleting: {e}", "error")
    return redirect(url_for('index'))

@app.route('/save-middleware', methods=['POST'])
def save_middleware():
    try:
        mw_name = request.form.get('middlewareName').strip()
        mw_content = request.form.get('middlewareContent').strip()
        is_edit = request.form.get('isMwEdit') == 'true'
        original_id = request.form.get('originalMwId')
        create_backup(); config = load_config()
        if 'middlewares' not in config['http']: config['http']['middlewares'] = {}
        if is_edit and original_id and original_id != mw_name:
            if original_id in config['http']['middlewares']:
                del config['http']['middlewares'][original_id]
        config['http']['middlewares'][mw_name] = yaml.load(mw_content)
        save_config(config)
        flash(f"Successfully saved middleware {mw_name}", "success")
    except Exception as e:
        logger.error(f"Middleware save error: {e}")
        flash(f"Error saving middleware: {e}", "error")
    return redirect(url_for('index'))

@app.route('/delete-middleware/<mw_name>', methods=['POST'])
def delete_middleware(mw_name):
    try:
        create_backup(); config = load_config()
        mws = config.get('http', {}).get('middlewares', {})
        if mw_name in mws:
            del mws[mw_name]; save_config(config)
            flash(f"Deleted middleware {mw_name}", "success")
    except Exception as e:
        logger.error(f"Middleware delete error: {e}")
        flash(f"Error deleting middleware: {e}", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG', 'false') == 'true')
