"""SkillGap Quest: tiny local server. Run: python server.py  (opens http://localhost:8000)"""
import http.server, socketserver, os, webbrowser
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))
PORT = int(os.environ.get("PORT", 8000))
with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as srv:
    print(f"SkillGap Quest running at http://localhost:{PORT}  (Ctrl+C to stop)")
    webbrowser.open(f"http://localhost:{PORT}")
    srv.serve_forever()
