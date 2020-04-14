import subprocess
import sys

from flask import render_template

from webapp import app
from webapp.configForm import ConfigForm


@app.route('/')
@app.route('/index')
def index():
    res_load_info = subprocess.run([sys.executable, 'main.py', 'load', '--info'], stdout=subprocess.PIPE, text=True)

    res_show = subprocess.run([sys.executable, 'main.py', 'show'], stdout=subprocess.PIPE, text=True)
    context = dict(load_info=format(res_load_info.stdout), show=format(res_show.stdout))

    return render_template('index.html', title='Home', context=context)


@app.route('/staging')
def staging():
    res = subprocess.run([sys.executable, 'main.py', 'show'], stdout=subprocess.PIPE, text=True)
    context = dict(output=format(res.stdout))

    return render_template('staging.html', title='Staging', context=context)


@app.route('/load')
def load():
    res_load = subprocess.run([sys.executable, 'main.py', 'load', '--strava'], stdout=subprocess.PIPE, text=True)
    res_status = subprocess.run([sys.executable, 'main.py', 'show'], stdout=subprocess.PIPE, text=True)
    context = dict(message=format(res_load.stdout), output=format(res_status.stdout))

    return render_template('staging.html', title='Staging', context=context)


@app.route('/config', methods=['GET', 'POST'])
def config():
    res = subprocess.run([sys.executable, 'main.py', 'config', '--list'], stdout=subprocess.PIPE, text=True)

    context = dict(output=format(res.stdout))

    data = format_config_list(res.stdout)

    form = ConfigForm(port=data['port'],
                      velohero_sso_id=data['velohero_sso_id'],
                      strava_client_id=data['strava_client_id'],
                      strava_description__BY__strava_name=data['strava_description__BY__strava_name'],
                      strava_description__BY__training_type=data['strava_description__BY__training_type'],
                      strava_reset=False
                      )

    if form.is_submitted():
        message = []
        err = False

        if form.validate():
            if form.port.data != data['port']:
                ret = subprocess.run([sys.executable, 'main.py', 'config', '--port', str(form.port.data)],
                                     stdout=subprocess.PIPE, text=True)
                if ret.returncode != 0:
                    message.append(f"Update 'port' failed !")
                    err = True

            if form.velohero_sso_id.data != data['velohero_sso_id']:
                ret = subprocess.run(
                    [sys.executable, 'main.py', 'config', '--velohero_sso_id', str(form.velohero_sso_id.data)],
                    stdout=subprocess.PIPE, text=True)
                if ret.returncode != 0:
                    message.append(f"Update 'velohero_sso_id' failed !")
                    err = True

            if form.strava_description__BY__strava_name.data != data['strava_description__BY__strava_name']:
                if len("form.strava_description__BY__strava_name.data") > 0:
                    if data['strava_description__BY__strava_name'].count("?") == 1:
                        parts = data['strava_description__BY__strava_name'].split("?",1 )
                        value = f"strava_name({parts[0]})?{parts[1]}"
                        ret = subprocess.run(
                            [sys.executable, 'main.py', 'config', '--strava_description', value],
                            stdout=subprocess.PIPE, text=True)
                        if ret.returncode != 0:
                            message.append(f"Update 'strava_description__BY__strava_name' failed !")
                            err = True
                    else:
                        message.append(f"'strava_description__BY__strava_name': Invalid value !")
                        err = True

            # print(f"form.strava_client_id.data={form.strava_client_id.data}, data={data['strava_client_id']}")
            # TODO fehler in heroscript
            if form.strava_client_id.data != data['strava_client_id']:
                ret = subprocess.run(
                    [sys.executable, 'main.py', 'config', '--strava_client_id', form.strava_client_id.data],
                    stdout=subprocess.PIPE, text=True)
                if ret.returncode != 0:
                    message.append(f"Update 'strava_client_id' failed !")
                    err = True

            if form.strava_reset.data:
                ret = subprocess.run([sys.executable, 'main.py', 'config', '--strava_reset'],
                                     stdout=subprocess.PIPE, text=True)
                if ret.returncode != 0:
                    message.append("Strava reset failed !")
                    err = True

        else:
            err = True
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    message.append(f"{fieldName}: '{err}'")

        if err is False:
            message.append("Saved !")
            res = subprocess.run([sys.executable, 'main.py', 'config', '--list'], stdout=subprocess.PIPE, text=True)
            context = dict(output=format(res.stdout))

        context['message'] = message

    # Always set to false in the UI
    form.strava_reset.data = False

    return render_template('config.html', title='Config', form=form, context=context)


@app.route('/masterdata/show')
def masterdata_show():
    res = subprocess.run([sys.executable, 'main.py', 'masterdata', '--list'], stdout=subprocess.PIPE, text=True)

    context = dict(output=format(res.stdout))

    return render_template('masterdata.html', title='Masterdata', context=context)


@app.route('/masterdata/update')
def masterdata_update():
    res_refresh = subprocess.run([sys.executable, 'main.py', 'masterdata', '--refresh'], stdout=subprocess.PIPE,
                                 text=True)
    res_list = subprocess.run([sys.executable, 'main.py', 'masterdata', '--list'], stdout=subprocess.PIPE, text=True)

    context = dict(output=format(res_list.stdout), message=format(res_refresh.stdout))

    return render_template('masterdata.html', title='Masterdata', context=context)


def format_config_list(text):
    """"
    Returns a dictionary with key value pairs and one special key 'descriptions' with a list
    """
    ret = dict()

    for line in format(text):
        if ": " in line:
            (key, value) = line.split(": ", 1)
            ret[key.strip()] = value.strip()

    # It's easier if there is always an item
    if not 'strava_description__BY__strava_name' in ret:
        ret['strava_description__BY__strava_name'] = ""
    if not 'strava_description__BY__training_type' in ret:
        ret['strava_description__BY__training_type'] = ""
    return ret


def format(text):
    """"
    Returns a list with lines
    """
    return text.split("\n")
