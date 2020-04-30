import re
import subprocess
import sys

from flask import render_template, redirect, url_for, session, make_response, request

import strava
from webapp import app
from webapp.configForm import ConfigForm
from webapp.downloadForm import DownloadForm
from webapp.transferForm import TransferForm

@app.route('/authenticate-strava', methods=['GET', 'POST'])
def authenticate_strava():
    session.clear()
    base_url = strava.get_strava_authorization_url(request.url_root)
    print(f"Redirection to url={base_url}")

    response = make_response(redirect(base_url, 302))
    return response

@app.route('/')
@app.route('/index')
def index():

    print(f"index() session={session}\n request={request}")

    #if a code is being returned from authorization
    if request.args.get('code'):
        strava_code = request.args.get('code')
        print(f"New Strava code={strava_code}")
        #take code and convert to token
        strava.obtain_new_token(strava_code)

    # if this is the user's first visit, load page for authentication
    if strava.need_strava_authorization():
        print("App needs to be authorized by Strava")
        return redirect(url_for('authenticate_strava'))


    if 'messages' in session:
        messages = session['messages']       # counterpart for session
        session['messages'] = None
    else:
        messages = None

    res_load_info = subprocess.run([sys.executable, 'main.py', 'load', '--info'], stdout=subprocess.PIPE, text=True)

    res_show = subprocess.run([sys.executable, 'main.py', 'show'], stdout=subprocess.PIPE, text=True)
    context = dict(load_info=format(res_load_info.stdout), show=format(res_show.stdout), messages=messages)

    return render_template('index.html', title='Home', context=context)


@app.route('/authenticate', methods=['GET', 'POST'])
def auth():
    session.clear()
    base_url = strava.get_strava_authorization_url(request.url_root)
    response = make_response(redirect(base_url, 302))
    return response


@app.route('/staging')
def staging():
    res = subprocess.run([sys.executable, 'main.py', 'show'], stdout=subprocess.PIPE, text=True)

    # print(f"session={session}")
    if 'messages' in session:
        messages = session['messages']       # counterpart for session
        session['messages'] = None
    else:
        messages = None

    result=get_show_output(res.stdout)
    # print(f"result={result}")
    print(result)
    context = dict(result=result, messages=messages)

    return render_template('staging.html', title='Staging', context=context)


@app.route('/load')
def load():

    # # Ensure that app is authorized at Strava
    # if strava.need_strava_authorization():
    #     url = strava.get_strava_authorization_url(url_for("/authorize"))


    res_load = subprocess.run([sys.executable, 'main.py', 'load', '--strava'], stdout=subprocess.PIPE, text=True)
    res_status = subprocess.run([sys.executable, 'main.py', 'show'], stdout=subprocess.PIPE, text=True)
    context = dict(messages=format(res_load.stdout), result=get_show_output(res_status.stdout))

    return render_template('staging.html', title='Staging', context=context)


@app.route('/purge')
def purge():
    return render_template('purge.html', title='Purge', context=None)


@app.route('/download', methods=['GET', 'POST'])
def download():
    res = subprocess.run([sys.executable, 'main.py', 'download', '--info'], stdout=subprocess.PIPE, text=True)
    output = format(res.stdout)

    if output[0].startswith("Last downloaded activity"):
        default = "N"
    else:
        default = "L"

    form = DownloadForm(type=default,
                        nr_of_latest=5, )

    messages = []
    if form.is_submitted():
        err = False

        if form.validate():

            if form.type == "L" and not form.nr_of_latest > 0:
                messages.append("L wrong")
                messages.append("Missing number of activities !")
                err = True
            else:
                # print(f"form.type={form.type.data}")
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
                        messages.append(line)

                    # Print the rest
                    for line in p.stdout.readlines():
                        print(line)
                        messages.append(line)

                    # Print the rest
                    for line in p.stderr.readlines():
                        print(line)
                        messages.append(line)

                print("done")
                res = subprocess.run([sys.executable, 'main.py', 'download', '--info'], stdout=subprocess.PIPE,
                                     text=True)
                output = format(res.stdout)

        else:
            err = True
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    messages.append(f"{fieldName}: '{err}'")

    context = dict(output=output, messages=messages)

    return render_template('download.html', title='Donwload', form=form, context=context)


@app.route('/config', methods=['GET', 'POST'])
def config():
    res = subprocess.run([sys.executable, 'main.py', 'config', '--list'], stdout=subprocess.PIPE, text=True)
    data = format_config_list(res.stdout)

    form = ConfigForm(port=data['port'],
                      archive_dir=data['archive_dir'],
                      load_dir=data['load_dir'],
                      velohero_sso_id=data['velohero_sso_id'],
                      strava_client_id=data['strava_client_id'],
                      garmin_connect_username=data['garmin_connect_username'],
                      garmin_connect_password=data['garmin_connect_password'],
                      strava_description__BY__strava_name=data['strava_description__BY__strava_name'],
                      strava_description__BY__training_type=data['strava_description__BY__training_type'],
                      strava_reset=False
                      )

    messages = []
    if form.is_submitted():
        err = False

        if form.validate():
            if form.archive_dir.data != data['archive_dir']:
                if len(form.archive_dir.data) == 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'archive_dir'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Delete 'archive_dir' failed !")
                        err = True
                else:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--archive_dir', str(form.archive_dir.data)],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Update 'archive_dir' failed !")
                        err = True

            if form.load_dir.data != data['load_dir']:
                if len(form.load_dir.data) == 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'load_dir'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Delete 'load_dir' failed !")
                        err = True
                else:
                    ret = subprocess.run([sys.executable, 'main.py', 'config', '--load_dir', str(form.load_dir.data)],
                                         stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Update 'load_dir' failed !")
                        err = True

            if form.port.data != data['port']:
                if form.port.data < 1:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'port'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Delete 'port' failed !")
                        err = True
                else:
                    ret = subprocess.run([sys.executable, 'main.py', 'config', '--port', str(form.port.data)],
                                         stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Update 'port' failed !")
                        err = True

            if form.velohero_sso_id.data != data['velohero_sso_id']:
                if len(form.velohero_sso_id.data) == 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'velohero_sso_id'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Delete 'velohero_sso_id    ' failed !")
                        err = True
                else:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--velohero_sso_id', str(form.velohero_sso_id.data)],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Update 'velohero_sso_id' failed !")
                        err = True

            if form.garmin_connect_username.data != data['garmin_connect_username']:
                if len(form.garmin_connect_username.data) == 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'garmin_connect_username'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Delete 'garmin_connect_username    ' failed !")
                        err = True
                else:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--garmin_connect_username',
                         str(form.garmin_connect_username.data)],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Update 'garmin_connect_username' failed !")
                        err = True

            if form.garmin_connect_password.data != data['garmin_connect_password']:
                if len(form.garmin_connect_password.data) == 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'garmin_connect_password'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Delete 'garmin_connect_password    ' failed !")
                        err = True
                else:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--garmin_connect_password',
                         str(form.garmin_connect_password.data)],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Update 'garmin_connect_password' failed !")
                        err = True

            if form.strava_description__BY__strava_name.data != data['strava_description__BY__strava_name']:
                value = None
                if len(form.strava_description__BY__strava_name.data) > 0:
                    if form.strava_description__BY__strava_name.data.count("?") == 1:
                        parts = form.strava_description__BY__strava_name.data.split("?", 1)
                        value = f"strava_name({parts[0]})?{parts[1]}"
                    else:
                        messages.append(f"'strava_description__BY__strava_name': Invalid value !")
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
                            messages.append(f"Delete 'strava_description__BY__strava_name' failed !")
                            err = True

                    else:
                        ret = subprocess.run(
                            [sys.executable, 'main.py', 'config', '--strava_description', value],
                            stdout=subprocess.PIPE, text=True)
                        if ret.returncode != 0:
                            messages.append(f"Update 'strava_description__BY__strava_name' failed !")
                            err = True

            if form.strava_description__BY__training_type.data != data['strava_description__BY__training_type']:
                value = None
                if len(form.strava_description__BY__training_type.data) > 0:
                    if form.strava_description__BY__training_type.data.count("?") == 1:
                        parts = form.strava_description__BY__training_type.data.split("?", 1)
                        value = f"training_type({parts[0]})?{parts[1]}"
                    else:
                        messages.append(f"'strava_description__BY__training_type': Invalid value !")
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
                            messages.append(f"Delete 'strava_description__BY__training_type' failed !")
                            err = True

                    else:
                        ret = subprocess.run(
                            [sys.executable, 'main.py', 'config', '--strava_description', value],
                            stdout=subprocess.PIPE, text=True)
                        if ret.returncode != 0:
                            messages.append(f"Update 'strava_description__BY__training_type' failed !")
                            err = True

            # print(f"form.strava_client_id.data={form.strava_client_id.data}, data={data['strava_client_id']}")
            if form.strava_client_id.data != data['strava_client_id']:
                if len(form.strava_client_id.data) > 0:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--strava_client_id', form.strava_client_id.data],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Update 'strava_client_id' failed !")
                        err = True
                else:
                    ret = subprocess.run(
                        [sys.executable, 'main.py', 'config', '--delete', 'strava_client_id'],
                        stdout=subprocess.PIPE, text=True)
                    if ret.returncode != 0:
                        messages.append(f"Delete 'strava_client_id' failed !")
                        err = True

            if form.strava_reset.data:
                ret = subprocess.run([sys.executable, 'main.py', 'config', '--strava_reset'],
                                     stdout=subprocess.PIPE, text=True)
                if ret.returncode != 0:
                    messages.append("Strava reset failed !")
                    err = True

        else:
            err = True
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    messages.append(f"{fieldName}: '{err}'")

        if err is False:
            messages.append("Saved !")
            res = subprocess.run([sys.executable, 'main.py', 'config', '--list'], stdout=subprocess.PIPE, text=True)

    # Data can be set to default value, so read again
    res = subprocess.run([sys.executable, 'main.py', 'config', '--list'], stdout=subprocess.PIPE, text=True)
    context = dict(output=format(res.stdout))

    if form.is_submitted():
        context['messages'] = messages

    data = format_config_list(res.stdout)

    form.port.data = data['port']
    form.archive_dir.data = data['archive_dir']
    form.load_dir.data = data['load_dir']
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


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    print("Transfer")
    res = subprocess.run([sys.executable, 'main.py', 'show'], stdout=subprocess.PIPE, text=True)
    result=get_show_output(res.stdout)
    context = dict(result=result)

    form = TransferForm(velohero=result['velohero'] == False,
                        strava=result['strava'],
                        archive= result['archived'] == False,
                        )

    messages = []
    if form.is_submitted():
        err = False

        if form.validate():
            pass
            if form.velohero.data:
                ret = subprocess.run([sys.executable, 'main.py', 'transfer', '--velohero'],
                                     stdout=subprocess.PIPE, text=True)
                if ret.returncode == 0:
                    messages.append("Velohero uploaded.")
                else:
                    messages.append("Velohero upload failed !")
                    err = True

            if form.strava.data:
                ret = subprocess.run([sys.executable, 'main.py', 'transfer', '--strava'],
                                     stdout=subprocess.PIPE, text=True)
                if ret.returncode == 0:
                    messages.append("Strava uploaded.")
                else:
                    messages.append("Strava upload failed !")
                    err = True

            if form.archive.data:
                ret = subprocess.run([sys.executable, 'main.py', 'transfer', '--archive'],
                                     stdout=subprocess.PIPE, text=True)
                if ret.returncode == 0:
                    messages.append("Track file archived.")
                else:
                    messages.append("Failed to archive the track file !")
                    err = True

        else:
            err = True
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    messages.append(f"{fieldName}: '{err}'")

        session['messages'] = messages

        res_load_info = subprocess.run([sys.executable, 'main.py', 'load', '--info'], stdout=subprocess.PIPE, text=True)
        if res_load_info.stdout.strip().startswith("No track file found in "):
            return redirect(url_for('index') )
        else:
            return redirect(url_for('staging') )

    return render_template('transfer.html', title='Transfer', form=form, context=context)


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

    context = dict(output=format(res_list.stdout), messages=format(res_refresh.stdout))

    return render_template('masterdata.html', title='Masterdata', context=context)


def format_config_list(text):
    """"
    Returns a dictionary with key value pairs and special keys for
        - List of Strings 'descriptions'
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


def get_show_output(text):
    """"
    Returns a dict with:
        - List of Strings 'output'
        - Boolean 'file' with false, if file not found. Otherwise true
        - Boolean 'velohero' with false, if there is no ID. Otherwise true
        - Boolean 'strava' with false, if there is no ID. Otherwise true
        - Boolean 'archived' with false, if not archived. Otherwise true
        - Boolean 'loaded' with false, if no Load exists
    """
    ret = dict()

    ret['output'] = format(text)

    # print(f"text={text}")
    if text.strip().startswith('No activity loaded yet.'):
        ret['file'] = False
        ret['strava'] = False
        ret['velohero'] = False
        ret['archived'] = False
        ret['loaded'] = False
        return ret

    ret['loaded'] = True
    for line in format(text):
        if ": " in line:
            (key, value) = line.split(": ", 1)

            if key.strip().lower() == "file name":
                ret['file'] = (re.match(".*MISSING.*", value) is None)
                print(f"check file name={ret['file']}")

            elif key.strip().lower() == "activity id":
                ret['strava'] = value.lower().strip() != 'none'

            elif key.strip().lower() == "velohero workout id":
                ret['velohero'] = value.lower().strip() != 'none'

            elif key.strip().lower() == "archived to":
                ret['archived'] = value.lower().strip() != 'none'

    # print(f"ret={ret}")

    return ret
