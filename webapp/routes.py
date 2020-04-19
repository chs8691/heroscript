import re
from os import path, scandir
import subprocess
import sys
import json
from datetime import datetime

from flask import render_template

from webapp import app
from webapp.configForm import ConfigForm
from webapp.downloadForm import DownloadForm
import config as heroscript_config


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


@app.route('/download', methods=['GET', 'POST'])
def download():

    res = subprocess.run([sys.executable, 'main.py', 'download', '--info'], stdout=subprocess.PIPE, text=True)
    output = format(res.stdout)

    if output[0].startswith("Last downloaded activity"):
        default = "N"
    else:
        default = "L"

    form = DownloadForm(type=default,
                        nr_of_latest = 5,)

    message = []
    if form.is_submitted():
        err = False

        if form.validate():

            if form.type == "L" and not form.nr_of_latest > 0:
                message.append("L wrong")
                message.append("Missing number of activities !")
                err = True
            else:
                print(f"form.type={form.type.data}")
                if form.type.data == "L":
                    args = [sys.executable, 'main.py', 'download', '--count', str(form.nr_of_latest.data)]
                else:
                    args = [sys.executable, 'main.py', 'download']

                print(f"args={args}")
                with subprocess.Popen(args,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True,
                                     text=True) as p:

                    # Doesn't flush for garmin but flushs for pings. Why?
                    for line in p.stdout:
                        print(line, end='', flush=True)
                        message.append(line)

                    # Print the rest
                    for line in p.stdout.readlines():
                        print(line)
                        message.append(line)

                    # Print the rest
                    for line in p.stderr.readlines():
                        print(line)
                        message.append(line)

                print("done")
                res = subprocess.run([sys.executable, 'main.py', 'download', '--info'], stdout=subprocess.PIPE, text=True)
                output = format(res.stdout)

        else:
            err = True
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    message.append(f"{fieldName}: '{err}'")

    context = dict(output = output, message=message)

    return render_template('download.html', title='Donwload', form=form, context=context)


@app.route('/config', methods=['GET', 'POST'])
def config():

    res = subprocess.run([sys.executable, 'main.py', 'config', '--list'], stdout=subprocess.PIPE, text=True)
    data = format_config_list(res.stdout)


    form = ConfigForm(port=data['port'],
                      velohero_sso_id=data['velohero_sso_id'],
                      strava_client_id=data['strava_client_id'],
                      garmin_connect_username = data['garmin_connect_username'],
                      garmin_connect_password = data['garmin_connect_password'],
                      strava_description__BY__strava_name=data['strava_description__BY__strava_name'],
                      strava_description__BY__training_type=data['strava_description__BY__training_type'],
                      strava_reset=False
                      )

    message = []
    if form.is_submitted():
        err = False

        if form.validate():
            if form.port.data != data['port']:
                if form.port.data < 1:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'port'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Delete 'port' failed !")
                        err = True
                else:
                    ret = subprocess.run([sys.executable, 'main.py', 'config', '--port', str(form.port.data)],
                                         stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Update 'port' failed !")
                        err = True

            if form.velohero_sso_id.data != data['velohero_sso_id']:
                if len(form.velohero_sso_id.data) == 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'velohero_sso_id'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Delete 'velohero_sso_id    ' failed !")
                        err = True
                else:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--velohero_sso_id', str(form.velohero_sso_id.data)],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Update 'velohero_sso_id' failed !")
                        err = True

            if form.garmin_connect_username.data != data['garmin_connect_username']:
                if len(form.garmin_connect_username.data) == 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'garmin_connect_username'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Delete 'garmin_connect_username    ' failed !")
                        err = True
                else:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--garmin_connect_username', str(form.garmin_connect_username.data)],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Update 'garmin_connect_username' failed !")
                        err = True

            if form.garmin_connect_password.data != data['garmin_connect_password']:
                if len(form.garmin_connect_password.data) == 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'garmin_connect_password'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Delete 'garmin_connect_password    ' failed !")
                        err = True
                else:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--garmin_connect_password', str(form.garmin_connect_password.data)],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Update 'garmin_connect_password' failed !")
                        err = True



            if form.strava_description__BY__strava_name.data != data['strava_description__BY__strava_name']:
                value = None
                if len(form.strava_description__BY__strava_name.data) > 0:
                    if form.strava_description__BY__strava_name.data.count("?") == 1:
                        parts = form.strava_description__BY__strava_name.data.split("?",1)
                        value = f"strava_name({parts[0]})?{parts[1]}"
                    else:
                        message.append(f"'strava_description__BY__strava_name': Invalid value !")
                        err = True
                else:
                    value = ""

                if not err:
                    print(f"data='{value}'")
                    if len(value) == 0:
                        ret = subprocess.run(
                            [sys.executable, 'main.py', 'config', '--delete', 'strava_description__BY__strava_name'],
                            stdout=subprocess.PIPE, text=True)
                        if ret.returncode != 0:
                            message.append(f"Delete 'strava_description__BY__strava_name' failed !")
                            err = True

                    else:
                        ret = subprocess.run(
                            [sys.executable, 'main.py', 'config', '--strava_description', value],
                            stdout=subprocess.PIPE, text=True)
                        if ret.returncode != 0:
                            message.append(f"Update 'strava_description__BY__strava_name' failed !")
                            err = True

            if form.strava_description__BY__training_type.data != data['strava_description__BY__training_type']:
                value = None
                if len(form.strava_description__BY__training_type.data) > 0:
                    if form.strava_description__BY__training_type.data.count("?") == 1:
                        parts = form.strava_description__BY__training_type.data.split("?",1)
                        value = f"training_type({parts[0]})?{parts[1]}"
                    else:
                        message.append(f"'strava_description__BY__training_type': Invalid value !")
                        err = True
                else:
                    value = ""

                if not err:
                    print(f"data='{value}'")
                    if len(value) == 0:
                        ret = subprocess.run(
                            [sys.executable, 'main.py', 'config', '--delete', 'strava_description__BY__training_type'],
                            stdout=subprocess.PIPE, text=True)
                        if ret.returncode != 0:
                            message.append(f"Delete 'strava_description__BY__training_type' failed !")
                            err = True

                    else:
                        ret = subprocess.run(
                            [sys.executable, 'main.py', 'config', '--strava_description', value],
                            stdout=subprocess.PIPE, text=True)
                        if ret.returncode != 0:
                            message.append(f"Update 'strava_description__BY__training_type' failed !")
                            err = True


            # print(f"form.strava_client_id.data={form.strava_client_id.data}, data={data['strava_client_id']}")
            if form.strava_client_id.data != data['strava_client_id']:
                if len(form.strava_client_id.data) > 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--strava_client_id', form.strava_client_id.data],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Update 'strava_client_id' failed !")
                        err = True
                else:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'strava_client_id'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        message.append(f"Delete 'strava_client_id' failed !")
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

    # Data can be set to default value, so read again
    res = subprocess.run([sys.executable, 'main.py', 'config', '--list'], stdout=subprocess.PIPE, text=True)
    context = dict(output=format(res.stdout))

    if form.is_submitted():
        context['message'] = message

    data = format_config_list(res.stdout)

    form.port.data = data['port']
    form.velohero_sso_id.data = data['velohero_sso_id']
    form.strava_client_id.data = data['strava_client_id']
    form.garmin_connect_username.data = data['garmin_connect_username']
    form.garmin_connect_password.data = data['garmin_connect_password']
    form.strava_description__BY__strava_name.data = data['strava_description__BY__strava_name']
    form.strava_description__BY__training_type.data = data['strava_description__BY__training_type']
    form.strava_reset.data = False

    # print(f"context={context}")
    # print(f"form={form.garmin_connect_username}")

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
