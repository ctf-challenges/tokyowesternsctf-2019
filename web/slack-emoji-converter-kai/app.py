from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
)
import subprocess
import tempfile
import os

def convert_by_imagemagick(fname):
    proc = subprocess.run(["identify", "-format", "%w %h", fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.stdout, proc.stderr
    if len(out) == 0:
        return None
    w, h = list(map(int, out.decode("utf-8").split()))
    r = 128/max(w, h)
    proc = subprocess.run(["convert", "-resize", f"{int(w*r)}x{int(h*r)}", fname, fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.stdout, proc.stderr
    img = open(fname, "rb").read()
    os.unlink(fname)
    return img

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/source')
def source():
    return open(__file__).read()

@app.route('/policy.xml')
def imagemagick_policy_xml():
    return open("/etc/ImageMagick-6/policy.xml").read()

@app.route('/conv', methods=['POST'])
def conv():
    f = request.files.get('image', None)
    if not f:
        return redirect(url_for('index'))
    ext = f.filename.split('.')[-1]
    fname = tempfile.mktemp("emoji")
    fname = "{}.{}".format(fname, ext)
    f.save(fname)
    response = make_response()
    img = convert_by_imagemagick(fname)
    if not img:
        return redirect(url_for('index'))
    response.data = img
    response.headers['Content-Disposition'] = 'attachment; filename=emoji_{}'.format(f.filename)
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
