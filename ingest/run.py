from plugin_manager import PluginManager
from app import app
from config import LISTEN_PORT, DEBUG


if __name__ == "__main__":
    pm = PluginManager()
    pm.load_plugins()

    if DEBUG:
        app.jinja_env.auto_reload = True
        app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host="0.0.0.0", debug=DEBUG, port=LISTEN_PORT)
