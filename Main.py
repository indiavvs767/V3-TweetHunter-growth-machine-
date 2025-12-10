import threading, signal, sys
from health import app as health_app
from werkzeug.serving import make_server

class HealthServerThread(threading.Thread):
    def __init__(self, app, host='0.0.0.0', port=8080):
        threading.Thread.__init__(self)
        self.srv = make_server(host, port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()

# before starting other threads:
health_port = int(os.getenv("HEALTH_PORT", "8080"))
health_thread = HealthServerThread(health_app, port=health_port)
health_thread.daemon = True
health_thread.start()
logger.info("Health server started on port %s", health_port)

def shutdown(signum, frame):
    logger.info("signal %s received: shutting down", signum)
    health_thread.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)
